import os
import uuid
import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Any
from PIL import Image

from app.schemas.ocr_schema import OCRResult, Recipient, HandwrittenText
from app.utils.pdf_utils import extract_pdf_pages_as_images, extract_pdf_page_text_blocks
from app.utils.image_utils import load_image_from_bytes
from app.services.ocr_service import ocr_service
from app.services.json_service import save_output_json

from app.config import UPLOAD_DIR
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}


def generate_document_id() -> str:
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    short_uid = uuid.uuid4().hex[:6].upper()
    return f"CIR-{today_str}-{short_uid}"


def is_allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def save_upload_file(file_bytes: bytes, filename: str, doc_id: str) -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(filename).suffix.lower()
    saved_filename = f"{doc_id}{ext}"
    saved_path = UPLOAD_DIR / saved_filename
    with open(saved_path, "wb") as f:
        f.write(file_bytes)
    return saved_path


class DocumentService:
    def process_document(self, file_bytes: bytes, filename: str) -> Tuple[OCRResult, str]:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("Only PDF, JPG, JPEG, PNG and WEBP files are supported.")

        doc_id = generate_document_id()
        _saved_path = save_upload_file(file_bytes, filename, doc_id)

        file_type = "pdf" if ext == ".pdf" else "image"
        page_images: List[Tuple[int, Image.Image]] = []
        pages_lines: List[Tuple[int, List[Dict[str, Any]]]] = []

        if file_type == "pdf":
            # 1. Convert PDF pages to PIL Images
            try:
                page_images = extract_pdf_pages_as_images(file_bytes)
            except Exception:
                page_images = []

            # 2. Extract text blocks natively from PDF if available
            pdf_text_blocks = extract_pdf_page_text_blocks(file_bytes)

            for pnum, blocks in pdf_text_blocks:
                lines = []
                for b in blocks:
                    for line_str in b.get("lines", []):
                        lines.append({
                            "text": line_str,
                            "confidence": None,
                            "type": "printed",
                            "source_page": pnum
                        })
                pages_lines.append((pnum, lines))

            # If no native PDF lines extracted, run OCR on rendered page images
            if not any(lines for _, lines in pages_lines) and page_images:
                pages_lines = []
                for pnum, img in page_images:
                    lines = ocr_service.process_page_image(img, pnum)
                    pages_lines.append((pnum, lines))
        else:
            # Image input (.jpg, .jpeg, .png, .webp)
            img = load_image_from_bytes(file_bytes)
            page_images = [(1, img)]
            lines = ocr_service.process_page_image(img, 1)
            pages_lines = [(1, lines)]

        # 3. Locate Copy-to section & extract recipients & handwritten text
        copy_to_found, copy_to_pages, recipients, handwritten_text = ocr_service.parse_document_text_blocks(
            pages_lines, page_images
        )

        ocr_result = OCRResult(
            document_id=doc_id,
            filename=filename,
            file_type=file_type,
            status="success",
            copy_to_found=copy_to_found,
            copy_to_pages=copy_to_pages,
            recipients=recipients,
            handwritten_text=handwritten_text
        )

        # 4. Save output JSON physical file to outputs/<document_id>.json
        output_file_path = save_output_json(ocr_result)
        relative_output_path = f"outputs/{output_file_path.name}"

        return ocr_result, relative_output_path


# Global instance
document_service = DocumentService()
