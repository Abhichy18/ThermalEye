"""ThermalEye API — Intervention Ledger & Response Stopwatch Endpoints.

Tracks official regulatory action audit log and response latencies.
"""
from typing import Dict, Any, List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Query

from shared.config import REGION
from intelligence.agents.ledger import get_ledger_history, record_intervention_event

router = APIRouter(prefix="/ledger", tags=["Intervention Ledger"])


class LedgerStatusUpdateRequest(BaseModel):
    status: str
    inspector_id: str = "OFFICER-01"
    notes: str = ""


@router.get("", response_model=List[Dict[str, Any]])
def get_intervention_ledger(
    region: str = Query(default=REGION, description="Target geographic region")
):
    """Retrieve full regulatory intervention ledger history."""
    return get_ledger_history(region=region)


@router.post("/{cluster_id}/action")
def update_ledger_status(
    cluster_id: str,
    payload: LedgerStatusUpdateRequest,
    region: str = Query(default=REGION, description="Target region")
):
    """Update regulatory status for an intervention."""
    from app.backend.api.clusters import get_cluster_by_id
    try:
        record = get_cluster_by_id(cluster_id, region=region)
        entry = record_intervention_event(
            cluster_record=record,
            action_status=payload.status.upper(),
            inspector_id=payload.inspector_id,
            notes=payload.notes
        )
        return {
            "status": "SUCCESS",
            "ledger_entry": entry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update ledger: {str(e)}")
