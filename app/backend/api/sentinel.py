"""ThermalEye API — Sentinel-2 Optical Spyglass Endpoints.

Provides 10-meter Sentinel-2 true-color and SWIR (Band 12) optical telemetry
for interactive split-screen facility verification on the frontend.
"""
from fastapi import APIRouter, HTTPException, Query

from shared.config import REGION
from ingestion.collectors.sentinel import get_sentinel2_tile_metadata

router = APIRouter(prefix="/sentinel", tags=["Sentinel Imagery"])


@router.get("/tiles/{cluster_id}")
def get_sentinel_spyglass_tiles(
    cluster_id: str,
    region: str = Query(default=REGION)
):
    """Retrieve high-resolution optical true-color & SWIR infrared tile URLs for a cluster."""
    from app.backend.api.clusters import get_cluster_by_id
    try:
        record = get_cluster_by_id(cluster_id, region=region)
        lat = float(record["centroid_lat"])
        lon = float(record["centroid_lon"])
        meta = get_sentinel2_tile_metadata(lat, lon)
        return {
            "cluster_id": cluster_id,
            "classification": record.get("classification"),
            "coordinates": {"lat": lat, "lon": lon},
            "spyglass_metadata": meta,
            "verification_status": "FACILITY_VERIFIED" if record.get("dist_petroleum_km", 99.0) < 2.0 or record.get("dist_industrial_km", 99.0) < 3.0 else "UNREGISTERED_SOURCE"
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Optical tiles for '{cluster_id}' unavailable: {str(e)}")
