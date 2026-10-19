import pytest
from fastapi.testclient import TestClient

from main import app
from app.schemas.ocr_schema import Recipient, OCRResult

client = TestClient(app)


def test_recipient_extraction_contract():
    """Verify that recipient schema adheres strictly to extraction-only fields."""
    recipient = Recipient(
        raw_text="1. HOD - CSE",
        text="HOD - CSE",
        type="printed",
        confidence=0.98,
        source_page=1
    )
    assert recipient.raw_text == "1. HOD - CSE"
    assert recipient.text == "HOD - CSE"
    assert recipient.type == "printed"
    assert recipient.confidence == 0.98
    assert recipient.source_page == 1

    # Ensure no employee matching or email fields are required or attached
    data = recipient.model_dump()
    assert "matched_email" not in data
    assert "matched_entry" not in data
    assert "email" not in data


def test_abbreviation_preservation_in_recipient_contract():
    """Verify common abbreviations are preserved as extracted without expansions."""
    sample_texts = ["HOD - CSE", "PO - CSE", "Dean Acad.", "VP - Admin"]
    recipients = [
        Recipient(raw_text=f"{i+1}. {txt}", text=txt, type="printed", source_page=1)
        for i, txt in enumerate(sample_texts)
    ]
    extracted = [r.text for r in recipients]
    for orig in sample_texts:
        assert orig in extracted
    # Verify no expansion happened
    assert "Head of Department" not in extracted


def test_ocr_result_structure():
    """Verify OCRResult structure contains only extraction and document metadata."""
    ocr_res = OCRResult(
        document_id="CIR-20261019-TEST",
        filename="circular_notice.pdf",
        file_type="pdf",
        status="success",
        copy_to_found=True,
        copy_to_pages=[1],
        recipients=[
            Recipient(raw_text="1. The Principal", text="The Principal", type="printed", source_page=1)
        ],
        handwritten_text=[]
    )
    dumped = ocr_res.model_dump()
    assert dumped["document_id"] == "CIR-20261019-TEST"
    assert dumped["copy_to_found"] is True
    assert len(dumped["recipients"]) == 1
    assert "directory_matched" not in dumped
    assert "dispatched_emails" not in dumped


def test_retired_endpoints_return_404():
    """Verify directory and email dispatch APIs are not accessible."""
    res_dir = client.get("/api/directory")
    assert res_dir.status_code == 404

    res_res = client.post("/api/circular/CIR-123/resolve-recipients")
    assert res_res.status_code == 404

    res_send = client.post("/api/circular/CIR-123/send-mail", json={})
    assert res_send.status_code == 404
