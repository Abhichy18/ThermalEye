"""ThermalEye — District/Ward Administrative Layer.

Maps H3 cells to administrative districts for alert routing and enforcement
memo addressing. Two modes, same schema:

  * REAL     — point-in-polygon against official district GeoJSON.
  * FALLBACK — deterministic Voronoi tessellation of the H3 fabric around
               N_FALLBACK_DISTRICTS seed cells.

Adapted from AirCase wards.py — relabeled from "wards" to "districts" to
match the national-scale thermal source classification context.

INVARIANT: The district of a given cell NEVER changes between runs. Memos
and enforcement notices must be reproducible.
"""
import json
from functools import lru_cache
from typing import Optional

import numpy as np
import pandas as pd

from shared.config import DISTRICT_GEOJSON, N_FALLBACK_DISTRICTS, H3_RES
from shared.grid import region_cells, cell_center

DISTRICT_UNASSIGNED = "unassigned"


# ─── Point-in-Polygon (hand-rolled ray casting) ─────────────────────────
# Keeps shapely/geopandas out of hard requirements for this module.

def _point_in_ring(lon: float, lat: float, ring: list) -> bool:
    """Ray casting against one linear ring of [lon, lat] pairs."""
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            x_cross = xi + (lat - yi) * (xj - xi) / (yj - yi)
            if lon < x_cross:
                inside = not inside
        j = i
    return inside


def _point_in_polygon(lon: float, lat: float, polygon: list) -> bool:
    """GeoJSON Polygon coordinates: [outer_ring, hole, hole, ...]."""
    if not polygon or not _point_in_ring(lon, lat, polygon[0]):
        return False
    return not any(_point_in_ring(lon, lat, hole) for hole in polygon[1:])


def _feature_polygons(geom: dict) -> list:
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPolygon":
        return list(geom["coordinates"])
    return []


def _ring_bbox(polys: list) -> tuple[float, float, float, float]:
    pts = np.array([p for poly in polys for p in poly[0]], dtype=float)
    return pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()


def _district_name(props: dict, idx: int) -> str:
    """Extract district name from GeoJSON properties.

    Supports common Indian district boundary GeoJSON formats:
    - Datameet: dtname, DISTRICT, district
    - Survey of India: NAME_2, NAME_3
    - Custom: name, Name, district_name
    """
    for k in (
        "dtname", "DISTRICT", "district", "District",
        "NAME_2", "NAME_3",
        "name", "Name", "district_name", "DIST_NAME",
        "Ward_Name", "ward_name",
    ):
        if props.get(k):
            return str(props[k]).strip().title()
    return f"District {idx + 1:03d}"


def _state_name(props: dict) -> str:
    """Extract state name from GeoJSON properties."""
    for k in ("stname", "STATE", "state", "State", "NAME_1"):
        if props.get(k):
            return str(props[k]).strip().title()
    return "Unknown"


# ─── Mode: Real GeoJSON ─────────────────────────────────────────────────

def _districts_from_geojson(cells: list[str]) -> pd.DataFrame:
    """Map cells to districts using official boundary GeoJSON."""
    gj = json.loads(DISTRICT_GEOJSON.read_text(encoding="utf-8"))
    feats = []
    for i, f in enumerate(gj["features"]):
        polys = _feature_polygons(f.get("geometry") or {})
        if not polys:
            continue
        props = f.get("properties") or {}
        feats.append({
            "district_id": f"D{i + 1:03d}",
            "district_name": _district_name(props, i),
            "state": _state_name(props),
            "polys": polys,
            "bbox": _ring_bbox(polys),
        })

    rows = []
    for c in cells:
        lat, lon = cell_center(c)
        hit = None
        for f in feats:
            x0, y0, x1, y1 = f["bbox"]
            if not (x0 <= lon <= x1 and y0 <= lat <= y1):
                continue  # bbox prefilter: skips ~99% of tests
            if any(_point_in_polygon(lon, lat, p) for p in f["polys"]):
                hit = f
                break
        rows.append({
            "cell": c,
            "district_id": hit["district_id"] if hit else DISTRICT_UNASSIGNED,
            "district_name": hit["district_name"] if hit else "Outside boundaries",
            "state": hit["state"] if hit else "Unknown",
        })
    return pd.DataFrame(rows)


# ─── Mode: Voronoi Fallback ─────────────────────────────────────────────

# Pre-defined district seeds for known thermal regions.
# These are real district headquarters coordinates for accurate fallback.
KNOWN_DISTRICT_SEEDS = {
    "barmer": [
        ("Barmer", "Rajasthan", 25.75, 71.39),
        ("Jaisalmer", "Rajasthan", 26.92, 70.91),
        ("Jodhpur", "Rajasthan", 26.29, 73.02),
    ],
    "punjab": [
        ("Bathinda", "Punjab", 30.21, 74.94),
        ("Sangrur", "Punjab", 30.25, 75.84),
        ("Ludhiana", "Punjab", 30.90, 75.85),
        ("Patiala", "Punjab", 30.34, 76.39),
        ("Moga", "Punjab", 30.82, 75.17),
        ("Amritsar", "Punjab", 31.63, 74.87),
        ("Fatehgarh Sahib", "Punjab", 30.64, 76.39),
    ],
    "delhi": [
        ("North Delhi", "Delhi", 28.73, 77.15),
        ("South Delhi", "Delhi", 28.52, 77.22),
        ("East Delhi", "Delhi", 28.63, 77.32),
        ("West Delhi", "Delhi", 28.66, 77.05),
        ("Faridabad", "Haryana", 28.41, 77.31),
        ("Gurugram", "Haryana", 28.46, 77.03),
    ],
    "hazira": [
        ("Surat", "Gujarat", 21.17, 72.83),
        ("Bharuch", "Gujarat", 21.70, 73.00),
    ],
    "jharia": [
        ("Dhanbad", "Jharkhand", 23.79, 86.43),
        ("Bokaro", "Jharkhand", 23.67, 86.15),
    ],
}


def _districts_voronoi(cells: list[str], region: Optional[str] = None) -> pd.DataFrame:
    """Deterministic Voronoi districts. Seeded so cell→district is reproducible."""
    from shared.config import REGION

    region = region or REGION

    if region in KNOWN_DISTRICT_SEEDS:
        # Use real district headquarters as seeds
        seeds_data = KNOWN_DISTRICT_SEEDS[region]
        seed_names = [s[0] for s in seeds_data]
        seed_states = [s[1] for s in seeds_data]
        seed_pts = np.array([[s[2], s[3]] for s in seeds_data])
    else:
        # Fall back to random Voronoi
        rng = np.random.default_rng(1729)
        n = min(N_FALLBACK_DISTRICTS, len(cells))
        chosen = sorted(rng.choice(cells, size=n, replace=False).tolist())
        seed_names = [f"District {i + 1:03d}" for i in range(n)]
        seed_states = ["Unknown"] * n
        seed_pts = np.array([cell_center(s) for s in chosen])

    pts = np.array([cell_center(c) for c in cells])

    # Equirectangular nearest-seed assignment
    lat0 = np.radians(pts[:, 0].mean())
    dy = pts[:, None, 0] - seed_pts[None, :, 0]
    dx = (pts[:, None, 1] - seed_pts[None, :, 1]) * np.cos(lat0)
    nearest = np.argmin(dx ** 2 + dy ** 2, axis=1)

    return pd.DataFrame({
        "cell": cells,
        "district_id": [f"D{i + 1:03d}" for i in nearest],
        "district_name": [seed_names[i] for i in nearest],
        "state": [seed_states[i] for i in nearest],
    })


# ─── Public API ──────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def district_frame(res: int = H3_RES) -> pd.DataFrame:
    """cell → (district_id, district_name, state) for every cell in the region.

    Cached for the lifetime of the process.
    """
    cells = region_cells(res)
    if DISTRICT_GEOJSON.exists():
        df = _districts_from_geojson(cells)
        df.attrs["synthetic"] = False
        n_out = int((df.district_id == DISTRICT_UNASSIGNED).sum())
        print(f"[districts] {df.district_id.nunique()} districts from "
              f"{DISTRICT_GEOJSON.name} ({len(df) - n_out}/{len(df)} cells assigned)")
    else:
        df = _districts_voronoi(cells)
        df.attrs["synthetic"] = True
        print(f"[districts] {DISTRICT_GEOJSON.name} not found — "
              f"{df.district_id.nunique()} FALLBACK Voronoi districts "
              f"(using known HQ coordinates)")
    return df


def district_map(res: int = H3_RES) -> dict[str, str]:
    """cell → district_id."""
    df = district_frame(res)
    return dict(zip(df.cell, df.district_id))


def cell_to_district(cell: str) -> dict:
    """Get district info for a single cell."""
    df = district_frame()
    row = df[df.cell == cell]
    if row.empty:
        return {"district_id": DISTRICT_UNASSIGNED,
                "district_name": "Unknown",
                "state": "Unknown"}
    r = row.iloc[0]
    return {"district_id": r.district_id,
            "district_name": r.district_name,
            "state": r.state}


def attach_districts(df: pd.DataFrame, cell_col: str = "cell") -> pd.DataFrame:
    """Left-join district_id/district_name/state onto anything with a cell column."""
    d = district_frame().rename(columns={"cell": cell_col})
    return df.merge(d, on=cell_col, how="left")


# ─── Self-Test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = district_frame()
    print(f"\n✅ Districts loaded: {df.district_id.nunique()} unique")
    print(f"   Cells covered: {len(df)}")
    print(f"   Synthetic: {df.attrs.get('synthetic', 'unknown')}")
    print(f"\n   Distribution:")
    print(df.groupby("district_name").size().sort_values(ascending=False).head(10).to_string())
