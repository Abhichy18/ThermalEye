"""ThermalEye API — Thermal Clusters & Case File Endpoints.

Provides:
- `GET /api/clusters`: Filterable list of all active thermal clusters.
- `GET /api/clusters/{cluster_id}`: Deep single-cluster intelligence dossier.
- `GET /api/clusters/stats/summary`: Aggregate executive risk telemetry.
"""
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import numpy as np

from shared.config import REGION, REGIONS, get_region_config

router = APIRouter(prefix="/clusters", tags=["Thermal Clusters"])


def _load_classifications(region_name: str) -> List[Dict[str, Any]]:
    """Helper to load classified clusters JSON for a region."""
    cfg = get_region_config(region_name)
    json_path = cfg["data_out"] / "classifications.json"

    if not json_path.exists():
        # Fallback to trigger orchestrator if output not yet generated
        from intelligence.orchestrator import run_orchestrator
        return run_orchestrator(region_name=region_name)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[api] Error reading classifications for {region_name}: {e}")
        return []


@router.get("", response_model=List[Dict[str, Any]])
def get_clusters(
    region: str = REGION,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    min_frp: float = 0.0,
    min_confidence: float = 0.0,
):
    """Retrieve all classified thermal source clusters with multi-parameter filtering."""
    records = _load_classifications(region)
    if not records:
        return []

    filtered = []
    for r in records:
        if category and r.get("classification", "").lower() != str(category).lower():
            continue
        if priority and r.get("priority_tier", "").upper() != str(priority).upper():
            continue
        if float(r.get("median_frp", 0.0)) < min_frp:
            continue
        if float(r.get("confidence", 0.0)) < min_confidence:
            continue
        filtered.append(r)

    return filtered


@router.get("/stats/summary")
def get_clusters_summary(
    region: str = Query(default=REGION, description="Target geographic region")
):
    """Compute executive telemetry metrics across all active thermal sources."""
    records = _load_classifications(region)
    if not records:
        return {
            "region": region,
            "total_clusters": 0,
            "total_radiative_power_mw": 0.0,
            "critical_p1_count": 0,
            "category_distribution": {},
            "priority_distribution": {},
            "districts_affected": []
        }

    df = pd.DataFrame(records)
    total_mw = float(df["median_frp"].sum()) if "median_frp" in df.columns else 0.0
    p1_count = int((df["priority_tier"] == "P1").sum()) if "priority_tier" in df.columns else 0
    
    cat_dist = df["classification"].value_counts().to_dict() if "classification" in df.columns else {}
    pri_dist = df["priority_tier"].value_counts().to_dict() if "priority_tier" in df.columns else {}
    districts = sorted(list(df["district_name"].dropna().unique())) if "district_name" in df.columns else []

    return {
        "region": region,
        "region_name": REGIONS.get(region, {}).get("name", region.title()),
        "total_clusters": len(records),
        "total_radiative_power_mw": round(total_mw, 1),
        "critical_p1_count": p1_count,
        "category_distribution": cat_dist,
        "priority_distribution": pri_dist,
        "districts_affected": districts,
        "available_regions": list(REGIONS.keys())
    }


@router.get("/{cluster_id}")
def get_cluster_by_id(
    cluster_id: str,
    region: str = Query(default=REGION, description="Target geographic region")
):
    """Retrieve full intelligence dossier for a single specific cluster."""
    records = _load_classifications(region)
    for r in records:
        if r.get("cluster_id", "").upper() == cluster_id.upper():
            return r
    raise HTTPException(status_code=404, detail=f"Thermal cluster '{cluster_id}' not found in region '{region}'.")
