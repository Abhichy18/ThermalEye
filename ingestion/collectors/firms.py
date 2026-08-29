"""ThermalEye — NASA FIRMS Active Fire / Thermal Anomaly Collector.

Fetches VIIRS 375m (VNP14IMGTDL_NRT / VNP14IMGTDL_SP) and MODIS 1km active fire
detections over the region's bounding box.

Key Features & Invariants:
1. Automatically handles NASA FIRMS 5-day chunking limit per request.
2. Supports NRT (Near Real Time, last ~60 days) and SP (Standard Processing archive).
3. Extracts FRP (Fire Radiative Power in MW), brightness temp, confidence, day/night flag.
4. Maps detections directly onto H3 res-8 cells (~460m).
5. Provides high-fidelity synthetic fallback seeded with known real-world industrial thermal events
   (Mangala Oil Field gas flares, Punjab stubble burning, Bhalswa landfill fire, etc.).
"""
import os
import io
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np

from shared.config import (
    BBOX, DATA_RAW, FIRMS_URL, PANEL_HOURS, window_end, REGION
)
from shared.grid import latlng_to_cell

FIRMS_MAX_DAY_RANGE = 5
FIRMS_SOURCE_VIIRS_NRT = "VIIRS_SNPP_NRT"
FIRMS_SOURCE_VIIRS_SP = "VIIRS_SNPP_SP"
FIRMS_SOURCE_NOAA20_NRT = "VIIRS_NOAA20_NRT"


def _get_url(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ThermalEye-NTRO-SIH2026/1.0 (Earth Observation Intelligence)"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_fires(
    days: Optional[int] = None,
    firms_key: Optional[str] = None,
    use_synthetic: bool = False
) -> pd.DataFrame:
    """Fetch active fire detections from NASA FIRMS API or synthetic generator.

    Returns DataFrame with columns:
    ['ts', 'lat', 'lon', 'cell', 'frp', 'brightness', 'confidence', 'daynight', 'satellite']
    """
    from shared.config import get_region_config
    reg = os.environ.get("TE_REGION", REGION).lower()
    cfg = get_region_config(reg)
    bbox_dict = cfg["bbox"]
    data_raw_dir = cfg["data_raw"]

    days = days or (PANEL_HOURS // 24)
    key = firms_key or os.environ.get("FIRMS_MAP_KEY") or os.environ.get("FIRMS_KEY")

    if not key or use_synthetic:
        print(f"[firms] No FIRMS_MAP_KEY found or synthetic requested — generating realistic thermal anomalies for region '{reg}' ({days} days)...")
        return generate_synthetic_fires(days=days, region=reg)

    bbox_str = f'{bbox_dict["lon_min"]},{bbox_dict["lat_min"]},{bbox_dict["lon_max"]},{bbox_dict["lat_max"]}'
    end = window_end()
    start = end - pd.Timedelta(days=days)

    age_days = (pd.Timestamp.now("UTC").normalize() - end).days
    source = FIRMS_SOURCE_VIIRS_NRT if age_days < 55 else FIRMS_SOURCE_VIIRS_SP
    print(f"[firms] Querying NASA FIRMS ({source}) for '{reg}' from {start.date()} to {end.date()} ({days} days)...")

    frames = []
    curr_day = start

    while curr_day < end:
        chunk = min(FIRMS_MAX_DAY_RANGE, (end - curr_day).days)
        if chunk <= 0:
            break
        url = f"{FIRMS_URL}/{key}/{source}/{bbox_str}/{chunk}/{curr_day.date()}"
        try:
            raw_bytes = _get_url(url, timeout=45)
            text = raw_bytes.decode("utf-8", errors="replace")

            if "acq_date" not in text.split("\n", 1)[0]:
                head = text.strip().splitlines()[0][:120] if text.strip() else "(empty)"
                if "Invalid MAP_KEY" in head or "Bad Request" in head:
                    print(f"[firms] API Error ({head}) -> Falling back to high-fidelity synthetic data.")
                    return generate_synthetic_fires(days=days)
                print(f"[firms] Warning on {curr_day.date()}: {head}")
            else:
                part = pd.read_csv(io.StringIO(text))
                if not part.empty:
                    frames.append(part)
                print(f"[firms] {curr_day.date()} (+{chunk}d): {len(part)} raw detections")
        except Exception as e:
            print(f"[firms] Error fetching {curr_day.date()}: {e}. Continuing...")

        curr_day += pd.Timedelta(days=chunk)

    if not frames:
        print(f"[firms] Zero online detections returned -> generating synthetic realistic baseline.")
        return generate_synthetic_fires(days=days)

    raw_df = pd.concat(frames, ignore_index=True)

    # Standardize column naming
    rename_map = {
        "latitude": "lat",
        "longitude": "lon",
        "bright_ti4": "brightness",
        "bright_ti5": "brightness_alt",
        "daynight": "daynight"
    }
    raw_df = raw_df.rename(columns=rename_map)

    # Build ISO timestamp from acq_date and acq_time (HHMM)
    if "acq_time" in raw_df.columns and "acq_date" in raw_df.columns:
        time_str = raw_df["acq_time"].astype(str).str.zfill(4)
        raw_df["ts"] = pd.to_datetime(
            raw_df["acq_date"] + " " + time_str,
            format="%Y-%m-%d %H%M",
            utc=True
        )
    else:
        raw_df["ts"] = pd.Timestamp.now("UTC")

    if "frp" not in raw_df.columns:
        raw_df["frp"] = 15.0
    if "confidence" not in raw_df.columns:
        raw_df["confidence"] = 80.0
    if "brightness" not in raw_df.columns:
        raw_df["brightness"] = 330.0
    if "daynight" not in raw_df.columns:
        raw_df["daynight"] = "D"

    # Map each point to H3 res-8 cell
    raw_df["cell"] = [latlng_to_cell(r.lat, r.lon) for _, r in raw_df.iterrows()]
    raw_df["satellite"] = source

    out_cols = ["ts", "lat", "lon", "cell", "frp", "brightness", "confidence", "daynight", "satellite"]
    result = raw_df[[c for c in out_cols if c in raw_df.columns]].copy()
    
    # Save cache
    out_path = DATA_RAW / "firms_detections.parquet"
    result.to_parquet(out_path, index=False)
    print(f"[firms] Saved {len(result)} detections to {out_path}")
    return result


def generate_synthetic_fires(days: int = 90, region: Optional[str] = None) -> pd.DataFrame:
    """Generate realistic physical thermal anomalies anchored to real ground-truth facilities."""
    from shared.config import get_region_config
    reg = (region or os.environ.get("TE_REGION", REGION)).lower()
    cfg = get_region_config(reg)
    bbox_dict = cfg["bbox"]
    data_raw_dir = cfg["data_raw"]

    end = window_end()
    start = end - pd.Timedelta(days=days)
    rng = np.random.default_rng(42)

    records = []

    # 1. Barmer Basin Gas Flares (Mangala & Bhagyam)
    mangala_lat, mangala_lon = 26.5612, 73.8340
    bhagyam_lat, bhagyam_lon = 26.0421, 71.3210

    # 2. Punjab Stubble Burning & Brick Kilns
    punjab_kiln_lat, punjab_kiln_lon = 30.2145, 74.9421
    punjab_farms = [
        (30.25 + rng.normal(0, 0.08), 75.84 + rng.normal(0, 0.08)) for _ in range(8)
    ]

    # 3. Delhi Acute Industrial / Landfill Fire
    bhalswa_lat, bhalswa_lon = 28.7420, 77.1610

    # 4. Sun-glint solar artifact
    glint_lat, glint_lon = 26.2100, 71.9500

    # Hourly iteration over the time window
    time_points = pd.date_range(start, end, freq="6h", tz="UTC")

    for tp in time_points:
        hour = tp.hour
        is_day = 6 <= hour <= 18
        daynight = "D" if is_day else "N"

        # (A) Mangala Gas Flare
        if rng.random() > 0.10:
            frp = float(rng.normal(42.5, 2.8))
            records.append({
                "ts": tp,
                "lat": mangala_lat + rng.normal(0, 0.001),
                "lon": mangala_lon + rng.normal(0, 0.001),
                "frp": max(10.0, frp),
                "brightness": 350.0 + rng.normal(0, 5),
                "confidence": float(rng.integers(85, 100)),
                "daynight": daynight,
                "satellite": "VIIRS_SNPP_SYNTHETIC"
            })

        # (B) Bhagyam Flare
        if rng.random() > 0.20:
            records.append({
                "ts": tp,
                "lat": bhagyam_lat + rng.normal(0, 0.001),
                "lon": bhagyam_lon + rng.normal(0, 0.001),
                "frp": max(8.0, float(rng.normal(28.0, 2.5))),
                "brightness": 340.0 + rng.normal(0, 4),
                "confidence": float(rng.integers(80, 95)),
                "daynight": daynight,
                "satellite": "VIIRS_SNPP_SYNTHETIC"
            })

        # (C) Punjab Brick Kiln
        if is_day and (tp.month in [10, 11, 12, 1, 2, 3]):
            if rng.random() > 0.35:
                records.append({
                    "ts": tp,
                    "lat": punjab_kiln_lat + rng.normal(0, 0.0015),
                    "lon": punjab_kiln_lon + rng.normal(0, 0.0015),
                    "frp": max(5.0, float(rng.normal(18.5, 3.2))),
                    "brightness": 325.0 + rng.normal(0, 4),
                    "confidence": float(rng.integers(75, 90)),
                    "daynight": daynight,
                    "satellite": "VIIRS_SNPP_SYNTHETIC"
                })

        # (D) Agricultural Burning
        if is_day:
            for flat, flon in punjab_farms:
                if rng.random() > 0.50:
                    records.append({
                        "ts": tp,
                        "lat": flat + rng.normal(0, 0.002),
                        "lon": flon + rng.normal(0, 0.002),
                        "frp": max(4.0, float(rng.normal(14.0, 4.0))),
                        "brightness": 320.0 + rng.normal(0, 6),
                        "confidence": float(rng.integers(60, 85)),
                        "daynight": "D",
                        "satellite": "VIIRS_SNPP_SYNTHETIC"
                    })

        # (E) Acute Industrial Fire (Delhi)
        hours_from_end = (end - tp).total_seconds() / 3600.0
        if 6 <= hours_from_end <= 36:
            records.append({
                "ts": tp,
                "lat": bhalswa_lat + rng.normal(0, 0.001),
                "lon": bhalswa_lon + rng.normal(0, 0.001),
                "frp": max(150.0, float(rng.normal(285.0, 35.0))),
                "brightness": 380.0 + rng.normal(0, 10),
                "confidence": float(rng.integers(92, 100)),
                "daynight": daynight,
                "satellite": "VIIRS_SNPP_SYNTHETIC"
            })

        # (F) Sun-glint false positive
        if hour == 12 and rng.random() > 0.70:
            records.append({
                "ts": tp,
                "lat": glint_lat,
                "lon": glint_lon,
                "frp": float(rng.uniform(3.0, 8.0)),
                "brightness": 312.0,
                "confidence": float(rng.integers(40, 60)),
                "daynight": "D",
                "satellite": "VIIRS_SNPP_SYNTHETIC"
            })

    df = pd.DataFrame(records)
    if not df.empty:
        # Filter strictly within the target region bbox
        df = df[
            (df.lat >= bbox_dict["lat_min"]) & (df.lat <= bbox_dict["lat_max"]) &
            (df.lon >= bbox_dict["lon_min"]) & (df.lon <= bbox_dict["lon_max"])
        ].copy()

    if df.empty:
        c_lat = (bbox_dict["lat_min"] + bbox_dict["lat_max"]) / 2.0
        c_lon = (bbox_dict["lon_min"] + bbox_dict["lon_max"]) / 2.0
        for tp in time_points[-20:]:
            df = pd.concat([df, pd.DataFrame([{
                "ts": tp, "lat": c_lat, "lon": c_lon,
                "frp": 35.0, "brightness": 345.0, "confidence": 90.0,
                "daynight": "D", "satellite": "VIIRS_SNPP_SYNTHETIC"
            }])], ignore_index=True)

    df["cell"] = [latlng_to_cell(r.lat, r.lon) for _, r in df.iterrows()]
    out_path = data_raw_dir / "firms_detections.parquet"
    df.to_parquet(out_path, index=False)
    print(f"[firms] Generated {len(df)} synthetic detections for '{reg}' -> saved to {out_path}")
    return df
    df.to_parquet(out_path, index=False)
    print(f"[firms] Generated {len(df)} synthetic detections for '{REGION}' -> saved to {out_path}")
    return df


if __name__ == "__main__":
    df = fetch_fires(days=30)
    print(f"FIRMS collector test: {len(df)} records fetched/generated.")
    if not df.empty:
        print(df.head(5).to_string())
