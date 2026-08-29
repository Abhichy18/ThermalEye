"""ThermalEye — Open-Meteo Weather & Atmospheric Vector Collector.

Queries Open-Meteo (ECMWF physics model) across coarse H3 weather cells covering the region.
Key meteorological signals extracted:
1. `wind_speed_10m` (m/s) & `wind_direction_10m` (degrees from north)
2. `boundary_layer_height` (meters) — critical dispersion predictor
3. `temperature_2m` (°C) & `surface_pressure` (hPa)
4. $u$ and $v$ wind vector components for particle streamline rendering on 3D map.

Open-Meteo is completely free and keyless.
"""
import os
import json
import math
import urllib.request
import urllib.parse
from typing import Optional, List, Dict

import pandas as pd
import numpy as np

from shared.config import (
    BBOX, DATA_RAW, OPENMETEO_URL, OPENMETEO_ARCHIVE_URL, PANEL_HOURS, window_end, REGION
)
from shared.grid import weather_grid_cells, cell_center


def fetch_weather(days: Optional[int] = None, use_synthetic: bool = False) -> pd.DataFrame:
    """Fetch hourly weather vectors across weather grid cells covering region.

    Returns DataFrame with columns:
    ['weather_cell', 'ts', 'wind_from_deg', 'wind_ms', 'u_wind', 'v_wind', 'blh_m', 'temp_c']
    """
    days = days or (PANEL_HOURS // 24)
    grid_cells = weather_grid_cells()
    centers = [cell_center(c) for c in grid_cells]

    if not centers or use_synthetic:
        return generate_synthetic_weather(days=days, grid_cells=grid_cells)

    # Subsample weather points if too large (Open-Meteo max ~50 points per query)
    MAX_WEATHER_POINTS = 35
    if len(centers) > MAX_WEATHER_POINTS:
        step = max(1, len(centers) // MAX_WEATHER_POINTS)
        sampled_cells = grid_cells[::step][:MAX_WEATHER_POINTS]
        sampled_centers = centers[::step][:MAX_WEATHER_POINTS]
    else:
        sampled_cells = grid_cells
        sampled_centers = centers

    lats = ",".join(f"{lat:.4f}" for lat, _ in sampled_centers)
    lons = ",".join(f"{lon:.4f}" for _, lon in sampled_centers)

    end = window_end()
    start = end - pd.Timedelta(days=days)
    age_days = (pd.Timestamp.now("UTC").normalize() - end).days

    historical = days > 90 or age_days > 60
    if historical:
        q = urllib.parse.urlencode({
            "latitude": lats,
            "longitude": lons,
            "start_date": str(start.date()),
            "end_date": str(end.date()),
            "hourly": "wind_speed_10m,wind_direction_10m,temperature_2m,boundary_layer_height",
            "wind_speed_unit": "ms",
        })
        url = f"{OPENMETEO_ARCHIVE_URL}?{q}"
    else:
        q = urllib.parse.urlencode({
            "latitude": lats,
            "longitude": lons,
            "hourly": "wind_speed_10m,wind_direction_10m,temperature_2m,boundary_layer_height",
            "past_days": min(days, 90),
            "forecast_days": 2,
            "wind_speed_unit": "ms",
        })
        url = f"{OPENMETEO_URL}?{q}"

    print(f"[weather] Querying Open-Meteo for {len(sampled_cells)} weather stations ({days} days)...")

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ThermalEye-NTRO-SIH2026/1.0"}
        )
        with urllib.request.urlopen(req, timeout=45) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))

        locations = parsed if isinstance(parsed, list) else [parsed]
        frames = []
        for cell, loc in zip(sampled_cells, locations):
            if "hourly" not in loc:
                continue
            h = loc["hourly"]
            w_deg = np.array(h.get("wind_direction_10m", []), dtype=float)
            w_spd = np.array(h.get("wind_speed_10m", []), dtype=float)

            # Convert meteorological wind direction (comes FROM) to u/v vector components (m/s)
            # u: eastward component, v: northward component
            rad = np.radians(w_deg)
            u_wind = -w_spd * np.sin(rad)
            v_wind = -w_spd * np.cos(rad)

            frames.append(pd.DataFrame({
                "weather_cell": cell,
                "ts": pd.to_datetime(h["time"], utc=True),
                "wind_from_deg": w_deg,
                "wind_ms": w_spd,
                "u_wind": u_wind,
                "v_wind": v_wind,
                "blh_m": h.get("boundary_layer_height", [500.0] * len(w_deg)),
                "temp_c": h.get("temperature_2m", [28.0] * len(w_deg)),
            }))

        if frames:
            result = pd.concat(frames, ignore_index=True)
            out_path = DATA_RAW / "weather_vectors.parquet"
            result.to_parquet(out_path, index=False)
            print(f"[weather] Successfully saved {len(result)} weather vectors to {out_path}")
            return result
    except Exception as e:
        print(f"[weather] Live fetch failed ({e}) -> generating physics-calibrated synthetic weather.")

    return generate_synthetic_weather(days=days, grid_cells=grid_cells)


def generate_synthetic_weather(days: int = 90, grid_cells: Optional[List[str]] = None) -> pd.DataFrame:
    """Generate realistic diurnal weather with seasonal wind patterns."""
    end = window_end()
    start = end - pd.Timedelta(days=days)
    grid_cells = grid_cells or weather_grid_cells()
    if not grid_cells:
        grid_cells = ["weather_seed_cell"]

    # Sample top 15 cells for synthetic representation
    sampled = grid_cells[:15]
    time_points = pd.date_range(start, end, freq="3h", tz="UTC")
    rng = np.random.default_rng(2026)

    frames = []
    for cell in sampled:
        lat, lon = cell_center(cell) if cell != "weather_seed_cell" else (26.5, 71.5)
        
        # Predominant wind for Barmer/North-West India: South-Westerly in Monsoon, North-Easterly in Winter
        base_wind_deg = 240.0 if any(tp.month in [6, 7, 8, 9] for tp in [start]) else 60.0
        
        hours = np.array([tp.hour for tp in time_points])
        # Diurnal temperature cycle: peaks at 14:00 (08:30 UTC), dips at 05:00 (23:30 UTC)
        temp_c = 28.0 + 8.0 * np.sin(np.radians((hours - 3) * 15)) + rng.normal(0, 1.5, len(hours))
        
        # BLH: high during day (~1800m), collapsed at night (~250m)
        blh_m = 250.0 + 1500.0 * np.maximum(0, np.sin(np.radians((hours - 6) * 15))) + rng.normal(0, 50, len(hours))
        
        wind_spd = np.clip(rng.normal(4.5, 1.8, len(hours)), 0.5, 18.0)
        wind_dir = (base_wind_deg + rng.normal(0, 25.0, len(hours))) % 360.0

        rad = np.radians(wind_dir)
        u_wind = -wind_spd * np.sin(rad)
        v_wind = -wind_spd * np.cos(rad)

        frames.append(pd.DataFrame({
            "weather_cell": cell,
            "ts": time_points,
            "wind_from_deg": wind_dir,
            "wind_ms": wind_spd,
            "u_wind": u_wind,
            "v_wind": v_wind,
            "blh_m": np.maximum(50.0, blh_m),
            "temp_c": temp_c,
        }))

    result = pd.concat(frames, ignore_index=True)
    out_path = DATA_RAW / "weather_vectors.parquet"
    result.to_parquet(out_path, index=False)
    print(f"[weather] Generated {len(result)} weather records -> saved to {out_path}")
    return result


if __name__ == "__main__":
    df = fetch_weather(days=7, use_synthetic=True)
    print(f"Weather collector test: {len(df)} records.")
    print(df.head(5).to_string())
