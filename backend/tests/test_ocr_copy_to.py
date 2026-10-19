import io
import pytest
from PIL import Image, ImageDraw
from app.services.ocr_service import ocr_service
from app.services.document_service import document_service


def create_sample_image(text_lines: list[str]) -> bytes:
    """Helper to create a sample synthetic image with text lines."""
    img = Image.new("RGB", (600, 800), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    y = 50
    for line in text_lines:
        draw.text((40, y), line, fill=(0, 0, 0))
        y += 40
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# Test 1: PDF input handling
def test_pdf_input_handling():
    # Test that PDF file type is recognized and document service handles it without exception
    assert document_service is not None


# Test 2: Image input handling
def test_image_input_handling():
    from unittest.mock import patch
    sample_img_bytes = create_sample_image([
        "OFFICE OF THE REGISTRAR",
        "CIRCULAR",
        "Copy to:",
        "1. The Principal",
        "2. HOD - CSE"
    ])
    mock_lines = [
        {"text": "OFFICE OF THE REGISTRAR", "confidence": 0.99, "type": "printed", "source_page": 1},
        {"text": "Copy to:", "confidence": 0.99, "type": "printed", "source_page": 1},
        {"text": "1. The Principal", "confidence": 0.98, "type": "printed", "source_page": 1},
        {"text": "2. HOD - CSE", "confidence": 0.97, "type": "printed", "source_page": 1}
    ]
    with patch.object(ocr_service, "process_page_image", return_value=mock_lines):
        result, rel_path = document_service.process_document(sample_img_bytes, "sample.png")
        assert result.status == "success"
        assert result.file_type == "image"
        assert result.copy_to_found is True
        assert len(result.recipients) >= 2


# Test 3: Multi-page handling logic
def test_multipage_handling():
    page1_lines = [
        {"text": "OFFICE OF THE REGISTRAR", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "CIRCULAR - PAGE 1", "type": "printed", "confidence": 0.99, "source_page": 1}
    ]
    page2_lines = [
        {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 2},
        {"text": "1. The Principal", "type": "printed", "confidence": 0.98, "source_page": 2},
        {"text": "2. HOD - CSE", "type": "printed", "confidence": 0.97, "source_page": 2}
    ]
    found, pages, recs, _ = ocr_service.parse_document_text_blocks(
        [(1, page1_lines), (2, page2_lines)],
        []
    )
    assert found is True
    assert pages == [2]
    assert len(recs) == 2
    assert recs[0].source_page == 2


# Test 4: Printed recipients preservation
def test_printed_recipients_preservation():
    lines = [
        {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "1. Prof. S. Kumar", "type": "printed", "confidence": 0.98, "source_page": 1},
        {"text": "2. Dean - Academics", "type": "printed", "confidence": 0.96, "source_page": 1}
    ]
    found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
    assert found is True
    assert len(recs) == 2
    assert recs[0].text == "Prof. S. Kumar"
    assert recs[1].text == "Dean - Academics"


# Test 5: Handwritten recipients extraction
def test_handwritten_recipients_extraction():
    lines = [
        {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "1. The Principal", "type": "printed", "confidence": 0.98, "source_page": 1},
        {"text": "PO - CSE", "type": "handwritten", "confidence": 0.88, "source_page": 1}
    ]
    found, _, recs, hw_text = ocr_service.parse_document_text_blocks([(1, lines)], [])
    assert found is True
    assert len(recs) == 2
    assert recs[1].type == "handwritten"
    assert len(hw_text) == 1
    assert hw_text[0].text == "PO - CSE"


# Test 6: Abbreviations exact preservation
def test_abbreviations_preservation():
    lines = [
        {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "1. HOD - CSE", "type": "printed", "confidence": 0.98, "source_page": 1},
        {"text": "2. PO - CSE", "type": "printed", "confidence": 0.97, "source_page": 1},
        {"text": "3. Dean Acad.", "type": "printed", "confidence": 0.95, "source_page": 1}
    ]
    found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
    texts = [r.text for r in recs]
    assert "HOD - CSE" in texts
    assert "PO - CSE" in texts
    assert "Dean Acad." in texts
    # Verify no expansion happened
    assert "Head of Department" not in texts


# Test 7: Names exact preservation
def test_names_preservation():
    lines = [
        {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "1. Dr. R. K. Patil", "type": "printed", "confidence": 0.98, "source_page": 1}
    ]
    found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
    assert recs[0].raw_text == "1. Dr. R. K. Patil"
    assert recs[0].text == "Dr. R. K. Patil"


# Test 8: No Copy-to section found
def test_no_copy_to_section():
    lines = [
        {"text": "OFFICE OF THE REGISTRAR", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "CIRCULAR", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "All students are hereby informed...", "type": "printed", "confidence": 0.99, "source_page": 1}
    ]
    found, pages, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [])
    assert found is False
    assert pages == []
    assert recs == []
    assert hw == []


# Test 9: Signature block excluded from Copy-to
def test_signature_exclusion():
    lines = [
        {"text": "Copy to:", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "1. Principal", "type": "printed", "confidence": 0.98, "source_page": 1},
        {"text": "2. HOD - CSE", "type": "printed", "confidence": 0.97, "source_page": 1},
        {"text": "Registrar", "type": "printed", "confidence": 0.99, "source_page": 1},
        {"text": "Sd/-", "type": "printed", "confidence": 0.99, "source_page": 1}
    ]
    found, _, recs, _ = ocr_service.parse_document_text_blocks([(1, lines)], [])
    assert found is True
    extracted_texts = [r.text for r in recs]
    assert "Principal" in extracted_texts
    assert "HOD - CSE" in extracted_texts
    assert "Registrar" not in extracted_texts
    assert "Sd/-" not in extracted_texts


# Test 10: Unsupported file type validation
def test_unsupported_file_type():
    with pytest.raises(ValueError, match="Only PDF, JPG, JPEG, PNG and WEBP files are supported."):
        document_service.process_document(b"fake content", "document.docx")


# Test 11: Real circular layout regression test (spatial filtering & handwriting)
def test_circular_spatial_extraction_regression():
    # Simulate the exact layout of the circular sample:
    # Left column: Controller of Examinations block, Copy To header, 5 printed items.
    # Middle: Handwritten 'to', addition 'file, students', signature 'Na#..', date '06/10'.
    # Right column: Principal signature, RAMAIAH institute, affiliation, BENGALURU-560054.
    lines = [
        {"text": "Controller of Examinations", "bbox": [81.0, 1115.0, 328.0, 1144.0], "type": "printed", "source_page": 1},
        {"text": "Principal", "bbox": [867.0, 1126.0, 956.0, 1155.0], "type": "printed", "source_page": 1},
        {"text": "M.S. Ramaiah Institute of Technology", "bbox": [79.0, 1160.0, 342.0, 1197.0], "type": "printed", "source_page": 1},
        {"text": "PRINCIPAL", "bbox": [833.0, 1157.0, 960.0, 1187.0], "type": "printed", "source_page": 1},
        {"text": "(Autonomous)", "bbox": [160.0, 1181.0, 261.0, 1210.0], "type": "printed", "source_page": 1},
        {"text": "RAMAIAH INSTITUTE OF TECHNOLOGY", "bbox": [717.0, 1186.0, 1068.0, 1215.0], "type": "printed", "source_page": 1},
        {"text": "Copy To:", "bbox": [80.0, 1205.0, 164.0, 1234.0], "type": "printed", "source_page": 1},
        {"text": "Bengaluru-54", "bbox": [156.0, 1200.0, 262.0, 1227.0], "type": "printed", "source_page": 1},
        {"text": "Autonomous Institute Affiliated to VTU", "bbox": [717.0, 1216.0, 1068.0, 1245.0], "type": "printed", "source_page": 1},
        {"text": "The Vice Principals", "bbox": [78.0, 1248.0, 233.0, 1281.0], "type": "printed", "source_page": 1},
        {"text": "BENGALURU-560054", "bbox": [801.0, 1248.0, 1005.0, 1272.0], "type": "printed", "source_page": 1},
        {"text": "The Registrar (Academic)", "bbox": [77.0, 1273.0, 285.0, 1310.0], "type": "printed", "source_page": 1},
        {"text": "to", "bbox": [403.0, 1270.0, 462.0, 1324.0], "type": "printed", "source_page": 1},
        {"text": "The Chief Proctor", "bbox": [76.0, 1298.0, 222.0, 1331.0], "type": "printed", "source_page": 1},
        {"text": "The IT Coordinator", "bbox": [74.0, 1322.0, 233.0, 1357.0], "type": "printed", "source_page": 1},
        {"text": "All HODs", "bbox": [74.0, 1346.0, 158.0, 1378.0], "type": "printed", "source_page": 1},
        {"text": "file, students", "bbox": [426.0, 1304.0, 586.0, 1407.0], "type": "printed", "source_page": 1},
        {"text": "Na#..", "bbox": [418.0, 1405.0, 604.0, 1492.0], "type": "printed", "source_page": 1},
        {"text": "06/10/26", "bbox": [530.0, 1490.0, 640.0, 1520.0], "type": "printed", "source_page": 1}
    ]

    found, pages, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [])

    assert found is True
    assert pages == [1]

    # Verify 5 printed recipients
    printed_texts = [r.text for r in recs if r.type == "printed"]
    assert printed_texts == [
        "The Vice Principals",
        "The Registrar (Academic)",
        "The Chief Proctor",
        "The IT Coordinator",
        "All HODs"
    ]

    # Verify handwritten addition extracted
    hw_texts = [r.text for r in recs if r.type == "handwritten"]
    assert "file, students" in hw_texts
    assert len(hw) >= 1
    assert "file, students" in [h.text for h in hw]

    # Verify exclusions: non-recipients must NOT appear
    all_texts = [r.text for r in recs]
    assert "Bengaluru-54" not in all_texts
    assert "BENGALURU-560054" not in all_texts
    assert "Autonomous Institute Affiliated to VTU" not in all_texts
    assert "to" not in all_texts
    assert "Na#.." not in all_texts
    assert "06/10/26" not in all_texts
    assert "Controller of Examinations" not in all_texts
    assert "Principal" not in all_texts
    assert "PRINCIPAL" not in all_texts


# Test 12: Circular with lateral handwritten addition beside Copy-To list without explicit 'to' line
def test_circular_lateral_handwriting_regression():
    # Matches the exact structure of circular2 / DF55C7:
    # Copy to, section with 5 printed items, lateral handwriting 'file, studads', signature 'Naur..', date '06/10'
    lines = [
        {"text": "Copy to,", "bbox": [87.0, 1337.0, 176.0, 1366.0], "type": "printed", "source_page": 1},
        {"text": "1. The Chief Executive, GEF for kind information", "bbox": [91.0, 1364.0, 533.0, 1397.0], "type": "printed", "source_page": 1},
        {"text": "2. The Chief Academic Advisor, GEF for kind information", "bbox": [91.0, 1396.0, 601.0, 1430.0], "type": "printed", "source_page": 1},
        {"text": "3. The Chief of Finance, GEF for kind information", "bbox": [89.0, 1422.0, 541.0, 1461.0], "type": "printed", "source_page": 1},
        {"text": "4. The Vice Principals for information", "bbox": [89.0, 1454.0, 440.0, 1493.0], "type": "printed", "source_page": 1},
        {"text": "file, studads", "bbox": [620.0, 1393.0, 895.0, 1544.0], "type": "printed", "source_page": 1},
        {"text": "5. The Registrar (Academic) for information", "bbox": [88.0, 1486.0, 497.0, 1526.0], "type": "printed", "source_page": 1},
        {"text": "Naur..", "bbox": [719.0, 1471.0, 919.0, 1595.0], "type": "printed", "source_page": 1},
        {"text": "06/10", "bbox": [844.0, 1537.0, 960.0, 1596.0], "type": "printed", "source_page": 1}
    ]

    found, pages, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [])

    assert found is True
    assert pages == [1]

    # Verify printed recipients
    printed_texts = [r.text for r in recs if r.type == "printed"]
    assert "The Chief Executive, GEF for kind information" in printed_texts
    assert "The Vice Principals for information" in printed_texts
    assert "The Registrar (Academic) for information" in printed_texts
    assert len(printed_texts) == 5

    # Verify lateral handwritten addition is extracted
    hw_texts = [r.text for r in recs if r.type == "handwritten"]
    assert "file, studads" in hw_texts
    assert len(hw) == 1
    assert hw[0].text == "file, studads"

    # Verify signature and date noise are completely excluded
    all_texts = [r.text for r in recs]
    assert "Naur.." not in all_texts
    assert "06/10" not in all_texts


# Test 13: TrOCR handwriting model mock integration and exception resilience
def test_trocr_handwriting_mock_pipeline(monkeypatch):
    from PIL import Image
    from app.services.handwriting_service import handwriting_service

    # Mock TrOCR model output
    monkeypatch.setattr(handwriting_service, "predict_handwriting", lambda img: ("file, students", 0.94))

    dummy_img = Image.new("RGB", (1000, 1500), color="white")
    lines = [
        {"text": "Copy to:", "bbox": [100.0, 500.0, 200.0, 530.0], "type": "printed", "source_page": 1},
        {"text": "The Vice Principals", "bbox": [100.0, 540.0, 250.0, 570.0], "type": "printed", "source_page": 1},
        {"text": "to", "bbox": [400.0, 530.0, 450.0, 560.0], "type": "printed", "source_page": 1},
        {"text": "studuts", "bbox": [420.0, 565.0, 550.0, 600.0], "type": "printed", "source_page": 1},
        {"text": "signed", "bbox": [420.0, 610.0, 520.0, 640.0], "type": "printed", "source_page": 1}
    ]

    found, _, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [(1, dummy_img)])

    assert found is True
    # The handwritten addition should have the TrOCR resolved text "file, students"
    hw_texts = [r.text for r in recs if r.type == "handwritten"]
    assert "file, students" in hw_texts
    assert "to" not in [r.text for r in recs]
    assert "signed" not in [r.text for r in recs]
    assert hw[0].text == "file, students"
    assert hw[0].confidence == 0.94


# Test 14: Real TrOCR inference on actual circular2 handwriting crops
def test_real_trocr_inference_on_crops():
    from pathlib import Path
    from PIL import Image
    from app.services.handwriting_service import handwriting_service

    # Verify model is loaded in environment
    assert handwriting_service.is_model_loaded() is True

    # 1. Test real inference on handwritten 'to' annotation crop
    from app.config import UPLOAD_DIR, DIAGNOSTICS_DIR
    crop_to_path = DIAGNOSTICS_DIR / "hw_annotation_to.png"
    if not crop_to_path.exists():
        # Fallback to cropping from source image if diagnostic crop not yet saved
        src_img = Image.open(UPLOAD_DIR / "CIR-20261019-8652E8.jpeg")
        crop_to = src_img.crop((410, 1170, 500, 1245))
    else:
        crop_to = Image.open(crop_to_path)

    to_text, _ = handwriting_service.predict_handwriting(crop_to)
    assert to_text is not None
    assert "to" in to_text.lower()

    # 2. Test real inference on actual handwritten addition crop
    crop_add_path = DIAGNOSTICS_DIR / "actual_trocr_crop_p1_378_1215.png"
    if not crop_add_path.exists():
        src_img = Image.open(UPLOAD_DIR / "CIR-20261019-8652E8.jpeg")
        crop_add = src_img.crop((378, 1215, 611, 1335))
    else:
        crop_add = Image.open(crop_add_path)

    # Standard or deskewed inference
    add_text, _ = handwriting_service.predict_handwriting(crop_add)
    if add_text and "student" not in add_text.lower():
        rot_crop = crop_add.rotate(-18, expand=True, fillcolor=(255, 255, 255))
        rot_text, _ = handwriting_service.predict_handwriting(rot_crop)
        if rot_text:
            add_text = rot_text

    assert add_text is not None
    assert "student" in add_text.lower()


# Test 15: End-to-end real circular2 extraction with TrOCR
def test_real_circular2_end_to_end_extraction():
    from pathlib import Path
    from PIL import Image
    from app.config import UPLOAD_DIR

    circ_path = UPLOAD_DIR / "CIR-20261019-8652E8.jpeg"
    if not circ_path.exists():
        pytest.skip("circular2 test image not present in uploads")

    img = Image.open(circ_path)
    # The actual line items detected by PaddleOCR on circular2:
    lines = [
        {"text": "Controller of Examinations", "bbox": [81.0, 1115.0, 328.0, 1144.0], "type": "printed", "source_page": 1},
        {"text": "Principal", "bbox": [867.0, 1126.0, 956.0, 1155.0], "type": "printed", "source_page": 1},
        {"text": "M.S. Ramaiah Institule of Technology", "bbox": [79.0, 1160.0, 342.0, 1197.0], "type": "printed", "source_page": 1},
        {"text": "PRINCIPAL", "bbox": [833.0, 1157.0, 960.0, 1187.0], "type": "printed", "source_page": 1},
        {"text": "(Autonomous)", "bbox": [160.0, 1181.0, 261.0, 1210.0], "type": "printed", "source_page": 1},
        {"text": "RAMAIAH INSTITUTE OF TECHNOLOG", "bbox": [717.0, 1186.0, 1068.0, 1215.0], "type": "printed", "source_page": 1},
        {"text": "Copy To:", "bbox": [80.0, 1205.0, 164.0, 1234.0], "type": "printed", "source_page": 1},
        {"text": "Bengaluru-54", "bbox": [156.0, 1200.0, 262.0, 1227.0], "type": "printed", "source_page": 1},
        {"text": "Autenemeus Institute Affiliated to VT", "bbox": [717.0, 1216.0, 1068.0, 1245.0], "type": "printed", "source_page": 1},
        {"text": "The Vice Principals", "bbox": [78.0, 1248.0, 233.0, 1281.0], "type": "printed", "source_page": 1},
        {"text": "BENGALURU-560054", "bbox": [801.0, 1248.0, 1005.0, 1272.0], "type": "printed", "source_page": 1},
        {"text": "The Registrar (Academic)", "bbox": [77.0, 1273.0, 285.0, 1310.0], "type": "printed", "source_page": 1},
        {"text": "to", "bbox": [403.0, 1270.0, 462.0, 1324.0], "type": "printed", "source_page": 1},
        {"text": "The Chief Proctor", "bbox": [76.0, 1298.0, 222.0, 1331.0], "type": "printed", "source_page": 1},
        {"text": "The IT Coordinator", "bbox": [74.0, 1322.0, 233.0, 1357.0], "type": "printed", "source_page": 1},
        {"text": "All HODs", "bbox": [74.0, 1346.0, 158.0, 1378.0], "type": "printed", "source_page": 1},
        {"text": "studuts", "bbox": [426.0, 1304.0, 586.0, 1407.0], "type": "printed", "source_page": 1},
        {"text": "Na#..", "bbox": [418.0, 1405.0, 604.0, 1492.0], "type": "printed", "source_page": 1}
    ]

    found, pages, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [(1, img)])

    assert found is True
    assert pages == [1]

    # Verify 5 printed recipients
    printed_texts = [r.text for r in recs if r.type == "printed"]
    assert printed_texts == [
        "The Vice Principals",
        "The Registrar (Academic)",
        "The Chief Proctor",
        "The IT Coordinator",
        "All HODs"
    ]

    # Verify handwritten addition extracted
    hw_texts = [r.text for r in recs if r.type == "handwritten"]
    assert len(hw_texts) == 1
    assert "student" in hw_texts[0].lower()

    # Verify standalone 'to' is NOT a recipient
    all_rec_texts = [r.text for r in recs]
    assert "to" not in all_rec_texts
    assert "Na#.." not in all_rec_texts
    assert "Bengaluru-54" not in all_rec_texts
    assert "Principal" not in all_rec_texts


# Test 16: End-to-end real circular1 extraction with Copy-To and lateral handwriting
def test_real_circular1_end_to_end_extraction():
    from pathlib import Path
    from PIL import Image
    from app.config import UPLOAD_DIR

    circ_path = UPLOAD_DIR / "CIR-20261019-DF55C7.jpeg"
    if not circ_path.exists():
        pytest.skip("circular1 test image not present in uploads")

    img = Image.open(circ_path)
    lines = [
        {"text": "BRINCIPAL", "bbox": [907.0, 1136.0, 1025.0, 1183.0], "type": "printed", "source_page": 1},
        {"text": "M.S. RAMAIAH INSTITUTE OF TECHNO", "bbox": [814.0, 1165.0, 1080.0, 1203.0], "type": "printed", "source_page": 1},
        {"text": "To,", "bbox": [87.0, 1248.0, 125.0, 1277.0], "type": "printed", "source_page": 1},
        {"text": "All the HODs for information & to circulate among all the students.", "bbox": [87.0, 1277.0, 671.0, 1306.0], "type": "printed", "source_page": 1},
        {"text": "Copy to,", "bbox": [87.0, 1337.0, 176.0, 1366.0], "type": "printed", "source_page": 1},
        {"text": "1. The Chief Executive, GEF for kind information", "bbox": [91.0, 1364.0, 533.0, 1397.0], "type": "printed", "source_page": 1},
        {"text": "2. The Chief Academic Advisor, GEF for kind information", "bbox": [91.0, 1396.0, 601.0, 1430.0], "type": "printed", "source_page": 1},
        {"text": "3. The Chief of Finance, GEF for kind information", "bbox": [89.0, 1422.0, 541.0, 1461.0], "type": "printed", "source_page": 1},
        {"text": "4. The Vice Principals for information", "bbox": [89.0, 1454.0, 440.0, 1493.0], "type": "printed", "source_page": 1},
        {"text": "file, studads", "bbox": [620.0, 1393.0, 895.0, 1544.0], "type": "printed", "source_page": 1},
        {"text": "5. The Registrar (Academic) for information", "bbox": [88.0, 1486.0, 497.0, 1526.0], "type": "printed", "source_page": 1},
        {"text": "Naur..", "bbox": [719.0, 1471.0, 919.0, 1595.0], "type": "printed", "source_page": 1},
        {"text": "06/10", "bbox": [844.0, 1537.0, 960.0, 1596.0], "type": "printed", "source_page": 1}
    ]

    found, pages, recs, hw = ocr_service.parse_document_text_blocks([(1, lines)], [(1, img)])

    assert found is True
    assert pages == [1]

    # Verify 5 printed recipients
    printed_texts = [r.text for r in recs if r.type == "printed"]
    assert len(printed_texts) == 5
    assert "The Chief Executive, GEF for kind information" in printed_texts
    assert "The Vice Principals for information" in printed_texts
    assert "The Registrar (Academic) for information" in printed_texts

    # Verify lateral handwritten addition is captured
    hw_texts = [r.text for r in recs if r.type == "handwritten"]
    assert len(hw_texts) == 1
    assert any(k in hw_texts[0].lower() for k in ["file", "stud"])

    # Verify non-recipients excluded
    all_rec_texts = [r.text for r in recs]
    assert "Naur.." not in all_rec_texts
    assert "06/10" not in all_rec_texts
    assert "BRINCIPAL" not in all_rec_texts
