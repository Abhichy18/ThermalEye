"""ThermalEye — H3 Spatial Fabric & Geometry Utilities.

Every thermal detection from every satellite source gets stamped onto an H3 cell.
Provides geometry utilities used by clustering, classification, and attribution
(bearings, wind alignment, distance calculations).

Adapted from AirCase grid.py with thermal-source-specific enhancements:
- Multi-resolution grid support for weather vs. thermal vs. district mapping
- Spatial growth rate calculation for wildfire discrimination
- Cluster centroid computation for district routing

INVARIANT: H3 res-8 (~460m) matches VIIRS 375m footprint. Do not change.
"""
import math
from typing import Sequence

import h3
import numpy as np

from shared.config import BBOX, H3_RES

# Coarse H3 res for weather query points: ~3.2 km edge.
# Derived from H3_RES so a bigger region gets more weather points automatically.
WEATHER_GRID_RES = H3_RES - 2

# District-level coarse grid for alert routing
DISTRICT_GRID_RES = H3_RES - 4  # ~23 km edge — district-level aggregation


# ─── Bbox & Cell Generation ─────────────────────────────────────────────

def _bbox_poly() -> "h3.LatLngPoly":
    """Create H3 polygon from region bounding box."""
    return h3.LatLngPoly([
        (BBOX["lat_min"], BBOX["lon_min"]),
        (BBOX["lat_min"], BBOX["lon_max"]),
        (BBOX["lat_max"], BBOX["lon_max"]),
        (BBOX["lat_max"], BBOX["lon_min"]),
    ])


def region_cells(res: int = H3_RES) -> list[str]:
    """All H3 cells whose center falls inside the region bbox."""
    return sorted(h3.polygon_to_cells(_bbox_poly(), res))


def weather_grid_cells(res: int = WEATHER_GRID_RES) -> list[str]:
    """Coarse H3 cells covering the region — one weather query point each.

    Derived from region_cells()'s ACTUAL parents at `res`, not a second,
    independent polygon_to_cells call. This guarantees every fine cell has
    a covering weather point, by construction (AirCase lesson: independent
    calls can orphan 11% of boundary cells).
    """
    return sorted({cell_to_weather_cell(c, res) for c in region_cells()})


# ─── Cell Conversions ────────────────────────────────────────────────────

def cell_to_weather_cell(cell: str, res: int = WEATHER_GRID_RES) -> str:
    """The weather grid cell a fine H3 cell belongs to."""
    return h3.cell_to_parent(cell, res)


def cell_center(cell: str) -> tuple[float, float]:
    """(lat, lon) of a cell center."""
    return h3.cell_to_latlng(cell)


def latlng_to_cell(lat: float, lon: float, res: int = H3_RES) -> str:
    """Convert lat/lon to H3 cell index."""
    return h3.latlng_to_cell(lat, lon, res)


def neighbors(cell: str, k: int = 1) -> list[str]:
    """Ring-k neighbors (excluding the cell itself)."""
    return [c for c in h3.grid_disk(cell, k) if c != cell]


def annulus(cell: str, k_inner: int, k_outer: int) -> list[str]:
    """Cells in the annular ring between k_inner and k_outer radii.

    Used for neighbourhood contrast: the cell is compared against this annulus,
    not the whole region. The annulus must sit OUTSIDE the satellite's ~2.5km
    blur, or the source contaminates the baseline it's being measured against.
    """
    inner = set(h3.grid_disk(cell, k_inner))
    outer = set(h3.grid_disk(cell, k_outer))
    return sorted(outer - inner)


# ─── Distance & Bearing ─────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in kilometers."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial bearing from point 1 to point 2, degrees clockwise from north."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def wind_alignment(
    src_lat: float, src_lon: float,
    dst_lat: float, dst_lon: float,
    wind_from_deg: float,
) -> float:
    """How well does the wind blow FROM the source TOWARD the destination?

    wind_from_deg: meteorological convention (direction wind comes FROM).
    Returns cos similarity in [0, 1]: 1 = destination exactly downwind of source.
    Used by attribution evidence builder and wind-weighted forecast adjacency.
    """
    wind_to = (wind_from_deg + 180.0) % 360.0
    src_to_dst = bearing_deg(src_lat, src_lon, dst_lat, dst_lon)
    cos_sim = math.cos(math.radians(wind_to - src_to_dst))
    return max(0.0, cos_sim)


def circular_mean_deg(degrees: Sequence[float]) -> float:
    """Mean of a set of bearings, on the circle.

    A plain arithmetic mean of 350° and 10° gives 180° — the exact opposite
    of the right answer. This is the only correct way to summarise wind
    direction over a temporal window.
    """
    a = np.radians(np.asarray(list(degrees), dtype=float))
    if a.size == 0:
        return float("nan")
    return float(np.degrees(np.arctan2(np.sin(a).mean(), np.cos(a).mean())) % 360.0)


def cell_distance_km(c1: str, c2: str) -> float:
    """Distance in km between two H3 cell centers."""
    a, b = cell_center(c1), cell_center(c2)
    return haversine_km(a[0], a[1], b[0], b[1])


# ─── Thermal-Specific Spatial Utilities ──────────────────────────────────

def cluster_centroid(cells: list[str]) -> tuple[float, float]:
    """Compute the geographic centroid of a set of H3 cells.

    Used for district routing: map a classified cluster to its nearest
    administrative district for alert dispatch.
    """
    if not cells:
        return (0.0, 0.0)
    pts = np.array([cell_center(c) for c in cells])
    return (float(pts[:, 0].mean()), float(pts[:, 1].mean()))


def spatial_footprint_km2(cells: list[str]) -> float:
    """Approximate spatial footprint of a set of H3 cells in km².

    H3 res-8 cell area is approximately 0.737 km². This is a fast estimate
    used for wildfire spatial growth rate calculation.
    """
    H3_RES8_AREA_KM2 = 0.737
    return len(set(cells)) * H3_RES8_AREA_KM2


def spatial_growth_rate(
    cells_t1: list[str], cells_t2: list[str], hours_elapsed: float,
) -> float:
    """Spatial expansion rate in km²/day between two timesteps.

    Positive growth rate is a key discriminator for wildfire vs. other classes.
    Wildfires spread; flares, kilns, and industrial fires do not.
    """
    if hours_elapsed <= 0:
        return 0.0
    area_t1 = spatial_footprint_km2(cells_t1)
    area_t2 = spatial_footprint_km2(cells_t2)
    days = hours_elapsed / 24.0
    return max(0.0, (area_t2 - area_t1) / days)


def bounding_box_cells(
    lat_min: float, lat_max: float,
    lon_min: float, lon_max: float,
    res: int = H3_RES,
) -> list[str]:
    """All H3 cells within an arbitrary bounding box (for OSM/VNF sub-queries)."""
    poly = h3.LatLngPoly([
        (lat_min, lon_min), (lat_min, lon_max),
        (lat_max, lon_max), (lat_max, lon_min),
    ])
    return sorted(h3.polygon_to_cells(poly, res))


# ─── Self-Test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    cells = region_cells()
    print(f"✅ {len(cells)} H3 res-{H3_RES} cells cover the {BBOX} bbox")

    c = cells[len(cells) // 2]
    lat, lon = cell_center(c)
    print(f"   Sample cell: {c}")
    print(f"   Center: ({lat:.4f}, {lon:.4f})")
    print(f"   Neighbors (k=1): {len(neighbors(c))}")
    print(f"   Annulus (1-5): {len(annulus(c, 1, 5))} cells")

    wcells = weather_grid_cells()
    print(f"✅ {len(wcells)} weather grid cells (res={WEATHER_GRID_RES})")

    # Quick distance test: Mangala oil field to Barmer town (~50 km)
    d = haversine_km(26.56, 73.83, 25.75, 71.39)
    print(f"✅ Distance Mangala→Barmer: {d:.1f} km")

    print(f"✅ Cluster centroid of {len(cells)} cells: {cluster_centroid(cells)}")
    print(f"✅ Footprint of {len(cells)} cells: {spatial_footprint_km2(cells):.1f} km²")
