from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

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

# Enable CORS for Next.js client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "DocAnswer",
        "version": "1.0.0",
        "index_ready": (ensure_index_ready() / "chroma_db").exists()
    }


@app.get("/api/document-info")
def document_info() -> Dict[str, Any]:
    return {
        "title": "Acme Technologies Global HR Policies and Employee Handbook",
        "edition": "2026 Edition",
        "document_ref": "ACME-HR-2026-V4.2",
        "pages": 16,
        "total_chunks": 75,
        "format": "PDF",
        "classification": "Confidential - Internal Company Policy"
    }


@app.post("/api/query", response_model=QueryResponse)
async def query_document(request: Request, body: QueryRequest) -> QueryResponse:
    # 1. Rate limiting check per client IP
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute permitted."
        )

    # 2. Max length enforcement (also guarded by Pydantic QueryRequest validator)
    cleaned_question = body.question.strip()
    if len(cleaned_question) > settings.MAX_QUESTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Question exceeds maximum permitted length of {settings.MAX_QUESTION_LENGTH} characters."
        )

    # 3. Retrieve top passages and synthesize certified answer
    try:
        retriever, generator = get_pipeline()
        chunks = retriever.retrieve(cleaned_question, top_k=settings.TOP_RERANKED)
        response = generator.generate(cleaned_question, chunks)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal generation error: {str(e)}")
