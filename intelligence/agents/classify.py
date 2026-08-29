"""ThermalEye — Hybrid 7-Class Thermal Classifier Agent.

Executes:
1. Sun-Glint & Noise Pre-filter (discards optical false alarms)
2. Deterministic Physical & Spatial Rules (Transparent, Auditable)
3. LightGBM Machine Learning Ensemble (Statistical Tie-Breaker)
4. Calibrated Confidence Scoring

Invariant #1: "Deterministic Arithmetic Ranks, LLM Only Explains."
"""
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

from shared.config import (
    THERMAL_CLASSES, VNF_FLARE_TEMP_K, FRP_COV_FLARE_MAX,
    OSM_PROXIMITY
)
from intelligence.models.temporal_features import extract_cluster_features
from intelligence.models.classifier import predict_thermal_class


def is_sun_glint_artifact(features: Dict[str, float]) -> bool:
    """Pre-filter false positives from solar reflection on metal industrial roofs.

    Rule: If FRP is very low (<10 MW), zero night detections, and duration is very short -> Artifact.
    """
    if (
        features["median_frp"] < 10.0 and
        features["diurnal_ratio"] == 0.0 and
        features["duration_hours"] <= 24.0 and
        features["vnf_temp_k"] == 0.0
    ):
        return True
    return False


def classify_cluster_hybrid(cluster_row: Dict[str, Any]) -> Dict[str, Any]:
    """Classify a single thermal cluster into the 7-class taxonomy with full decision rationale."""
    features = extract_cluster_features(cluster_row)

    # ── Step 1: Sun Glint Pre-filter ──
    if is_sun_glint_artifact(features):
        return {
            "cluster_id": cluster_row.get("cluster_id"),
            "classification": "sun_glint",
            "confidence": 0.95,
            "decision_path": "Deterministic Pre-Filter (Specular Reflection / Low FRP / Zero Nocturnal Signature)",
            "features": features,
            "probabilities": {"sun_glint": 0.95}
        }

    # ── Step 2: High-Certainty Deterministic Physical Rules ──
    rule_match: Optional[Tuple[str, float, str]] = None

    # (A) Gas Flare: Ultra-high VNF combustion temperature (>1200K) OR 24/7 steady burning near petroleum
    if features["vnf_temp_k"] >= VNF_FLARE_TEMP_K:
        rule_match = (
            "gas_flare",
            0.96,
            f"VNF Planck combustion temperature {features['vnf_temp_k']:.0f}K matches atmospheric gas flare (>1200K standard)."
        )
    elif (
        features["persistence_score"] >= 0.60 and
        features["cov_frp"] <= FRP_COV_FLARE_MAX and
        features["dist_petroleum_km"] <= OSM_PROXIMITY["petroleum"]
    ):
        rule_match = (
            "gas_flare",
            0.93,
            f"Persistent 24/7 signature (Persistence: {features['persistence_score']:.2f}, CoV: {features['cov_frp']:.2f}) within {features['dist_petroleum_km']:.1f}km of petroleum infrastructure."
        )

    # (B) Industrial Fire: Sudden intense spike, short duration, near industrial zone
    elif (
        features["duration_hours"] <= 48.0 and
        (features["median_frp"] >= 120.0 or features["spike_ratio"] >= 2.5) and
        features["dist_industrial_km"] <= OSM_PROXIMITY["industrial"]
    ):
        rule_match = (
            "industrial_fire",
            0.92,
            f"Acute thermal spike ({features['median_frp']:.1f} MW, Duration: {features['duration_hours']:.1f}h) within {features['dist_industrial_km']:.1f}km of industrial polygon."
        )

    # (C) Brick Kiln: Firing profile, moderate FRP, adjacent to mapped kiln
    elif (
        features["dist_kiln_km"] <= OSM_PROXIMITY["kiln"] and
        features["diurnal_ratio"] <= 0.35 and
        features["median_frp"] <= 50.0
    ):
        rule_match = (
            "brick_kiln",
            0.91,
            f"Diurnal firing cycle located {features['dist_kiln_km']:.2f}km from registered brick kiln."
        )

    # (D) Agricultural Burn: Strictly daytime only, farmland, brief multi-day pulse
    elif (
        features["diurnal_ratio"] == 0.0 and
        features["dist_farmland_km"] <= OSM_PROXIMITY["farmland"] and
        features["duration_hours"] <= 96.0
    ):
        rule_match = (
            "agricultural_burn",
            0.94,
            f"Zero night detections (Diurnal ratio: 0.0) situated on farmland ({features['dist_farmland_km']:.2f}km) with brief duration ({features['duration_hours']:.1f}h)."
        )

    # (E) Mining: Persistent quarry/mining lease proximity
    elif (
        features["dist_mining_km"] <= OSM_PROXIMITY["quarry"] and
        features["duration_hours"] >= 96.0
    ):
        rule_match = (
            "mining",
            0.89,
            f"Persistent thermal presence within {features['dist_mining_km']:.2f}km of active quarry/mine boundary."
        )

    # (F) Wildfire: Forest proximity, spreading multi-day footprint
    elif (
        features["dist_forest_km"] <= OSM_PROXIMITY["forest"] and
        features["duration_hours"] >= 24.0
    ):
        rule_match = (
            "wildfire",
            0.88,
            f"Thermal cluster located inside/adjacent to natural forest area ({features['dist_forest_km']:.2f}km)."
        )

    # ── Step 3: Ensemble ML Prediction ──
    ml_class, ml_conf, ml_probs = predict_thermal_class(features)

    if rule_match:
        rule_class, rule_conf, rule_reason = rule_match
        # If Rule and ML agree, boost confidence
        final_conf = min(0.99, rule_conf + 0.03) if rule_class == ml_class else rule_conf
        final_class = rule_class
        decision_path = f"Deterministic Rule Match: {rule_reason}"
    else:
        # Fallback to calibrated LightGBM model
        final_class = ml_class
        final_conf = ml_conf
        decision_path = f"LightGBM Multi-Class Model Consensus (Statistical Classification)"

    return {
        "cluster_id": cluster_row.get("cluster_id"),
        "classification": final_class,
        "confidence": round(final_conf, 3),
        "decision_path": decision_path,
        "features": features,
        "probabilities": ml_probs
    }


def classify_panel_dataframe(panel_df: pd.DataFrame) -> pd.DataFrame:
    """Run hybrid classifier across all clusters in a panel DataFrame."""
    if panel_df.empty:
        return pd.DataFrame()

    results = []
    for _, row in panel_df.iterrows():
        res = classify_cluster_hybrid(row.to_dict())
        results.append({
            **row.to_dict(),
            "classification": res["classification"],
            "confidence": res["confidence"],
            "decision_path": res["decision_path"],
            "probabilities": res["probabilities"],
        })

    return pd.DataFrame(results)
