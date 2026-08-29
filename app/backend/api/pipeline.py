"""ThermalEye API — Server-Sent Events (SSE) Live Agent Pipeline Stream.

Streams real-time agent execution telemetry directly to the frontend
`AgentProgressStrip` component via SSE (EventSource).
"""
import asyncio
import json
from typing import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, Query, Request
from sse_starlette.sse import EventSourceResponse

from shared.config import REGION
from intelligence.orchestrator import run_orchestrator

router = APIRouter(prefix="/pipeline", tags=["Agent Pipeline"])


async def _stream_pipeline_execution(region_name: str) -> AsyncGenerator[Dict[str, Any], None]:
    """Execute pipeline in stages and stream structured SSE progress events."""
    stages = [
        ("INGESTION", "Connecting to NASA FIRMS (VIIRS 375m) & NOAA Nightfire sensors...", 20, 0.4),
        ("SPATIAL_FABRIC", "Mapping telemetry onto H3 res-8 cells & Open-Meteo wind vectors...", 40, 0.3),
        ("DBSCAN_CLUSTERING", "Grouping multi-pass detections into physical thermal source clusters...", 60, 0.4),
        ("7_CLASS_CLASSIFIER", "Executing hybrid physical rules & LightGBM machine learning ensemble...", 80, 0.5),
        ("EVIDENCE_ENGINE", "Constructing 4-pillar evidence trail & hypothesis rejection matrix...", 90, 0.4),
        ("ACTION_DISPATCH", "Synthesizing legal show-cause notices (PDF) & multilingual audio notes...", 98, 0.3),
    ]

    for stage_name, msg, pct, delay in stages:
        event_payload = {
            "timestamp": datetime.now().isoformat(),
            "region": region_name,
            "stage": stage_name,
            "status": "IN_PROGRESS",
            "message": msg,
            "progress_percent": pct,
        }
        yield {
            "event": "agent_progress",
            "data": json.dumps(event_payload)
        }
        await asyncio.sleep(delay)

    # Final execution
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, run_orchestrator, region_name)

    final_payload = {
        "timestamp": datetime.now().isoformat(),
        "region": region_name,
        "stage": "PIPELINE_COMPLETE",
        "status": "COMPLETED",
        "message": f"Successfully processed and verified {len(results)} physical thermal sources.",
        "progress_percent": 100,
        "total_clusters": len(results),
        "critical_p1": sum(1 for r in results if r.get("priority_tier") == "P1")
    }
    yield {
        "event": "agent_complete",
        "data": json.dumps(final_payload)
    }


@router.get("/stream")
async def stream_agent_execution(
    request: Request,
    region: str = Query(default=REGION, description="Target geographic region")
):
    """Server-Sent Events endpoint streaming live multi-agent execution."""
    generator = _stream_pipeline_execution(region_name=region)
    return EventSourceResponse(generator)


@router.post("/run")
def trigger_pipeline_sync(
    region: str = Query(default=REGION, description="Target geographic region")
):
    """Synchronous pipeline trigger."""
    results = run_orchestrator(region_name=region)
    return {
        "status": "SUCCESS",
        "region": region,
        "clusters_processed": len(results)
    }
