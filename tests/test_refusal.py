import pytest
from api.generator import AnswerGenerator
from api.retriever import HybridRetriever

REFUSAL_STRING = "I couldn't find this in the provided documents."

@pytest.fixture
def pipeline():
    return HybridRetriever(), AnswerGenerator()


def test_refusal_unanswerable_pet_insurance(pipeline):
    retriever, generator = pipeline
    q = "What is the reimbursement limit and deductible for pet health insurance?"
    chunks = retriever.retrieve(q, top_k=4)
    resp = generator.generate(q, chunks)

    assert resp.found is False
    assert resp.answer == REFUSAL_STRING
    assert resp.citations == []


def test_refusal_unanswerable_stock_options(pipeline):
    retriever, generator = pipeline
    q = "How are stock options and RSUs granted and what is the equity vesting schedule?"
    chunks = retriever.retrieve(q, top_k=4)
    resp = generator.generate(q, chunks)

    assert resp.found is False
    assert resp.answer == REFUSAL_STRING
    assert resp.citations == []


def test_refusal_unanswerable_company_car(pipeline):
    retriever, generator = pipeline
    q = "Does Acme provide a monthly company car allowance or electric vehicle lease?"
    chunks = retriever.retrieve(q, top_k=4)
    resp = generator.generate(q, chunks)

    assert resp.found is False
    assert resp.answer == REFUSAL_STRING
    assert resp.citations == []


def test_refusal_empty_chunks():
    generator = AnswerGenerator()
    resp = generator.generate("Any question?", [])
    assert resp.found is False
    assert resp.answer == REFUSAL_STRING
    assert resp.citations == []

