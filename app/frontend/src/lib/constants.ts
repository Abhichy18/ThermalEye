/**
 * ThermalEye — Geographic Regions, Default Constants & Static Meta.
 */
import { RegionId, RegionMetadata, ThermalCategory } from './types';

export const REGIONS: Record<RegionId, RegionMetadata> = {
  barmer: {
    id: 'barmer',
    name: 'Barmer Basin (Rajasthan)',
    state: 'Rajasthan',
    lat: 26.35,
    lon: 71.65,
    zoom: 8.5,
    pitch: 45,
    bearing: -15,
    description: "India's largest onshore oil basin — Mangala, Bhagyam, Aishwariya fields with persistent flaring",
    primaryClasses: ['gas_flare', 'mining'],
  },
  punjab: {
    id: 'punjab',
    name: 'Punjab Harvest Belt',
    state: 'Punjab',
    lat: 30.50,
    lon: 75.30,
    zoom: 8.0,
    pitch: 40,
    bearing: 0,
    description: 'Paddy stubble burning epicenter & Indo-Gangetic Plain brick kiln clusters',
    primaryClasses: ['agricultural_burn', 'brick_kiln'],
  },
  delhi: {
    id: 'delhi',
    name: 'Delhi-NCR Industrial',
    state: 'Delhi-NCR',
    lat: 28.65,
    lon: 77.15,
    zoom: 9.8,
    pitch: 50,
    bearing: 20,
    description: 'Bhalswa/Ghazipur landfill fires & industrial manufacturing corridors',
    primaryClasses: ['industrial_fire', 'brick_kiln'],
  },
  hazira: {
    id: 'hazira',
    name: 'Hazira Gas Complex',
    state: 'Gujarat',
    lat: 21.10,
    lon: 72.65,
    zoom: 11.0,
    pitch: 55,
    bearing: -25,
    description: 'Major ONGC / Shell LNG terminal with multi-stack continuous industrial flares',
    primaryClasses: ['gas_flare', 'industrial_fire'],
  },
  jharia: {
    id: 'jharia',
    name: 'Jharia Coalfield',
    state: 'Jharkhand',
    lat: 23.75,
    lon: 86.40,
    zoom: 10.5,
    pitch: 45,
    bearing: 10,
    description: 'Historic underground coal seam fires & opencast mining thermal anomalies',
    primaryClasses: ['mining', 'industrial_fire'],
  },
  india: {
    id: 'india',
    name: 'Pan-India Overview',
    state: 'National',
    lat: 22.50,
    lon: 79.50,
    zoom: 4.8,
    pitch: 20,
    bearing: 0,
    description: 'National overview surveillance across all monitored energy & industrial sectors',
    primaryClasses: ['gas_flare', 'industrial_fire', 'brick_kiln', 'agricultural_burn', 'mining', 'wildfire'],
  },
};

export const DEFAULT_REGION: RegionId = 'barmer';

export const CATEGORY_DESCRIPTIONS: Record<ThermalCategory, { title: string; description: string; rule: string }> = {
  gas_flare: {
    title: 'Industrial Gas Flare',
    description: 'Controlled combustion of associated petroleum gas at oil/gas production wells & refineries.',
    rule: 'Persistence > 60%, Diurnal ratio ~0.50, VNF Temp > 1200K, FRP CoV < 0.15.',
  },
  industrial_fire: {
    title: 'Acute Industrial Fire',
    description: 'Sudden high-intensity thermal spike indicating accidental chemical fire or explosion.',
    rule: 'Duration < 48h, Spike ratio > 2.5, Near industrial polygons, Extreme FRP.',
  },
  brick_kiln: {
    title: 'Brick Kiln (FCK / Zig-Zag)',
    description: 'Seasonal clay brick baking kilns with cyclic diurnal firing profiles.',
    rule: 'Cyclic morning firing, Active Oct–Mar, IGP agricultural belt proximity.',
  },
  agricultural_burn: {
    title: 'Agricultural Stubble Burning',
    description: 'Open-field post-harvest crop residue combustion.',
    rule: 'Strictly daytime only (0 night detections), 1-3 day lifespan, Farmland boundary.',
  },
  mining: {
    title: 'Opencast Mining / Quarry Heat',
    description: 'Thermal anomaly associated with heavy excavation, blasting, or coal seam combustion.',
    rule: 'Adjacent to quarry boundary, Moderate persistent radiative signature.',
  },
  wildfire: {
    title: 'Forest Wildfire',
    description: 'Uncontrolled vegetation fire in natural woodland or forest reserve.',
    rule: 'Inside forest boundary, Non-zero radial spatial expansion rate.',
  },
  sun_glint: {
    title: 'Solar Specular Glint Artifact',
    description: 'Optical false alarm caused by solar reflection on metal industrial roofs at solar noon.',
    rule: 'FRP < 10 MW, Solar noon pass only, Zero nocturnal signature. Suppressed.',
  },
};
