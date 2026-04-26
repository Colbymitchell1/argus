from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from datetime import datetime, timezone
from typing import Optional
import json

from models.schemas import (
    TrainingCaptureRequest,
    TrainingCaptureResponse,
    TrainingStatsResponse,
)
from services import training_service
from config import settings

router = APIRouter()


@router.post("/capture", response_model=TrainingCaptureResponse)
async def capture_interaction(req: TrainingCaptureRequest):
    """Append one interaction to the training dataset (JSONL)."""
    payload = req.model_dump(exclude_none=True)
    total = training_service.append_capture(settings.TRAINING_DATA_PATH, payload)
    return TrainingCaptureResponse(
        saved=True,
        captured_at=datetime.now(timezone.utc),
        total_records=total,
        path=settings.TRAINING_DATA_PATH,
    )


@router.get("/stats", response_model=TrainingStatsResponse)
async def get_stats():
    """Dataset stats — record count, file size, last capture timestamp."""
    s = training_service.stats(settings.TRAINING_DATA_PATH)
    last = None
    if s["last_capture"]:
        try:
            last = datetime.fromisoformat(s["last_capture"].replace("Z", "+00:00"))
        except ValueError:
            last = None
    return TrainingStatsResponse(
        total_records=s["total_records"],
        path=settings.TRAINING_DATA_PATH,
        size_bytes=s["size_bytes"],
        last_capture=last,
    )


@router.get("/export")
async def export_dataset(since: Optional[str] = Query(None, description="ISO8601 timestamp")):
    """Stream the dataset as JSONL. Optional ?since= filter for incremental pulls."""
    def stream():
        for rec in training_service.export_iter(settings.TRAINING_DATA_PATH, since=since):
            yield json.dumps(rec, ensure_ascii=False) + "\n"

    filename = f"argus-training-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.jsonl"
    return StreamingResponse(
        stream(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
