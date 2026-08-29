# 🛰️ THERMALEYE — Frontend Architecture & UI/UX Design System
## Space-Grade Thermal Intelligence & Enforcement Console (SIH 2026)

---

## 1. Executive Design Philosophy & Vision

### 1.1 The Core Problem & UI Mandate
Judges and NTRO/SPCB regulators do **not** want another generic dashboard with red dots scattered over OpenStreetMap. NASA FIRMS already provides a raw heat map. 

**ThermalEye's UI mandate is clear:**
> **"Turn 2,000+ noisy satellite thermal anomalies into a prioritized, explainable, and legally actionable enforcement queue within 3 seconds of page load."**

### 1.2 Design Synthesis: AirCase Base + Top 15 Benchmarks
We build upon the proven architecture of **AirCase** (Next.js 15, Deck.gl, React 19, TypeScript, CSS Variables, SWR, FastAPI contracts) and elevate it using design patterns from the world's best earth observation platforms:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THERMALEYE UI HYBRID ENGINE                                 │
├────────────────────────────┬─────────────────────────────┬──────────────────────────────────┤
│ Base Foundation (AirCase)  │ Visual WOW (Kepler / VEDA)  │ Tactical Operations (Watch Duty) │
│ • SWR city-scoped caching  │ • 3D H3 Hexagon Extrusion   │ • Live Event Stream Sidebar      │
│ • LangGraph SSE progress   │ • FRP Glow & Elevation      │ • Urgency Badging & Triage       │
│ • Deterministic math view  │ • Optical Spyglass (S2)     │ • 1-Click Enforcement Memo       │
│ • Read-only JSON contracts │ • Animated Wind Streamlines │ • Field Inspector Feedback Modal │
└────────────────────────────┴─────────────────────────────┴──────────────────────────────────┘
```

---

## 2. Design System & Tokens (`globals.css`)

The UI follows a **Tactical Cyber-Intelligence / Space Command Center** theme. Chromatic saturation is strictly reserved for **data encoding** (thermal intensity, confidence, categories). Chrome and surfaces remain sleek, dark, and near-achromatic.

### 2.1 Color Palette & Tokens

```css
:root {
  /* ── Deep Space Surfaces ── */
  --bg-base:          #08090b;   /* Main viewport backdrop */
  --bg-surface:       #0e1116;   /* Cards and sidebars */
  --bg-surface-hover: #151921;   /* Hover states */
  --bg-elevated:      #1a1f29;   /* Modals and popovers */
  --bg-glass:         rgba(14, 17, 22, 0.85);
  --bg-glass-border:  rgba(255, 255, 255, 0.08);

  /* ── Typography Colors ── */
  --text-primary:     #f0f3f6;   /* Headings, high emphasis */
  --text-secondary:   #9ca3af;   /* Labels, metadata */
  --text-muted:       #64748b;   /* Timestamps, grid markings */
  --text-code:        #38bdf8;   /* Coordinates, IDs, numbers */

  /* ── Primary Tactical Accent ── */
  --accent-cyan:      #06b6d4;   /* Telemetry, selection outlines */
  --accent-glow:      rgba(6, 182, 212, 0.25);

  /* ── 7-Class Thermal Classification Color Ramp (Data Only) ── */
  --class-industrial-fire: #ef4444; /* Neon Crimson  (Acute hazard) */
  --class-gas-flare:       #f97316; /* Amber Flare   (Persistent flaring) */
  --class-brick-kiln:      #eab308; /* Golden Kiln   (Seasonal cyclical) */
  --class-agri-burn:       #84cc16; /* Lime Green    (Farmland stubble) */
  --class-mining:          #a855f7; /* Violet Mining (Quarry processing) */
  --class-wildfire:        #ec4899; /* Hot Pink      (Spreading forest) */
  --class-artifact:        #64748b; /* Slate Gray    (Sun glint / filtered) */

  /* ── FRP Intensity Scale (for 3D Extrusion) ── */
  --frp-low:          #fed7aa; /* < 20 MW */
  --frp-medium:       #fb923c; /* 20 - 100 MW */
  --frp-high:         #ea580c; /* 100 - 300 MW */
  --frp-extreme:      #dc2626; /* > 300 MW (Explosions/Massive fires) */

  /* ── Borders & HUD Lines ── */
  --border-subtle:    rgba(255, 255, 255, 0.06);
  --border-active:    rgba(6, 182, 212, 0.50);
  --border-critical:  rgba(239, 68, 68, 0.40);
}
```

### 2.2 Typography Hierarchy
- **UI & Body:** `Inter` (geometric, clean legibility at 11–13px)
- **Telemetry & Numerical Data:** `JetBrains Mono` (tabular numbers, alignment for FRP, coordinates, dates)
- **Scale:**
  - Micro Header: `9px / uppercase / tracking-wider`
  - HUD Metric Value: `18px / 600 / JetBrains Mono`
  - Title / Header: `15px / 600 / Inter`
  - Body Text: `12px / 400 / Inter`

---

## 3. Screen Layout Architecture

The application is structured into **3 core screens**:

```
                               ┌─────────────────────────────┐
                               │  / (Root Landing & Region)  │
                               └──────────────┬──────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
     ┌─────────────────────────────┐                     ┌─────────────────────────────┐
     │   /admin (Command Console)  │                     │   /citizen (Public Portal)  │
     │   • 3D Geospatial Deck.gl   │                     │   • Localized Fire Alerts   │
     │   • Action Queue & Triage   │                     │   • 1-Tap Incident Report   │
     │   • Evidence Chain Engine   │                     │   • Hindi/Regional Voice    │
     │   • Sentinel-2 Comparison   │                     │   • Compliance History      │
     └─────────────────────────────┘                     └─────────────────────────────┘
```

---

## 4. Screen 1: The Tactical Admin Command Center (`/admin`)

The central operational hub for regulators (SPCB/CPCB), intelligence officers (NTRO), and emergency responders.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛰️ THERMALEYE // NATIONAL THERMAL INTELLIGENCE PLATFORM           [Region: Barmer Basin ▾] [● SATELLITE LIVE: 3h]   │
├──────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┤
│ 🗺️ VIEWPORT: 3D DECK.GL ENGINE (70% Width)           │ 📋 SIDEBAR: ACTION QUEUE & CASE FILE (30% Width)             │
│                                                      │ ──────────────────────────────────────────────────────────── │
│  [Top HUD: Agent Pipeline Progress Strip]            │ 🔍 Search cluster, district, or facility... [Filter ▾]       │
│  [✓ Ingest] ── [✓ Cluster] ── [✓ Classify] ── [✓ EPS]│                                                              │
│                                                      │ ┌──────────────────────────────────────────────────────────┐ │
│  ┌─────────────────────────┐                         │ │ 🔴 CLU-8941 · BARMER MANGALA-3            EPS: 92.4 [P1] │ │
│  │ Layer Control (HUD)     │                         │ │ Gas Flare (24/7 Persistent) · Confidence: 94.2%          │ │
│  │ [x] 3D H3 Hexagons      │                         │ │ 42.8 MW avg · 0.8km from Petroleum Well · Steady         │ │
│  │ [x] VIIRS Detections    │                         │ └──────────────────────────────────────────────────────────┘ │
│  │ [x] Wind Vectors        │                         │ ┌──────────────────────────────────────────────────────────┐ │
│  │ [ ] S2 Optical Overlay  │                         │ │ 🟡 CLU-1042 · PUNJAB BATHINDA EAST        EPS: 78.1 [P2] │ │
│  └─────────────────────────┘                         │ │ Brick Kiln (Cyclical Zig-Zag) · Confidence: 88.0%        │ │
│                                                      │ │ 18.2 MW · Non-compliant Distance to Habitat (420m)       │ │
│   📍 3D Extruded Columns (Height = FRP)              │ └──────────────────────────────────────────────────────────┘ │
│   💨 Animated Wind Streamlines                       │ ──────────────────────────────────────────────────────────── │
│   🎯 Active Selection Beacon                         │ 📊 SELECTED CLUSTER DEEP-DIVE                                │
│                                                      │ [Tabs: Evidence Chain | S2 Optical | FRP Trend | Legal Memo] │
├──────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┤
│ ⏱️ TIME-WARP SCRUBBER: [ ◀◀ 30d History ────────────●──────────── Live Window (Nov 2025) ▶▶ ]   [Play / Pause ⏯️]  │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Component Breakdown & Interaction Specs

#### Component A: 3D Map Viewport (`MapContainer.tsx`)
- **Technology:** `deck.gl v9` + `Mapbox GL JS` (Dark Matter v11 base map).
- **Layers Rendered:**
  1. **`H3HexagonLayer` (3D Extruded):**
     - `getElevation`: Driven by `cluster.mean_frp * 25` (giving physical 3D bar height).
     - `getFillColor`: Mapped to `SourceCategoryColor[cluster.classification]`.
     - `opacity`: 0.85, wireframe: true.
  2. **`ScatterplotLayer` (Hotspot Beacons):**
     - Pulsing ripple effect (`@keyframes beacon-pulse`) over active `industrial_fire` clusters.
  3. **`WindVectorLayer` (from Earth Nullschool concept):**
     - Animated particle stream showing local wind direction and velocity ($u, v$ components from Open-Meteo).
     - Instantly proves to judges whether smoke/heat is blowing downwind toward residential areas.
  4. **`OSMPolygonLayer`:**
     - Highlighting registered industrial parks, refineries, quarry boundaries, and brick kiln clusters on hover.

#### Component B: Top Agent Pipeline Strip (`AgentProgressStrip.tsx`)
- Reads real-time **Server-Sent Events (SSE)** from `/run/agent`.
- Visual progress state with micro-timings:
  - `Ingest (FIRMS+VNF+S5P): 1.2s` $\to$ `Clustering (DBSCAN): 0.4s` $\to$ `Classifier (7-Class): 0.8s` $\to$ `Evidence Builder: 1.1s` $\to$ `EPS Ranker: 0.3s`.
- Proves autonomous multi-agent capability in real-time.

#### Component C: Cluster Case File & Evidence Drawer (`CaseFileDrawer.tsx`)
When any cluster on the map or sidebar is clicked, the bottom-right panel expands into a **4-Tab Intelligence Suite**:

##### Tab 1: 📋 Evidence Chain (`EvidenceChainTab.tsx`)
- **Deterministic Metrics Table:**
  - `Temporal Persistence`: "28 of 30 days active (93.3% window coverage)"
  - `Diurnal Ratio (Day/Night)`: "1.02 (Identical day and night combustion $\to$ Flare signature)"
  - `FRP CoV (Variance)`: "0.07 (Flat line $\to$ Controlled engineered flaring)"
  - `VNF Temperature`: "1,847 K (Atmospheric methane combustion)"
  - `OSM Proximity`: "0.80 km to 'Mangala Wellpad #4'"
- **Alternative Hypotheses Rejected (Anti-Hallucination Box):**
  - ❌ `wildfire`: Rejected (Spatial growth rate = 0.00 km²/day; arid terrain).
  - ❌ `industrial_fire`: Rejected (Duration > 720 hours rules out acute explosion).
- **LLM Grounded Synthesis:** 2-sentence plain English briefing generated strictly from the numbers above.

##### Tab 2: 🛰️ Sentinel-2 Optical Spyglass (`OpticalComparisonTab.tsx`)
- High-resolution 10-meter **Sentinel-2 optical satellite imagery** fetched for that exact coordinate.
- **Interactive Split-Screen Slider (Spyglass):**
  - Left: Sentinel-2 True Color image (showing actual industrial flare stack or kiln chimney).
  - Right: Short-Wave Infrared (SWIR Band 12) + Thermal FIRMS heat bloom overlay.
- *Judges can visually confirm the physical facility with their own eyes.*

##### Tab 3: 📈 FRP Time-Series Sparkline (`FRPTimeSeriesTab.tsx`)
- 30-day interactive timeline chart (powered by Chart.js / Tremor).
- Visual profile signature:
  - `gas_flare`: Flat horizontal line with zero variance.
  - `industrial_fire`: Sharp vertical Dirac-delta spike followed by rapid decay.
  - `brick_kiln`: Diurnal sawtooth wave (morning firing cycle).
  - `agricultural_burn`: 2-day isolated pulse during afternoon hours.

##### Tab 4: ⚖️ 1-Click Enforcement Memo (`MemoGeneratorTab.tsx`)
- Pre-filled legal action notice:
  - Target Authority: *PNGRB / Gujarat SPCB / Directorate of Mine Safety*.
  - Matched Violation: *Rule 14(b) of MoPNG Natural Gas Flaring Guidelines (2025)* OR *CPCB Zig-Zag Conversion Mandate*.
  - Buttons: `[ Download Official PDF ]`, `[ Dispatch to Inspector WhatsApp ]`, `[ Log in Ledger ]`.

---

## 5. Screen 2: Citizen & Inspector Field Portal (`/citizen`)

Mobile-first responsive design for field officers and local residents.

```
┌────────────────────────────────────────────────────────┐
│ 📍 DISTRICT: BARMER (RAJASTHAN)           [Language: हिन्दी ▾]│
├────────────────────────────────────────────────────────┤
│ 🔔 ACTIVE REGIONAL THERMAL SOURCES (2)                 │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ ⛽ Industrial Gas Flare (Routine)                   │ │
│ │ Location: Mangala Terminal (3.2 km away)           │ │
│ │ Status: COMPLIANT & CONTROLLED                     │ │
│ │ Note: No threat to nearby settlements.              │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ 🔊 AUDIO ADVISORY (Voice Note Player):                 │
│ ▶ [ ●────────────────────────── 0:24 ] (Hindi TTS)     │
│ "बरमेर जिले में मंगला टर्मिनल के पास गैस फ्लेयर..."   │
│                                                        │
│ ────────────────────────────────────────────────────── │
│ 📸 REPORT AN UNIDENTIFIED FIRE / DUST                  │
│ [ Take Camera Photo ] [ Record Voice Note ] [ Pin GPS] │
│                                                        │
│ 👮 INSPECTOR ACTION LOOP:                              │
│ [ Enter Inspection PIN ] ➔ [ Mark Action Resolved ]    │
└────────────────────────────────────────────────────────┘
```

### 5.1 Key Capabilities:
1. **Regional Voice Briefing:** Native Hindi / Tamil / Kannada / English voice advisory synthesized via Google TTS.
2. **Citizen Corroboration Intake:**
   - Citizens can upload geo-tagged photos of illegal burning.
   - Multimodal LLM extracts category (`waste_burning`, `illegal_kiln`) and feeds it back to the Python backend to increment the cluster's confidence score (`+0.07` cap).
3. **Two-Sided Inspector Closure Loop:**
   - Field officers receive inspection alerts on Telegram/Web, conduct site audits, and tap `[ Mark Inspected ]`.
   - Automatically timestamps the **Intervention Ledger** to calculate official response time.

---

## 6. Detailed Component Tree & File Mapping

```
app/frontend/src/
├── app/
│   ├── layout.tsx                     # Root layout (Inter + JetBrains font loaders)
│   ├── globals.css                    # Space-grade design tokens, animations, HUD styling
│   ├── admin/
│   │   ├── page.tsx                   # Master Admin Command Console
│   │   └── loading.tsx                # Cybernetic pulse loader
│   ├── citizen/
│   │   └── page.tsx                   # Mobile-first Citizen & Field Inspector Portal
│   └── api/
│       └── proxy/                     # Backend API proxy with static fallback cache
│
├── components/
│   ├── hud/                           # ── Tactical HUD Elements ──
│   │   ├── HeaderBar.tsx              # Telemetry stats, Region Switcher, Live status
│   │   ├── AgentProgressStrip.tsx     # 5-stage real-time agent execution pipeline
│   │   └── MetricBentoGrid.tsx        # Total FRP, Active Flares, Violations count
│   │
│   ├── map/                           # ── 3D Geospatial Visualizer ──
│   │   ├── MapContainer.tsx           # Deck.gl + Mapbox engine
│   │   ├── layers/
│   │   │   ├── HexagonThermalLayer.ts # 3D H3 Extruded Layer (Height = FRP, Color = Class)
│   │   │   ├── HotspotBeaconLayer.ts  # Pulsing SVG animated beacons on active fires
│   │   │   ├── WindStreamlineLayer.ts # Real-time animated atmospheric wind vectors
│   │   │   └── OSMBoundaryLayer.ts    # Industrial parks & quarry polygon borders
│   │   └── controls/
│   │       ├── LayerToggleHUD.tsx     # Toggle VIIRS, S2, Wind, Hexagons, OSM
│   │       └── TimeScrubber.tsx       # 30-day temporal playback slider with play/pause
│   │
│   ├── panels/                        # ── Sidebars & Case File Inspection ──
│   │   ├── ActionQueue.tsx            # Ranked list of classified clusters (EPS order)
│   │   ├── ClusterCard.tsx            # Individual cluster card with classification badges
│   │   ├── CaseFileModal.tsx          # Expanded 4-tab intelligence suite
│   │   ├── tabs/
│   │   │   ├── EvidenceChainTab.tsx   # Mathematical evidence & rejected hypotheses
│   │   │   ├── OpticalComparisonTab.ts# Sentinel-2 true color vs thermal split-screen
│   │   │   ├── FRPTimeSeriesTab.tsx   # 30-day FRP sparkline chart (Chart.js)
│   │   │   └── MemoGeneratorTab.tsx   # PDF enforcement notice generator
│   │   └── InspectorFeedbackModal.tsx # Ground-truth feedback loop submission form
│   │
│   └── citizen/                       # ── Citizen & Inspector Components ──
│       ├── VoicePlayer.tsx            # Audio player for multilingual advisory MP3s
│       ├── IncidentReportForm.tsx     # GPS + Photo + Voice report submission
│       └── InspectorResolution.tsx    # Field closure & response time logger
│
├── lib/                               # ── Utilities, Contracts & State ──
│   ├── types.ts                       # TypeScript interfaces matching backend JSON contracts
│   ├── api.ts                         # SWR fetchers with static offline JSON fallback
│   ├── colors.ts                      # Thermal classification color scales & thresholds
│   ├── h3utils.ts                     # H3 index $\leftrightarrow$ coordinate conversion
│   └── constants.ts                   # Pre-locked demo case studies (Barmer, Punjab, etc.)
│
└── hooks/                             # ── Custom React Hooks ──
    ├── useThermalClusters.ts          # SWR hook for `/clusters` endpoint
    ├── useClusterDetails.ts           # SWR hook for single cluster evidence profile
    ├── useAgentPipeline.ts            # SSE hook for live LangGraph execution
    └── useTimeScrubber.ts             # State manager for 30-day temporal animation
```

---

## 7. User Journey & Live Demo Flow (Step-by-Step)

Here is the exact interactive sequence for judges on demo day:

```
[ STEP 1: INITIAL LOAD (0s - 15s) ]
  • Screen opens on `/admin` with dark command center theme.
  • Map initializes in 3D tilted view over India with H3 extruded hexagonal heat columns.
  • Top Metric Bento displays: 
    "Active Thermal Clusters: 48 | Industrial Fires: 2 | Gas Flares: 11 | Farm Fires: 35 | Model Confidence: 92.4%".
  • Agent progress strip pulses green showing "Pipeline: Synchronized (6 Free Feeds Active)".

[ STEP 2: PRESET FLY-TO (15s - 45s) ]
  • Presenter clicks Preset Dropdown ➔ selects "Mangala Oil Field (Barmer Basin)".
  • Camera smoothly animates and flies into Barmer, Rajasthan with 45° 3D pitch.
  • Yellow-orange 3D column stands steady over the coordinates.
  • Wind streamline particles blow gently eastward across the terrain.

[ STEP 3: INSPECTING THE EVIDENCE (45s - 1m 30s) ]
  • Presenter clicks the Barmer cluster card on the right Action Queue.
  • Case File Drawer slides up smoothly.
  • Tab 1 (Evidence): Shows "28/30 Days Persistence", "VNF Temp: 1,847K", "OSM Petroleum Well 0.8km".
  • Tab 2 (Optical): Presenter slides the Sentinel-2 spyglass slider showing the real optical flare stack under the satellite overlay.
  • Tab 3 (FRP Trend): Shows flat, zero-variance sparkline proving it's an engineered flare, not a wildfire.

[ STEP 4: STUBBLE NOISE REJECTION (1m 30s - 2m 15s) ]
  • Presenter clicks Preset "Punjab Harvest Belt (Oct-Nov)".
  • Map flies to Punjab showing 400+ green dots.
  • Presenter toggles filter: "Hide Agricultural Noise".
  • System instantly de-emphasizes seasonal farm burns, leaving 3 hidden industrial brick kilns standing out.

[ STEP 5: ACTION & CLOSURE (2m 15s - 3m 00s) ]
  • Presenter clicks a non-compliant brick kiln ➔ clicks "Generate Legal Memo".
  • Instant modal renders official PDF citing CPCB Zig-Zag Technology Mandate with pre-filled coordinates.
  • Presenter shows `/citizen` view on phone: plays 10-second Hindi voice note.
  • Presenter taps "Inspector Resolved" ➔ Intervention Ledger logs 1.4-hour response time.
```

---

## 8. Anti-Slop & Scientific Integrity Safeguards

To ensure absolute credibility before senior NTRO and ISRO/academic judges:

1. **Zero Hallucinated Numbers:** Every single metric, percentage, distance in kilometers, and FRP megawatt value is computed via deterministic Python math before being served to the UI. The LLM only writes explanatory English sentences.
2. **No Placeholder Maps:** Real vector tiles and real Sentinel-2 / FIRMS coordinate overlays are rendered.
3. **Offline Demo Insurance:** If the internet connection drops during the hackathon presentation, the SWR layer transparently falls back to pre-bundled, high-fidelity static JSON outputs in `public/data/` so the map, 3D animations, and modal popups never fail.

---

*(This specification represents the complete, production-ready frontend design system for ThermalEye, fully compatible with the backend implementation plan in `implementation_plan.md`.)*
