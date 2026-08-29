/**
 * ThermalEye — Client API Gateway with Resilient Offline Fallbacks.
 */
import {
  ThermalCluster,
  ExecutiveSummaryStats,
  SentinelSpyglassData,
  LedgerEntry,
  InspectorFeedbackSubmission,
  CitizenReportSubmission,
} from './types';
import { REGIONS } from './constants';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// ── Fallback Offline Mock Data for Demo Insurance ─────────────────────────────
const FALLBACK_CLUSTERS: Record<string, ThermalCluster[]> = {
  barmer: [
    {
      cluster_id: 'CLU-8941',
      centroid_lat: 26.5612,
      centroid_lon: 73.834,
      centroid_cell: '883d16d4d5fffff',
      detections_count: 114,
      day_detections: 58,
      night_detections: 56,
      diurnal_ratio: 0.49,
      first_seen: '2026-07-28T02:00:00Z',
      last_seen: '2026-08-28T14:00:00Z',
      duration_hours: 744.0,
      active_days: 30,
      persistence_score: 1.0,
      median_frp: 42.8,
      mean_frp: 43.1,
      max_frp: 49.5,
      cov_frp: 0.07,
      vnf_temp_k: 1845.0,
      dist_industrial_km: 0.8,
      dist_petroleum_km: 0.25,
      dist_kiln_km: 35.0,
      dist_mining_km: 42.0,
      dist_farmland_km: 12.0,
      dist_forest_km: 55.0,
      dist_vulnerable_km: 4.8,
      closest_osm_name: 'Mangala Processing Terminal (MPT)',
      closest_osm_tag: 'landuse=industrial;operator=Vedanta Cairn',
      closest_osm_kind: 'industrial',
      temporal_urgency: 'chronic',
      district_id: 'D-RAJ-BAR',
      district_name: 'Barmer',
      state: 'Rajasthan',
      region: 'barmer',
      classification: 'gas_flare',
      confidence: 0.99,
      decision_path: 'Deterministic Rule Match: VNF Planck combustion temperature 1845K matches atmospheric gas flare (>1200K standard).',
      probabilities: {
        gas_flare: 0.99,
        industrial_fire: 0.005,
        brick_kiln: 0.002,
        agricultural_burn: 0.001,
        mining: 0.001,
        wildfire: 0.0005,
        sun_glint: 0.0005,
      },
      grounded_briefing: 'Cluster CLU-8941 at Mangala Oil Field operates as a continuous, engineered gas flare (1845 K combustion temperature, 42.8 MW median FRP) with steady 24/7 flaring.',
      evidence_chain: {
        temporal: 'Active across 30 of 30 days (100.0% coverage). Diurnal ratio: 0.49 (Day: 58, Night: 56).',
        thermal: 'Median FRP: 42.8 MW (CoV: 0.07). VIIRS Nightfire Planck combustion temp: 1845 K.',
        spatial: 'Located in Barmer district. 0.25 km from Mangala Wellpad #4 petroleum infrastructure.',
        contextual: 'Jurisdiction: Directorate General of Hydrocarbons (DGH) & MoPNG Flaring Compliance Cell.',
      },
      alternative_hypotheses_rejected: [
        { hypothesis: 'industrial_fire', reason: 'Duration of 744h exceeds acute explosion limit (<48h) by 15.5x.' },
        { hypothesis: 'wildfire', reason: 'Zero spatial growth rate (0.00 km²/day); stationary engineered stack.' },
        { hypothesis: 'agricultural_burn', reason: 'Equal day and night combustion (Diurnal ratio 0.49 rules out daytime stubble clearance).' },
      ],
      regulatory_recommendation: 'MONITOR — Flare complies with routine flaring caps under Vedanta Cairn PML license. Review Flare Gas Recovery system efficiency.',
      eps_score: 52.4,
      priority_tier: 'P3',
      priority_label: 'MODERATE',
      sla_target: 'Review < 7 Days',
      action_directive: 'Routine Environmental Compliance Audit',
      memo_pdf_url: '/outputs/barmer/memos/MEMO_CLU-8941.pdf',
      voice_note_hi_url: '/outputs/barmer/audio/ADVISORY_CLU-8941_hi.mp3',
      voice_note_en_url: '/outputs/barmer/audio/ADVISORY_CLU-8941_en.mp3',
    },
    {
      cluster_id: 'CLU-2014',
      centroid_lat: 26.042,
      centroid_lon: 71.321,
      centroid_cell: '883d16d4d1fffff',
      detections_count: 82,
      day_detections: 42,
      night_detections: 40,
      diurnal_ratio: 0.48,
      first_seen: '2026-07-28T02:00:00Z',
      last_seen: '2026-08-28T14:00:00Z',
      duration_hours: 744.0,
      active_days: 28,
      persistence_score: 0.93,
      median_frp: 28.5,
      mean_frp: 28.9,
      max_frp: 34.2,
      cov_frp: 0.08,
      vnf_temp_k: 1690.0,
      dist_industrial_km: 1.2,
      dist_petroleum_km: 0.4,
      dist_kiln_km: 40.0,
      dist_mining_km: 18.0,
      dist_farmland_km: 8.0,
      dist_forest_km: 60.0,
      dist_vulnerable_km: 3.5,
      closest_osm_name: 'Bhagyam Wellpad A',
      closest_osm_tag: 'man_made=petroleum_well',
      closest_osm_kind: 'petroleum_well',
      temporal_urgency: 'chronic',
      district_id: 'D-RAJ-BAR',
      district_name: 'Barmer',
      state: 'Rajasthan',
      region: 'barmer',
      classification: 'gas_flare',
      confidence: 0.98,
      decision_path: 'Deterministic Rule Match: VNF Planck combustion temperature 1690K matches petroleum gas flare.',
      probabilities: {
        gas_flare: 0.98,
        industrial_fire: 0.01,
        brick_kiln: 0.003,
        agricultural_burn: 0.002,
        mining: 0.002,
        wildfire: 0.001,
        sun_glint: 0.002,
      },
      grounded_briefing: 'Cluster CLU-2014 at Bhagyam Wellpad A shows continuous flare combustion with median 28.5 MW power at 1690 K.',
      evidence_chain: {
        temporal: 'Active across 28 of 30 days (93.3% coverage). Diurnal ratio: 0.48.',
        thermal: 'Median FRP: 28.5 MW (CoV: 0.08). VIIRS Nightfire Temp: 1690 K.',
        spatial: 'Located 0.4 km from Bhagyam Wellpad A.',
        contextual: 'Jurisdiction: Rajasthan State Pollution Control Board & PNGRB.',
      },
      alternative_hypotheses_rejected: [
        { hypothesis: 'industrial_fire', reason: 'Sustained 744-hour duration rules out acute uncontained fire.' },
      ],
      regulatory_recommendation: 'MONITOR — Standard field flaring.',
      eps_score: 48.0,
      priority_tier: 'P3',
      priority_label: 'MODERATE',
      sla_target: 'Review < 7 Days',
      action_directive: 'Routine Environmental Audit',
      memo_pdf_url: '/outputs/barmer/memos/MEMO_CLU-2014.pdf',
      voice_note_hi_url: '/outputs/barmer/audio/ADVISORY_CLU-2014_hi.mp3',
      voice_note_en_url: '/outputs/barmer/audio/ADVISORY_CLU-2014_en.mp3',
    },
  ],
  punjab: [
    {
      cluster_id: 'CLU-4401',
      centroid_lat: 30.214,
      centroid_lon: 74.941,
      centroid_cell: '883d16d4c1fffff',
      detections_count: 64,
      day_detections: 54,
      night_detections: 10,
      diurnal_ratio: 0.16,
      first_seen: '2026-08-01T04:00:00Z',
      last_seen: '2026-08-28T10:00:00Z',
      duration_hours: 650.0,
      active_days: 22,
      persistence_score: 0.73,
      median_frp: 18.5,
      mean_frp: 19.2,
      max_frp: 26.0,
      cov_frp: 0.22,
      vnf_temp_k: 950.0,
      dist_industrial_km: 12.0,
      dist_petroleum_km: 45.0,
      dist_kiln_km: 0.2,
      dist_mining_km: 60.0,
      dist_farmland_km: 0.5,
      dist_forest_km: 25.0,
      dist_vulnerable_km: 1.1,
      closest_osm_name: 'Bathinda Brick Kiln Cluster #14',
      closest_osm_tag: 'man_made=kiln;technology=FCK',
      closest_osm_kind: 'brick_kiln',
      temporal_urgency: 'chronic',
      district_id: 'D-PUN-BAT',
      district_name: 'Bathinda',
      state: 'Punjab',
      region: 'punjab',
      classification: 'brick_kiln',
      confidence: 0.94,
      decision_path: 'Deterministic Rule Match: Cyclic diurnal firing cycle 0.2km from registered Fixed Chimney Kiln.',
      probabilities: {
        brick_kiln: 0.94,
        agricultural_burn: 0.03,
        industrial_fire: 0.01,
        gas_flare: 0.005,
        mining: 0.005,
        wildfire: 0.005,
        sun_glint: 0.005,
      },
      grounded_briefing: 'Cluster CLU-4401 in Bathinda exhibits cyclic brick baking emissions adjacent to registered kiln #14 with 18.5 MW median FRP.',
      evidence_chain: {
        temporal: 'Active across 22 days. Diurnal ratio: 0.16 (Daytime firing concentration).',
        thermal: 'Median FRP: 18.5 MW (CoV: 0.22). Combustion temp: ~950 K.',
        spatial: 'Located 0.2 km from mapped brick kiln in Bathinda district.',
        contextual: 'Jurisdiction: Punjab Pollution Control Board (PPCB).',
      },
      alternative_hypotheses_rejected: [
        { hypothesis: 'gas_flare', reason: 'Combustion temp <1000K and diurnal firing cycle rule out continuous gas flaring.' },
      ],
      regulatory_recommendation: 'COMPLIANCE AUDIT — Verify CPCB Zig-Zag conversion compliance and emission stack filters.',
      eps_score: 68.5,
      priority_tier: 'P2',
      priority_label: 'HIGH',
      sla_target: 'Site Audit < 24 Hours',
      action_directive: 'Dispatch District Environmental Squad for Zig-Zag Verification',
      memo_pdf_url: '/outputs/punjab/memos/MEMO_CLU-4401.pdf',
      voice_note_hi_url: '/outputs/punjab/audio/ADVISORY_CLU-4401_hi.mp3',
      voice_note_en_url: '/outputs/punjab/audio/ADVISORY_CLU-4401_en.mp3',
    },
  ],
};

export async function fetchClusters(region: string = 'barmer'): Promise<ThermalCluster[]> {
  try {
    const res = await fetch(`${API_BASE}/clusters?region=${region}`, {
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) return data;
    }
  } catch (e) {
    console.warn(`[api] Live fetch failed for /clusters?region=${region}; using demo insurance bundle.`, e);
  }
  return FALLBACK_CLUSTERS[region] || FALLBACK_CLUSTERS.barmer;
}

export async function fetchClustersSummary(region: string = 'barmer'): Promise<ExecutiveSummaryStats> {
  try {
    const res = await fetch(`${API_BASE}/clusters/stats/summary?region=${region}`, { cache: 'no-store' });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn(`[api] Live fetch failed for summary; computing from fallback.`);
  }
  const clusters = FALLBACK_CLUSTERS[region] || FALLBACK_CLUSTERS.barmer;
  const totalMw = clusters.reduce((acc, c) => acc + (c.median_frp || 0), 0);
  return {
    region,
    region_name: REGIONS[region as keyof typeof REGIONS]?.name || region.toUpperCase(),
    total_clusters: clusters.length,
    total_radiative_power_mw: Math.round(totalMw * 10) / 10,
    critical_p1_count: clusters.filter((c) => c.priority_tier === 'P1').length,
    category_distribution: clusters.reduce((acc: Record<string, number>, c) => {
      acc[c.classification] = (acc[c.classification] || 0) + 1;
      return acc;
    }, {}),
    priority_distribution: clusters.reduce((acc: Record<string, number>, c) => {
      acc[c.priority_tier] = (acc[c.priority_tier] || 0) + 1;
      return acc;
    }, {}),
    districts_affected: Array.from(new Set(clusters.map((c) => c.district_name))),
    available_regions: Object.keys(REGIONS),
  };
}

export async function fetchClusterDetail(clusterId: string, region: string = 'barmer'): Promise<ThermalCluster | null> {
  try {
    const res = await fetch(`${API_BASE}/clusters/${clusterId}?region=${region}`, { cache: 'no-store' });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn(`[api] Live fetch failed for cluster detail ${clusterId}.`);
  }
  const clusters = FALLBACK_CLUSTERS[region] || FALLBACK_CLUSTERS.barmer;
  return clusters.find((c) => c.cluster_id.toUpperCase() === clusterId.toUpperCase()) || clusters[0] || null;
}

export async function fetchSentinelSpyglass(clusterId: string, region: string = 'barmer'): Promise<SentinelSpyglassData> {
  try {
    const res = await fetch(`${API_BASE}/sentinel/tiles/${clusterId}?region=${region}`, { cache: 'no-store' });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn(`[api] Live fetch failed for sentinel spyglass.`);
  }
  return {
    cluster_id: clusterId,
    classification: 'gas_flare',
    coordinates: { lat: 26.5612, lon: 73.834 },
    spyglass_metadata: {
      lat: 26.5612,
      lon: 73.834,
      cloud_coverage_pct: 1.8,
      acquisition_date: '2025-11-12',
      true_color_url: 'https://tiles.maps.eox.at/wms?service=wms&request=getmap&version=1.1.1&layers=s2cloudless-2024&styles=&format=image/jpeg&transparent=false&srs=EPSG:4326&width=512&height=512&bbox=73.819,26.546,73.849,26.576',
      swir_thermal_url: 'https://tiles.maps.eox.at/wms?service=wms&request=getmap&version=1.1.1&layers=sentinel2-swir&styles=&format=image/png&transparent=true&srs=EPSG:4326&width=512&height=512&bbox=73.819,26.546,73.849,26.576',
      resolution_m: 10.0,
      satellite: 'Sentinel-2B MSI',
    },
    verification_status: 'FACILITY_VERIFIED',
  };
}

export async function submitInspectorFeedback(payload: InspectorFeedbackSubmission): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn(`[api] Post feedback error`, e);
  }
  return { status: 'SUCCESS', message: 'Feedback logged (demo mode)' };
}

export async function submitCitizenReport(payload: CitizenReportSubmission): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/citizen/report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (res.ok) return await res.json();
  } catch (e) {
    console.warn(`[api] Post citizen report error`, e);
  }
  return { status: 'SUCCESS', message: 'Citizen report logged (demo mode)' };
}
