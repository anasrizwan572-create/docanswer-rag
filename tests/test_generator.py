
import json

import pytest

from api.generator import AnswerGenerator, REFUSAL_PHRASE
from api.models import RetrievedChunk


@pytest.fixture
def sample_chunks():
    return [
        RetrievedChunk(
            chunk_id="chunk_1",
            source="acme_corp_hr_policy.pdf",
            page=2,
            section="Section 2.3",
            text=(
                "Qualified remote employees receive "
                "a monthly internet connectivity stipend of $60 USD."
            ),
            score=0.95,
        ),
        RetrievedChunk(
            chunk_id="chunk_2",
            source="acme_corp_hr_policy.pdf",
            page=3,
            section="Section 2.4",
            text=(
                "Remote employees are eligible for "
                "a one-time reimbursement of up to $800 USD."
            ),
            score=0.90,
        ),
    ]


def make_response(answer, citations, found=True, confidence="high"):
    return json.dumps({
        "answer": answer,
        "cited_passage_ids": citations,
        "confidence": confidence,
        "found": found,
    })


def test_gemini_generates_answer(monkeypatch, sample_chunks):
    generator = AnswerGenerator()
    generator.gemini_client = object()
    calls = []

    def fake_gemini(prompt, system=None):
        calls.append(prompt)
        return make_response(
            "Remote employees receive a $60 monthly stipend [1].",
            [1],
        )

    monkeypatch.setattr(generator, "_call_gemini", fake_gemini)

    result = generator.generate(
        "What monthly stipend do remote employees receive?",
        sample_chunks,
    )

    assert len(calls) == 1
    assert result.found is True
    assert "$60" in result.answer
    assert len(result.citations) == 1
    assert result.citations[0].id == 1


def test_gemini_failure_uses_offline_fallback(
    monkeypatch, sample_chunks
):
    generator = AnswerGenerator()
    generator.gemini_client = object()

    def failing_gemini(prompt, system=None):
        raise RuntimeError("Simulated Gemini API failure")

    monkeypatch.setattr(
        generator,
        "_call_gemini",
        failing_gemini,
    )

    result = generator.generate(
        "What monthly stipend do remote employees receive?",
        sample_chunks,
    )

    assert result.found is True
    assert len(result.citations) >= 1


def test_gemini_invalid_json_uses_offline_fallback(
    monkeypatch, sample_chunks
):
    generator = AnswerGenerator()
    generator.gemini_client = object()

    monkeypatch.setattr(
        generator,
        "_call_gemini",
        lambda prompt, system=None: "This is not JSON",
    )

    result = generator.generate(
        "What monthly stipend do remote employees receive?",
        sample_chunks,
    )

    assert result.found is True
    assert len(result.citations) >= 1


def test_gemini_invalid_citation_retries(
    monkeypatch, sample_chunks
):
    generator = AnswerGenerator()
    generator.gemini_client = object()
    responses = [
        make_response(
            "Remote employees receive a stipend [9].",
            [9],
        ),
        make_response(
            "Remote employees receive a $60 monthly stipend [1].",
            [1],
        ),
    ]

    calls = []

    def fake_gemini(prompt, system=None):
        calls.append(prompt)
        return responses.pop(0)

    monkeypatch.setattr(generator, "_call_gemini", fake_gemini)

    result = generator.generate(
        "What monthly stipend do remote employees receive?",
        sample_chunks,
    )

    assert len(calls) == 2
    assert result.found is True
    assert "$60" in result.answer
    assert [citation.id for citation in result.citations] == [1]


def test_gemini_refusal_is_preserved(
    monkeypatch, sample_chunks
):
    generator = AnswerGenerator()
    generator.gemini_client = object()

    monkeypatch.setattr(
        generator,
        "_call_gemini",
        lambda prompt, system=None: make_response(
            REFUSAL_PHRASE,
            [],
            found=False,
        ),
    )

    result = generator.generate(
        "Does the company provide pet insurance?",
        sample_chunks,
    )

    assert result.found is False
    assert result.answer == REFUSAL_PHRASE
    assert result.citations == []


def test_citation_metadata_mapping(sample_chunks):
    generator = AnswerGenerator()
    generator.gemini_client = object()

    monkeypatch = pytest.MonkeyPatch()
    try:
        monkeypatch.setattr(
            generator,
            "_call_gemini",
            lambda prompt, system=None: make_response(
                "Remote employees receive $60 monthly [1].",
                [1],
            ),
        )

        result = generator.generate(
            "What monthly stipend do remote employees receive?",
            sample_chunks,
        )

        citation = result.citations[0]

        assert citation.id == 1
        assert citation.source == "acme_corp_hr_policy.pdf"
        assert citation.page == 2
        assert citation.section == "Section 2.3"
        assert citation.passage_text == sample_chunks[0].text

    finally:
        monkeypatch.undo()


def test_empty_chunks_return_exact_refusal():
    generator = AnswerGenerator()

    result = generator.generate("Any question?", [])

    assert result.found is False
    assert result.answer == REFUSAL_PHRASE
    assert result.citations == []


def test_offline_fallback_refuses_when_no_relevant_sentence():
    generator = AnswerGenerator()

    chunks = [
        RetrievedChunk(
            chunk_id="chunk_1",
            source="acme_corp_hr_policy.pdf",
            page=11,
            section="Section 11.2",
            text=(
                "Any workplace injury must be reported "
                "to the Safety Coordinator within "
                "twenty-four hours."
            ),
            score=0.95,
        )
    ]

    result = generator._offline_fallback_generator(
        "What are the core collaboration hours?",
        chunks,
    )

    assert result["found"] is False
    assert result["answer"] == REFUSAL_PHRASE
    assert result["cited_passage_ids"] == []
