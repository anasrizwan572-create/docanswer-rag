"""
Offline Ingestion Script for DocAnswer.
Parses PDF page by page, extracts metadata (page number, section headings),
chunks via RecursiveCharacterTextSplitter (~800 chars, 150 overlap),
generates hosted/deterministic embeddings, and builds offline ChromaDB + BM25 index in /index.
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pypdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

from api.config import settings
from api.embeddings import get_embedding_function


HEADING_LINE_PATTERN = re.compile(
    r"^(?:Section\s+\d+[:\.\s]+[A-Za-z0-9\s,&/Î“Ã‡Ã´Î“Ã‡Ã¶\(\)]+|\d+\.\d+(?:\.\d+)?\s+[A-Za-z0-9\s,&/Î“Ã‡Ã´Î“Ã‡Ã¶\(\)]+|##\s+[^\n]+|###\s+[^\n]+)$",
    re.IGNORECASE
)



def extract_pages_with_metadata(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Parses PDF page by page and preserves the section active
    at the beginning of each page.
    """
    reader = pypdf.PdfReader(str(pdf_path))
    pages_data = []
    current_section = "General Information"

    for page_idx, page in enumerate(reader.pages, start=1):
        page_start_section = current_section

        text = page.extract_text() or ""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned_lines = []

        for line in lines:
            if (
                re.match(r"^Page \d+ of \d+", line)
                or "CONFIDENTIAL & PROPRIETARY" in line
                or "Document Ref: ACME" in line
                or "Acme Technologies Inc." in line
            ):
                continue

            if HEADING_LINE_PATTERN.match(line) and len(line) < 90:
                current_section = line.replace('#', '').strip()

            cleaned_lines.append(line)

        pages_data.append({
            "page_num": page_idx,
            "section": page_start_section,
            "text": "\n".join(cleaned_lines)
        })

    return pages_data



def detect_chunk_heading(chunk_text: str, default_section: str) -> str:
    """
    Finds if chunk text contains a specific heading line.
    Ignores parenthetical cross-references like '(see Section 9.4)'.
    """
    lines = chunk_text.split("\n")
    for line in lines:
        line_clean = line.strip()
        if HEADING_LINE_PATTERN.match(line_clean) and len(line_clean) < 90:
            return line_clean.replace("#", "").strip()
    return default_section



def chunk_document(
    pages_data: List[Dict[str, Any]],
    source_name: str
) -> List[Dict[str, Any]]:
    """
    Splits each section independently.
    Overlap is allowed within a section but never across section boundaries.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", ", ", " "]
    )

    all_chunks = []
    chunk_counter = 0

    for page_data in pages_data:
        page_num = page_data["page_num"]
        active_section = page_data["section"]
        current_lines = []
        segments = []

        for line in page_data["text"].splitlines():
            line = line.strip()
            if not line:
                continue

            is_heading = (
                HEADING_LINE_PATTERN.match(line) is not None
                and len(line) < 90
            )

            if is_heading:
                if current_lines:
                    segments.append({
                        "section": active_section,
                        "text": "\n".join(current_lines)
                    })

                active_section = line.replace("#", "").strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            segments.append({
                "section": active_section,
                "text": "\n".join(current_lines)
            })

        for segment in segments:
            section = segment["section"]
            raw_chunks = splitter.split_text(segment["text"])

            for chunk_text in raw_chunks:
                chunk_text = chunk_text.strip()

                if not chunk_text or len(chunk_text) < 25:
                    continue

                chunk_counter += 1

                all_chunks.append({
                    "chunk_id": f"chunk_p{page_num}_{chunk_counter}",
                    "source": source_name,
                    "page": page_num,
                    "section": section,
                    "text": chunk_text
                })

    return all_chunks



def build_bm25_index(chunks: List[Dict[str, Any]], output_file: Path):
    """
    Builds and serializes BM25 corpus and metadata for offline keyword retrieval.
    """
    print(f"Building BM25 index for {len(chunks)} chunks...")
    corpus = []
    for c in chunks:
        # Tokenize chunk text + section metadata for BM25 matching (preserving section numbers like 2.4)
        combined = f"{c['section']} {c['text']}"
        tokens = re.findall(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*", combined.lower())
        corpus.append(tokens)

    index_payload = {
        "chunks": chunks,
        "tokenized_corpus": corpus,
        "total_chunks": len(chunks)
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, indent=2)
    print(f"[OK] BM25 index saved to {output_file}")


def build_chroma_index(chunks: List[Dict[str, Any]], index_dir: Path):
    """
    Builds offline Chroma vector database with embeddings.
    """
    chroma_dir = index_dir / "chroma_db"
    if chroma_dir.exists():
        print(f"Clearing previous Chroma store at {chroma_dir}...")
        shutil.rmtree(chroma_dir)
    chroma_dir.mkdir(parents=True, exist_ok=True)

    print(f"Initializing Chroma client at {chroma_dir}...")
    client = chromadb.PersistentClient(path=str(chroma_dir))

    embedding_fn = get_embedding_function()
    print(f"Using embedding function: {type(embedding_fn).__name__}")

    collection = client.create_collection(
        name="hr_policy",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "page": c["page"],
            "section": c["section"],
            "chunk_id": c["chunk_id"]
        }
        for c in chunks
    ]

    print(f"Computing embeddings for {len(documents)} chunks...")
    embeddings = embedding_fn(documents)

    print("Adding vectors to Chroma collection...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print(f"[OK] Chroma index built with {collection.count()} vectors.")


def main():
    pdf_path = settings.DATA_DIR / "acme_corp_hr_policy.pdf"
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    print(f"[1/4] Parsing PDF: {pdf_path}...")
    pages_data = extract_pages_with_metadata(pdf_path)
    print(f"[OK] Extracted {len(pages_data)} pages.")

    print(f"[2/4] Chunking document...")
    chunks = chunk_document(pages_data, source_name="acme_corp_hr_policy.pdf")
    print(f"[OK] Generated {len(chunks)} chunks.")

    # Create index directory
    settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[3/4] Building BM25 index...")
    bm25_file = settings.INDEX_DIR / "bm25_index.json"
    build_bm25_index(chunks, bm25_file)

    print(f"[4/4] Building Chroma index...")
    build_chroma_index(chunks, settings.INDEX_DIR)

    print("\nÎ“Â£Ã  Ingestion complete! Index committed to /index.")


if __name__ == "__main__":
    main()
