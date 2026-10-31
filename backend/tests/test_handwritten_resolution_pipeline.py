import pytest
from app.services.directory_service import directory_service
from app.services.recipient_service import recipient_service
from app.schemas.ocr_schema import HandwrittenInstruction
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_directory_excel_data_loading():
    """Verify directory service correctly parses temp_data.xlsx."""
    # Test students
    students = directory_service.get_all_student_emails()
    assert len(students) == 4
    assert "1ms23cs211@msrit.edu" in students
    assert "1ms23cs212@msrit.edu" in students
    assert "1ms23cs213@msrit.edu" in students
    assert "1ms23cs214@msrit.edu" in students

    # Test faculty lookups case-insensitively
    vp = directory_service.get_faculty_by_id("vp")
    assert vp is not None
    assert vp.id == "vp"
    assert vp.name == "Vijay Patil"
    assert vp.email == "vijaypatil00046@gmail.com"

    vv = directory_service.get_faculty_by_id("VV")
    assert vv is not None
    assert vv.id == "vv"
    assert vv.name == "Venkatachala V"
    assert vv.email == "venkatachalavenku029@gmail.com"

    # Faculty with missing mail_id (vlk)
    vlk = directory_service.get_faculty_by_id("vlk")
    assert vlk is not None
    assert vlk.email == ""

    # Non-existent faculty
    assert directory_service.get_faculty_by_id("xyz") is None


def test_handwritten_instruction_separation():
    """Verify delimiter separation handles commas, ampersands, bullets and prefixes."""
    text1 = "To file & students & staff & vp"
    sep1 = recipient_service.separate_instructions(text1)
    assert sep1 == ["file", "students", "staff", "vp"]

    text2 = "1. file, 2. students + 3. vv\n4. staff"
    sep2 = recipient_service.separate_instructions(text2)
    assert sep2 == ["file", "students", "vv", "staff"]


def test_instruction_interpretation_rules():
    """Verify semantic meaning and resolution statuses."""
    # 1. file -> Informational
    res_file = recipient_service.interpret_instruction("file")
    assert res_file.status == "INFORMATIONAL"
    assert len(res_file.emails) == 0

    # 2. students -> All students
    res_stud = recipient_service.interpret_instruction("students")
    assert res_stud.status == "RESOLVED"
    assert len(res_stud.emails) == 4
    assert res_stud.interpretation == "ALL_STUDENTS"

    # 3. staff -> Unresolved (no assumption)
    res_staff = recipient_service.interpret_instruction("staff")
    assert res_staff.status == "UNRESOLVED"
    assert res_staff.interpretation == "Needs administrator review"
    assert "do not assume staff means faculty" in res_staff.unresolved_reason.lower()

    # 4. vp -> Matched Faculty
    res_vp = recipient_service.interpret_instruction("vp")
    assert res_vp.status == "RESOLVED"
    assert res_vp.matched_faculty["Faculty_id"] == "vp"
    assert "vijaypatil00046@gmail.com" in res_vp.emails

    # 5. vlk -> Unresolved due to missing email
    res_vlk = recipient_service.interpret_instruction("vlk")
    assert res_vlk.status == "UNRESOLVED"
    assert "missing" in res_vlk.unresolved_reason.lower()


def test_handwritten_resolution_with_manual_correction():
    """Verify raw_ocr_text is preserved and corrected tokens are marked MANUALLY CORRECTED."""
    raw = "To file & students & staff & vp"
    corrected = "To file & students & vv & vp"

    resolved = recipient_service.resolve_handwritten_section(raw, corrected)
    assert len(resolved) == 4

    # file
    assert resolved[0].instruction == "file"
    assert resolved[0].status == "INFORMATIONAL"

    # students
    assert resolved[1].instruction == "students"
    assert resolved[1].status == "RESOLVED"
    assert len(resolved[1].emails) == 4

    # staff was corrected to vv
    assert resolved[2].instruction == "vv"
    assert resolved[2].raw_text == "staff"
    assert resolved[2].status == "MANUALLY CORRECTED"
    assert resolved[2].matched_faculty["faculty_name"] == "Venkatachala V"
    assert "venkatachalavenku029@gmail.com" in resolved[2].emails

    # vp
    assert resolved[3].instruction == "vp"
    assert resolved[3].status == "RESOLVED"


def test_api_handwriting_correction_endpoint():
    """Verify POST /api/circular/{document_id}/handwriting/correct updates physical storage and preserves raw OCR."""
    doc_id = "CIR-20261031-EBC75B"

    # Get circular first
    get_res = client.get(f"/api/circular/{doc_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    raw_ocr = data.get("raw_ocr_text")
    assert raw_ocr is not None

    # Send correction for instruction index 1 ("stlft" -> "vp")
    correct_payload = {
        "instruction_index": 1,
        "corrected_instruction": "vp"
    }
    post_res = client.post(f"/api/circular/{doc_id}/handwriting/correct", json=correct_payload)
    assert post_res.status_code == 200
    updated_data = post_res.json()
    assert updated_data["status"] == "success"
    assert updated_data["raw_ocr_text"] == raw_ocr  # Strictly preserved!
    assert "vp" in updated_data["corrected_text"]

    interpreted = updated_data["interpreted_recipients"]
    assert any(i["instruction"] == "vp" and i["status"] == "MANUALLY CORRECTED" for i in interpreted)
