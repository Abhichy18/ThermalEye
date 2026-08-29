"""ThermalEye — OpenStreetMap (OSM) Infrastructure Collector.

Queries Overpass API across multiple redundant mirrors for ground infrastructure:
- Industrial zones, factories, refineries (`landuse=industrial`, `industrial=*`)
- Petroleum wells & gas flare stacks (`man_made=petroleum_well`, `man_made=flare`, `pipeline`)
- Brick kilns (`man_made=kiln`)
- Mining & quarries (`landuse=quarry`, `industrial=mine`, `resource=coal`)
- Agricultural farmland (`landuse=farmland`)
- Forests & protected areas (`natural=wood`, `natural=forest`)
- Sensitive receptors: Schools & Hospitals (`amenity=school`, `amenity=hospital`)

Includes automatic mirror rotation and realistic pre-tagged infrastructure fallback.
"""
import os
import json
import time
import urllib.request
import urllib.parse
from typing import Optional, List, Dict

import pandas as pd
import numpy as np

from shared.config import BBOX, DATA_RAW, OVERPASS_URL, REGION
from shared.grid import latlng_to_cell

OVERPASS_MIRRORS = [
    OVERPASS_URL,
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
]


def fetch_osm(use_synthetic: bool = False) -> pd.DataFrame:
    """Fetch OSM infrastructure for the region bbox.

    Returns DataFrame with columns:
    ['name', 'kind', 'tag', 'lat', 'lon', 'cell']
    """
    if use_synthetic:
        return generate_synthetic_osm()

    bbox_str = f'{BBOX["lat_min"]},{BBOX["lon_min"]},{BBOX["lat_max"]},{BBOX["lon_max"]}'

    query = f"""
    [out:json][timeout:90];
    (
      way["landuse"="industrial"]({bbox_str});
      node["man_made"~"^(petroleum_well|flare|kiln)$"]({bbox_str});
      way["man_made"~"^(petroleum_well|flare|kiln)$"]({bbox_str});
      way["landuse"="quarry"]({bbox_str});
      way["industrial"="mine"]({bbox_str});
      way["landuse"="farmland"]({bbox_str});
      way["natural"~"^(wood|forest)$"]({bbox_str});
      node["amenity"~"^(school|hospital)$"]({bbox_str});
      way["amenity"~"^(school|hospital)$"]({bbox_str});
    );
    out center 5000;
    """

    elements = None
    print(f"[osm] Querying Overpass API for region '{REGION}'...")

    for attempt, endpoint in enumerate(OVERPASS_MIRRORS):
        try:
            req = urllib.request.Request(
                endpoint,
                data=urllib.parse.urlencode({"data": query}).encode("utf-8"),
                headers={
                    "User-Agent": "ThermalEye-NTRO-SIH2026/1.0 (Earth Observation Spatial Analysis)",
                    "Accept": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elements = data.get("elements", [])
                if elements:
                    print(f"[osm] Success from {endpoint.split('/')[2]}: {len(elements)} elements found.")
                    break
        except Exception as e:
            print(f"[osm] Mirror {endpoint} failed ({e}) — trying next mirror...")
            time.sleep(1)

    if not elements:
        print("[osm] Overpass unavailable or empty -> generating realistic region infrastructure.")
        return generate_synthetic_osm()

    rows = []
    for el in elements:
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue

        tags = el.get("tags", {})
        landuse = tags.get("landuse")
        man_made = tags.get("man_made")
        industrial = tags.get("industrial")
        natural = tags.get("natural")
        amenity = tags.get("amenity")

        if man_made == "petroleum_well" or "petroleum" in str(tags):
            kind = "petroleum_well"
        elif man_made == "flare":
            kind = "gas_flare"
        elif man_made == "kiln":
            kind = "brick_kiln"
        elif landuse == "quarry" or industrial == "mine":
            kind = "mining"
        elif landuse == "industrial":
            kind = "industrial"
        elif landuse == "farmland":
            kind = "farmland"
        elif natural in ("wood", "forest"):
            kind = "forest"
        elif amenity in ("school", "hospital"):
            kind = "vulnerable_receptor"
        else:
            kind = "other_infrastructure"

        name = tags.get("name", f"{kind}_{el.get('id')}")
        tag_str = ";".join(f"{k}={v}" for k, v in list(tags.items())[:3])
        rows.append({
            "name": name,
            "kind": kind,
            "tag": tag_str,
            "lat": lat,
            "lon": lon,
            "cell": latlng_to_cell(lat, lon)
        })

    df = pd.DataFrame(rows)
    out_path = DATA_RAW / "osm_infrastructure.parquet"
    df.to_parquet(out_path, index=False)
    return df


def generate_synthetic_osm() -> pd.DataFrame:
    """Generate realistic OSM tagged infrastructure for the active region."""
    records = []

    if REGION == "barmer":
        records = [
            {"name": "Mangala Processing Terminal (MPT)", "kind": "industrial", "tag": "landuse=industrial;operator=Vedanta Cairn", "lat": 26.5610, "lon": 73.8335},
            {"name": "Mangala Wellpad #1", "kind": "petroleum_well", "tag": "man_made=petroleum_well", "lat": 26.5590, "lon": 73.8310},
            {"name": "Mangala Wellpad #4", "kind": "petroleum_well", "tag": "man_made=petroleum_well", "lat": 26.5650, "lon": 73.8380},
            {"name": "Bhagyam Central Processing Facility", "kind": "industrial", "tag": "landuse=industrial;operator=Cairn", "lat": 26.0420, "lon": 71.3200},
            {"name": "Bhagyam Wellpad A", "kind": "petroleum_well", "tag": "man_made=petroleum_well", "lat": 26.0410, "lon": 71.3220},
            {"name": "Barmer Lignite Mining Area", "kind": "mining", "tag": "landuse=quarry;resource=lignite", "lat": 25.9800, "lon": 71.4500},
            {"name": "Thar Desert Farmland Belt", "kind": "farmland", "tag": "landuse=farmland;crop=mustard", "lat": 26.2000, "lon": 72.1000},
            {"name": "Barmer District Hospital", "kind": "vulnerable_receptor", "tag": "amenity=hospital", "lat": 25.7520, "lon": 71.3910},
            {"name": "Govt High School Baytu", "kind": "vulnerable_receptor", "tag": "amenity=school", "lat": 25.8890, "lon": 71.7710},
        ]
    elif REGION == "punjab":
        records = [
            {"name": "Bathinda Brick Kiln Cluster #14", "kind": "brick_kiln", "tag": "man_made=kiln;technology=FCK", "lat": 30.2140, "lon": 74.9410},
            {"name": "Sangrur Certified Zig-Zag Kiln", "kind": "brick_kiln", "tag": "man_made=kiln;technology=zigzag", "lat": 30.2510, "lon": 75.8390},
            {"name": "Paddy Cultivation Field #102", "kind": "farmland", "tag": "landuse=farmland;crop=paddy", "lat": 30.2800, "lon": 75.1200},
            {"name": "Ludhiana Industrial Focal Point", "kind": "industrial", "tag": "landuse=industrial", "lat": 30.8800, "lon": 75.8900},
            {"name": "Bir Moti Bagh Wildlife Sanctuary", "kind": "forest", "tag": "natural=wood", "lat": 30.2900, "lon": 76.3800},
            {"name": "Civil Hospital Bathinda", "kind": "vulnerable_receptor", "tag": "amenity=hospital", "lat": 30.2110, "lon": 74.9510},
        ]
    elif REGION == "delhi":
        records = [
            {"name": "Bhalswa Landfill & Waste Processing", "kind": "industrial", "tag": "landuse=landfill;industrial=waste", "lat": 28.7410, "lon": 77.1600},
            {"name": "Ghazipur Industrial Complex", "kind": "industrial", "tag": "landuse=industrial", "lat": 28.6250, "lon": 77.3300},
            {"name": "Okhla Industrial Area Phase-II", "kind": "industrial", "tag": "landuse=industrial", "lat": 28.5300, "lon": 77.2700},
            {"name": "Asola Bhatti Wildlife Sanctuary", "kind": "forest", "tag": "natural=forest", "lat": 28.4800, "lon": 77.2500},
            {"name": "Babu Jagjivan Ram Memorial Hospital", "kind": "vulnerable_receptor", "tag": "amenity=hospital", "lat": 28.7300, "lon": 77.1700},
        ]
    else:
        c_lat = (BBOX["lat_min"] + BBOX["lat_max"]) / 2.0
        c_lon = (BBOX["lon_min"] + BBOX["lon_max"]) / 2.0
        records = [
            {"name": f"{REGION.title()} Industrial Complex", "kind": "industrial", "tag": "landuse=industrial", "lat": c_lat + 0.05, "lon": c_lon + 0.05},
            {"name": f"{REGION.title()} District Farmland", "kind": "farmland", "tag": "landuse=farmland", "lat": c_lat - 0.05, "lon": c_lon - 0.05},
            {"name": f"{REGION.title()} District Hospital", "kind": "vulnerable_receptor", "tag": "amenity=hospital", "lat": c_lat, "lon": c_lon},
        ]

    for r in records:
        r["cell"] = latlng_to_cell(r["lat"], r["lon"])

    df = pd.DataFrame(records)
    out_path = DATA_RAW / "osm_infrastructure.parquet"
    df.to_parquet(out_path, index=False)
    print(f"[osm] Saved {len(df)} infrastructure landmarks for '{REGION}' to {out_path}")
    return df


if __name__ == "__main__":
    df = fetch_osm(use_synthetic=True)
    print(f"OSM collector test: {len(df)} records.")
    print(df.to_string())
