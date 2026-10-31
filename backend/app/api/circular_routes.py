import os
import json
import logging
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from app.schemas.ocr_schema import ProcessResponse
from app.services.document_service import document_service, is_allowed_file
from app.services.json_service import load_output_json
from app.services.recipient_service import recipient_service
from app.config import UPLOAD_DIR, OUTPUT_DIR, DIAGNOSTICS_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["circular"])


class HandwritingCorrectionRequest(BaseModel):
    corrected_text: Optional[str] = Field(None, description="Complete corrected handwritten text line")
    instruction_index: Optional[int] = Field(None, description="Index of specific separated instruction to correct")
    corrected_instruction: Optional[str] = Field(None, description="Replacement text for specific instruction")


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
