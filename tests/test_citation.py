import pytest
from api.generator import AnswerGenerator
from api.models import RetrievedChunk


@pytest.fixture
def sample_chunks():
    return [
        RetrievedChunk(
            chunk_id="chunk_1",
            source="acme_corp_hr_policy.pdf",
            page=2,
            section="Section 2.3",
            text="Qualified remote employees receive a monthly internet connectivity stipend of $60 USD.",
            score=0.95
        ),
        RetrievedChunk(
            chunk_id="chunk_2",
            source="acme_corp_hr_policy.pdf",
            page=2,
            section="Section 2.3",
            text="Remote employees are eligible for a one-time reimbursement of up to $800 USD.",
            score=0.90
        )
    ]


def test_citation_validation_in_bounds(sample_chunks):
    gen = AnswerGenerator()
    valid_answer = "Remote employees receive a $60 monthly subsidy [1] and up to $800 for home office setup [2]."
    is_valid, cited_ids = gen._validate_citations(valid_answer, len(sample_chunks))
    assert is_valid is True
    assert cited_ids == [1, 2]


def test_citation_validation_out_of_bounds(sample_chunks):
    gen = AnswerGenerator()
    invalid_answer = "Employees receive standard coverage [3]."
    is_valid, cited_ids = gen._validate_citations(invalid_answer, len(sample_chunks))
    assert is_valid is False
    assert cited_ids == [3]


def test_citation_mapping_in_response(sample_chunks):
    gen = AnswerGenerator()
    q = "What stipends do remote employees get?"
    resp = gen.generate(q, sample_chunks)
    assert resp.found is True
    assert len(resp.citations) >= 1
    for cit in resp.citations:
        assert cit.id in [1, 2]
        assert cit.source == "acme_corp_hr_policy.pdf"
        assert cit.page == 2
        assert cit.section == "Section 2.3"
