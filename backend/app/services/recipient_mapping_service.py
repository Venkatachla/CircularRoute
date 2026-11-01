import json
import re
from pathlib import Path
from typing import Dict, List, Optional


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
        search_name = normalize_name(name)
        if not search_name:
            return None
        for entry in self._entries():
            if not isinstance(entry, dict):
                continue
            candidates = [entry.get("name", ""), *(entry.get("aliases", []) or [])]
            if any(normalize_name(str(candidate)) == search_name for candidate in candidates):
                email = str(entry.get("email", "")).strip()
                if re.fullmatch(r"[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+", email):
                    return email
                return None
        return None


recipient_mapping_service = RecipientMappingService()
