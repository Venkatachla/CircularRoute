import os
import json
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.schemas.distribution_schema import DistributionRow, TimelineEvent, DistributionResponse

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DISTRIBUTION_FILE = DATA_DIR / "distribution.json"

DEFAULT_DISTRIBUTION_SEED: Dict[str, Any] = {
    "timeline": [
        {
            "t": "10:30 AM",
            "text": "System initialized and ready for circular distribution.",
            "kind": "info"
        }
    ],
    "rows": []
}


class DistributionService:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not DISTRIBUTION_FILE.exists():
            with open(DISTRIBUTION_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_DISTRIBUTION_SEED, f, indent=2)

    def get_distribution(self) -> DistributionResponse:
        self._ensure_file()
        try:
            with open(DISTRIBUTION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            timeline = [TimelineEvent(**item) for item in data.get("timeline", [])]
            rows = [DistributionRow(**item) for item in data.get("rows", [])]
            return DistributionResponse(
                status="success",
                total_distributed=len(rows),
                timeline=timeline,
                rows=rows
            )
        except Exception:
            return DistributionResponse(
                status="success",
                total_distributed=0,
                timeline=[],
                rows=[]
            )

    def record_mail_dispatch(
        self, document_id: str, dispatch_results: List[Dict[str, Any]], subject: str = ""
    ) -> DistributionResponse:
        self._ensure_file()
        current_data = self.get_distribution()

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        now_time_only = datetime.datetime.now().strftime("%I:%M %p")

        new_rows = list(current_data.rows)
        new_timeline = list(current_data.timeline)

        sent_count = 0
        failed_count = 0

        for r in dispatch_results:
            row_id = f"DIST-{uuid.uuid4().hex[:6].upper()}"
            status_state = "delivered" if r["status"] == "sent" else "failed"

            if r["status"] == "sent":
                sent_count += 1
            else:
                failed_count += 1

            new_rows.insert(0, DistributionRow(
                id=row_id,
                document_id=document_id,
                name=r["name"],
                email=r["email"],
                dept=r["dept"],
                sentAt=now_str,
                state=status_state,
                error=r.get("error")
            ))

        # Add event to timeline
        summary_msg = f"Dispatched circular {document_id} to {sent_count} recipient(s)."
        if failed_count > 0:
            summary_msg += f" ({failed_count} failed)"
            kind = "warning"
        else:
            kind = "success"

        new_timeline.insert(0, TimelineEvent(
            t=now_time_only,
            text=summary_msg,
            kind=kind
        ))

        # Keep max 100 rows and max 50 timeline events
        new_rows = new_rows[:100]
        new_timeline = new_timeline[:50]

        data_to_save = {
            "timeline": [t.model_dump() for t in new_timeline],
            "rows": [r.model_dump() for r in new_rows]
        }

        with open(DISTRIBUTION_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2)

        return DistributionResponse(
            status="success",
            total_distributed=len(new_rows),
            timeline=new_timeline,
            rows=new_rows
        )


# Global instance
distribution_service = DistributionService()
