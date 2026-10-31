import os
import logging
from pathlib import Path
from typing import List, Optional

import openpyxl

from app.schemas.recipient_schema import DirectoryEntry

logger = logging.getLogger(__name__)


class DirectoryService:
    """Service to load and cache directory information from the Excel workbook.

    Expected workbook location: backend/temp_data.xlsx.
    Sheets:
        - student_list with column `student_mail_id`
        - faculty_list with columns `Faculty_id`, `faculty_name`, `mail_id`
    """

    def __init__(self, excel_path: Optional[Path] = None):
        if excel_path:
            self._excel_path = excel_path
        else:
            # Look in backend root or current dir
            root_dir = Path(__file__).parents[2]
            p = root_dir / "temp_data.xlsx"
            if not p.exists():
                p = Path("backend/temp_data.xlsx")
            if not p.exists():
                p = Path("temp_data.xlsx")
            self._excel_path = p.resolve()

        self._cache: List[DirectoryEntry] = []
        self._last_modified: Optional[float] = None
        self._load_excel_if_needed()

    def _load_excel_if_needed(self):
        if not self._excel_path.exists():
            logger.warning(f"Excel directory file not found: {self._excel_path}")
            return
        try:
            mtime = self._excel_path.stat().st_mtime
            if self._last_modified == mtime and self._cache:
                return
            self._cache = self._load_excel()
            self._last_modified = mtime
            logger.info(f"Loaded {len(self._cache)} directory records from {self._excel_path}")
        except Exception as e:
            logger.error(f"Error loading Excel directory: {e}")

    def reload(self):
        """Force reload of the Excel workbook."""
        self._last_modified = None
        self._load_excel_if_needed()

    def _load_excel(self) -> List[DirectoryEntry]:
        wb = openpyxl.load_workbook(self._excel_path, data_only=True)
        entries: List[DirectoryEntry] = []

        # ------------------- Students -------------------------------------
        if "student_list" in wb.sheetnames:
            student_sheet = wb["student_list"]
            rows = list(student_sheet.iter_rows(values_only=True))
            if rows:
                header = [str(cell).strip().lower() if cell else "" for cell in rows[0]]
                email_idx = next((i for i, h in enumerate(header) if "student_mail_id" in h or "email" in h or "mail" in h), None)
                if email_idx is not None:
                    for row in rows[1:]:
                        if not row or email_idx >= len(row):
                            continue
                        val = row[email_idx]
                        if not val or str(val).strip().lower() in ("none", "null", ""):
                            continue
                        email = str(val).strip()
                        entries.append(
                            DirectoryEntry(
                                id=email,
                                name="",
                                designation="Student",
                                department="",
                                email=email,
                                phone=None,
                                aliases=[email.lower()],
                            )
                        )

        # ------------------- Faculty --------------------------------------
        if "faculty_list" in wb.sheetnames:
            faculty_sheet = wb["faculty_list"]
            rows = list(faculty_sheet.iter_rows(values_only=True))
            if rows:
                header = [str(cell).strip().lower() if cell else "" for cell in rows[0]]
                id_idx = next((i for i, h in enumerate(header) if h == "faculty_id" or "id" in h), None)
                name_idx = next((i for i, h in enumerate(header) if "name" in h), None)
                mail_idx = next((i for i, h in enumerate(header) if "mail" in h or "email" in h), None)

                for row in rows[1:]:
                    if not row:
                        continue
                    fid = str(row[id_idx]).strip() if id_idx is not None and id_idx < len(row) and row[id_idx] is not None else ""
                    name = str(row[name_idx]).strip() if name_idx is not None and name_idx < len(row) and row[name_idx] is not None else ""
                    raw_mail = row[mail_idx] if mail_idx is not None and mail_idx < len(row) else None
                    email = str(raw_mail).strip() if raw_mail is not None and str(raw_mail).strip().lower() not in ("none", "null", "") else ""

                    if not fid and not name:
                        continue

                    entries.append(
                        DirectoryEntry(
                            id=fid,
                            name=name,
                            designation="Faculty",
                            department="",
                            email=email,
                            phone=None,
                            aliases=[fid.lower()] if fid else [],
                        )
                    )

        return entries

    def get_all_student_emails(self) -> List[str]:
        """Returns deduplicated student emails from student_list sheet."""
        self._load_excel_if_needed()
        seen = set()
        emails = []
        for e in self._cache:
            if e.designation.lower() == "student" and e.email:
                clean = e.email.strip()
                if clean and clean.lower() not in seen:
                    seen.add(clean.lower())
                    emails.append(clean)
        return emails

    def get_all_faculty_emails(self) -> List[str]:
        """Returns deduplicated faculty emails with non-empty valid addresses."""
        self._load_excel_if_needed()
        seen = set()
        emails = []
        for e in self._cache:
            if e.designation.lower() == "faculty" and e.email:
                clean = e.email.strip()
                if clean and clean.lower() not in seen:
                    seen.add(clean.lower())
                    emails.append(clean)
        return emails

    def get_faculty_by_id(self, fid: str) -> Optional[DirectoryEntry]:
        """Exact case-insensitive match on Faculty_id."""
        self._load_excel_if_needed()
        fid_norm = fid.strip().lower()
        matches = [e for e in self._cache if e.designation.lower() == "faculty" and e.id.strip().lower() == fid_norm]
        if len(matches) == 1:
            return matches[0]
        return None

    def get_faculty_matches(self, fid: str) -> List[DirectoryEntry]:
        """Returns all matches for ambiguity detection."""
        self._load_excel_if_needed()
        fid_norm = fid.strip().lower()
        return [e for e in self._cache if e.designation.lower() == "faculty" and e.id.strip().lower() == fid_norm]

    def get_directory(self) -> List[DirectoryEntry]:
        """Return the full cached directory (students + faculty)."""
        self._load_excel_if_needed()
        return self._cache


directory_service = DirectoryService()
