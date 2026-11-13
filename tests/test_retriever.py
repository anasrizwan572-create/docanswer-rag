import pytest
from api.retriever import Retriever, HybridRetriever
from api.models import RetrievedChunk


def test_retriever_subclass_interface():
    assert issubclass(HybridRetriever, Retriever)


def test_retriever_top_k_chunks():
    retriever = HybridRetriever()
    chunks = retriever.retrieve("What is the 401(k) company match?", top_k=4)
    assert len(chunks) == 4
    for c in chunks:
        assert isinstance(c, RetrievedChunk)
        assert c.score >= 0.0
        assert c.score <= 1.0
        assert c.source == "acme_corp_hr_policy.pdf"
        assert c.page >= 1


def test_retriever_exact_section_boost():
    retriever = HybridRetriever()
    chunks = retriever.retrieve("What are the terms of Section 2.4?", top_k=4)
    top_chunk = chunks[0]
    assert "2.4" in top_chunk.section or "2.4" in top_chunk.text

