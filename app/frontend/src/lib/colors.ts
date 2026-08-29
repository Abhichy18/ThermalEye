/**
 * ThermalEye — Color System & Visual Palette Tokens.
 *
 * Strict chromatic discipline:
 * - 7 distinct thermal source category colors (meaning-carrying, desaturated)
 * - 4 Priority Tier colors (P1 Critical -> P4 Routine)
 * - Deck.gl RGBA color mapping
 */
import { ThermalCategory, PriorityTier } from './types';

export const CATEGORY_COLORS: Record<ThermalCategory, { hex: string; rgb: [number, number, number]; label: string }> = {
  gas_flare: {
    hex: '#d97706',
    rgb: [217, 119, 6],
    label: 'Gas Flare',
  },
  industrial_fire: {
    hex: '#ef4444',
    rgb: [239, 68, 68],
    label: 'Industrial Fire',
  },
  brick_kiln: {
    hex: '#c2410c',
    rgb: [194, 65, 12],
    label: 'Brick Kiln',
  },
  agricultural_burn: {
    hex: '#eab308',
    rgb: [234, 179, 8],
    label: 'Agricultural Burn',
  },
  mining: {
    hex: '#a8a29e',
    rgb: [168, 162, 158],
    label: 'Mining / Quarry',
  },
  wildfire: {
    hex: '#f97316',
    rgb: [249, 115, 22],
    label: 'Wildfire',
  },
  sun_glint: {
    hex: '#64748b',
    rgb: [100, 116, 139],
    label: 'Sun-Glint Artifact',
  },
};

export const PRIORITY_COLORS: Record<PriorityTier, { hex: string; rgb: [number, number, number]; bgSoft: string; label: string }> = {
  P1: {
    hex: '#dc2626',
    rgb: [220, 38, 38],
    bgSoft: 'rgba(220, 38, 38, 0.15)',
    label: 'P1 CRITICAL',
  },
  P2: {
    hex: '#ea580c',
    rgb: [234, 88, 12],
    bgSoft: 'rgba(234, 88, 12, 0.15)',
    label: 'P2 HIGH',
  },
  P3: {
    hex: '#d97706',
    rgb: [217, 119, 6],
    bgSoft: 'rgba(217, 119, 6, 0.15)',
    label: 'P3 MODERATE',
  },
  P4: {
    hex: '#3b82f6',
    rgb: [59, 130, 246],
    bgSoft: 'rgba(59, 130, 246, 0.15)',
    label: 'P4 ROUTINE',
  },
};

export function getCategoryColor(category: string): string {
  const cat = category.toLowerCase() as ThermalCategory;
  return CATEGORY_COLORS[cat]?.hex || '#94a3b8';
}

export function getCategoryRgb(category: string): [number, number, number] {
  const cat = category.toLowerCase() as ThermalCategory;
  return CATEGORY_COLORS[cat]?.rgb || [148, 163, 184];
}

export function getPriorityColor(priority: string): string {
  const p = priority.toUpperCase() as PriorityTier;
  return PRIORITY_COLORS[p]?.hex || '#94a3b8';
}

export function getPriorityBgSoft(priority: string): string {
  const p = priority.toUpperCase() as PriorityTier;
  return PRIORITY_COLORS[p]?.bgSoft || 'rgba(148, 163, 184, 0.12)';
}

export function getFrpColorScale(frp: number): [number, number, number, number] {
  // Low (<15MW): Yellow-Amber, Med (15-60MW): Orange, High (>100MW): Intense Red-Crimson
  if (frp < 15) {
    return [234, 179, 8, 200];
  } else if (frp < 50) {
    return [249, 115, 22, 220];
  } else if (frp < 120) {
    return [239, 68, 68, 240];
  } else {
    return [220, 38, 38, 255];
  }
}
