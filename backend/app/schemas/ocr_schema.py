from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Recipient(BaseModel):
    raw_text: str = Field(..., description="Original extracted raw text of the recipient")
    text: str = Field(..., description="Minimally normalized recipient text (whitespace trimmed)")
    type: Literal["printed", "handwritten"] = Field(..., description="Recipient text type")
    confidence: Optional[float] = Field(None, description="OCR confidence score if available")
    source_page: int = Field(..., description="1-indexed page number where recipient was found")


class HandwrittenInstruction(BaseModel):
    instruction: str = Field(..., description="Individual extracted or separated instruction token")
    raw_text: Optional[str] = Field(None, description="Exact original raw instruction text")
    corrected_text: Optional[str] = Field(None, description="Administrator corrected instruction text")
    interpretation: str = Field(..., description="Semantic meaning resolved by application")
    status: Literal["RESOLVED", "UNRESOLVED", "INFORMATIONAL", "MANUALLY CORRECTED"] = Field(
        ..., description="Resolution status"
    )
    result: str = Field(..., description="Formatted resolution result or human-readable summary")
    emails: List[str] = Field(default_factory=list, description="Resolved email address list from directory")
    matched_faculty: Optional[Dict[str, Any]] = Field(None, description="Matched faculty details (id, name, email)")
    unresolved_reason: Optional[str] = Field(None, description="Reason if instruction remains unresolved")


class HandwrittenText(BaseModel):
    text: str = Field(..., description="Recognized handwritten text string")
    confidence: Optional[float] = Field(None, description="Handwriting recognition confidence")
    associated_with: str = Field("copy_to", description="Target section association")
    source_page: int = Field(..., description="1-indexed page number of handwritten addition")
    raw_ocr_text: Optional[str] = Field(None, description="Exact text returned by handwriting recognition")
    corrected_text: Optional[str] = Field(None, description="Optional administrator correction")
    crop_image: Optional[str] = Field(None, description="Cropped handwritten image data URL")
    interpreted_recipients: List[HandwrittenInstruction] = Field(
        default_factory=list, description="Semantic meaning resolved by application"
    )


class OCRResult(BaseModel):
    document_id: str = Field(..., description="Unique document ID (e.g. CIR-20261007-001)")
    filename: str = Field(..., description="Original filename uploaded")
    file_type: str = Field(..., description="File extension category (pdf, image)")
    status: str = Field("success", description="Processing status")
    copy_to_found: bool = Field(..., description="Whether a Copy to / distribution section was found")
    copy_to_pages: List[int] = Field(default_factory=list, description="Pages where Copy to sections reside")
    recipients: List[Recipient] = Field(default_factory=list, description="Extracted recipients list")
    handwritten_text: List[HandwrittenText] = Field(default_factory=list, description="Handwritten text blocks")
    handwritten_crop_image: Optional[str] = Field(None, description="Original cropped handwritten image from PDF/image")
    raw_ocr_text: Optional[str] = Field(None, description="Exact text returned by handwriting recognition")
    corrected_text: Optional[str] = Field(None, description="Optional administrator correction")
    interpreted_recipients: List[HandwrittenInstruction] = Field(
        default_factory=list, description="Semantic meaning resolved by application"
    )


class ProcessResponse(BaseModel):
    status: str = "success"
    document_id: str
    output_file: str
    data: OCRResult


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
