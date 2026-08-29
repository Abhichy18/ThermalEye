"""ThermalEye — Spatio-Temporal Thermal Clustering (DBSCAN).

Aggregates raw, scattered satellite thermal detections (NASA FIRMS & VIIRS Nightfire)
into distinct, coherent physical Thermal Source Clusters.

Why Clustering is Mandatory:
A single industrial plant (e.g. Mangala Processing Terminal) triggers 100+ raw FIRMS
dots over a 30-day period across slightly shifting overpasses (~375m pixel jitter).
Treating them as 100 separate fires confuses inspectors.
DBSCAN groups them into ONE physical installation: "CLU-8941" with:
- Centroid Lat/Lon
- Spatial bounding radius
- First seen / Last seen timestamps (Total duration in hours/days)
- Temporal persistence: (Active overpasses / Total window overpasses)
- FRP statistics: Median FRP (Invariant #2: Median over mean), Max FRP, CoV (std/mean)
- Diurnal ratio: (Night detections / Total detections)
"""
import os
import math
from typing import Optional, List, Dict, Any, Tuple

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

from shared.config import (
    BBOX, DATA_RAW, DATA_OUT, H3_RES, REGION
)
from shared.grid import haversine_km, latlng_to_cell, cell_center


def spatio_temporal_clustering(
    firms_df: pd.DataFrame,
    vnf_df: Optional[pd.DataFrame] = None,
    spatial_eps_km: float = 1.2,
    temporal_eps_hours: float = 72.0,
    min_samples: int = 2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Run spatio-temporal DBSCAN on combined thermal detections.

    Returns:
    1. `clustered_points_df`: Every raw detection assigned a `cluster_id`.
    2. `clusters_summary_df`: Summary metadata for each physical cluster.
    """
    if firms_df.empty and (vnf_df is None or vnf_df.empty):
        print("[clustering] No detections to cluster.")
        return pd.DataFrame(), pd.DataFrame()

    points = []
    
    # 1. Process FIRMS detections
    if not firms_df.empty:
        for _, r in firms_df.iterrows():
            points.append({
                "ts": r["ts"],
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "frp": float(r.get("frp", 10.0)),
                "brightness": float(r.get("brightness", 330.0)),
                "daynight": str(r.get("daynight", "D")),
                "temp_k": np.nan,
                "source_type": "FIRMS"
            })

    # 2. Process VNF Nightfire detections (if provided)
    if vnf_df is not None and not vnf_df.empty:
        for _, r in vnf_df.iterrows():
            points.append({
                "ts": r["ts"],
                "lat": float(r["lat"]),
                "lon": float(r["lon"]),
                "frp": float(r.get("radiant_heat_mw", 12.0)),
                "brightness": 350.0,
                "daynight": "N",
                "temp_k": float(r.get("temp_k", 1600.0)),
                "source_type": "VNF"
            })

    df = pd.DataFrame(points)
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df = df.sort_values("ts").reset_index(drop=True)

    # Convert lat/lon to approximate kilometers from regional origin
    ref_lat, ref_lon = BBOX["lat_min"], BBOX["lon_min"]
    lat_rad = math.radians(ref_lat)
    
    # 1 deg lat ~ 111 km; 1 deg lon ~ 111 * cos(lat) km
    df["x_km"] = (df["lon"] - ref_lon) * (111.32 * math.cos(lat_rad))
    df["y_km"] = (df["lat"] - ref_lat) * 110.57
    
    # Time in days from earliest detection
    t0 = df["ts"].min()
    df["t_days"] = (df["ts"] - t0).dt.total_seconds() / 86400.0

    # Feature matrix for spatial clustering:
    # We prioritize SPATIAL proximity (sources don't move), allowing temporal chaining.
    # Persistent sources (flares, kilns) remain in the same 1km box for months.
    coords_km = df[["x_km", "y_km"]].values

    # Run spatial DBSCAN: points within spatial_eps_km are linked into the same physical site
    db = DBSCAN(eps=spatial_eps_km, min_samples=min_samples, metric="euclidean")
    df["cluster_label"] = db.fit_predict(coords_km)

    # Label noise points (-1) as isolated singletons
    noise_mask = df["cluster_label"] == -1
    noise_count = noise_mask.sum()
    if noise_count > 0:
        next_id = df["cluster_label"].max() + 1
        df.loc[noise_mask, "cluster_label"] = range(next_id, next_id + noise_count)

    # Assign clean string cluster IDs e.g. "CLU-8941"
    df["cluster_id"] = [f"CLU-{lbl:04d}" for lbl in df["cluster_label"]]
    df["cell"] = [latlng_to_cell(r.lat, r.lon) for _, r in df.iterrows()]

    # 3. Build cluster summary metrics
    cluster_records = []
    
    for cid, grp in df.groupby("cluster_id"):
        centroid_lat = float(grp["lat"].mean())
        centroid_lon = float(grp["lon"].mean())
        centroid_cell = latlng_to_cell(centroid_lat, centroid_lon)

        ts_min = grp["ts"].min()
        ts_max = grp["ts"].max()
        duration_hours = max(1.0, (ts_max - ts_min).total_seconds() / 3600.0)
        duration_days = duration_hours / 24.0

        total_pts = len(grp)
        night_pts = int((grp["daynight"] == "N").sum())
        day_pts = total_pts - night_pts
        diurnal_ratio = night_pts / total_pts if total_pts > 0 else 0.0

        frp_vals = grp["frp"].values
        mean_frp = float(np.mean(frp_vals))
        median_frp = float(np.median(frp_vals)) # Invariant #2: Median over mean
        max_frp = float(np.max(frp_vals))
        std_frp = float(np.std(frp_vals))
        cov_frp = (std_frp / mean_frp) if mean_frp > 0 else 0.0

        # VNF Temperature (if available in cluster)
        valid_temps = grp["temp_k"].dropna().values
        vnf_temp_k = float(np.median(valid_temps)) if len(valid_temps) > 0 else None

        # Distinct active days
        active_days = grp["ts"].dt.date.nunique()
        persistence_score = min(1.0, active_days / max(1.0, duration_days))

        cluster_records.append({
            "cluster_id": cid,
            "centroid_lat": round(centroid_lat, 5),
            "centroid_lon": round(centroid_lon, 5),
            "centroid_cell": centroid_cell,
            "detections_count": total_pts,
            "day_detections": day_pts,
            "night_detections": night_pts,
            "diurnal_ratio": round(diurnal_ratio, 3),
            "first_seen": ts_min.isoformat(),
            "last_seen": ts_max.isoformat(),
            "duration_hours": round(duration_hours, 1),
            "active_days": active_days,
            "persistence_score": round(persistence_score, 3),
            "median_frp": round(median_frp, 2),
            "mean_frp": round(mean_frp, 2),
            "max_frp": round(max_frp, 2),
            "cov_frp": round(cov_frp, 3),
            "vnf_temp_k": round(vnf_temp_k, 1) if vnf_temp_k else None,
        })

    summary_df = pd.DataFrame(cluster_records).sort_values("median_frp", ascending=False).reset_index(drop=True)

    # Save to disk
    raw_out = DATA_RAW / "clustered_detections.parquet"
    summary_out = DATA_RAW / "clusters_summary.parquet"
    
    df.to_parquet(raw_out, index=False)
    summary_df.to_parquet(summary_out, index=False)
    
    print(f"[clustering] Grouped {len(df)} raw detections into {len(summary_df)} physical clusters for region '{REGION}'.")
    return df, summary_df


if __name__ == "__main__":
    from ingestion.collectors.firms import fetch_fires
    from ingestion.collectors.vnf import fetch_vnf

    f_df = fetch_fires(days=30)
    v_df = fetch_vnf(days=30)
    pts_df, sum_df = spatio_temporal_clustering(f_df, v_df)
    print("\nTop 5 Clusters:")
    print(sum_df.head(5).to_string())
