"""ThermalEye API — Citizen Portal & Public Hazard Intake Endpoints.

Handles:
- `POST /api/citizen/report`: Geo-tagged public complaint intake with photo/voice note.
- `GET /api/citizen/feed`: Local area hazard feed with simplified advisory text.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from shared.config import REGION, DATA_OUT, get_region_config
from shared.grid import haversine_km

router = APIRouter(prefix="/citizen", tags=["Citizen Portal"])


class CitizenReportRequest(BaseModel):
    lat: float
    lon: float
    description: str = Field(..., description="Observed incident description")
    category_reported: str = Field(default="unidentified_fire", description="Reported fire/smoke type")
    photo_url: Optional[str] = None
    voice_note_url: Optional[str] = None
    reporter_name: Optional[str] = "Anonymous Citizen"
    phone_number: Optional[str] = None
    region: str = Field(default=REGION)


@router.post("/report", status_code=201)
def submit_citizen_report(payload: CitizenReportRequest):
    """Submit a citizen incident report with GPS coordinates and multimedia."""
    cfg = get_region_config(payload.region)
    reports_file = cfg["data_out"] / "citizen_reports.json"

    reports = []
    if reports_file.exists():
        try:
            import json
            with open(reports_file, "r", encoding="utf-8") as f:
                reports = json.load(f)
        except Exception:
            reports = []

    report_id = f"CIT-REP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    entry = {
        "report_id": report_id,
        "timestamp": datetime.now().isoformat(),
        "lat": payload.lat,
        "lon": payload.lon,
        "description": payload.description,
        "category_reported": payload.category_reported,
        "photo_url": payload.photo_url or "https://thermaleye.sih/evidence/citizen_report.jpg",
        "reporter_name": payload.reporter_name,
        "status": "RECEIVED_PENDING_TRIAGE"
    }
    reports.append(entry)

    import json
    with open(reports_file, "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)

    return {
        "status": "SUCCESS",
        "message": "Incident report registered with District Environmental Control Room.",
        "report_id": report_id
    }


@router.get("/feed")
def get_citizen_hazard_feed(
    lat: float = Query(default=26.56, description="Citizen current latitude"),
    lon: float = Query(default=73.83, description="Citizen current longitude"),
    radius_km: float = Query(default=50.0, description="Alert radius in km"),
    region: str = Query(default=REGION)
):
    """Retrieve nearby active thermal hazards for public safety awareness."""
    from app.backend.api.clusters import get_clusters
    all_clusters = get_clusters(region=region)

    nearby = []
    for c in all_clusters:
        if c.get("classification") == "sun_glint":
            continue
        c_lat = float(c.get("centroid_lat", 0.0))
        c_lon = float(c.get("centroid_lon", 0.0))
        dist_km = haversine_km(lat, lon, c_lat, c_lon)

        if dist_km <= radius_km:
            nearby.append({
                "cluster_id": c.get("cluster_id"),
                "classification": c.get("classification"),
                "hazard_label": c.get("classification", "").replace("_", " ").title(),
                "distance_km": round(dist_km, 1),
                "priority_tier": c.get("priority_tier"),
                "advisory_summary": c.get("grounded_briefing"),
                "voice_note_hi_url": c.get("voice_note_hi_url"),
                "voice_note_en_url": c.get("voice_note_en_url"),
                "status": "MONITORED_AND_CONTROLLED" if c.get("classification") == "gas_flare" else "ACTIVE_ALERT"
            })

    nearby.sort(key=lambda x: x["distance_km"])
    return {
        "user_coordinates": {"lat": lat, "lon": lon},
        "search_radius_km": radius_km,
        "hazards_detected_count": len(nearby),
        "hazard_feed": nearby
    }
