import json
import logging
import re
import asyncio
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, status, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from app.schemas.ocr_schema import ProcessResponse
from app.services.document_service import document_service, is_allowed_file
from app.services.json_service import load_output_json, save_output_data
from app.services.recipient_service import recipient_service
from app.services.recipient_mapping_service import recipient_mapping_service
from app.services.name_resolution_service import name_resolution_service
from app.services.email_service import email_service
from app.services.distribution_service import distribution_service
from app.schemas.distribution_schema import SendMailRequest, ResolveRecipientsRequest, EmailRecipientPayload
from app.config import UPLOAD_DIR, OUTPUT_DIR, DIAGNOSTICS_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["circular"])


class HandwritingCorrectionRequest(BaseModel):
    corrected_text: Optional[str] = Field(None, description="Complete corrected handwritten text line")
    instruction_index: Optional[int] = Field(None, description="Index of specific separated instruction to correct")
    corrected_instruction: Optional[str] = Field(None, description="Replacement text for specific instruction")


def _resolve_circular_recipients(data, recipient_names=None):
    resolved_items = data.get("llm_resolved_recipients") or []
    if not resolved_items:
        return [], ["Resolve extracted names before sending."], []
    names = recipient_names if recipient_names is not None else [item.get("recipient_name", "") for item in resolved_items]
    if len(names) != len(resolved_items):
        return [], ["Recipient list changed; resolve the names again before sending."], []
    stored_names = [str(item.get("recipient_name") or "").strip() for item in resolved_items]
    if recipient_names is not None and [str(name or "").strip() for name in names] != stored_names:
        return [], ["Recipient names changed; resolve them again before sending."], []
    targets = []
    unresolved = []
    rows = []
    seen = set()

    for index, item in enumerate(resolved_items):
        name = str(names[index] or "").strip()
        if item.get("status") == "skipped" and name.casefold() == "file":
            rows.append({**item, "recipient_name": name, "emails": [], "status": "skipped"})
            continue
        match = recipient_mapping_service.resolve(name, item.get("faculty_id")) if name else {"status": "unmatched", "emails": []}
        emails = match["emails"]
        rows.append({**item, "recipient_name": name, "emails": emails, "status": match["status"]})
        if match["status"] == "unmatched":
            unresolved.append(name or item.get("extracted_text") or "Recipient name is empty")
        for email in emails:
            if email.casefold() not in seen:
                seen.add(email.casefold())
                targets.append(EmailRecipientPayload(name=name, email=email, department="General"))
    return targets, unresolved, rows


def _extracted_name_items(data):
    """Collect printed names and handwriting once, splitting handwriting instructions."""
    def usable_handwriting_phrase(*values):
        for value in values:
            phrase = str(value or "").strip()
            if phrase and phrase.casefold().strip(" .,:;-") not in {"handwritten", "unknown", "unreadable"}:
                return phrase
        return ""

    items = []
    for index, recipient in enumerate(data.get("recipients") or []):
        if not isinstance(recipient, dict):
            continue
        text = str(recipient.get("text") or recipient.get("raw_text") or "").strip()
        source_type = recipient.get("type", "printed")
        if not text:
            continue
        if source_type == "handwritten":
            continue
        items.append({"source_id": f"printed-{index}", "source_type": "printed", "source_page": recipient.get("source_page"), "text": text, "source_text": text})

    handwriting = []
    seen_phrases = set()
    for recipient in data.get("recipients") or []:
        if isinstance(recipient, dict) and recipient.get("type") == "handwritten":
            # Old runs stored a generic TrOCR fallback in `text` but retained the useful
            # line-recognition result in `raw_text`; recover it for re-resolution.
            phrase = usable_handwriting_phrase(recipient.get("text"), recipient.get("raw_text"))
            page = recipient.get("source_page")
            if phrase and (phrase.casefold(), page) not in seen_phrases:
                handwriting.append((phrase, page))
                seen_phrases.add((phrase.casefold(), page))
    for note in data.get("handwritten_text") or []:
        if not isinstance(note, dict):
            continue
        phrase = usable_handwriting_phrase(note.get("corrected_text"), note.get("text"), note.get("raw_ocr_text"))
        page = note.get("source_page")
        if phrase and (phrase.casefold(), page) not in seen_phrases:
            handwriting.append((phrase, page))
            seen_phrases.add((phrase.casefold(), page))

    for phrase_index, (phrase, page) in enumerate(handwriting):
        parts = recipient_service.separate_instructions(phrase) or [phrase]
        for part_index, part in enumerate(parts):
            items.append({
                "source_id": f"handwritten-{phrase_index}-{part_index}",
                "source_type": "handwritten",
                "source_page": page,
                "text": part,
                "source_text": phrase,
            })
    return items


@router.get("/health", summary="Health check endpoint")
async def health_check():
    return {
        "status": "healthy",
        "service": "CircularRoute Backend"
    }


@router.post("/circular/process", response_model=ProcessResponse, summary="Upload and process circular PDF or Image")
async def process_circular(file: UploadFile = File(...)):
    if not file.filename or not is_allowed_file(file.filename):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "error_code": "UNSUPPORTED_FILE_TYPE",
                "message": "Only PDF, JPG, JPEG, PNG and WEBP files are supported."
            }
        )

    try:
        file_bytes = await file.read()
        ocr_result, output_file_rel = document_service.process_document(file_bytes, file.filename)

        return ProcessResponse(
            status="success",
            document_id=ocr_result.document_id,
            output_file=output_file_rel,
            data=ocr_result
        )
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "error_code": "UNSUPPORTED_FILE_TYPE",
                "message": str(ve)
            }
        )
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error_code": "OCR_PROCESSING_FAILED",
                "message": "Unable to process the uploaded circular."
            }
        )


@router.get("/circular/{document_id}", summary="Get extracted JSON data for a document")
async def get_circular_data(document_id: str):
    data = load_output_json(document_id)
    if not data:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "error_code": "DOCUMENT_NOT_FOUND",
                "message": f"No structured OCR data found for document ID: {document_id}"
            }
        )

    # Backfill interpreted_recipients if missing in stored JSON
    hw_list = data.get("handwritten_text") or []
    interpreted = data.get("interpreted_recipients") or []
    if hw_list and not interpreted:
        first_hw = hw_list[0]
        raw_hw = data.get("raw_ocr_text")
        if not raw_hw:
            raw_hw = first_hw.get("raw_ocr_text") if isinstance(first_hw, dict) else getattr(first_hw, "raw_ocr_text", None)
            if not raw_hw:
                raw_hw = first_hw.get("text") if isinstance(first_hw, dict) else getattr(first_hw, "text", "")
        if raw_hw:
            resolved = recipient_service.resolve_handwritten_section(raw_hw, data.get("corrected_text"))
            data["raw_ocr_text"] = raw_hw
            data["interpreted_recipients"] = [r.model_dump() for r in resolved]
            if isinstance(first_hw, dict):
                first_hw["raw_ocr_text"] = raw_hw
                first_hw["interpreted_recipients"] = data["interpreted_recipients"]

    # Backfill crop image if missing
    if not data.get("handwritten_crop_image") and hw_list:
        first_hw = hw_list[0]
        crop_img = first_hw.get("crop_image") if isinstance(first_hw, dict) else getattr(first_hw, "crop_image", None)
        if crop_img:
            data["handwritten_crop_image"] = crop_img
        else:
            diag_crops = list(DIAGNOSTICS_DIR.glob(f"*{document_id}*")) + list(DIAGNOSTICS_DIR.glob("actual_trocr_crop_*.png"))
            if diag_crops:
                try:
                    import base64
                    data["handwritten_crop_image"] = f"data:image/png;base64,{base64.b64encode(diag_crops[0].read_bytes()).decode('utf-8')}"
                except Exception:
                    pass

    return data


@router.post("/circular/{document_id}/send-mail", summary="Resolve recipients and send a circular through Resend")
async def send_circular_mail(document_id: str, request: SendMailRequest):
    data = load_output_json(document_id)
    if not data:
        return JSONResponse(status_code=404, content={"status": "error", "message": f"Circular '{document_id}' was not found."})

    targets, unresolved, _ = _resolve_circular_recipients(data, request.recipient_names or None)
    if unresolved:
        return JSONResponse(status_code=409, content={"status": "error", "message": "Add email mappings for all recipient names in backend/recipient_email_map.json before sending.", "unresolved": unresolved})
    if not targets:
        return JSONResponse(status_code=422, content={"status": "error", "message": "No email recipients were resolved from this circular."})

    results = await email_service.send_circular_emails(
        document_id, targets, request.subject, request.message_body, request.attach_document
    )
    distribution = distribution_service.record_mail_dispatch(document_id, results, request.subject or "")
    sent = sum(result["status"] == "sent" for result in results)
    return {"status": "success" if sent == len(results) else "partial" if sent else "failed", "document_id": document_id, "total": len(results), "sent": sent, "results": results, "distribution": distribution.model_dump()}


@router.post("/circular/{document_id}/resolve-recipients", summary="Resolve printed and handwritten OCR names with Groq and retrieve mapped emails")
async def resolve_circular_recipients(document_id: str, request: ResolveRecipientsRequest):
    data = load_output_json(document_id)
    if not data:
        return JSONResponse(status_code=404, content={"status": "error", "message": f"Circular '{document_id}' was not found."})
    extracted_items = _extracted_name_items(data)
    if not extracted_items:
        return {"status": "unresolved", "document_id": document_id, "matches": [], "unresolved": ["No printed or handwritten names were extracted."]}
    try:
        name_overrides = request.recipient_names or None
        if name_overrides and len(name_overrides) != len(extracted_items):
            # A legacy extraction may have produced one placeholder card for a line
            # that now splits into several real names. Drop only that stale placeholder.
            if all(str(name or "").strip().casefold() == "handwritten" for name in name_overrides):
                name_overrides = None
        resolved = await asyncio.to_thread(
            name_resolution_service.resolve,
            extracted_items,
            name_overrides,
        )
    except Exception as exc:
        logger.exception("Recipient name resolution failed for %s", document_id)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    for row in resolved:
        if row["status"] == "skipped":
            continue
        if row["recipient_name"]:
            match = recipient_mapping_service.resolve(row["recipient_name"], row.get("faculty_id"))
            row["emails"] = match["emails"]
            if match["status"] == "unmatched":
                row["status"] = "unmatched"
        else:
            row["emails"] = []
            row["status"] = "unmatched"

    data["llm_resolved_recipients"] = resolved
    save_output_data(document_id, data)
    targets, unresolved, rows = _resolve_circular_recipients(data)
    return {
        "status": "resolved" if targets and not unresolved else "unresolved",
        "document_id": document_id,
        "matches": rows,
        "unresolved": unresolved,
    }


@router.get("/distribution", summary="Get email distribution history")
async def get_distribution_history():
    return distribution_service.get_distribution().model_dump()


@router.post("/circular/{document_id}/handwriting/correct", summary="Correct handwritten instructions and re-run resolution")
async def correct_handwriting(document_id: str, request: HandwritingCorrectionRequest):
    data = load_output_json(document_id)
    if not data:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "error_code": "DOCUMENT_NOT_FOUND",
                "message": f"Document ID '{document_id}' not found."
            }
        )

    raw_ocr = data.get("raw_ocr_text")
    if not raw_ocr:
        hw_list = data.get("handwritten_text") or []
        if hw_list:
            first_hw = hw_list[0]
            raw_ocr = first_hw.get("raw_ocr_text") if isinstance(first_hw, dict) else getattr(first_hw, "raw_ocr_text", None)
            if not raw_ocr:
                raw_ocr = first_hw.get("text") if isinstance(first_hw, dict) else getattr(first_hw, "text", "")
    if not raw_ocr:
        raw_ocr = ""

    if request.corrected_text is not None:
        new_corrected_text = request.corrected_text.strip()
    elif request.instruction_index is not None and request.corrected_instruction is not None:
        current_text = data.get("corrected_text") or raw_ocr
        separated = recipient_service.separate_instructions(current_text)
        if 0 <= request.instruction_index < len(separated):
            separated[request.instruction_index] = request.corrected_instruction.strip()
            new_corrected_text = " & ".join(separated)
        else:
            separated.append(request.corrected_instruction.strip())
            new_corrected_text = " & ".join(separated)
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": "Must provide either corrected_text or (instruction_index and corrected_instruction)."}
        )

    # Re-run recipient interpretation and Excel lookup
    resolved = recipient_service.resolve_handwritten_section(raw_ocr, new_corrected_text)

    # Update data dictionary while strictly preserving raw_ocr_text
    data["raw_ocr_text"] = raw_ocr
    data["corrected_text"] = new_corrected_text
    data["interpreted_recipients"] = [r.model_dump() for r in resolved]

    # Also update handwritten_text list inside data
    if "handwritten_text" in data and data["handwritten_text"]:
        if isinstance(data["handwritten_text"][0], dict):
            data["handwritten_text"][0]["raw_ocr_text"] = raw_ocr
            data["handwritten_text"][0]["corrected_text"] = new_corrected_text
            data["handwritten_text"][0]["interpreted_recipients"] = data["interpreted_recipients"]

    # Save physical JSON file
    file_path = OUTPUT_DIR / f"{document_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Handwriting corrected for document {document_id}: '{new_corrected_text}'")

    return {
        "status": "success",
        "document_id": document_id,
        "raw_ocr_text": raw_ocr,
        "corrected_text": new_corrected_text,
        "interpreted_recipients": data["interpreted_recipients"],
        "data": data
    }


@router.get("/circular/{document_id}/json", summary="Download physical JSON output file")
async def download_circular_json(document_id: str):
    file_path = OUTPUT_DIR / f"{document_id}.json"
    if not file_path.exists():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "error_code": "FILE_NOT_FOUND",
                "message": f"JSON output file for document ID '{document_id}' does not exist."
            }
        )

    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=f"{document_id}.json"
    )


@router.get("/circular/{document_id}/file", summary="Serve uploaded circular document for browser preview")
async def get_circular_file(document_id: str):
    matched_files = list(UPLOAD_DIR.glob(f"{document_id}.*"))
    if not matched_files:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "error_code": "FILE_NOT_FOUND",
                "message": f"Uploaded document file for ID '{document_id}' not found."
            }
        )

    file_path = matched_files[0]
    ext = file_path.suffix.lower()
    mime_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    media_type = mime_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name,
        headers={"Content-Disposition": f"inline; filename={file_path.name}"}
    )
