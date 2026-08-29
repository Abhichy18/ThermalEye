"""ThermalEye — Enforcement Priority Scoring (EPS) Agent.

Quantifies regulatory urgency into a deterministic, auditable score from 0.0 to 100.0:
- Rank-orders all active thermal clusters into a clear tactical dispatch queue.
- Replaces subjective human guesses with multi-factor risk weighting:
  1. Thermal Severity (FRP magnitude & hazard category)
  2. Temporal Urgency (Acute explosion vs Chronic flare)
  3. Spatial Proximity Risk (Distance to hospitals, schools, and residential settlements)
  4. Environmental Compliance Gap (CPCB Zig-Zag / MoPNG Flaring Caps)
  5. Citizen Report Corroboration

Output:
- EPS Score: 0.0 – 100.0
- Priority Tier: P1 (CRITICAL), P2 (HIGH), P3 (MODERATE), P4 (ROUTINE)
- Action Mandate & SLA (e.g. "Immediate Dispatch < 2h")
"""
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from shared.config import EPS_WEIGHTS


CATEGORY_SEVERITY_WEIGHT = {
    "industrial_fire": 1.00,
    "wildfire": 0.85,
    "gas_flare": 0.65,
    "brick_kiln": 0.55,
    "mining": 0.50,
    "agricultural_burn": 0.30,
    "sun_glint": 0.00,
}


def calculate_eps_score(cluster_record: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate the Enforcement Priority Score (0-100) and priority tier."""
    category = cluster_record.get("classification", "unknown")
    median_frp = float(cluster_record.get("median_frp", 10.0))
    urgency = str(cluster_record.get("temporal_urgency", "chronic"))
    dist_vulnerable_km = float(cluster_record.get("dist_vulnerable_km", 99.0))
    citizen_count = int(cluster_record.get("citizen_reports_count", 0))

    # ── 1. Severity Score (0.0 – 1.0) ──
    base_sev = CATEGORY_SEVERITY_WEIGHT.get(category, 0.40)
    frp_scale = min(1.0, median_frp / 200.0)
    severity_score = (0.7 * base_sev) + (0.3 * frp_scale)

    # ── 2. Temporal Urgency Score (0.0 – 1.0) ──
    if category == "industrial_fire" or urgency == "acute":
        urgency_score = 1.00   # Immediate loss of containment
    elif urgency == "emerging":
        urgency_score = 0.75   # Newly activated unauthorized source
    elif category == "gas_flare":
        urgency_score = 0.50   # Steady continuous combustion
    elif category == "sun_glint":
        urgency_score = 0.00
    else:
        urgency_score = 0.40

    # ── 3. Proximity Risk to Sensitive Receptors (0.0 – 1.0) ──
    if dist_vulnerable_km <= 0.8:
        proximity_score = 1.00
    elif dist_vulnerable_km <= 2.0:
        proximity_score = 0.70
    elif dist_vulnerable_km <= 5.0:
        proximity_score = 0.40
    else:
        proximity_score = 0.15

    # ── 4. Compliance Violation Gap (0.0 – 1.0) ──
    if category == "industrial_fire":
        compliance_score = 1.00
    elif category == "brick_kiln" and dist_vulnerable_km < 1.0:
        compliance_score = 0.90   # Violates CPCB minimum 800m distance from habitat
    elif category == "gas_flare" and median_frp > 50.0:
        compliance_score = 0.75   # Exceeds routine flaring volume threshold
    elif category == "sun_glint":
        compliance_score = 0.00
    else:
        compliance_score = 0.30

    # ── 5. Citizen Corroboration Term (0.0 – 1.0) ──
    citizen_score = min(1.0, citizen_count * 0.25)

    # ── Weighted Formula ──
    w = EPS_WEIGHTS
    eps_raw = (
        w["thermal_severity"] * severity_score +
        w["persistence"] * urgency_score +
        w["proximity_risk"] * proximity_score +
        w["compliance_gap"] * compliance_score +
        w["citizen_reports"] * citizen_score
    ) * 100.0

    if category == "sun_glint":
        eps_final = 0.0
    else:
        eps_final = max(5.0, min(99.5, eps_raw))

    # ── Assign Priority Tier & SLA ──
    if eps_final >= 85.0:
        tier = "P1"
        tier_label = "CRITICAL"
        sla = "Emergency Dispatch < 2 Hours"
        action_directive = "Issue Section 31A Emergency Stop & Dispatch Hazardous Fire Squad"
    elif eps_final >= 65.0:
        tier = "P2"
        tier_label = "HIGH"
        sla = "Site Audit < 24 Hours"
        action_directive = "Dispatch District Environmental Inspector for Verification"
    elif eps_final >= 40.0:
        tier = "P3"
        tier_label = "MODERATE"
        sla = "Review < 7 Days"
        action_directive = "Log for Routine State Pollution Control Board Compliance Audit"
    else:
        tier = "P4"
        tier_label = "ROUTINE"
        sla = "Automated Monitoring"
        action_directive = "Continuous Satellite Tracking & Baseline Record"

    return {
        "eps_score": round(eps_final, 1),
        "priority_tier": tier,
        "priority_label": tier_label,
        "sla_target": sla,
        "action_directive": action_directive,
        "eps_breakdown": {
            "thermal_severity": round(severity_score, 2),
            "temporal_urgency": round(urgency_score, 2),
            "proximity_risk": round(proximity_score, 2),
            "compliance_gap": round(compliance_score, 2),
            "citizen_corroboration": round(citizen_score, 2),
        }
    }


def attach_eps_scores(classified_df: pd.DataFrame) -> pd.DataFrame:
    """Compute and attach EPS priority metrics to all classified clusters."""
    if classified_df.empty:
        return pd.DataFrame()

    results = []
    for _, r in classified_df.iterrows():
        eps_res = calculate_eps_score(r.to_dict())
        results.append({
            **r.to_dict(),
            "eps_score": eps_res["eps_score"],
            "priority_tier": eps_res["priority_tier"],
            "priority_label": eps_res["priority_label"],
            "sla_target": eps_res["sla_target"],
            "action_directive": eps_res["action_directive"],
            "eps_breakdown": eps_res["eps_breakdown"],
        })

    df = pd.DataFrame(results)
    # Sort by EPS descending (highest risk first)
    return df.sort_values("eps_score", ascending=False).reset_index(drop=True)
