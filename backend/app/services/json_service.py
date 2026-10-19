import os
import json
from pathlib import Path
from typing import Optional
from app.schemas.ocr_schema import OCRResult
from app.config import OUTPUT_DIR


def save_output_json(ocr_result: OCRResult, output_dir: Optional[Path] = None) -> Path:
    """
    Writes physical JSON file to backend/outputs/<document_id>.json.
    """
    target_dir = output_dir or OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / f"{ocr_result.document_id}.json"

    # Dump model to dict with clean formatting
    data = ocr_result.model_dump()

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return file_path


def load_output_json(document_id: str, output_dir: Optional[Path] = None) -> Optional[dict]:
    """
    Loads output JSON for a document_id if it exists.
    """
    target_dir = output_dir or OUTPUT_DIR
    file_path = target_dir / f"{document_id}.json"

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
