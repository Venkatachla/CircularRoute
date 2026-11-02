import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from app.services.directory_service import directory_service


MAPPING_FILE = Path(__file__).resolve().parents[2] / "recipient_email_map.json"


def normalize_name(value: str) -> str:
    """Normalize recipient names for case- and punctuation-insensitive exact lookup."""
    cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", value or "")
    return re.sub(r"[^a-z0-9]+", "", cleaned.casefold())


class RecipientMappingService:
    def __init__(self, mapping_file: Path = MAPPING_FILE):
        self.mapping_file = mapping_file

    def _entries(self) -> List[Dict[str, object]]:
        if not self.mapping_file.exists():
            return []
        with self.mapping_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get("recipients", []) if isinstance(data, dict) else []

    def find_email(self, name: str) -> Optional[str]:
        emails = self.resolve(name).get("emails", [])
        return emails[0] if emails else None

    def resolve(self, name: str, faculty_id: Optional[str] = None) -> Dict[str, object]:
        search_name = normalize_name(name)
        if not search_name:
            return {"status": "unmatched", "emails": []}
        for entry in self._entries():
            if not isinstance(entry, dict):
                continue
            candidates = [entry.get("name", ""), *(entry.get("aliases", []) or [])]
            if any(normalize_name(str(candidate)) == search_name for candidate in candidates):
                if entry.get("skip") is True:
                    return {"status": "skipped", "emails": []}
                values = entry.get("emails") or ([entry.get("email")] if entry.get("email") else [])
                emails = [str(value).strip() for value in values if isinstance(value, str) and re.fullmatch(r"[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+", value.strip())]
                return {"status": "matched" if emails else "unmatched", "emails": emails}

        # Canonical faculty names outside the small test map can use the official workbook.
        for faculty in directory_service.get_directory():
            if faculty.designation.lower() != "faculty":
                continue
            name_matches = normalize_name(faculty.name) == search_name or any(normalize_name(alias) == search_name for alias in faculty.aliases)
            id_matches = bool(faculty_id) and normalize_name(faculty.id) == normalize_name(faculty_id)
            if name_matches or id_matches:
                email = faculty.email.strip()
                if re.fullmatch(r"[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+", email):
                    return {"status": "matched", "emails": [email]}
                return {"status": "unmatched", "emails": []}
        return {"status": "unmatched", "emails": []}


recipient_mapping_service = RecipientMappingService()
