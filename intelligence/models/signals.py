"""ThermalEye — Robust Signal Processing & Statistical Engines.

Implements Invariant #2 (Median Over Mean) and spatial contrast calculations.
A single intense campfire or flare spike must never artificially inflate the
background baseline.

Key Algorithms:
1. `robust_median_mad(series)`: Computes median and Median Absolute Deviation (MAD).
2. `neighbourhood_contrast(cell, cell_values, annulus_cells)`:
   Compares a target H3 cell against its surrounding annular background ring (k=5..10),
   preventing self-contamination by the source's own thermal/emission plume.
3. `classify_persistence(active_ratio)`: Buckets temporal persistence into acute/emerging/chronic.
"""
from typing import Dict, List, Optional, Tuple, Sequence
import numpy as np
import pandas as pd


def robust_median_mad(values: Sequence[float]) -> Tuple[float, float]:
    """Compute robust median and Median Absolute Deviation (MAD).

    MAD = median(|x - median(x)|) * 1.4826 (normal distribution scaling factor)
    """
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return 0.0, 0.0
    med = float(np.median(arr))
    abs_dev = np.abs(arr - med)
    mad = float(np.median(abs_dev) * 1.4826)
    return med, mad


def robust_z_score(value: float, background_median: float, background_mad: float) -> float:
    """Calculate modified Z-score using median and MAD."""
    if background_mad <= 1e-6:
        return 0.0 if abs(value - background_median) < 1e-6 else 5.0
    return (value - background_median) / background_mad


def neighbourhood_contrast(
    center_val: float,
    annulus_vals: Sequence[float],
) -> Dict[str, float]:
    """Compute contrast ratio of a center cell against its outer annular ring.

    Returns:
    - `median_bg`: Background median value
    - `mad_bg`: Background MAD
    - `contrast_ratio`: (center_val - median_bg) / max(1.0, median_bg)
    - `z_score`: Robust Z-score
    """
    med_bg, mad_bg = robust_median_mad(annulus_vals)
    ratio = (center_val - med_bg) / max(1.0, med_bg)
    z = robust_z_score(center_val, med_bg, mad_bg)
    return {
        "median_bg": round(med_bg, 3),
        "mad_bg": round(mad_bg, 3),
        "contrast_ratio": round(ratio, 3),
        "robust_z_score": round(z, 2)
    }


def classify_persistence(active_fraction: float) -> str:
    """Classify temporal persistence based on window fraction."""
    if active_fraction < 0.15:
        return "acute"       # Short-lived event (hours / 1-2 days)
    elif active_fraction < 0.40:
        return "emerging"    # Intermittent or newly starting source
    else:
        return "chronic"     # Long-term established persistent source
