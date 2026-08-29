"""ThermalEye API — Legal Enforcement Memo PDF Endpoint.

Serves pre-generated and dynamic ReportLab PDF show-cause notices for active clusters.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from shared.config import REGION, get_region_config

router = APIRouter(prefix="/memos", tags=["Legal Notices"])


@router.get("/{cluster_id}/pdf")
def get_memo_pdf(
    cluster_id: str,
    region: str = Query(default=REGION, description="Target region")
):
    """Download official legal show-cause notice PDF for a thermal cluster."""
    cfg = get_region_config(region)
    pdf_path = cfg["data_out"] / "memos" / f"MEMO_{cluster_id.upper()}.pdf"

    if not pdf_path.exists():
        # Check if cluster exists and generate memo on the fly
        from app.backend.api.clusters import get_cluster_by_id
        from intelligence.agents.memo import generate_enforcement_memo_pdf
        try:
            record = get_cluster_by_id(cluster_id, region=region)
            pdf_path_str = generate_enforcement_memo_pdf(record, output_dir=cfg["data_out"])
            pdf_path = Path(pdf_path_str)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Legal memo for '{cluster_id}' not found.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"STATUTORY_NOTICE_{cluster_id}.pdf"
    )
