"""ThermalEye — Jurisdictional Alert Router Agent.

Routes classified thermal anomalies to the exact regulatory authority, emergency agency,
and regional pollution control officer responsible under Indian law.

Jurisdiction Mapping:
1. `industrial_fire`  ➔ District Fire & Emergency Services + SPCB Hazmat Unit
2. `gas_flare`        ➔ Petroleum and Natural Gas Regulatory Board (PNGRB) / DGH
3. `brick_kiln`       ➔ State Pollution Control Board (Regional Officer)
4. `agricultural_burn`➔ District Agriculture Officer (DAO) + CAQM
5. `mining`           ➔ Directorate General of Mine Safety (DGMS)
6. `wildfire`         ➔ Divisional Forest Officer (DFO) / State Forest Department
7. `sun_glint`        ➔ Filtered / Discarded
"""
from typing import Dict, Any, List


AGENCY_REGISTRY = {
    "industrial_fire": {
        "agency_name": "District Disaster Management Authority (DDMA) & Fire Service",
        "jurisdiction": "Section 30, Disaster Management Act 2005",
        "action_channel": "EMERGENCY_SMS_WHATSAPP",
        "escalation_sla_hours": 2,
        "recipient_role": "Chief Fire Officer / District Magistrate Control Room",
    },
    "gas_flare": {
        "agency_name": "Petroleum and Natural Gas Regulatory Board (PNGRB)",
        "jurisdiction": "MoPNG Natural Gas Flaring Guidelines (2025)",
        "action_channel": "REGULATORY_DISPATCH_PORTAL",
        "escalation_sla_hours": 72,
        "recipient_role": "Director of Upstream Compliance / PNGRB",
    },
    "brick_kiln": {
        "agency_name": "State Pollution Control Board (SPCB)",
        "jurisdiction": "Section 31A, Air (Prevention & Control of Pollution) Act 1981",
        "action_channel": "REGIONAL_INSPECTOR_QUEUE",
        "escalation_sla_hours": 24,
        "recipient_role": "Regional Officer (SPCB)",
    },
    "agricultural_burn": {
        "agency_name": "Commission for Air Quality Management (CAQM) / District Agriculture Office",
        "jurisdiction": "CAQM Stubble Burning Directives (2025)",
        "action_channel": "DISTRICT_AGRICULTURE_FEED",
        "escalation_sla_hours": 12,
        "recipient_role": "District Agriculture Officer",
    },
    "mining": {
        "agency_name": "Directorate General of Mine Safety (DGMS)",
        "jurisdiction": "Mines Act 1952 / Coal Mines Regulations 2017",
        "action_channel": "MINE_INSPECTOR_DISPATCH",
        "escalation_sla_hours": 48,
        "recipient_role": "Inspector of Mines (Regional)",
    },
    "wildfire": {
        "agency_name": "State Forest Department (Territorial)",
        "jurisdiction": "Indian Forest Act 1927 & Wildlife Protection Act",
        "action_channel": "FOREST_RAPID_RESPONSE",
        "escalation_sla_hours": 4,
        "recipient_role": "Divisional Forest Officer (DFO)",
    },
}


def route_alert_jurisdiction(cluster_record: Dict[str, Any]) -> Dict[str, Any]:
    """Determine responsible agency, routing metadata, and dispatch payload."""
    cat = cluster_record.get("classification", "industrial_fire")
    cid = cluster_record.get("cluster_id", "CLU-0000")
    lat = cluster_record.get("centroid_lat", 0.0)
    lon = cluster_record.get("centroid_lon", 0.0)
    district = cluster_record.get("district_name", "District Headquarters")
    state = cluster_record.get("state", "State")
    priority = cluster_record.get("priority_tier", "P2")

    if cat == "sun_glint":
        return {
            "routed": False,
            "reason": "Sun-glint artifact suppressed. No authority alert dispatched."
        }

    agency_info = AGENCY_REGISTRY.get(cat, AGENCY_REGISTRY["industrial_fire"])

    google_maps_pin = f"https://www.google.com/maps?q={lat},{lon}"

    dispatch_payload = {
        "routed": True,
        "cluster_id": cid,
        "priority": priority,
        "classification": cat.upper(),
        "target_agency": f"{agency_info['agency_name']} ({district}, {state})",
        "legal_jurisdiction": agency_info["jurisdiction"],
        "recipient_role": agency_info["recipient_role"],
        "action_channel": agency_info["action_channel"],
        "escalation_sla_hours": agency_info["escalation_sla_hours"],
        "coordinates": {"lat": lat, "lon": lon},
        "gps_pin_url": google_maps_pin,
        "dispatch_message": (
            f"🚨 [THERMALEYE {priority}] {cat.upper()} detected in {district} ({state}) at ({lat:.4f}, {lon:.4f}). "
            f"Radiative Power: {cluster_record.get('median_frp', 0.0):.1f} MW. "
            f"Action required under {agency_info['jurisdiction']}. "
            f"Verify coordinates: {google_maps_pin}"
        )
    }
    return dispatch_payload
