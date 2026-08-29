"""ThermalEye — Backend API Verification Test Suite.

Tests all FastAPI endpoints using TestClient to verify 100% route health.
"""
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)


def test_all_routes():
    print("=" * 70)
    print("TESTING THERMALEYE PRODUCTION FASTAPI BACKEND ROUTES")
    print("=" * 70)

    # 1. Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f"1. /health -> 200 OK | Response: {res.json()['status']}")

    # 2. Clusters List
    res = client.get("/api/clusters?region=barmer")
    assert res.status_code == 200, f"Clusters query failed: {res.text}"
    clusters = res.json()
    print(f"2. /api/clusters?region=barmer -> 200 OK | {len(clusters)} clusters retrieved.")

    # 3. Clusters Summary Stats
    res = client.get("/api/clusters/stats/summary?region=barmer")
    assert res.status_code == 200, f"Summary stats failed: {res.text}"
    summary = res.json()
    print(f"3. /api/clusters/stats/summary -> 200 OK | Total MW: {summary['total_radiative_power_mw']} MW")

    # 4. Single Cluster Dossier
    if clusters:
        sample_id = clusters[0]["cluster_id"]
        res = client.get(f"/api/clusters/{sample_id}?region=barmer")
        assert res.status_code == 200, f"Cluster detail failed: {res.text}"
        detail = res.json()
        print(f"4. /api/clusters/{sample_id} -> 200 OK | Category: {detail['classification'].upper()} ({detail['confidence']:.1%})")

        # 5. Sentinel Spyglass
        res = client.get(f"/api/sentinel/tiles/{sample_id}?region=barmer")
        assert res.status_code == 200, f"Sentinel tiles failed: {res.text}"
        print(f"5. /api/sentinel/tiles/{sample_id} -> 200 OK | Spyglass metadata resolved.")

    # 6. Citizen Hazard Feed
    res = client.get("/api/citizen/feed?region=barmer")
    assert res.status_code == 200, f"Citizen feed failed: {res.text}"
    print(f"6. /api/citizen/feed -> 200 OK | {len(res.json()['hazard_feed'])} active alerts in citizen feed.")

    # 7. Intervention Ledger
    res = client.get("/api/ledger?region=barmer")
    assert res.status_code == 200, f"Ledger failed: {res.text}"
    print(f"7. /api/ledger -> 200 OK | {len(res.json())} ledger intervention entries.")

    # 8. Feedback Metrics
    res = client.get("/api/feedback/metrics?region=barmer")
    assert res.status_code == 200, f"Feedback metrics failed: {res.text}"
    print(f"8. /api/feedback/metrics -> 200 OK | Accuracy: {res.json()['accuracy_pct']}%")

    print("\n" + "=" * 70)
    print("ALL FASTAPI BACKEND ROUTES TESTED AND VERIFIED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    test_all_routes()
