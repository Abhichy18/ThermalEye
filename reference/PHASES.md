# 🚀 THERMALEYE — STEP-BY-STEP DEVELOPMENT PHASES
## Production-Grade Execution Roadmap for SIH 2026

---

## 🗺️ Master Phase Overview

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  Phase 0: Environment & Core Scaffolding                                               │
│  Phase 1: Ingestion, Multi-Satellite Collectors & Spatio-Temporal Clustering           │
│  Phase 2: Core Intelligence, 7-Class Thermal Classifier & Evidence Engine              │
│  Phase 3: Action Layer: EPS Scorer, Legal Memos, Voice Notes & Feedback Loop           │
│  Phase 4: Production FastAPI Backend, SSE Streamer & Static JSON Exporter              │
│  Phase 5: Next.js 15 Space-Tech Frontend Foundation & HUD Dashboard                   │
│  Phase 6: 3D Geospatial Deck.gl Visualizer (Hexagon Extrusions & Wind Streamlines)    │
│  Phase 7: Deep Intelligence Panels & Case File Drawer (S2 Optical Spyglass & Charts)  │
│  Phase 8: Citizen & Inspector Field Portal (/citizen with Hindi TTS Audio)             │
│  Phase 9: End-to-End Validation, Ground-Truth Benchmarks & Hackathon Demo Package      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Project Setup & Core Environment Foundation
**Goal:** Establish clean workspace structure, install Python & Node dependencies, configure environment variables and shared spatial utilities.

### Deliverables:
- [ ] `requirements.txt`: Python 3.11 core dependencies (FastAPI, Uvicorn, LangGraph, LightGBM, Pandas, GeoPandas, H3-Py, Requests, OpenAI SDK for NIM).
- [ ] `.env.example` & `.env` configuration loader (supporting NASA FIRMS, NVIDIA NIM, Gemini, Groq, GEE).
- [ ] `shared/config.py`: Regional bounding boxes (Barmer, Punjab, Delhi, Gujarat, Chhattisgarh), file paths, persistence window thresholds.
- [ ] `shared/grid.py`: H3 hexagonal grid utilities (`cell_to_latlng`, `haversine_km`, `bearing_deg`, `wind_alignment`, `circular_mean_deg`).
- [ ] `shared/wards.py` & district GIS boundary helpers.

### Verification Criteria:
- Running `python -c "import shared.config; import shared.grid; print('Shared setup OK')"` succeeds with zero errors.

---

## Phase 1: Ingestion, Multi-Satellite Collectors & Spatio-Temporal Clustering
**Goal:** Build resilient data collectors for NASA FIRMS, VIIRS Nightfire, OSM, Sentinel-2/5P, and Open-Meteo, with spatio-temporal clustering.

### Deliverables:
- [ ] `ingestion/collectors/firms.py`: NASA FIRMS API fetcher for VIIRS 375m & MODIS 1km active fires with FRP, brightness, confidence.
- [ ] `ingestion/collectors/vnf.py`: VIIRS Nightfire collector for combustion temperature (Kelvin) and radiant heat output.
- [ ] `ingestion/collectors/osm.py`: Overpass API collector for industrial infrastructure, petroleum wells, refineries, quarries, brick kilns, forests, farmland.
- [ ] `ingestion/collectors/weather.py`: Open-Meteo API fetcher for wind vector $u/v$ components, surface temperature, and planetary boundary layer height.
- [ ] `ingestion/collectors/sentinel.py`: Sentinel-5P NO₂ tropospheric column & Sentinel-2 optical tile metadata collector.
- [ ] `ingestion/preprocessing/clustering.py`: Spatio-temporal DBSCAN algorithm aggregating raw thermal dots into distinct physical cluster objects.
- [ ] `ingestion/preprocessing/panel.py`: Multi-window ($24\text{h} / 7\text{d} / 30\text{d}$) cell $\times$ feature aggregation panel.

### Verification Criteria:
- Running `python -m ingestion.preprocessing.panel --region barmer` creates populated `data/raw/barmer/` and creates clustered thermal features.

---

## Phase 2: Core Intelligence, 7-Class Thermal Classifier & Evidence Engine
**Goal:** Implement the physical rule-based and LightGBM machine learning classifier with deterministic evidence chains and LLM explainers.

### Deliverables:
- [ ] `intelligence/models/signals.py`: Robust neighborhood contrast algorithms using spatial medians and Median Absolute Deviation (MAD).
- [ ] `intelligence/models/temporal_features.py`: Feature extraction engine (Diurnal ratio, persistence fraction, FRP coefficient of variation, spatial expansion rate).
- [ ] `intelligence/models/classifier.py`: Trained LightGBM multi-class model with calibrated probability outputs and TreeSHAP explainability.
- [ ] `intelligence/agents/classify.py`: Hybrid classification agent executing the 7-class taxonomy with Sun-Glint pre-filter.
- [ ] `intelligence/agents/evidence.py`: Evidence profile generator computing deterministic metrics and rejected alternative hypotheses.
- [ ] `intelligence/agents/llm_gateway.py`: Robust multi-provider LLM gateway (NVIDIA NIM $\to$ Gemini $\to$ Groq $\to$ Deterministic Rule Fallback).
- [ ] `intelligence/orchestrator.py`: LangGraph `StateGraph` orchestrator coordinating the execution pipeline with error isolation per node.

### Verification Criteria:
- Running `python -m intelligence.orchestrator --region barmer` outputs `data/outputs/barmer/classifications.json` with 100% valid schema and >90% classification accuracy on test benchmarks.

---

## Phase 3: Action Layer: EPS Scorer, Legal Memos, Voice Notes & Feedback Loop
**Goal:** Transform classified thermal anomalies into prioritized regulatory actions, legal enforcement memos, and field feedback mechanisms.

### Deliverables:
- [ ] `intelligence/agents/prioritise.py`: Enforcement Priority Score (EPS: 0–100) combining thermal severity, persistence, and proximity to sensitive receptors.
- [ ] `intelligence/agents/alert_router.py`: Jurisdictional router matching cluster categories to responsible agencies (SPCB, PNGRB, Forest Dept, District Collector).
- [ ] `intelligence/agents/memo.py`: Legal memo generator producing notices citing Air Act §31A, MoPNG 2025 Flaring Caps, and CPCB Zig-Zag kiln mandates.
- [ ] `intelligence/agents/voice.py`: Multilingual audio synthesizer generating Hindi & English advisory voice notes via Google Cloud TTS.
- [ ] `intelligence/agents/ledger.py`: Intervention ledger recording alert timestamps, inspector dispatches, and measuring counterfactual response times.
- [ ] `intelligence/agents/feedback.py`: Inspector feedback ingestion updating ground-truth verification logs.

### Verification Criteria:
- Running `python -m scripts.test_action_pipeline` generates compliant legal memos and synthesized audio files in `data/outputs/`.

---

## Phase 4: Production FastAPI Backend & Contract Validation
**Goal:** Build high-performance REST API with Server-Sent Events (SSE) for live agent execution and static JSON export for offline resilience.

### Deliverables:
- [ ] `app/backend/main.py`: Production FastAPI server with CORS, compression, error handlers, and 20+ specialized endpoints.
- [ ] `/api/clusters`: Returns ranked classified thermal clusters with EPS, confidence, and categories.
- [ ] `/api/cluster/{id}/evidence`: Returns full mathematical evidence chain, rejected hypotheses, and LLM briefing.
- [ ] `/api/cluster/{id}/optical`: Serves Sentinel-2 10m high-res optical imagery and SWIR thermal overlays.
- [ ] `/api/run/agent`: SSE endpoint streaming live LangGraph agent execution progress to the frontend.
- [ ] `scripts/export_static_bundle.py`: Offline exporter saving complete static JSON responses in `app/frontend/public/data/`.

### Verification Criteria:
- Running `uvicorn app.backend.main:app --port 8000` starts server cleanly; all endpoints pass automated HTTP contract tests.

---

## Phase 5: Next.js 15 Frontend Foundation & Space-Grade HUD Dashboard
**Goal:** Scaffold modern Next.js 15 frontend with Tactical Cyber-Intelligence theme, design tokens, HUD telemetry bar, and SWR state.

### Deliverables:
- [ ] `app/frontend/package.json`: Dependencies setup (Next.js 15, React 19, TypeScript, Deck.gl, TailwindCSS, Lucide-React, SWR, Chart.js).
- [ ] `app/frontend/src/app/globals.css`: Full implementation of design tokens, deep space surfaces, HUD borders, and 7-class color ramps.
- [ ] `app/frontend/src/lib/types.ts`: TypeScript definitions matching backend JSON schemas exactly.
- [ ] `app/frontend/src/lib/api.ts`: Resilient SWR fetchers with automatic static JSON fallback for offline presentations.
- [ ] `app/frontend/src/components/hud/HeaderBar.tsx`: Telemetry HUD, Region selector, Live status beacon.
- [ ] `app/frontend/src/components/hud/AgentProgressStrip.tsx`: Real-time 5-stage agent execution progress bar.
- [ ] `app/frontend/src/components/hud/MetricBentoGrid.tsx`: Bento cards for Active Clusters, Flares, Fires, Violations, Confidence.

### Verification Criteria:
- `npm run dev` boots the frontend on `localhost:3000` with clean UI, zero hydration errors, and responsive layouts.

---

## Phase 6: 3D Geospatial Deck.gl Visualizer & Interactive Map
**Goal:** Build high-performance 3D WebGL map viewport featuring extruded H3 thermal columns, animated wind streamlines, and fly-to presets.

### Deliverables:
- [ ] `app/frontend/src/components/map/MapContainer.tsx`: Deck.gl v9 + Mapbox GL engine with 45° 3D tilt controls.
- [ ] `app/frontend/src/components/map/layers/HexagonThermalLayer.ts`: 3D H3 Extruded Layer where height = FRP and color = 7-class category.
- [ ] `app/frontend/src/components/map/layers/HotspotBeaconLayer.ts`: Pulsing beacon animations over active industrial hazards.
- [ ] `app/frontend/src/components/map/layers/WindStreamlineLayer.ts`: Real-time animated atmospheric wind particle vectors.
- [ ] `app/frontend/src/components/map/controls/TimeScrubber.tsx`: 30-day temporal playback scrubber with animated time-warp.
- [ ] `app/frontend/src/components/map/controls/LayerToggleHUD.tsx`: Floating HUD layer toggles (VIIRS, S2, Wind, OSM, 3D Hexagons).

### Verification Criteria:
- 3D Map renders at 60 FPS with smooth panning, zooming, 3D column extrusion, and active wind animations.

---

## 7: Deep Intelligence Panels & Case File Suite
**Goal:** Implement the triage Action Queue and the expanded 4-Tab Case File Drawer for deep dive investigations.

### Deliverables:
- [ ] `app/frontend/src/components/panels/ActionQueue.tsx`: Ranked list of thermal clusters sorted by EPS priority with category badges.
- [ ] `app/frontend/src/components/panels/CaseFileModal.tsx`: Expandable multi-tab intelligence drawer.
- [ ] `app/frontend/src/components/panels/tabs/EvidenceChainTab.tsx`: Mathematical evidence table + rejected hypotheses checklist + LLM brief.
- [ ] `app/frontend/src/components/panels/tabs/OpticalComparisonTab.tsx`: Interactive split-screen spyglass comparing Sentinel-2 True Color vs SWIR.
- [ ] `app/frontend/src/components/panels/tabs/FRPTimeSeriesTab.tsx`: 30-day FRP sparkline chart showing temporal signatures.
- [ ] `app/frontend/src/components/panels/tabs/MemoGeneratorTab.tsx`: One-click legal PDF notice generator with pre-filled citations.

### Verification Criteria:
- Clicking any cluster card seamlessly opens the case file modal with live charts, optical spyglass, and instant PDF download.

---

## Phase 8: Citizen & Inspector Field Portal (`/citizen`)
**Goal:** Deliver responsive mobile-first portal for local residents and field officers with multilingual audio and closure loops.

### Deliverables:
- [ ] `app/frontend/src/app/citizen/page.tsx`: Mobile-optimized public hazard viewer.
- [ ] `app/frontend/src/components/citizen/VoicePlayer.tsx`: Audio player for native Hindi and regional language advisory notes.
- [ ] `app/frontend/src/components/citizen/IncidentReportForm.tsx`: 1-tap photo, GPS, and voice note submission tool.
- [ ] `app/frontend/src/components/citizen/InspectorResolution.tsx`: Field officer PIN validation and response time logging mechanism.

### Verification Criteria:
- `/citizen` operates seamlessly on mobile viewport with functional audio playback and report submission.

---

## Phase 9: End-to-End Validation, Ground-Truth Benchmarks & Hackathon Demo Package
**Goal:** Validate system against global ground-truth databases (World Bank GGFR, SentinelKilnDB), prepare pre-locked demo case studies, and finalize presentation.

### Deliverables:
- [ ] `validation/eval_classification.py`: Precision, Recall, and F1-score evaluation benchmark against GGFR flares and SentinelKilnDB.
- [ ] `scripts/demo_case_studies.py`: Pre-seeded data pack for Barmer Basin, Punjab Harvest, ONGC Hazira, and Bhalswa Landfill.
- [ ] Complete offline demo resilience check (verifying full functionality with network disconnected).
- [ ] `README.md`: Comprehensive, world-class documentation with architecture diagrams, setup guide, and API reference.
- [ ] 3-Minute Live Pitch Rehearsal Run-through.

### Verification Criteria:
- Full automated test suite passes; ground-truth evaluation reports $>91\%$ accuracy; demo runs flawlessly offline.
