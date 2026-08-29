"""ThermalEye — Master Intelligence Orchestrator (LangGraph Multi-Agent Graph).

Coordinates all 4 intelligence & action stages:
1. `load_panel_node`      ➔ Loads Phase 1 multi-window feature panel
2. `classify_node`        ➔ Executes hybrid 7-class classifier & physical rules
3. `evidence_node`        ➔ Generates 4-pillar evidence & rejected alternative hypotheses
4. `action_node`          ➔ Computes EPS (0-100), routes alerts, generates legal PDF memos,
                             synthesizes Hindi/English voice notes, and logs to the intervention ledger.

Usage:
    python -m intelligence.orchestrator --region barmer
    python -m intelligence.orchestrator --region punjab
"""
import os
import json
import argparse
from typing import Dict, Any, List, TypedDict, Optional
from pathlib import Path

import pandas as pd
import numpy as np
from langgraph.graph import StateGraph, END

from shared.config import REGION, DATA_RAW, DATA_OUT, get_region_config
from intelligence.agents.classify import classify_panel_dataframe
from intelligence.agents.evidence import build_evidence_profile
from intelligence.agents.llm_gateway import synthesize_briefing_llm
from intelligence.agents.prioritise import calculate_eps_score
from intelligence.agents.alert_router import route_alert_jurisdiction
from intelligence.agents.memo import generate_enforcement_memo_pdf
from intelligence.agents.voice import synthesize_voice_advisory
from intelligence.agents.ledger import record_intervention_event


class PipelineState(TypedDict):
    region: str
    panel_df: Optional[pd.DataFrame]
    classified_df: Optional[pd.DataFrame]
    evidence_profiles: List[Dict[str, Any]]
    final_output: List[Dict[str, Any]]
    status: str


def load_panel_node(state: PipelineState) -> Dict[str, Any]:
    """Node 1: Load enriched feature panel from Phase 1 ingestion."""
    reg = state.get("region", os.environ.get("TE_REGION", "barmer")).lower()
    cfg = get_region_config(reg)
    raw_panel_path = cfg["data_raw"] / "enriched_clusters_panel.parquet"

    if not raw_panel_path.exists():
        print(f"[orchestrator] Panel not found at {raw_panel_path} -> Running ingestion first...")
        from scripts.run_ingest import run_ingestion_pipeline
        panel_df = run_ingestion_pipeline(region_name=reg, days=30)
    else:
        panel_df = pd.read_parquet(raw_panel_path)

    print(f"[orchestrator] Stage 1: Loaded panel with {len(panel_df)} thermal clusters for '{reg}'.")
    return {"panel_df": panel_df, "status": "PANEL_LOADED"}


def classification_node(state: PipelineState) -> Dict[str, Any]:
    """Node 2: Run hybrid 7-class classifier on all clusters."""
    panel_df = state["panel_df"]
    classified_df = classify_panel_dataframe(panel_df)
    print(f"[orchestrator] Stage 2: Classified {len(classified_df)} clusters across 7-class taxonomy.")
    return {"classified_df": classified_df, "status": "CLASSIFIED"}


def evidence_node(state: PipelineState) -> Dict[str, Any]:
    """Node 3: Build mathematical evidence profiles and rejected hypotheses."""
    classified_df = state["classified_df"]
    profiles = []

    for _, row in classified_df.iterrows():
        prof = build_evidence_profile(row.to_dict())
        briefing = synthesize_briefing_llm(
            cluster_id=prof["cluster_id"],
            category=prof["classification"],
            confidence=prof["confidence"],
            evidence_chain=prof["evidence_chain"],
            regulatory_recommendation=prof["regulatory_recommendation"],
            district_name=str(row.get("district_name", "District"))
        )
        prof["briefing"] = briefing
        
        full_record = {
            **row.to_dict(),
            **prof
        }
        profiles.append(full_record)

    print(f"[orchestrator] Stage 3: Generated {len(profiles)} full evidence profiles.")
    return {"evidence_profiles": profiles, "status": "EVIDENCE_BUILT"}


def action_node(state: PipelineState) -> Dict[str, Any]:
    """Node 4: Action Layer — EPS scoring, alert routing, PDF legal notice, voice note, ledger."""
    profiles = state["evidence_profiles"]
    reg = state.get("region", os.environ.get("TE_REGION", "barmer")).lower()
    cfg = get_region_config(reg)

    actioned_records = []

    for item in profiles:
        cat = item.get("classification", "unknown")

        # 1. Enforcement Priority Score (EPS: 0–100)
        eps_info = calculate_eps_score(item)
        item.update(eps_info)

        # 2. Jurisdictional Routing Payload
        routing = route_alert_jurisdiction(item)
        item["jurisdiction_dispatch"] = routing

        # 3. Action Artifacts Generation (for non-glint events)
        if cat != "sun_glint":
            # Generate official PDF Notice
            pdf_path = generate_enforcement_memo_pdf(item, output_dir=cfg["data_out"])
            item["memo_pdf_url"] = f"/outputs/{reg}/memos/{Path(pdf_path).name}"

            # Synthesize Hindi and English Voice Advisories
            audio_hi = synthesize_voice_advisory(item, lang="hi", output_dir=cfg["data_out"])
            audio_en = synthesize_voice_advisory(item, lang="en", output_dir=cfg["data_out"])
            item["voice_note_hi_url"] = f"/outputs/{reg}/audio/{Path(audio_hi).name}" if audio_hi else None
            item["voice_note_en_url"] = f"/outputs/{reg}/audio/{Path(audio_en).name}" if audio_en else None

            # Log to Regulatory Intervention Ledger
            ledger_entry = record_intervention_event(
                item,
                action_status="DISPATCHED",
                inspector_id=f"OFFICER-{item.get('district_name', 'REG').upper()}-01",
                notes=f"Auto-routed to {routing.get('target_agency')} under {routing.get('legal_jurisdiction')}."
            )
            item["ledger_entry"] = ledger_entry
        else:
            item["memo_pdf_url"] = None
            item["voice_note_hi_url"] = None
            item["voice_note_en_url"] = None
            item["ledger_entry"] = None

        actioned_records.append(item)

    # Sort descending by EPS score (Critical P1s at top)
    actioned_records.sort(key=lambda x: x.get("eps_score", 0.0), reverse=True)
    print(f"[orchestrator] Stage 4: Actioned {len(actioned_records)} clusters (Memos, Audio, Ledger, EPS).")
    return {"final_output": actioned_records, "status": "COMPLETE"}


def build_intelligence_graph() -> StateGraph:
    """Construct the complete multi-agent LangGraph workflow."""
    workflow = StateGraph(PipelineState)

    workflow.add_node("load_panel", load_panel_node)
    workflow.add_node("classify", classification_node)
    workflow.add_node("evidence", evidence_node)
    workflow.add_node("action", action_node)

    workflow.set_entry_point("load_panel")
    workflow.add_edge("load_panel", "classify")
    workflow.add_edge("classify", "evidence")
    workflow.add_edge("evidence", "action")
    workflow.add_edge("action", END)

    return workflow.compile()


def run_orchestrator(region_name: str = "barmer") -> List[Dict[str, Any]]:
    """Execute complete intelligence & action graph and export artifacts."""
    os.environ["TE_REGION"] = region_name.lower()
    from shared.config import get_region_config
    cfg = get_region_config(region_name)

    print("=" * 70)
    print(f"🧠  THERMALEYE INTELLIGENCE & ACTION GRAPH | REGION: {region_name.upper()}")
    print("=" * 70)

    app = build_intelligence_graph()
    init_state: PipelineState = {
        "region": region_name,
        "panel_df": None,
        "classified_df": None,
        "evidence_profiles": [],
        "final_output": [],
        "status": "INIT"
    }

    final_state = app.invoke(init_state)
    output_list = final_state.get("final_output", [])

    # Save to data/outputs/<region>/classifications.json
    out_dir = cfg["data_out"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "classifications.json"
    
    def default_serializer(obj):
        if isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        return str(obj)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output_list, f, indent=2, default=default_serializer)

    print("\n" + "=" * 70)
    print(f"✅ PHASE 2 & 3 COMPLETE & EXPORTED")
    print(f"   • Processed Thermal Clusters: {len(output_list)}")
    print(f"   • Priority Breakdown: {pd.DataFrame(output_list)['priority_tier'].value_counts().to_dict() if output_list else {}}")
    print(f"   • Output JSON: {out_json}")
    print(f"   • Legal Memos: {out_dir / 'memos'}")
    print(f"   • Voice Advisories: {out_dir / 'audio'}")
    print(f"   • Intervention Ledger: {out_dir / 'intervention_ledger.json'}")
    print("=" * 70)
    return output_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ThermalEye Orchestrator")
    parser.add_argument("--region", type=str, default=REGION, help="Target region")
    args = parser.parse_args()

    results = run_orchestrator(region_name=args.region)
    for r in results:
        print(f"\n[{r['cluster_id']}] {r['priority_tier']} ({r['eps_score']}/100) -> {r['classification'].upper()}")
        print(f"   Agency: {r.get('jurisdiction_dispatch', {}).get('target_agency')}")
        print(f"   Memo PDF: {r.get('memo_pdf_url')}")
        print(f"   Voice Note: {r.get('voice_note_hi_url')}")
