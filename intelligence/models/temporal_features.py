"""ThermalEye — Temporal Signature & Feature Vector Extractor.

Extracts the mathematical feature vector per thermal cluster used by both
the rule-based decision engine and the LightGBM classifier.

Features Extracted:
1. `diurnal_ratio`: (Night detections / Total detections). 0 = daytime only (agri burn).
2. `frp_cov`: (std / mean) of FRP. Low (<0.15) = engineered steady flaring.
3. `spike_ratio`: (max_frp / median_frp). High (>3.0) = sudden acute explosion.
4. `persistence_fraction`: Active days / Window days.
5. `vnf_temp_k`: Planck blackbody combustion temperature in Kelvin.
6. `spatial_spread_rate`: km²/day spatial expansion rate.
7. `osm_proximity_vector`: Distances in km to 6 land-use/infrastructure types.
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd


def extract_cluster_features(cluster_row: Dict[str, Any]) -> Dict[str, float]:
    """Convert an enriched cluster row into a numerical feature dictionary."""
    total_pts = float(cluster_row.get("detections_count", 1))
    night_pts = float(cluster_row.get("night_detections", 0))
    diurnal_ratio = night_pts / total_pts if total_pts > 0 else 0.0

    median_frp = float(cluster_row.get("median_frp", 10.0))
    mean_frp = float(cluster_row.get("mean_frp", 10.0))
    max_frp = float(cluster_row.get("max_frp", 10.0))
    cov_frp = float(cluster_row.get("cov_frp", 0.2))

    spike_ratio = (max_frp / max(1.0, median_frp))

    duration_h = float(cluster_row.get("duration_hours", 1.0))
    persistence = float(cluster_row.get("persistence_score", 0.1))

    vnf_temp = cluster_row.get("vnf_temp_k")
    vnf_temp_k = float(vnf_temp) if vnf_temp is not None and not np.isnan(vnf_temp) else 0.0

    return {
        "median_frp": median_frp,
        "max_frp": max_frp,
        "cov_frp": cov_frp,
        "spike_ratio": round(spike_ratio, 2),
        "duration_hours": duration_h,
        "persistence_score": persistence,
        "diurnal_ratio": round(diurnal_ratio, 3),
        "vnf_temp_k": vnf_temp_k,
        "dist_industrial_km": float(cluster_row.get("dist_industrial_km", 99.0)),
        "dist_petroleum_km": float(cluster_row.get("dist_petroleum_km", 99.0)),
        "dist_kiln_km": float(cluster_row.get("dist_kiln_km", 99.0)),
        "dist_mining_km": float(cluster_row.get("dist_mining_km", 99.0)),
        "dist_farmland_km": float(cluster_row.get("dist_farmland_km", 99.0)),
        "dist_forest_km": float(cluster_row.get("dist_forest_km", 99.0)),
        "dist_vulnerable_km": float(cluster_row.get("dist_vulnerable_km", 99.0)),
    }


def feature_dict_to_vector(feat: Dict[str, float]) -> List[float]:
    """Ordered vector for LightGBM inference."""
    keys = [
        "median_frp", "max_frp", "cov_frp", "spike_ratio",
        "duration_hours", "persistence_score", "diurnal_ratio", "vnf_temp_k",
        "dist_industrial_km", "dist_petroleum_km", "dist_kiln_km",
        "dist_mining_km", "dist_farmland_km", "dist_forest_km"
    ]
    return [feat[k] for k in keys]
