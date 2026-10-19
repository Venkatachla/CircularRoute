import os
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Optional, Tuple, Dict, Any
import openpyxl

from app.schemas.recipient_schema import DirectoryEntry, ResolvedRecipient
from app.schemas.ocr_schema import Recipient

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
EXCEL_FILE = DATA_DIR / "CircularRoute_Data.xlsx"
DIRECTORY_FILE = DATA_DIR / "directory.json"


class RecipientService:
    def __init__(self):
        self._ensure_directory()

    def _ensure_directory(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Primary source: CircularRoute_Data.xlsx or any .xlsx in data/
        excel_path = self._find_excel_file()
        if excel_path and excel_path.exists():
            entries = self.load_directory_from_excel(excel_path)
            if entries:
                self.save_directory(entries)
                return

        # 2. Secondary source: existing directory.json
        if DIRECTORY_FILE.exists():
            return

        # 3. Fallback: empty directory if no excel/json exists
        self.save_directory([])

    def _find_excel_file(self) -> Optional[Path]:
        if EXCEL_FILE.exists():
            return EXCEL_FILE
        for f in DATA_DIR.glob("*.xlsx"):
            return f
        return None

    def load_directory_from_excel(self, excel_path: Path) -> List[DirectoryEntry]:
        """
        Parses Excel directory spreadsheet (.xlsx) into DirectoryEntry objects.
        Flexibly handles columns: Faculty_id, Faculty_name, Faculty_email_id, Designation, Department, Aliases.
        """
        try:
            wb = openpyxl.load_workbook(excel_path)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return []

            header_row = [str(h).strip().lower() if h else "" for h in rows[0]]

            # Column Index Finder
            id_idx = next((i for i, h in enumerate(header_row) if "id" in h or "code" in h), None)
            name_idx = next((i for i, h in enumerate(header_row) if "name" in h or "faculty_name" in h), None)
            email_idx = next((i for i, h in enumerate(header_row) if "email" in h or "mail" in h), None)
            desig_idx = next((i for i, h in enumerate(header_row) if "designation" in h or "role" in h or "post" in h), None)
            dept_idx = next((i for i, h in enumerate(header_row) if "department" in h or "dept" in h), None)
            alias_idx = next((i for i, h in enumerate(header_row) if "alias" in h or "keyword" in h), None)

            entries: List[DirectoryEntry] = []

            for idx, row in enumerate(rows[1:], start=1):
                if not row or not any(row):
                    continue

                raw_id = str(row[id_idx]).strip() if id_idx is not None and row[id_idx] is not None else f"FAC-{idx:03d}"
                raw_name = str(row[name_idx]).strip() if name_idx is not None and row[name_idx] is not None else ""
                raw_email = str(row[email_idx]).strip() if email_idx is not None and row[email_idx] is not None else ""
                raw_desig = str(row[desig_idx]).strip() if desig_idx is not None and row[desig_idx] is not None else "Faculty Member"
                raw_dept = str(row[dept_idx]).strip() if dept_idx is not None and row[dept_idx] is not None else "CSE"
                raw_aliases = str(row[alias_idx]).strip() if alias_idx is not None and row[alias_idx] is not None else ""

                if not raw_name and not raw_email:
                    continue

                # Generate smart aliases
                aliases = []
                if raw_aliases:
                    aliases.extend([a.strip() for a in raw_aliases.split(",") if a.strip()])

                if raw_id and raw_id != f"FAC-{idx:03d}":
                    aliases.append(raw_id.lower())

                cleaned_name = re.sub(r'^(?:Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s*', '', raw_name, flags=re.IGNORECASE).strip()
                if cleaned_name and cleaned_name.lower() != raw_name.lower():
                    aliases.append(cleaned_name.lower())

                # Generate initials alias (e.g. Dr S Seema -> SS)
                name_words = cleaned_name.split()
                if len(name_words) >= 2:
                    initials = "".join(w[0] for w in name_words if w).lower()
                    if len(initials) >= 2 and initials not in aliases:
                        aliases.append(initials)

                entries.append(DirectoryEntry(
                    id=raw_id if raw_id else f"DIR-{idx:03d}",
                    name=raw_name,
                    designation=raw_desig,
                    department=raw_dept,
                    email=raw_email,
                    phone=None,
                    aliases=list(set(aliases))
                ))

            return entries
        except Exception as e:
            return []

    def get_directory(self) -> List[DirectoryEntry]:
        self._ensure_directory()
        try:
            with open(DIRECTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [DirectoryEntry(**item) for item in data]
        except Exception:
            return []

    def save_directory(self, entries: List[DirectoryEntry]):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(DIRECTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in entries], f, indent=2)

    def import_excel_bytes(self, file_bytes: bytes, filename: str) -> List[DirectoryEntry]:
        """
        Saves uploaded Excel bytes to data/CircularRoute_Data.xlsx and updates directory.
        """
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        excel_path = DATA_DIR / "CircularRoute_Data.xlsx"
        with open(excel_path, "wb") as f:
            f.write(file_bytes)

        entries = self.load_directory_from_excel(excel_path)
        if entries:
            self.save_directory(entries)
        return entries

    def add_directory_entry(self, entry: DirectoryEntry) -> DirectoryEntry:
        entries = self.get_directory()
        entries.append(entry)
        self.save_directory(entries)
        return entry

    def resolve_recipients(self, recipients: List[Recipient]) -> List[ResolvedRecipient]:
        """
        Resolves list of OCR Recipient objects against Excel directory records.
        """
        directory = self.get_directory()
        resolved_list: List[ResolvedRecipient] = []

        for rec in recipients:
            raw_text = rec.raw_text if hasattr(rec, "raw_text") else str(rec)
            norm_text = rec.text if hasattr(rec, "text") else self._normalize_phrase(raw_text)
            rec_type = rec.type if hasattr(rec, "type") else "printed"
            page_num = rec.source_page if hasattr(rec, "source_page") else 1

            matched_entry, matched_email, match_status, confidence = self._match_phrase_to_directory(norm_text, directory)

            resolved_list.append(ResolvedRecipient(
                raw_text=raw_text,
                normalized_text=norm_text,
                type=rec_type,
                matched_entry=matched_entry,
                matched_email=matched_email,
                match_status=match_status,
                confidence=confidence,
                source_page=page_num
            ))

        return resolved_list

    def resolve_raw_strings(self, raw_strings: List[str]) -> List[ResolvedRecipient]:
        """
        Directly resolves raw strings.
        """
        directory = self.get_directory()
        resolved_list: List[ResolvedRecipient] = []

        for raw_text in raw_strings:
            norm_text = self._normalize_phrase(raw_text)
            matched_entry, matched_email, match_status, confidence = self._match_phrase_to_directory(norm_text, directory)

            resolved_list.append(ResolvedRecipient(
                raw_text=raw_text,
                normalized_text=norm_text,
                type="printed",
                matched_entry=matched_entry,
                matched_email=matched_email,
                match_status=match_status,
                confidence=confidence,
                source_page=1
            ))

        return resolved_list

    def _normalize_phrase(self, text: str) -> str:
        # Strip bullets / list prefixes
        cleaned = re.sub(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|[\-•\*])\s*', '', text).strip()
        # Collapse internal spaces
        return re.sub(r'\s+', ' ', cleaned).strip()

    def _match_phrase_to_directory(
        self, phrase: str, directory: List[DirectoryEntry]
    ) -> Tuple[Optional[DirectoryEntry], Optional[str], str, float]:
        if not phrase:
            return None, None, "unresolved", 0.0

        p_lower = phrase.lower()

        # Check if an explicit email address is present in the raw text
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', phrase)
        inline_email = email_match.group(0) if email_match else None

        best_entry: Optional[DirectoryEntry] = None
        best_score: float = 0.0

        for entry in directory:
            # Clean names for candidate comparison
            clean_name = re.sub(r'^(?:Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s*', '', entry.name, flags=re.IGNORECASE).strip().lower()

            candidates = [entry.name.lower(), clean_name, entry.designation.lower(), entry.id.lower()] + [a.lower() for a in entry.aliases]

            # 1. Substring / Token Containment
            for candidate in candidates:
                if not candidate:
                    continue
                if candidate == p_lower or candidate in p_lower or p_lower in candidate:
                    score = 0.95 if len(candidate) >= 3 else 0.85
                    if score > best_score:
                        best_score = score
                        best_entry = entry

            # 2. SequenceMatcher similarity score
            for candidate in candidates:
                if not candidate:
                    continue
                ratio = SequenceMatcher(None, p_lower, candidate).ratio()
                if ratio > best_score:
                    best_score = ratio
                    best_entry = entry

        # Thresholding
        if best_entry and best_score >= 0.55:
            status = "matched" if best_score >= 0.80 else "fuzzy_match"
            email = inline_email or best_entry.email
            return best_entry, email, status, round(best_score, 2)

        if inline_email:
            return None, inline_email, "matched", 0.90

        return None, None, "unresolved", 0.0


# Global Instance
recipient_service = RecipientService()
