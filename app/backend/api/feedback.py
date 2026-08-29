"""ThermalEye API — Inspector Feedback & Model Calibration Endpoints.

Handles:
- `POST /api/feedback`: Ingest ground-truth inspection verifications.
- `GET /api/feedback/metrics`: Retrieve live field accuracy stats.
"""
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from shared.config import REGION
from intelligence.agents.feedback import submit_inspector_feedback, get_feedback_metrics

router = APIRouter(prefix="/feedback", tags=["Inspector Feedback"])


class FeedbackSubmissionRequest(BaseModel):
    cluster_id: str = Field(..., description="Target cluster ID e.g. CLU-8941")
    confirmed_category: str = Field(..., description="Ground-truth category verified on-site")
    original_category: str = Field(..., description="Model predicted category")
    inspector_name: str = Field(default="Field Officer", description="Name of the inspecting officer")
    badge_number: str = Field(default="SPCB-INSP-01", description="Official badge/ID")
    field_notes: str = Field(default="", description="Observations from physical site audit")
    photo_url: Optional[str] = Field(default=None, description="URL or base64 of on-site photo evidence")
    region: str = Field(default=REGION, description="Geographic region")


@router.post("", status_code=201)
def post_inspector_feedback(payload: FeedbackSubmissionRequest):
    """Submit an official ground-truth verification from a field inspection."""
    try:
        record = submit_inspector_feedback(
            cluster_id=payload.cluster_id,
            confirmed_category=payload.confirmed_category,
            original_category=payload.original_category,
            inspector_name=payload.inspector_name,
            badge_number=payload.badge_number,
            field_notes=payload.field_notes,
            photo_url=payload.photo_url,
            region=payload.region
        )
        return {
            "status": "SUCCESS",
            "message": "Ground-truth audit logged successfully.",
            "feedback_record": record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


@router.get("/metrics")
def get_model_calibration_metrics(
    region: str = Query(default=REGION, description="Target geographic region")
):
    """Retrieve accuracy and calibration metrics derived from inspector ground audits."""
    return get_feedback_metrics(region=region)
