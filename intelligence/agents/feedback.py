"""ThermalEye — Field Inspector Feedback & Ground-Truth Calibration Loop.

Enables human-in-the-loop regulatory feedback:
1. Field officers verify physical ground reality via mobile app / dashboard.
2. Officers confirm or correct the satellite classification:
   - Example: "Cluster CLU-8941 predicted as Gas Flare was verified on-site as Cairn MPT Flare Stack #2 (Accurate)."
   - Example: "Predicted as Brick Kiln was actually a seasonal Biomass Briquette drying yard (Correction)."
3. Stores verified records in `data/outputs/<region>/inspector_feedback.json`
   for active-learning retraining and model drift mitigation.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from shared.config import DATA_OUT, get_region_config


def submit_inspector_feedback(
    cluster_id: str,
    confirmed_category: str,
    original_category: str,
    inspector_name: str = "Inspector Verma",
    badge_number: str = "SPCB-RAJ-409",
    field_notes: str = "On-site GPS verification conducted.",
    photo_url: Optional[str] = None,
    region: str = "barmer"
) -> Dict[str, Any]:
    """Record an official ground-truth verification from a field officer."""
    cfg = get_region_config(region)
    feedback_file = cfg["data_out"] / "inspector_feedback.json"

    feedbacks = []
    if feedback_file.exists():
        try:
            with open(feedback_file, "r", encoding="utf-8") as f:
                feedbacks = json.load(f)
        except Exception:
            feedbacks = []

    is_agreement = (confirmed_category.lower() == original_category.lower())

    record = {
        "feedback_id": f"FDBK-{cluster_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "cluster_id": cluster_id,
        "region": region,
        "model_predicted_category": original_category,
        "inspector_confirmed_category": confirmed_category,
        "is_model_correct": is_agreement,
        "inspector_metadata": {
            "name": inspector_name,
            "badge_number": badge_number,
            "field_notes": field_notes,
            "verification_photo_url": photo_url or "https://thermaleye.sih/evidence/photo_placeholder.jpg"
        }
    }

    feedbacks.append(record)

    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2)

    print(f"[feedback] Logged inspector feedback for {cluster_id}: Model={original_category} vs Ground={confirmed_category} (Match: {is_agreement})")
    return record


def get_feedback_metrics(region: str = "barmer") -> Dict[str, Any]:
    """Compute ground-truth accuracy and calibration metrics from all logged feedback."""
    cfg = get_region_config(region)
    feedback_file = cfg["data_out"] / "inspector_feedback.json"

    if not feedback_file.exists():
        return {
            "total_verifications": 0,
            "accuracy_pct": 100.0,
            "corrections_logged": 0
        }

    with open(feedback_file, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)

    if not feedbacks:
        return {"total_verifications": 0, "accuracy_pct": 100.0, "corrections_logged": 0}

    total = len(feedbacks)
    correct = sum(1 for f in feedbacks if f.get("is_model_correct", False))

    return {
        "total_verifications": total,
        "accuracy_pct": round((correct / total) * 100.0, 1),
        "correct_count": correct,
        "corrections_logged": total - correct
    }
