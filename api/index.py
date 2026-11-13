
import json
from typing import Dict, Any

import chromadb
from fastapi import FastAPI, HTTPException, Request

from api.config import settings
from api.models import QueryRequest, QueryResponse
from api.retriever import HybridRetriever
from api.generator import AnswerGenerator
from api.utils import ensure_index_ready, check_rate_limit


app = FastAPI(
    title="DocAnswer API",
    description="Enterprise RAG Assistant with Strict Citations and Refusals",
    version="1.0.0"
)


# Global pipeline singletons (lazy-loaded on cold start)
_retriever = None
_generator = None


def get_pipeline():
    global _retriever, _generator

    if _retriever is None:
        index_dir = ensure_index_ready()
        _retriever = HybridRetriever(index_dir=index_dir)

    if _generator is None:
        _generator = AnswerGenerator()

    return _retriever, _generator


@app.post("/api/query", response_model=QueryResponse)
def query_document(
    request: QueryRequest,
    http_request: Request
) -> QueryResponse:

    client_ip = (
        http_request.client.host
        if http_request.client
        else "unknown"
    )

    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    try:
        retriever, generator = get_pipeline()

        chunks = retriever.retrieve(
            request.question,
            top_k=settings.TOP_RERANKED
        )

        result = generator.generate(
            request.question,
            chunks
        )

        return result

    except Exception as e:
        print(f"Query processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to process your question."
        )


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "DocAnswer",
        "version": "1.0.0",
        "index_ready": (
            ensure_index_ready() / "chroma_db"
        ).exists()
    }


@app.get("/api/document-info")
def document_info() -> Dict[str, Any]:
    index_dir = ensure_index_ready()
    bm25_file = index_dir / "bm25_index.json"
    chroma_dir = index_dir / "chroma_db"

    try:
        with open(bm25_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        chunks = data.get("chunks", [])

        pages = {
            chunk.get("page")
            for chunk in chunks
            if chunk.get("page") is not None
        }

        client = chromadb.PersistentClient(
            path=str(chroma_dir)
        )

        collection = client.get_collection(
            name="hr_policy"
        )

        chroma_count = collection.count()
        bm25_count = len(chunks)

        return {
            "title": "Acme Technologies Global HR Policies and Employee Handbook",
            "edition": "2026 Edition",
            "document_ref": "ACME-HR-2026-V4.2",
            "pages": len(pages),
            "total_chunks": chroma_count,
            "bm25_chunks": bm25_count,
            "counts_match": chroma_count == bm25_count,
            "index_ready": True,
            "format": "PDF",
            "classification": "Confidential - Internal Company Policy"
        }

    except Exception as e:
        print(f"Document info error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Document index information is currently unavailable."
        )
