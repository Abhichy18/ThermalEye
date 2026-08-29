"""ThermalEye — Central Configuration.

One place to change region, resolution, paths, detection windows, and API
endpoints. Adapted from AirCase with thermal-source-specific regions and
7-class classification parameters.

INVARIANT: This module is imported by every other module. It must remain
dependency-light (stdlib + os/pathlib only at module scope).
"""
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ─── Base data trees ─────────────────────────────────────────────────────
DATA_RAW_BASE = ROOT / "data" / "raw"
DATA_OUT_BASE = ROOT / "data" / "outputs"
GROUND_TRUTH_DIR = ROOT / "data" / "ground_truth"
MODELS_DIR = ROOT / "models"


def _load_dotenv(path: Path = ROOT / ".env") -> None:
    """Populate os.environ from .env. Real env vars always win (CI sets secrets).

    Hand-rolled rather than python-dotenv: six lines, one fewer dependency, and
    the documented workflow ('copy .env.example to .env') has to actually work.
    Adapted from AirCase — proven zero-bug loader.
    """
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.split("#")[0].strip().strip("'\"")
        if key and val:
            os.environ.setdefault(key, val)


_load_dotenv()


# ─── Thermal-Source Regions ──────────────────────────────────────────────
# Unlike AirCase (city-centric), ThermalEye targets INDUSTRIAL regions.
# Each region bbox is sized to capture the thermal activity zone + buffer.
REGIONS = {
    # ── Primary Demo Regions (pre-locked case studies) ──
    "barmer": {
        "name": "Barmer Basin (Rajasthan)",
        "lat_min": 25.80, "lat_max": 27.20, "lon_min": 70.80, "lon_max": 72.50,
        "description": "India's largest onshore oil basin — Mangala, Bhagyam, Aishwariya fields",
        "primary_classes": ["gas_flare", "mining"],
    },
    "punjab": {
        "name": "Punjab Harvest Belt",
        "lat_min": 29.50, "lat_max": 31.50, "lon_min": 74.00, "lon_max": 76.50,
        "description": "Stubble burning epicenter + brick kiln clusters in IGP",
        "primary_classes": ["agricultural_burn", "brick_kiln"],
    },
    "delhi": {
        "name": "Delhi-NCR",
        "lat_min": 28.40, "lat_max": 28.90, "lon_min": 76.80, "lon_max": 77.45,
        "description": "Bhalswa/Ghazipur landfill fires + industrial Faridabad belt",
        "primary_classes": ["industrial_fire", "brick_kiln"],
    },
    "hazira": {
        "name": "Hazira Gas Complex (Gujarat)",
        "lat_min": 20.90, "lat_max": 21.30, "lon_min": 72.50, "lon_max": 72.80,
        "description": "ONGC/GAIL LNG terminal — persistent gas flaring",
        "primary_classes": ["gas_flare"],
    },
    "jharia": {
        "name": "Jharia Coalfield (Jharkhand)",
        "lat_min": 23.60, "lat_max": 23.90, "lon_min": 86.10, "lon_max": 86.50,
        "description": "India's oldest coalfield — underground coal seam fires since 1916",
        "primary_classes": ["mining", "industrial_fire"],
    },
    # ── Pan-India (for national-level demo) ──
    "india": {
        "name": "Pan-India Overview",
        "lat_min": 6.50, "lat_max": 35.50, "lon_min": 68.00, "lon_max": 97.50,
        "description": "Full national coverage for overview dashboard",
        "primary_classes": ["all"],
    },
}

REGION = os.environ.get("TE_REGION", "barmer").lower()
if REGION not in REGIONS:
    raise ValueError(f"TE_REGION={REGION!r} unknown; choose from {list(REGIONS)}")
REGION_META = REGIONS[REGION]
BBOX = {k: REGION_META[k] for k in ("lat_min", "lat_max", "lon_min", "lon_max")}

# Per-region data trees
DATA_RAW = DATA_RAW_BASE / REGION
DATA_OUT = DATA_OUT_BASE / REGION


def get_region_config(region_name: str) -> dict:
    """Dynamically resolve configuration for an arbitrary region."""
    r = region_name.lower()
    if r not in REGIONS:
        raise ValueError(f"Region '{r}' unknown; choose from {list(REGIONS.keys())}")
    meta = REGIONS[r]
    bbox = {k: meta[k] for k in ("lat_min", "lat_max", "lon_min", "lon_max")}
    raw_dir = DATA_RAW_BASE / r
    out_dir = DATA_OUT_BASE / r
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "region": r,
        "meta": meta,
        "bbox": bbox,
        "data_raw": raw_dir,
        "data_out": out_dir,
    }


# ─── Historical Window ───────────────────────────────────────────────────
# Default: now. Set TE_WINDOW_END=2025-11-15 to run over stubble-burning season.
WINDOW_END = os.environ.get("TE_WINDOW_END")  # "YYYY-MM-DD" or None -> now


def window_end():
    """End of the collection window, as a UTC midnight Timestamp."""
    import pandas as pd
    if WINDOW_END:
        return pd.Timestamp(WINDOW_END, tz="UTC").normalize()
    return pd.Timestamp.now("UTC").normalize()


# ─── H3 Spatial Resolution ──────────────────────────────────────────────
H3_RES = 8            # ~460m edge → matches VIIRS 375m, finer than MODIS 1km

# ─── Multi-Window Detection ─────────────────────────────────────────────
# A real-time spike is noise; a source is something that persists across zoom-out.
# INVARIANT: Multi-window temporal separation is NON-NEGOTIABLE.
DETECT_WINDOWS_H = {
    "w24h":  24,            # Acute events (fires, explosions)
    "w7d":   24 * 7,        # Emerging patterns (new kiln, new flare)
    "w30d":  24 * 30,       # Chronic sources (established installations)
    "w90d":  24 * 90,       # Seasonal discrimination (ag burn vs kiln)
}

# Panel hours: 90-day sliding window for temporal profiling
PANEL_DAYS = 90
PANEL_HOURS = 24 * PANEL_DAYS

# Synthetic world anchor (fixed timestamp for reproducible numbers)
SYNTHETIC_ANCHOR = "2026-08-01T12:00:00"

# ─── Neighbourhood Contrast ─────────────────────────────────────────────
# Cell is compared against the ANNULUS around it, not the whole region.
CONTRAST_INNER_K = 1          # The zone itself (~0.8 km)
CONTRAST_OUTER_K = (5, 10)    # Surroundings (~4-8 km)

# ─── FIRMS / Satellite Parameters ────────────────────────────────────────
FIRE_RADIUS_KM = 1.5          # Attribution catchment for FIRMS detections
FIRE_FRAC_SCALE = 0.05        # 5% of window hours on fire = 1 evidence unit
SAT_BLUR_SIGMA_KM = 1.6       # Gaussian blur matching TROPOMI ~5.5km pixels

# ─── District / Ward Mapping ─────────────────────────────────────────────
DISTRICT_GEOJSON = ROOT / "data" / f"{REGION}_districts.geojson"
N_FALLBACK_DISTRICTS = 30     # Voronoi fallback when GeoJSON unavailable

# ─── 7-Class Thermal Taxonomy ────────────────────────────────────────────
THERMAL_CLASSES = [
    "industrial_fire",
    "gas_flare",
    "brick_kiln",
    "agricultural_burn",
    "mining",
    "wildfire",
    "sun_glint",
]

# FRP classification thresholds (Megawatts)
FRP_THRESHOLDS = {
    "low": 20,       # < 20 MW
    "medium": 100,    # 20-100 MW
    "high": 300,      # 100-300 MW
    "extreme": 300,   # > 300 MW (explosions/massive fires)
}

# VNF temperature threshold for gas flare discrimination (Kelvin)
VNF_FLARE_TEMP_K = 1200

# Temporal persistence thresholds
PERSISTENCE_THRESHOLDS = {
    "acute":    0.10,   # <10% of 30d window = acute event
    "emerging": 0.40,   # 10-40% of 30d window = newly emerging
    "chronic":  0.40,   # >40% of 30d window = established source
}

# Diurnal ratio: night_detections / total_detections
# agricultural_burn has ~0 night detections
DIURNAL_AGBURN_MAX = 0.05    # If ratio < 0.05, likely agricultural burn

# FRP coefficient of variation: std(frp) / mean(frp)
# Gas flares have very low variance (engineered, controlled)
FRP_COV_FLARE_MAX = 0.15     # CoV < 0.15 → likely gas flare

# Spatial growth rate (km²/day) for wildfire discrimination
SPATIAL_GROWTH_WILDFIRE_MIN = 0.1  # > 0.1 km²/day → spreading → wildfire

# OSM proximity thresholds (km) for contextual classification
OSM_PROXIMITY = {
    "industrial":  3.0,   # Within 3km of industrial=* tag
    "petroleum":   1.5,   # Within 1.5km of petroleum well/refinery
    "kiln":        1.5,   # Within 1.5km of brick kiln tag
    "quarry":      2.0,   # Within 2km of landuse=quarry
    "mining":      2.0,   # Within 2km of industrial=mine
    "farmland":    1.0,   # Within 1km of landuse=farmland
    "forest":      1.0,   # Within 1km of natural=wood/forest
}

# ─── GEE ─────────────────────────────────────────────────────────────────
GEE_PROJECT = os.environ.get("GEE_PROJECT", "thermaleye-sih2026")

# ─── API Endpoints (all free) ────────────────────────────────────────────
FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
VNF_BASE_URL = "https://eogdata.mines.edu/wwwdata/viirs_products/vnf/v33"
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
OPENMETEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# ─── LLM Configuration ──────────────────────────────────────────────────
LLM_PROVIDERS = {
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": os.environ.get("NVIDIA_NIM_MODEL", "meta/llama-3.1-70b-instruct"),
        "key_env": "NVIDIA_NIM_KEY",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",
        "key_env": "GEMINI_API_KEY",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-70b-versatile",
        "key_env": "GROQ_API_KEY",
    },
}

# ─── Enforcement Priority Score (EPS) Weights ────────────────────────────
EPS_WEIGHTS = {
    "thermal_severity":   0.30,   # FRP magnitude & class danger
    "persistence":        0.20,   # How long has it been active?
    "proximity_risk":     0.25,   # Near residential/sensitive areas?
    "compliance_gap":     0.15,   # Violation of known regulations?
    "citizen_reports":    0.10,   # Corroborating citizen complaints?
}


# ─── Create directory trees ──────────────────────────────────────────────
for d in (DATA_RAW, DATA_OUT, GROUND_TRUTH_DIR, MODELS_DIR):
    d.mkdir(parents=True, exist_ok=True)
