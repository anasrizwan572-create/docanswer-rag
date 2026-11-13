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

