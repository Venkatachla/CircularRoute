from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class Recipient(BaseModel):
    raw_text: str = Field(..., description="Original extracted raw text of the recipient")
    text: str = Field(..., description="Minimally normalized recipient text (whitespace trimmed)")
    type: Literal["printed", "handwritten"] = Field(..., description="Recipient text type")
    confidence: Optional[float] = Field(None, description="OCR confidence score if available")
    source_page: int = Field(..., description="1-indexed page number where recipient was found")


class HandwrittenText(BaseModel):
    text: str = Field(..., description="Recognized handwritten text string")
    confidence: Optional[float] = Field(None, description="Handwriting recognition confidence")
    associated_with: str = Field("copy_to", description="Target section association")
    source_page: int = Field(..., description="1-indexed page number of handwritten addition")


class OCRResult(BaseModel):
    document_id: str = Field(..., description="Unique document ID (e.g. CIR-20261007-001)")
    filename: str = Field(..., description="Original filename uploaded")
    file_type: str = Field(..., description="File extension category (pdf, image)")
    status: str = Field("success", description="Processing status")
    copy_to_found: bool = Field(..., description="Whether a Copy to / distribution section was found")
    copy_to_pages: List[int] = Field(default_factory=list, description="Pages where Copy to sections reside")
    recipients: List[Recipient] = Field(default_factory=list, description="Extracted recipients list")
    handwritten_text: List[HandwrittenText] = Field(default_factory=list, description="Handwritten text blocks")


class ProcessResponse(BaseModel):
    status: str = "success"
    document_id: str
    output_file: str
    data: OCRResult


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
