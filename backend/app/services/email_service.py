import os
import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from app.schemas.distribution_schema import EmailRecipientPayload
from app.config import UPLOAD_DIR

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_password = os.getenv("SMTP_PASSWORD", "").strip()
        self.from_email = os.getenv("SMTP_FROM_EMAIL", "circulars@univ.edu").strip()
        self.from_name = os.getenv("SMTP_FROM_NAME", "CircularRoute System").strip()
        self.use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

    def is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)

    async def send_circular_emails(
        self,
        document_id: str,
        recipients: List[EmailRecipientPayload],
        subject: Optional[str] = None,
        message_body: Optional[str] = None,
        attach_document: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Dispatches emails to target recipients. If SMTP is configured, sends via live SMTP.
        Otherwise operates in simulated delivery mode and records dispatch audit status.
        """
        results = []
        doc_subject = subject or f"Official Circular Notification [{document_id}]"

        # Locate circular file to attach if requested
        attachment_path = None
        if attach_document:
            for ext in [".pdf", ".jpg", ".jpeg", ".png"]:
                fpath = UPLOAD_DIR / f"{document_id}{ext}"
                if fpath.exists():
                    attachment_path = fpath
                    break

        for rec in recipients:
            email_addr = rec.email.strip()
            rec_name = rec.name or email_addr
            dept = rec.department or "General"

            if not email_addr or "@" not in email_addr:
                results.append({
                    "email": email_addr,
                    "name": rec_name,
                    "dept": dept,
                    "status": "failed",
                    "error": "Invalid recipient email address"
                })
                continue

            # Send asynchronously in executor to avoid blocking event loop
            if self.is_configured():
                success, error_msg = await asyncio.to_thread(
                    self._send_single_email,
                    email_addr,
                    doc_subject,
                    message_body,
                    document_id,
                    attachment_path
                )
                status = "sent" if success else "failed"
            else:
                # Simulated dispatch mode
                logger.info(f"[SIMULATED MAIL DISPATCH] To: {email_addr} | Subject: {doc_subject} | Doc: {document_id}")
                success = True
                status = "sent"
                error_msg = None

            results.append({
                "email": email_addr,
                "name": rec_name,
                "dept": dept,
                "status": status,
                "error": error_msg
            })

        return results

    def _send_single_email(
        self,
        to_email: str,
        subject: str,
        message_body: Optional[str],
        document_id: str,
        attachment_path: Optional[Path]
    ) -> Tuple[bool, Optional[str]]:
        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                        <h2 style="color: #2563eb; margin-top: 0;">Official Institutional Circular</h2>
                        <p><strong>Document ID:</strong> {document_id}</p>
                        <hr style="border: 0; border-top: 1px solid #eee;" />
                        <div style="margin: 20px 0;">
                            {message_body or "Please find the official circular document details processed via CircularRoute."}
                        </div>
                        <p style="font-size: 0.85em; color: #666; margin-top: 30px;">
                            This is an automated notification from CircularRoute Automatic Document Routing System.
                        </p>
                    </div>
                </body>
            </html>
            """
            msg.attach(MIMEText(html_content, "html"))

            if attachment_path and attachment_path.exists():
                with open(attachment_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=attachment_path.name)
                part['Content-Disposition'] = f'attachment; filename="{attachment_path.name}"'
                msg.attach(part)

            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            if self.use_tls:
                server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()

            return True, None
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False, str(e)


# Global instance
email_service = EmailService()
