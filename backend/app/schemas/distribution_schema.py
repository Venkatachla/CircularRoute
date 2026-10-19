from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EmailRecipientPayload(BaseModel):
    name: Optional[str] = Field(None, description="Recipient full name or title")
    email: str = Field(..., description="Target recipient email address")
    department: Optional[str] = Field(None, description="Department name or code")


class SendMailRequest(BaseModel):
    recipients: List[EmailRecipientPayload] = Field(..., description="List of target recipient emails")
    subject: Optional[str] = Field(None, description="Custom email subject line")
    message_body: Optional[str] = Field(None, description="Additional notes or message body")
    attach_document: bool = Field(True, description="Whether to attach original circular document")


class DistributionRow(BaseModel):
    id: str = Field(..., description="Unique distribution record ID")
    document_id: str = Field(..., description="Associated document ID")
    name: str = Field(..., description="Recipient name or title")
    email: str = Field(..., description="Recipient email address")
    dept: str = Field("General", description="Department code")
    sentAt: str = Field(..., description="Timestamp when email was sent/queued")
    state: str = Field("sent", description="sent, delivered, pending, failed")
    error: Optional[str] = Field(None, description="Failure reason if failed")


class TimelineEvent(BaseModel):
    t: str = Field(..., description="Timestamp string (HH:MM or YYYY-MM-DD HH:MM)")
    text: str = Field(..., description="Timeline message description")
    kind: str = Field("info", description="info, success, warning, error")


class DistributionResponse(BaseModel):
    status: str = "success"
    total_distributed: int
    timeline: List[TimelineEvent]
    rows: List[DistributionRow]
