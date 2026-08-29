# 🧠 THERMALEYE — PERSISTENT SYSTEM MEMORY & CONTEXT LEDGER
## Master Architecture, Contracts, Invariants & State Reference

---

## 1. Project Identity & Problem Statement

* **Project Name:** **ThermalEye** (AI-Powered National Thermal Source Classifier & Enforcement System)
* **Hackathon:** Smart India Hackathon (SIH) 2026
* **Problem ID:** SIH26162 (Space Technology Theme)
* **Sponsoring Agency:** National Technical Research Organisation (NTRO)
* **Core Mandate:** Convert raw satellite thermal anomalies (NASA FIRMS MODIS/VIIRS) into a **7-class, explainable, actionable, and legally defensible intelligence feed** using spatio-temporal persistence, VIIRS Nightfire (VNF), OpenStreetMap (OSM), Sentinel-2 optical verification, and atmospheric modeling.

---

## 2. System Architecture & Invariant Rules

### 2.1 The 4 Non-Negotiable Invariants
1. **Deterministic Arithmetic Ranks, LLM Only Explains:**
   - Classification categories, confidence scores, and Enforcement Priority Scores (EPS) are calculated **strictly by deterministic mathematical rules and LightGBM models**.
   - LLMs (NVIDIA NIM / Gemini / Groq) are invoked solely to generate human-readable briefing paragraphs.
   - If all LLM APIs fail or lose network, a deterministic rule-based template generates identical facts. The system **never** halts due to an API outage.
2. **Median Over Mean:**
   - In multi-window temporal calculations (24h / 7d / 30d), the **per-cell MEDIAN** of FRP and satellite signals is always used, never the arithmetic mean (which is easily corrupted by single-spike acute bonfires).
3. **Multi-Window Temporal Separation:**
   - Detections are evaluated across 3 sliding windows to separate operational urgencies:
     - `acute`: Detected within 24h only $\to$ Immediate Emergency Dispatch.
     - `emerging`: Elevated over 7d, but not in 30d history $\to$ Newly commissioned plant/unauthorized kiln; rapid inspection.
     - `chronic`: Elevated across both 7d and 30d $\to$ Established industrial installation; compliance audit.
4. **Offline Demo Insurance (Zero Failure Mode):**
   - The backend produces pre-computed, self-contained JSON artifacts in `data/outputs/<region>/`.
   - The frontend's SWR client loads these static JSON files seamlessly if live endpoints are unreachable.

---

## 3. Data Flow & Multi-Agent Orchestration

```
[ INGESTION LAYER ]
  NASA FIRMS (VIIRS 375m / MODIS 1km) ──┐
  VIIRS Nightfire (VNF 50m / Radiance) ──┼──> [ DBSCAN Space-Time Clustering ]
  Sentinel-5P NO₂ (GEE)                ──┤                    │
  Sentinel-2 10m Optical / SWIR (GEE)  ──┤                    ▼
  OpenStreetMap (Overpass API)         ──┤      [ Cell × Feature Panel ]
  Open-Meteo Weather (u/v Wind, BLH)   ──┘                    │
                                                              ▼
[ INTELLIGENCE GRAPH (LangGraph) ]
  1. Sun-Glint & Noise Pre-filter
  2. 7-Class Thermal Classifier (Physical Rules + LightGBM)
  3. Evidence Chain & Rejected Hypotheses Builder
  4. Enforcement Priority Scorer (EPS: 0-100)
  5. Legal Enforcement Memo Agent (CPCB / MoPNG / Forest Acts)
  6. Multilingual Advisory & TTS Voice Agent (Hindi/Regional)
  7. Intervention Ledger & Response Stopwatch
  8. Network Monitoring Gap Audit
                                                              │
                                                              ▼
[ PRODUCTION DELIVERY ]
  FastAPI Read-Only Endpoints + SSE Streamer ──> Next.js 15 + Deck.gl 3D Tactical Console
```

---

## 4. 7-Class Thermal Taxonomy & Mathematical Decision Boundaries

| Class ID | Target Category | Primary Thermal & Temporal Signature | Spatial / OSM Anchor | Key Physical Discriminator |
|---|---|---|---|---|
| `industrial_fire` | Factory Explosion / Chemical Hazard | Extreme FRP spike ($>150\text{ MW}$), duration $<48\text{ h}$, rapid decay | $\le 3\text{ km}$ to `industrial=*`, `power=plant` | Sudden emergence, high localized FRP, acute drop-off |
| `gas_flare` | Oil & Gas Flaring, LNG Terminals | Constant 24/7 detection ($>25/30\text{ d}$), low FRP variance ($\text{CoV} < 0.15$) | $\le 1.5\text{ km}$ to `man_made=petroleum_well`, `refinery` | **VNF Temp $>1200\text{ K}$**, zero diurnal drop |
| `brick_kiln` | Bull's Trench / Zig-Zag Kiln | Seasonal (Oct–Mar), diurnal pulse (morning firing), moderate FRP | Near farmland, cluster in IGP belt, no heavy industrial tags | Matched with **SentinelKilnDB**, seasonal activation cycle |
| `agricultural_burn` | Paddy/Wheat Stubble Burning | Daytime-only ($\text{Diurnal Ratio} \approx 0$), brief ($1\text{–}3\text{ d}$), high localized volume | `landuse=farmland`, rural belts | **Zero night detections**, Oct–Nov / Apr–May spikes |
| `mining` | Coal Seam Fire / Quarry Smelting | Moderate persistent FRP, broad spatial footprint, active during shift hours | $\le 2\text{ km}$ to `landuse=quarry`, `industrial=mine` | Coincides with documented mining lease perimeters |
| `wildfire` | Forest / Brush Fires | Multi-day spread, high total energy, spatial boundary expands radially | `natural=wood`, `natural=forest`, protected areas | **Positive spatial growth rate** ($\Delta \text{Area}/\Delta t > 0$) |
| `sun_glint` | Metallic Roof / Solar False Alarm | Low FRP ($<10\text{ MW}$), specular reflection geometry, isolated single pass | Solar zenith angle $\approx$ satellite sensor angle | **Zero nocturnal footprint**, specular angle match |

---

## 5. Verified Ground-Truth Benchmark Case Studies

1. **Barmer Basin — Mangala Oil Field (Rajasthan):**
   - Coordinates: `26.56°N, 73.83°E`
   - Classification: `gas_flare` (Confidence: $94.2\%$, EPS: $92.4$)
   - Validation: World Bank GGFR flaring registry ID #1492.
2. **Punjab Harvest Belt — Bathinda/Sangrur (Punjab):**
   - Coordinates: `30.21°N, 74.94°E`
   - Classification: `agricultural_burn` vs `brick_kiln`
   - Validation: CAQM & SentinelKilnDB ground truth (19,500+ tagged kilns).
3. **ONGC Hazira Gas Processing Complex (Gujarat):**
   - Coordinates: `21.10°N, 72.65°E`
   - Classification: `gas_flare` / Industrial Processing
   - Validation: Major national LNG critical infrastructure.
4. **Bhalswa Landfill / Industrial Cluster (Delhi-NCR):**
   - Coordinates: `28.74°N, 77.16°E`
   - Classification: `industrial_fire` / Methane Waste Combustion
   - Validation: AirCase historical ground-truth validation.

---

## 6. Technology Stack & Directory Standard

* **Backend:** Python 3.11, FastAPI, Uvicorn, LangGraph, LightGBM, Pandas, GeoPandas, Shapely, H3-Py, SWR Data Exporter.
* **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Deck.gl v9, Mapbox GL JS, TailwindCSS v4, Lucide-React, SWR.
* **APIs:** NASA FIRMS API, VIIRS Nightfire (EOG/NOAA), Google Earth Engine (Sentinel-2 & Sentinel-5P), OpenStreetMap Overpass, Open-Meteo, NVIDIA NIM / Gemini API.
* **Database:** Supabase PostgreSQL + PostGIS (Citizen Reports & Ledger), SQLite (Local Cached Snapshots).
