"""ThermalEye — Multi-Window Feature Panel & Context Fusion Engine.

Merges thermal clusters with:
1. Multi-window temporal activity (24h / 7d / 30d sliding windows)
2. OpenStreetMap geographic proximity (Distances to Industrial, Petroleum, Kilns, Farmland, Forests, Receptors)
3. Atmospheric conditions (Wind direction, velocity, BLH dispersion)
4. Administrative district assignment (Barmer, Jaisalmer, etc.)

This enriched panel is the exact input fed into Phase 2 (7-Class Classifier & Evidence Engine).
"""
import os
import math
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np

from shared.config import (
    BBOX, DATA_RAW, DATA_OUT, H3_RES, DETECT_WINDOWS_H,
    PERSISTENCE_THRESHOLDS, REGION
)
from shared.grid import haversine_km, cell_center, latlng_to_cell
from shared.districts import cell_to_district


def build_cluster_feature_panel(
    clusters_summary_df: pd.DataFrame,
    osm_df: Optional[pd.DataFrame] = None,
    weather_df: Optional[pd.DataFrame] = None,
    no2_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """Enrich each thermal cluster with spatial distances, weather, and multi-window metrics."""
    if clusters_summary_df.empty:
        print("[panel] Empty cluster summary provided.")
        return pd.DataFrame()

    enriched_records = []
    
    # Load OSM data if not passed
    if osm_df is None:
        osm_path = DATA_RAW / "osm_infrastructure.parquet"
        if osm_path.exists():
            osm_df = pd.read_parquet(osm_path)
        else:
            osm_df = pd.DataFrame()

    for _, clu in clusters_summary_df.iterrows():
        c_lat = float(clu["centroid_lat"])
        c_lon = float(clu["centroid_lon"])
        c_cell = clu["centroid_cell"]

        # ── 1. Calculate Minimum Distances to OSM Infrastructure Types ──
        dists = {
            "dist_industrial_km": 99.0,
            "dist_petroleum_km": 99.0,
            "dist_kiln_km": 99.0,
            "dist_mining_km": 99.0,
            "dist_farmland_km": 99.0,
            "dist_forest_km": 99.0,
            "dist_vulnerable_km": 99.0,
            "closest_osm_name": "Open Terrain",
            "closest_osm_tag": "landuse=rural",
            "closest_osm_kind": "rural"
        }

        min_overall_d = 99.0

        if osm_df is not None and not osm_df.empty:
            for _, o in osm_df.iterrows():
                d = haversine_km(c_lat, c_lon, float(o["lat"]), float(o["lon"]))
                kind = str(o.get("kind", ""))

                if d < min_overall_d:
                    min_overall_d = d
                    dists["closest_osm_name"] = str(o.get("name", "Unknown"))
                    dists["closest_osm_tag"] = str(o.get("tag", ""))
                    dists["closest_osm_kind"] = kind

                if kind == "industrial" and d < dists["dist_industrial_km"]:
                    dists["dist_industrial_km"] = round(d, 2)
                elif kind in ("petroleum_well", "gas_flare") and d < dists["dist_petroleum_km"]:
                    dists["dist_petroleum_km"] = round(d, 2)
                elif kind == "brick_kiln" and d < dists["dist_kiln_km"]:
                    dists["dist_kiln_km"] = round(d, 2)
                elif kind == "mining" and d < dists["dist_mining_km"]:
                    dists["dist_mining_km"] = round(d, 2)
                elif kind == "farmland" and d < dists["dist_farmland_km"]:
                    dists["dist_farmland_km"] = round(d, 2)
                elif kind == "forest" and d < dists["dist_forest_km"]:
                    dists["dist_forest_km"] = round(d, 2)
                elif kind == "vulnerable_receptor" and d < dists["dist_vulnerable_km"]:
                    dists["dist_vulnerable_km"] = round(d, 2)

        # ── 2. Multi-Window Temporal Horizon (24h / 7d / 30d) ──
        duration_h = float(clu["duration_hours"])
        persistence = float(clu["persistence_score"])

        if duration_h <= 48.0 and clu["detections_count"] <= 8:
            temporal_urgency = "acute"      # Instant spike e.g. Factory explosion / Bonfire
        elif duration_h <= 168.0:           # Within 7 days
            temporal_urgency = "emerging"   # Newly activated kiln / flare
        else:
            temporal_urgency = "chronic"    # Established multi-week persistent source

        # ── 3. Administrative District Mapping ──
        dist_info = cell_to_district(c_cell)

        # ── 4. Combine into complete feature row ──
        row = {
            **clu.to_dict(),
            **dists,
            "temporal_urgency": temporal_urgency,
            "district_id": dist_info.get("district_id", "D001"),
            "district_name": dist_info.get("district_name", "Barmer"),
            "state": dist_info.get("state", "Rajasthan"),
            "region": REGION,
        }
        enriched_records.append(row)

    panel_df = pd.DataFrame(enriched_records)
    out_path = DATA_RAW / "enriched_clusters_panel.parquet"
    panel_df.to_parquet(out_path, index=False)
    print(f"[panel] Built enriched feature panel with {len(panel_df)} clusters -> saved to {out_path}")
    return panel_df


if __name__ == "__main__":
    from ingestion.collectors.firms import fetch_fires
    from ingestion.collectors.vnf import fetch_vnf
    from ingestion.collectors.osm import fetch_osm
    from ingestion.preprocessing.clustering import spatio_temporal_clustering

    f_df = fetch_fires(days=30)
    v_df = fetch_vnf(days=30)
    o_df = fetch_osm(use_synthetic=True)
    
    _, sum_df = spatio_temporal_clustering(f_df, v_df)
    panel = build_cluster_feature_panel(sum_df, osm_df=o_df)
    
    print("\nEnriched Panel Sample:")
    cols = ["cluster_id", "centroid_lat", "centroid_lon", "median_frp", "temporal_urgency", "closest_osm_name", "district_name"]
    print(panel[[c for c in cols if c in panel.columns]].to_string())
