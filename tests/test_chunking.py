import pytest
from pathlib import Path
from scripts.ingest import extract_pages_with_metadata, chunk_document, detect_chunk_heading
from api.config import settings


def test_pdf_extraction_page_count():
    pdf_path = settings.DATA_DIR / "acme_corp_hr_policy.pdf"
    assert pdf_path.exists(), "acme_corp_hr_policy.pdf must exist in /data"
    pages = extract_pages_with_metadata(pdf_path)
    assert len(pages) >= 15, f"Expected 15+ pages, got {len(pages)}"


def test_chunking_metadata_fields():
    pdf_path = settings.DATA_DIR / "acme_corp_hr_policy.pdf"
    pages = extract_pages_with_metadata(pdf_path)
    chunks = chunk_document(pages, "acme_corp_hr_policy.pdf")

    assert len(chunks) > 0
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "source" in chunk
        assert "page" in chunk
        assert "section" in chunk
        assert "text" in chunk
        assert isinstance(chunk["page"], int)
        assert len(chunk["text"]) >= 25


def test_heading_detection_avoids_parenthetical_citations():
    default_sec = "Section 2.3 Remote Work Stipend"
    cross_ref = "Hardware must be returned within 48 hours of termination (see Section 9.4)."
    detected = detect_chunk_heading(cross_ref, default_sec)
    assert detected == default_sec, "Cross-reference (see Section 9.4) should NOT become section heading"

    valid_heading = "3.2 Sick Leave and Medical Certification\nEmployees receive 10 days..."
    detected_valid = detect_chunk_heading(valid_heading, default_sec)
    assert "3.2 Sick Leave" in detected_valid



def test_chunking_does_not_cross_section_boundaries():
    pages_data = [{
        "page_num": 1,
        "section": "General Information",
        "text": (
            "2.1 Standard Working Hours\n"
            + ("FIRST_SECTION_MARKER employee working hours policy details. " * 20)
            + "\n2.2 Remote Work Policy\n"
            + ("SECOND_SECTION_MARKER remote work policy details. " * 20)
        )
    }]

    chunks = chunk_document(pages_data, "test.pdf")

    first_section = [
        c for c in chunks
        if c["section"] == "2.1 Standard Working Hours"
    ]
    second_section = [
        c for c in chunks
        if c["section"] == "2.2 Remote Work Policy"
    ]

    assert first_section
    assert second_section

    assert all(
        "SECOND_SECTION_MARKER" not in c["text"]
        for c in first_section
    )
    assert all(
        "FIRST_SECTION_MARKER" not in c["text"]
        for c in second_section
    )


def test_chunk_ids_are_unique_across_pages():
    pages_data = [
        {
            "page_num": 1,
            "section": "General Information",
            "text": "First page contains enough text for a valid test chunk."
        },
        {
            "page_num": 2,
            "section": "General Information",
            "text": "Second page contains enough text for a valid test chunk."
        }
    ]

    chunks = chunk_document(pages_data, "test.pdf")
    chunk_ids = [c["chunk_id"] for c in chunks]

    assert len(chunk_ids) >= 2
    assert len(chunk_ids) == len(set(chunk_ids))
