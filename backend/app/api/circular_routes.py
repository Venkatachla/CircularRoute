import os
import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse, FileResponse

from app.schemas.ocr_schema import ProcessResponse
from app.services.document_service import document_service, is_allowed_file
from app.services.json_service import load_output_json
from app.config import UPLOAD_DIR, OUTPUT_DIR

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["circular"])


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
    return data


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
