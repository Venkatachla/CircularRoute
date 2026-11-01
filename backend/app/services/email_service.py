import asyncio
import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import EMAIL_ENABLED, UPLOAD_DIR
from app.schemas.distribution_schema import EmailRecipientPayload

logger = logging.getLogger(__name__)


class EmailService:
    """Send circular notifications through the Resend HTTP API."""

    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY", "").strip()
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "").strip()
        self.from_name = os.getenv("RESEND_FROM_NAME", "CircularRoute").strip()

    def is_configured(self) -> bool:
        return bool(EMAIL_ENABLED and self.api_key and self.from_email)

    async def send_circular_emails(
        self,
        document_id: str,
        recipients: List[EmailRecipientPayload],
        subject: Optional[str] = None,
        message_body: Optional[str] = None,
        attach_document: bool = True,
    ) -> List[Dict[str, Any]]:
        doc_subject = subject or f"Official Circular Notification [{document_id}]"
        attachment = self._find_attachment(document_id) if attach_document else None
        results = []

        for recipient in recipients:
            email = recipient.email.strip()
            base = {
                "email": email,
                "name": recipient.name or email,
                "dept": recipient.department or "General",
            }
            if not email or "@" not in email:
                results.append({**base, "status": "failed", "error": "Invalid recipient email address"})
            elif not EMAIL_ENABLED:
                results.append({**base, "status": "disabled", "error": "Email sending is disabled (EMAIL_ENABLED=false)"})
            elif not self.is_configured():
                results.append({**base, "status": "failed", "error": "Set RESEND_API_KEY, RESEND_FROM_EMAIL, and EMAIL_ENABLED=true"})
            else:
                success, error = await asyncio.to_thread(
                    self._send_one, email, doc_subject, message_body, document_id, attachment
                )
                results.append({**base, "status": "sent" if success else "failed", "error": error})
        return results

    @staticmethod
    def _find_attachment(document_id: str) -> Optional[Path]:
        for ext in (".pdf", ".jpg", ".jpeg", ".png", ".webp"):
            path = UPLOAD_DIR / f"{document_id}{ext}"
            if path.is_file():
                return path
        return None

    def _send_one(
        self, to_email: str, subject: str, body: Optional[str], document_id: str,
        attachment_path: Optional[Path],
    ) -> Tuple[bool, Optional[str]]:
        text = body or (
            f"Dear recipient,\n\nPlease find attached the official circular {document_id}.\n\n"
            "CircularRoute Automated Distribution System"
        )
        payload: Dict[str, Any] = {
            "from": f"{self.from_name} <{self.from_email}>",
            "to": [to_email],
            "subject": subject,
            "text": text,
        }
        if attachment_path:
            payload["attachments"] = [{
                "filename": attachment_path.name,
                "content": base64.b64encode(attachment_path.read_bytes()).decode("ascii"),
            }]

        request = Request(
            "https://api.resend.com/emails",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "CircularRoute/1.0",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=20) as response:
                response.read()
            logger.info("Resend accepted circular %s for %s", document_id, to_email)
            return True, None
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            logger.error("Resend rejected email to %s (%s): %s", to_email, exc.code, detail)
            return False, f"Resend API error ({exc.code}): {detail}"
        except (URLError, OSError, ValueError) as exc:
            logger.error("Resend request failed for %s: %s", to_email, exc)
            return False, str(exc)


email_service = EmailService()
