"""ThermalEye — Master Ingestion Pipeline Runner.

Runs all Phase 1 collectors and preprocessing in sequence:
1. NASA FIRMS Active Fires (VIIRS/MODIS)
2. VIIRS Nightfire (VNF Combustion Temperature)
3. OpenStreetMap Infrastructure (Industrial, Oil & Gas, Kilns, Farmland, Mines)
4. Open-Meteo Weather Vectors (Wind speed/direction, BLH, Temp)
5. Sentinel-5P NO₂ Column Density
6. Spatio-Temporal DBSCAN Clustering
7. Multi-Window Feature Panel Construction

Usage:
    python -m scripts.run_ingest --region barmer --days 30
    python -m scripts.run_ingest --region punjab --days 30 --synthetic
"""
import os
import sys
import argparse
from datetime import datetime

import pandas as pd

from shared.config import REGION, DATA_RAW
from ingestion.collectors.firms import fetch_fires
from ingestion.collectors.vnf import fetch_vnf
from ingestion.collectors.osm import fetch_osm
from ingestion.collectors.weather import fetch_weather
from ingestion.collectors.sentinel import fetch_sentinel5p_no2
from ingestion.preprocessing.clustering import spatio_temporal_clustering
from ingestion.preprocessing.panel import build_cluster_feature_panel


def run_ingestion_pipeline(region_name: str = "barmer", days: int = 30, use_synthetic: bool = False):
    """Execute complete Phase 1 ingestion suite."""
    os.environ["TE_REGION"] = region_name.lower()
    from shared.config import get_region_config
    cfg = get_region_config(region_name)

    print("=" * 70)
    print(f"🛰️  THERMALEYE INGESTION PIPELINE | REGION: {region_name.upper()} | DAYS: {days}")
    print("=" * 70)

    # 1. FIRMS Active Fires
    print("\n[Stage 1/6] Ingesting NASA FIRMS Active Fires...")
    fires_df = fetch_fires(days=days, use_synthetic=use_synthetic)

    # 2. VIIRS Nightfire
    print("\n[Stage 2/6] Ingesting VIIRS Nightfire (VNF) Temperatures...")
    vnf_df = fetch_vnf(days=days, use_synthetic=use_synthetic)

    # 3. OpenStreetMap Infrastructure
    print("\n[Stage 3/6] Ingesting OpenStreetMap Infrastructure Layers...")
    osm_df = fetch_osm(use_synthetic=use_synthetic)

    # 4. Open-Meteo Weather Vectors
    print("\n[Stage 4/6] Ingesting Atmospheric & Wind Field Vectors...")
    weather_df = fetch_weather(days=days, use_synthetic=use_synthetic)

    # 5. Sentinel-5P NO₂
    print("\n[Stage 5/6] Ingesting Sentinel-5P TROPOMI NO₂ Columns...")
    no2_df = fetch_sentinel5p_no2(days=days, use_synthetic=use_synthetic)

    # 6. Spatio-Temporal Clustering & Multi-Window Panel
    print("\n[Stage 6/6] Executing Spatio-Temporal DBSCAN & Feature Panel Construction...")
    clustered_pts, summary_df = spatio_temporal_clustering(fires_df, vnf_df)
    
    panel_df = build_cluster_feature_panel(
        summary_df, osm_df=osm_df, weather_df=weather_df, no2_df=no2_df
    )

    print("\n" + "=" * 70)
    print("✅ PHASE 1 INGESTION COMPLETE & VERIFIED")
    print(f"   • Raw Detections Processed: {len(clustered_pts)}")
    print(f"   • Physical Clusters Identified: {len(panel_df)}")
    print(f"   • Output Artifacts Saved: {DATA_RAW}")
    print("=" * 70)
    return panel_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ThermalEye Ingestion Pipeline")
    parser.add_argument("--region", type=str, default=REGION, help="Target region (barmer, punjab, delhi, etc.)")
    parser.add_argument("--days", type=int, default=30, help="Days of history to process")
    parser.add_argument("--synthetic", action="store_true", help="Force synthetic mode")

    args = parser.parse_args()
    run_ingestion_pipeline(region_name=args.region, days=args.days, use_synthetic=args.synthetic)
