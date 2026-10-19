from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DirectoryEntry(BaseModel):
    id: str = Field(..., description="Unique ID for directory record (e.g. DIR-001)")
    name: str = Field(..., description="Full name of person or title of post")
    designation: str = Field(..., description="Official designation (e.g. HOD Computer Science)")
    department: str = Field(..., description="Department key or name (e.g. cse, admin, sports)")
    email: str = Field(..., description="Official email address")
    phone: Optional[str] = Field(None, description="Contact phone number")
    aliases: List[str] = Field(default_factory=list, description="Common title aliases or abbreviations for matching")


class ResolvedRecipient(BaseModel):
    raw_text: str = Field(..., description="Extracted recipient raw text")
    normalized_text: str = Field(..., description="Normalized text string")
    type: str = Field("printed", description="printed or handwritten")
    matched_entry: Optional[DirectoryEntry] = Field(None, description="Matched directory entry if found")
    matched_email: Optional[str] = Field(None, description="Extracted or mapped email address")
    match_status: str = Field("unresolved", description="matched, fuzzy_match, or unresolved")
    confidence: float = Field(0.0, description="Match confidence score (0.0 to 1.0)")
    source_page: int = Field(1, description="Page number where recipient was extracted")


class RecipientResolutionRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="Document ID to load extracted recipients from")
    raw_recipients: Optional[List[str]] = Field(None, description="Optional raw recipient strings to resolve directly")


class RecipientResolutionResponse(BaseModel):
    status: str = "success"
    document_id: Optional[str] = None
    total_recipients: int
    resolved_count: int
    resolved_recipients: List[ResolvedRecipient]
