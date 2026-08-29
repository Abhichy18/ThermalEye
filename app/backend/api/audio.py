"""ThermalEye API — Multilingual Voice Advisory Audio Stream Endpoint.

Serves synthesized MP3 audio notes for district control rooms and field inspectors.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from shared.config import REGION, get_region_config

router = APIRouter(prefix="/audio", tags=["Voice Notes"])


@router.get("/{cluster_id}/{lang}")
def get_voice_advisory_audio(
    cluster_id: str,
    lang: str = "hi",
    region: str = Query(default=REGION, description="Target region")
):
    """Stream Hindi or English voice note for a thermal cluster."""
    if lang not in ("hi", "en"):
        raise HTTPException(status_code=400, detail="Language must be 'hi' (Hindi) or 'en' (English).")

    cfg = get_region_config(region)
    audio_path = cfg["data_out"] / "audio" / f"ADVISORY_{cluster_id.upper()}_{lang}.mp3"

    if not audio_path.exists():
        from app.backend.api.clusters import get_cluster_by_id
        from intelligence.agents.voice import synthesize_voice_advisory
        try:
            record = get_cluster_by_id(cluster_id, region=region)
            audio_path_str = synthesize_voice_advisory(record, lang=lang, output_dir=cfg["data_out"])
            audio_path = Path(audio_path_str)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Voice advisory audio for '{cluster_id}' not found.")

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=f"ADVISORY_{cluster_id}_{lang}.mp3"
    )
