import os
import json
import re
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Optional, Tuple, Dict, Any
import openpyxl

from app.schemas.recipient_schema import DirectoryEntry, ResolvedRecipient
from app.schemas.ocr_schema import Recipient, HandwrittenInstruction
from app.services.directory_service import directory_service

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
EXCEL_FILE = DATA_DIR / "CircularRoute_Data.xlsx"
DIRECTORY_FILE = DATA_DIR / "directory.json"


class RecipientService:
    def __init__(self):
        self._ensure_directory()

    def _ensure_directory(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        excel_path = self._find_excel_file()
        if excel_path and excel_path.exists():
            entries = self.load_directory_from_excel(excel_path)
            if entries:
                self.save_directory(entries)
                return

        if DIRECTORY_FILE.exists():
            return

        self.save_directory([])

    def _find_excel_file(self) -> Optional[Path]:
        if EXCEL_FILE.exists():
            return EXCEL_FILE
        for f in DATA_DIR.glob("*.xlsx"):
            return f
        return None

    def load_directory_from_excel(self, excel_path: Path) -> List[DirectoryEntry]:
        try:
            wb = openpyxl.load_workbook(excel_path)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return []

            header_row = [str(h).strip().lower() if h else "" for h in rows[0]]
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

                aliases = []
                if raw_aliases:
                    aliases.extend([a.strip() for a in raw_aliases.split(",") if a.strip()])
                if raw_id and raw_id != f"FAC-{idx:03d}":
                    aliases.append(raw_id.lower())

                cleaned_name = re.sub(r'^(?:Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s*', '', raw_name, flags=re.IGNORECASE).strip()
                if cleaned_name and cleaned_name.lower() != raw_name.lower():
                    aliases.append(cleaned_name.lower())

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
        except Exception:
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

    # -------------------------------------------------------------------------
    # Handwritten instruction separation & resolution
    # -------------------------------------------------------------------------
    def separate_instructions(self, raw_text: str) -> List[str]:
        """Separate a handwritten Copy-To instruction into individual tokens.

        Handles:
        - Commas, ampersands, new lines, semicolons, pluses, bullets, and 'and'.
        - Leading 'To:', 'To', 'Copy to:', etc.
        - Numbered bullets like '1.', 'a)', '-'.
        """
        if not raw_text or not raw_text.strip():
            return []

        cleaned = raw_text.strip()
        # Remove leading "Copy to:" or "To:" if followed by more text
        cleaned = re.sub(r'^\s*(?:copy\s+to|copies\s+to|to)\s*[:\-\.]?\s*', '', cleaned, flags=re.IGNORECASE).strip()

        # Split on delimiters: \n, \r, &, comma, semicolon, +, bullet, and word boundary 'and'
        delimiters = r'[\r\n&,;+•*·]+|\s+\band\b\s+'
        parts = re.split(delimiters, cleaned, flags=re.IGNORECASE)

        instructions = []
        for part in parts:
            item = part.strip()
            # Strip numbering/bullets like "1.", "2)", "a)", "-", "•"
            item = re.sub(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|[\-•\*])\s*', '', item).strip()
            # Strip surrounding punctuation
            item = item.strip(".,;:!?'\"`~-_/")
            if item:
                instructions.append(item)

        return instructions

    def interpret_instruction(
        self,
        instruction: str,
        is_manual_correction: bool = False,
        original_raw: Optional[str] = None
    ) -> HandwrittenInstruction:
        """Resolve a single separated handwritten instruction against temp_data.xlsx.

        Rules:
        - "file" → File/reference, not an email recipient (INFORMATIONAL)
        - "students" → all student emails from student_list sheet (RESOLVED)
        - "faculty" → all valid faculty emails from faculty_list sheet (RESOLVED)
        - "staff" → unknown group, needs admin review (UNRESOLVED)
        - 2-3 letter faculty id → exact case-insensitive lookup in Faculty_id (RESOLVED if unique with email, UNRESOLVED if missing email or unknown)
        - explicit email → RESOLVED
        - preserve original raw instruction and track admin corrections.
        """
        norm = instruction.strip()
        lower = norm.lower()

        raw_display = original_raw if original_raw else norm
        corrected_display = norm if is_manual_correction else None

        # 1. Direct Email Address Detection
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', norm)
        if email_match:
            em = email_match.group(0)
            status = "MANUALLY CORRECTED" if is_manual_correction else "RESOLVED"
            return HandwrittenInstruction(
                instruction=norm,
                raw_text=raw_display,
                corrected_text=corrected_display,
                interpretation="Direct email address",
                status=status,
                result=f"Direct email: {em}",
                emails=[em],
                matched_faculty=None,
                unresolved_reason=None
            )

        # 2. File / Reference / Non-email recipient (INFORMATIONAL)
        if lower in ("file", "to file", "file ref", "reference", "office copy", "records", "record"):
            return HandwrittenInstruction(
                instruction=norm,
                raw_text=raw_display,
                corrected_text=corrected_display,
                interpretation="File/reference, not an email recipient",
                status="INFORMATIONAL",
                result="File/reference",
                emails=[],
                matched_faculty=None,
                unresolved_reason=None
            )

        # 3. All Students Group (RESOLVED)
        if lower in ("students", "all students", "student", "all_students"):
            student_emails = directory_service.get_all_student_emails()
            count = len(student_emails)
            status = "MANUALLY CORRECTED" if is_manual_correction else "RESOLVED"
            return HandwrittenInstruction(
                instruction=norm,
                raw_text=raw_display,
                corrected_text=corrected_display,
                interpretation="ALL_STUDENTS",
                status=status,
                result=f"All Students ({count} recipients from directory)",
                emails=student_emails,
                matched_faculty=None,
                unresolved_reason=None
            )

        # 4. All Faculty Group (RESOLVED)
        if lower in ("faculty", "all faculty", "faculties", "all_faculty"):
            faculty_emails = directory_service.get_all_faculty_emails()
            count = len(faculty_emails)
            status = "MANUALLY CORRECTED" if is_manual_correction else "RESOLVED"
            return HandwrittenInstruction(
                instruction=norm,
                raw_text=raw_display,
                corrected_text=corrected_display,
                interpretation="ALL_FACULTY",
                status=status,
                result=f"All Faculty Members ({count} recipients from directory)",
                emails=faculty_emails,
                matched_faculty=None,
                unresolved_reason=None
            )

        # 5. Staff (UNRESOLVED - do not automatically assume staff means faculty)
        if lower in ("staff", "all staff", "office staff"):
            return HandwrittenInstruction(
                instruction=norm,
                raw_text=raw_display,
                corrected_text=corrected_display,
                interpretation="Needs administrator review",
                status="UNRESOLVED",
                result="Needs administrator review",
                emails=[],
                matched_faculty=None,
                unresolved_reason="Unknown group unless approved alias exists; do not assume staff means faculty"
            )

        # 6. Two- or Three-letter Faculty Identifier (exact lookup in Faculty_id)
        if 2 <= len(norm) <= 3 and norm.isalpha():
            matches = directory_service.get_faculty_matches(norm)
            if len(matches) == 1:
                faculty = matches[0]
                if faculty.email:
                    status = "MANUALLY CORRECTED" if is_manual_correction else "RESOLVED"
                    return HandwrittenInstruction(
                        instruction=norm,
                        raw_text=raw_display,
                        corrected_text=corrected_display,
                        interpretation=f"Matched faculty member ({faculty.name})",
                        status=status,
                        result=f"{faculty.name} ({faculty.id}) · {faculty.email}",
                        emails=[faculty.email],
                        matched_faculty={
                            "Faculty_id": faculty.id,
                            "faculty_name": faculty.name,
                            "mail_id": faculty.email,
                            "id": faculty.id,
                            "name": faculty.name,
                            "email": faculty.email,
                        },
                        unresolved_reason=None
                    )
                else:
                    return HandwrittenInstruction(
                        instruction=norm,
                        raw_text=raw_display,
                        corrected_text=corrected_display,
                        interpretation=f"Matched faculty member ({faculty.name})",
                        status="UNRESOLVED",
                        result=f"{faculty.name} ({faculty.id}) · Missing email",
                        emails=[],
                        matched_faculty={
                            "Faculty_id": faculty.id,
                            "faculty_name": faculty.name,
                            "mail_id": None,
                            "id": faculty.id,
                            "name": faculty.name,
                            "email": None,
                        },
                        unresolved_reason=f"Faculty member '{faculty.name}' ({faculty.id}) found in directory, but email address is missing"
                    )
            elif len(matches) > 1:
                return HandwrittenInstruction(
                    instruction=norm,
                    raw_text=raw_display,
                    corrected_text=corrected_display,
                    interpretation=f"Ambiguous faculty identifier ({norm})",
                    status="UNRESOLVED",
                    result="Ambiguous identifier",
                    emails=[],
                    matched_faculty=None,
                    unresolved_reason=f"Multiple faculty members match identifier '{norm}'"
                )
            else:
                return HandwrittenInstruction(
                    instruction=norm,
                    raw_text=raw_display,
                    corrected_text=corrected_display,
                    interpretation=f"Unknown faculty identifier ({norm})",
                    status="UNRESOLVED",
                    result="Needs administrator review",
                    emails=[],
                    matched_faculty=None,
                    unresolved_reason=f"Identifier '{norm}' not found in faculty directory"
                )

        # 7. Name / Designation lookup in faculty directory
        for entry in directory_service.get_directory():
            if entry.designation.lower() == "faculty":
                if entry.name and lower == entry.name.lower():
                    if entry.email:
                        status = "MANUALLY CORRECTED" if is_manual_correction else "RESOLVED"
                        return HandwrittenInstruction(
                            instruction=norm,
                            raw_text=raw_display,
                            corrected_text=corrected_display,
                            interpretation=f"Matched faculty member ({entry.name})",
                            status=status,
                            result=f"{entry.name} ({entry.id}) · {entry.email}",
                            emails=[entry.email],
                            matched_faculty={"id": entry.id, "name": entry.name, "email": entry.email},
                            unresolved_reason=None
                        )

        # 8. Unresolved Fallback
        return HandwrittenInstruction(
            instruction=norm,
            raw_text=raw_display,
            corrected_text=corrected_display,
            interpretation="Needs administrator review",
            status="UNRESOLVED",
            result="Needs administrator review",
            emails=[],
            matched_faculty=None,
            unresolved_reason=f"Unrecognized recipient instruction '{norm}'"
        )

    def resolve_handwritten_section(
        self,
        raw_ocr_text: str,
        corrected_text: Optional[str] = None
    ) -> List[HandwrittenInstruction]:
        """Separates and interprets all handwritten instructions.

        Never overwrites raw_ocr_text. Preserves original handwriting and
        resolves against temp_data.xlsx.
        """
        if not raw_ocr_text and not corrected_text:
            return []

        text_to_process = corrected_text.strip() if corrected_text and corrected_text.strip() else raw_ocr_text.strip()
        is_corrected = bool(corrected_text and corrected_text.strip() and corrected_text.strip() != raw_ocr_text.strip())

        raw_instructions = self.separate_instructions(raw_ocr_text) if raw_ocr_text else []
        active_instructions = self.separate_instructions(text_to_process)

        results: List[HandwrittenInstruction] = []
        for idx, instr in enumerate(active_instructions):
            orig_raw = raw_instructions[idx] if idx < len(raw_instructions) else None
            instr_was_corrected = is_corrected and (orig_raw is None or instr != orig_raw)
            resolved = self.interpret_instruction(
                instruction=instr,
                is_manual_correction=instr_was_corrected,
                original_raw=orig_raw or instr
            )
            results.append(resolved)

        return results

    # -------------------------------------------------------------------------
    # Legacy Recipient Resolution (for printed recipients & existing tests)
    # -------------------------------------------------------------------------
    def resolve_recipients(self, recipients: List[Recipient]) -> List[ResolvedRecipient]:
        directory = self.get_directory()
        resolved_list: List[ResolvedRecipient] = []

        for rec in recipients:
            # OCR results are loaded from JSON before routing, so recipients
            # arrive here as dictionaries rather than Pydantic model objects.
            if isinstance(rec, dict):
                raw_text = str(rec.get("raw_text") or rec.get("text") or "")
                norm_text = str(rec.get("text") or self._normalize_phrase(raw_text))
                rec_type = rec.get("type", "printed")
                page_num = rec.get("source_page", 1)
            else:
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
        cleaned = re.sub(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|[\-•\*])\s*', '', text).strip()
        return re.sub(r'\s+', ' ', cleaned).strip()

    def _match_phrase_to_directory(
        self, phrase: str, directory: List[DirectoryEntry]
    ) -> Tuple[Optional[DirectoryEntry], Optional[str], str, float]:
        if not phrase:
            return None, None, "unresolved", 0.0

        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', phrase)
        if email_match:
            return None, email_match.group(0), "matched", 0.90

        # Rule A – students (all)
        if re.search(r'\bstudents\b', phrase, re.IGNORECASE):
            emails = directory_service.get_all_student_emails()
            return None, ",".join(emails), "matched", 1.0

        # Rule B – faculty (all)
        if re.search(r'\bfaculty\b', phrase, re.IGNORECASE):
            emails = directory_service.get_all_faculty_emails()
            return None, ",".join(emails), "matched", 1.0

        # Rule C – short faculty identifier (2‑3 letters)
        identifier = phrase.strip().strip('.,;:!@#?$%&*()[]{}<>').lower()
        if 2 <= len(identifier) <= 3 and identifier.isalpha():
            entry = directory_service.get_faculty_by_id(identifier)
            if entry and entry.email:
                return entry, entry.email, "matched", 1.0
            return None, None, "unresolved", 0.0

        p_lower = phrase.lower()
        best_entry: Optional[DirectoryEntry] = None
        best_score: float = 0.0

        for entry in directory:
            clean_name = re.sub(r'^(?:Dr\.?|Prof\.?|Mr\.?|Mrs\.?|Ms\.?)\s*', '', entry.name, flags=re.IGNORECASE).strip().lower()
            candidates = [entry.name.lower(), clean_name, entry.designation.lower(), entry.id.lower()] + [a.lower() for a in entry.aliases]

            for candidate in candidates:
                if not candidate:
                    continue
                if candidate == p_lower or candidate in p_lower or p_lower in candidate:
                    score = 0.95 if len(candidate) >= 3 else 0.85
                    if score > best_score:
                        best_score = score
                        best_entry = entry

            for candidate in candidates:
                if not candidate:
                    continue
                ratio = SequenceMatcher(None, p_lower, candidate).ratio()
                if ratio > best_score:
                    best_score = ratio
                    best_entry = entry

        if best_entry and best_score >= 0.55:
            status = "matched" if best_score >= 0.80 else "fuzzy_match"
            email = best_entry.email
            return best_entry, email, status, round(best_score, 2)

        return None, None, "unresolved", 0.0


recipient_service = RecipientService()
