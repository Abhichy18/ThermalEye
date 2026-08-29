/**
 * ThermalEye — Core TypeScript Domain Models & API Types.
 */

export type ThermalCategory =
  | 'gas_flare'
  | 'industrial_fire'
  | 'brick_kiln'
  | 'agricultural_burn'
  | 'mining'
  | 'wildfire'
  | 'sun_glint';

export type PriorityTier = 'P1' | 'P2' | 'P3' | 'P4';

export type RegionId = 'barmer' | 'punjab' | 'delhi' | 'hazira' | 'jharia' | 'india';

export interface RegionMetadata {
  id: RegionId;
  name: string;
  state: string;
  lat: number;
  lon: number;
  zoom: number;
  pitch: number;
  bearing: number;
  description: string;
  primaryClasses: ThermalCategory[];
}

export interface EvidenceChain {
  temporal: string;
  thermal: string;
  spatial: string;
  contextual: string;
}

export interface RejectedHypothesis {
  hypothesis: string;
  reason: string;
}

export interface JurisdictionDispatch {
  routed: boolean;
  cluster_id: string;
  priority: PriorityTier;
  classification: string;
  target_agency: string;
  legal_jurisdiction: string;
  recipient_role: string;
  action_channel: string;
  escalation_sla_hours: number;
  coordinates: { lat: number; lon: number };
  gps_pin_url: string;
  dispatch_message: string;
}

export interface LedgerEntry {
  ledger_id: string;
  cluster_id: string;
  classification: string;
  district: string;
  priority: PriorityTier;
  eps_score: number;
  status: 'DISPATCHED' | 'INVESTIGATING' | 'RESOLVED' | 'CLOSED';
  timestamps: {
    satellite_detected_t0: string;
    alert_dispatched_t1: string;
    inspector_actioned_t2?: string;
  };
  response_stopwatch_mins: number;
  counterfactual_avoided_co2e_tonnes: number;
  assigned_inspector: string;
  audit_notes: string;
}

export interface ThermalCluster {
  cluster_id: string;
  centroid_lat: number;
  centroid_lon: number;
  centroid_cell: string;
  detections_count: number;
  day_detections: number;
  night_detections: number;
  diurnal_ratio: number;
  first_seen: string;
  last_seen: string;
  duration_hours: number;
  active_days: number;
  persistence_score: number;
  median_frp: number;
  mean_frp: number;
  max_frp: number;
  cov_frp: number;
  vnf_temp_k: number | null;
  dist_industrial_km: number;
  dist_petroleum_km: number;
  dist_kiln_km: number;
  dist_mining_km: number;
  dist_farmland_km: number;
  dist_forest_km: number;
  dist_vulnerable_km: number;
  closest_osm_name: string;
  closest_osm_tag: string;
  closest_osm_kind: string;
  temporal_urgency: 'acute' | 'emerging' | 'chronic';
  district_id: string;
  district_name: string;
  state: string;
  region: RegionId;
  classification: ThermalCategory;
  confidence: number;
  decision_path: string;
  probabilities: Record<ThermalCategory, number>;
  grounded_briefing: string;
  evidence_chain: EvidenceChain;
  alternative_hypotheses_rejected: RejectedHypothesis[];
  regulatory_recommendation: string;
  eps_score: number;
  priority_tier: PriorityTier;
  priority_label: string;
  sla_target: string;
  action_directive: string;
  eps_breakdown?: {
    thermal_severity: number;
    temporal_urgency: number;
    proximity_risk: number;
    compliance_gap: number;
    citizen_corroboration: number;
  };
  memo_pdf_url: string | null;
  voice_note_hi_url: string | null;
  voice_note_en_url: string | null;
  jurisdiction_dispatch?: JurisdictionDispatch;
  ledger_entry?: LedgerEntry;
}

export interface ExecutiveSummaryStats {
  region: string;
  region_name: string;
  total_clusters: number;
  total_radiative_power_mw: number;
  critical_p1_count: number;
  category_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
  districts_affected: string[];
  available_regions: string[];
}

export interface SentinelSpyglassData {
  cluster_id: string;
  classification: string;
  coordinates: { lat: number; lon: number };
  spyglass_metadata: {
    lat: number;
    lon: number;
    cloud_coverage_pct: number;
    acquisition_date: string;
    true_color_url: string;
    swir_thermal_url: string;
    resolution_m: number;
    satellite: string;
  };
  verification_status: string;
}

export interface InspectorFeedbackSubmission {
  cluster_id: string;
  confirmed_category: ThermalCategory;
  original_category: string;
  inspector_name: string;
  badge_number: string;
  field_notes?: string;
  photo_url?: string;
  region?: string;
}

export interface CitizenReportSubmission {
  lat: number;
  lon: number;
  description: string;
  category_reported: string;
  photo_url?: string;
  reporter_name?: string;
  region?: string;
}

export interface PipelineProgressEvent {
  timestamp: string;
  region: string;
  stage: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  message: string;
  progress_percent: number;
  total_clusters?: number;
  critical_p1?: number;
}
