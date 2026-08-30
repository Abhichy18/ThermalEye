'use client';

import React, { useState, useMemo, useEffect, useRef } from 'react';
import DeckGL from '@deck.gl/react';
import { ColumnLayer, ScatterplotLayer, TextLayer, PathLayer } from '@deck.gl/layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import { FlyToInterpolator } from '@deck.gl/core';
import Map from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

import { ThermalCluster, RegionId } from '@/lib/types';
import { REGIONS } from '@/lib/constants';
import { getCategoryRgb, getPriorityColor, getCategoryColor } from '@/lib/colors';

// ─── Google Earth & High-Resolution Basemap Styles ──────────────────────────
export type BasemapMode = 'google-hybrid' | 'google-satellite' | 'esri-satellite' | 'carto-dark';

const GOOGLE_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || '';
const GOOGLE_KEY_PARAM = GOOGLE_KEY ? `&key=${GOOGLE_KEY}` : '';

const BASEMAP_STYLES: Record<BasemapMode, any> = {
  'google-hybrid': {
    version: 8,
    sources: {
      'google-hybrid': {
        type: 'raster',
        tiles: [`https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}${GOOGLE_KEY_PARAM}`],
        tileSize: 256,
        attribution: '© Google Earth & Google Maps',
        maxzoom: 22,
      },
    },
    layers: [
      {
        id: 'google-hybrid-layer',
        type: 'raster',
        source: 'google-hybrid',
        minzoom: 0,
        maxzoom: 22,
      },
    ],
  },
  'google-satellite': {
    version: 8,
    sources: {
      'google-satellite': {
        type: 'raster',
        tiles: [`https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}${GOOGLE_KEY_PARAM}`],
        tileSize: 256,
        attribution: '© Google Earth',
        maxzoom: 22,
      },
    },
    layers: [
      {
        id: 'google-satellite-layer',
        type: 'raster',
        source: 'google-satellite',
        minzoom: 0,
        maxzoom: 22,
      },
    ],
  },
  'esri-satellite': {
    version: 8,
    sources: {
      'esri-satellite': {
        type: 'raster',
        tiles: [
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        ],
        tileSize: 256,
        attribution: '© Esri, Maxar, Earthstar Geographics',
        maxzoom: 19,
      },
    },
    layers: [
      {
        id: 'esri-satellite-layer',
        type: 'raster',
        source: 'esri-satellite',
        minzoom: 0,
        maxzoom: 19,
      },
    ],
  },
  'carto-dark': 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
};

interface TooltipInfo {
  x: number;
  y: number;
  cluster: ThermalCluster;
}

interface Props {
  region: RegionId;
  clusters: ThermalCluster[];
  selectedClusterId: string | null;
  onSelectCluster: (cluster: ThermalCluster | null) => void;
  is3dExtruded?: boolean;
  showWindVectors?: boolean;
  basemapMode?: BasemapMode;
  onBasemapChange?: (mode: BasemapMode) => void;
}

export default function ThermalDeckMap({
  region,
  clusters,
  selectedClusterId,
  onSelectCluster,
  is3dExtruded = true,
  showWindVectors = true,
  basemapMode = 'google-hybrid',
  onBasemapChange,
}: Props) {
  const regionMeta = REGIONS[region] || REGIONS.barmer;

  const [activeBasemap, setActiveBasemap] = useState<BasemapMode>(basemapMode);
  const [showHexGrid, setShowHexGrid] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [pulseTick, setPulseTick] = useState<number>(0);
  const [isOrbitalTransitioning, setIsOrbitalTransitioning] = useState<boolean>(false);

  const prevRegionRef = useRef<RegionId>(region);

  useEffect(() => {
    if (basemapMode) setActiveBasemap(basemapMode);
  }, [basemapMode]);

  const handleBasemapSelect = (mode: BasemapMode) => {
    setActiveBasemap(mode);
    if (onBasemapChange) onBasemapChange(mode);
  };

  const [viewState, setViewState] = useState({
    longitude: regionMeta.lon,
    latitude: regionMeta.lat,
    zoom: regionMeta.zoom,
    pitch: is3dExtruded ? 55 : 0,
    bearing: regionMeta.bearing || 0,
  });

  // ─── Cinematic Earth Orbit-to-Ground Fly-To Transition ────────────────────
  const triggerCinematicFlyTo = (targetRegion: RegionId) => {
    const meta = REGIONS[targetRegion] || REGIONS.barmer;
    setIsOrbitalTransitioning(true);

    setViewState({
      longitude: meta.lon,
      latitude: meta.lat,
      zoom: meta.zoom,
      pitch: is3dExtruded ? 55 : 0,
      bearing: meta.bearing || 15,
      transitionDuration: 2800, // 2.8 seconds cinematic orbital flight
      transitionInterpolator: new FlyToInterpolator({
        speed: 1.0,
        curve: 2.0, // High arc: pulls high into space orbit over India and swoops down!
      }),
    } as any);

    setTimeout(() => {
      setIsOrbitalTransitioning(false);
    }, 2800);
  };

  // Trigger cinematic orbit zoom whenever sector changes
  useEffect(() => {
    if (prevRegionRef.current !== region) {
      prevRegionRef.current = region;
      triggerCinematicFlyTo(region);
    }
  }, [region, is3dExtruded]);

  // If a specific cluster is selected in the sidebar, smoothly zoom to it
  useEffect(() => {
    if (!selectedClusterId) return;
    const target = clusters.find((c) => c.cluster_id === selectedClusterId);
    if (target) {
      setViewState((prev) => ({
        ...prev,
        longitude: target.centroid_lon,
        latitude: target.centroid_lat,
        zoom: Math.max(prev.zoom, 12.5),
        pitch: 58,
        transitionDuration: 1200,
        transitionInterpolator: new FlyToInterpolator({ speed: 1.5, curve: 1.2 }),
      } as any));
    }
  }, [selectedClusterId, clusters]);

  // Radar beacon pulsing animation
  useEffect(() => {
    const timer = setInterval(() => {
      setPulseTick((prev) => (prev + 1) % 60);
    }, 100);
    return () => clearInterval(timer);
  }, []);

  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);

  // Generate synthetic wind streamlines around region center
  const windStreamlines = useMemo(() => {
    if (!showWindVectors) return [];
    const lines = [];
    const baseLat = regionMeta.lat;
    const baseLon = regionMeta.lon;
    for (let i = -7; i <= 7; i++) {
      for (let j = -7; j <= 7; j++) {
        const startLat = baseLat + i * 0.14;
        const startLon = baseLon + j * 0.14;
        const endLat = startLat + 0.07 + Math.sin(i + j) * 0.01;
        const endLon = startLon + 0.11 + Math.cos(i) * 0.01;
        lines.push({
          path: [
            [startLon, startLat],
            [endLon, endLat],
          ],
        });
      }
    }
    return lines;
  }, [regionMeta, showWindVectors]);

  const pulseFactor = 1 + 0.3 * Math.sin((pulseTick / 60) * Math.PI * 2);

  // Deck.gl Visual Layers
  const layers = useMemo(() => {
    return [
      // ── Layer 1: Atmospheric Wind Streamlines ───────────────────────────
      new PathLayer({
        id: 'wind-vector-layer',
        data: windStreamlines,
        getPath: (d: any) => d.path,
        getColor: [140, 185, 255, 95],
        getWidth: 2.0,
        widthUnits: 'pixels',
        pickable: false,
        visible: showWindVectors,
      }),

      // ── Layer 2: Uber H3 Footprint Hexagons (Sat Footprint) ─────────────
      new H3HexagonLayer({
        id: 'h3-hex-footprint-layer',
        data: clusters.filter((d) => d.h3_index),
        getHexagon: (d: ThermalCluster) => d.h3_index,
        getFillColor: (d: ThermalCluster) => {
          const rgb = getCategoryRgb(d.classification);
          const isSelected = d.cluster_id === selectedClusterId;
          return [rgb[0], rgb[1], rgb[2], isSelected ? 95 : 40];
        },
        getLineColor: (d: ThermalCluster) => {
          const rgb = getCategoryRgb(d.classification);
          return [rgb[0], rgb[1], rgb[2], d.priority_tier === 'P1' ? 240 : 140];
        },
        lineWidthMinPixels: 2,
        extruded: false,
        stroked: true,
        filled: true,
        pickable: false,
        visible: showHexGrid,
      }),

      // ── Layer 3: Outer Sonar Pulsing Radar Rings (P1/P2 Critical Beacons)
      new ScatterplotLayer({
        id: 'thermal-sonar-pulse-layer',
        data: clusters.filter((d) => d.priority_tier === 'P1' || d.priority_tier === 'P2'),
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getRadius: (d: ThermalCluster) =>
          (d.priority_tier === 'P1' ? 1500 : 950) * pulseFactor,
        getFillColor: [239, 68, 68, 30],
        getLineColor: (d: ThermalCluster) =>
          d.priority_tier === 'P1' ? [239, 68, 68, 255] : [245, 158, 11, 220],
        stroked: true,
        filled: true,
        lineWidthMinPixels: 2.5,
        pickable: false,
      }),

      // ── Layer 4: Glowing Red Thermal Core Hotspots (Actual Fire Dots) ───
      new ScatterplotLayer({
        id: 'thermal-core-hotspots-layer',
        data: clusters,
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getRadius: (d: ThermalCluster) => (d.priority_tier === 'P1' ? 500 : 350),
        getFillColor: (d: ThermalCluster) => {
          const isSelected = d.cluster_id === selectedClusterId;
          if (d.priority_tier === 'P1') return [255, 30, 30, isSelected ? 255 : 240];
          if (d.priority_tier === 'P2') return [255, 130, 0, isSelected ? 255 : 220];
          const rgb = getCategoryRgb(d.classification);
          return [rgb[0], rgb[1], rgb[2], isSelected ? 255 : 210];
        },
        getLineColor: [255, 255, 255, 255],
        stroked: true,
        filled: true,
        lineWidthMinPixels: 2,
        pickable: true,
        autoHighlight: true,
        highlightColor: [255, 255, 255, 140],
        onClick: (info: any) => {
          if (info.object) {
            onSelectCluster(info.object as ThermalCluster);
          }
        },
        onHover: (info: any) => {
          if (info.object) {
            setTooltip({
              x: info.x,
              y: info.y,
              cluster: info.object as ThermalCluster,
            });
          } else {
            setTooltip(null);
          }
        },
      }),

      // ── Layer 5: Extruded 3D Thermal Plume Columns (FRP Megawatts) ───────
      new ColumnLayer({
        id: 'thermal-3d-columns-layer',
        data: clusters,
        diskResolution: 18,
        radius: 280,
        extruded: is3dExtruded,
        elevationScale: is3dExtruded ? 90 : 0,
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getElevation: (d: ThermalCluster) => Math.max(35, d.median_frp || 20),
        getFillColor: (d: ThermalCluster) => {
          const rgb = getCategoryRgb(d.classification);
          const isSelected = d.cluster_id === selectedClusterId;
          return [rgb[0], rgb[1], rgb[2], isSelected ? 255 : 200];
        },
        getLineColor: [255, 255, 255, 180],
        lineWidthMinPixels: 1.5,
        pickable: true,
        autoHighlight: true,
        highlightColor: [255, 255, 255, 120],
        onClick: (info: any) => {
          if (info.object) {
            onSelectCluster(info.object as ThermalCluster);
          }
        },
      }),

      // ── Layer 6: Tactical Billboard Labels & Hotspot IDs ────────────────
      new TextLayer({
        id: 'thermal-billboard-labels-layer',
        data: clusters,
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getText: (d: ThermalCluster) =>
          `${d.cluster_id} · ${Math.round(d.median_frp)}MW ${d.priority_tier === 'P1' ? '🔥' : ''}`,
        getSize: 12,
        getColor: (d: ThermalCluster) =>
          d.priority_tier === 'P1' ? [255, 230, 230, 255] : [255, 255, 255, 245],
        getAngle: 0,
        getTextAnchor: 'start',
        getAlignmentBaseline: 'center',
        pixelOffset: [18, -18],
        fontFamily: 'var(--font-mono, monospace)',
        fontWeight: 'bold',
        outlineWidth: 3.5,
        outlineColor: [8, 10, 14, 255],
        pickable: false,
        visible: showLabels,
      }),
    ];
  }, [
    clusters,
    selectedClusterId,
    is3dExtruded,
    showWindVectors,
    windStreamlines,
    showHexGrid,
    showLabels,
    pulseFactor,
    onSelectCluster,
  ]);

  const mapStyleDefinition = BASEMAP_STYLES[activeBasemap] || BASEMAP_STYLES['google-hybrid'];

  return (
    <div className="relative w-full h-full bg-[#060709] overflow-hidden select-none">
      <DeckGL
        viewState={viewState}
        onViewStateChange={(e: any) => setViewState(e.viewState)}
        controller={{ doubleClickZoom: false, dragRotate: true }}
        layers={layers}
        getCursor={({ isHovering }) => (isHovering ? 'pointer' : 'crosshair')}
      >
        <Map mapStyle={mapStyleDefinition} reuseMaps />
      </DeckGL>

      {/* ── Cinematic Orbital Fly-In HUD Banner ─────────────────────────── */}
      {isOrbitalTransitioning && (
        <div
          style={{
            position: 'absolute',
            top: '24px',
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 60,
            background: 'rgba(10, 14, 22, 0.92)',
            border: '1px solid #3b82f6',
            borderRadius: '10px',
            padding: '10px 20px',
            boxShadow: '0 0 30px rgba(59, 130, 246, 0.5), 0 8px 32px rgba(0,0,0,0.8)',
            backdropFilter: 'blur(16px)',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            color: '#93c5fd',
            letterSpacing: '0.05em',
            animation: 'fadeIn 0.2s ease-out',
          }}
        >
          <span
            style={{
              width: '10px',
              height: '10px',
              borderRadius: '50%',
              backgroundColor: '#3b82f6',
              boxShadow: '0 0 12px #3b82f6',
              animation: 'pulse 1s infinite',
            }}
          />
          <span style={{ fontWeight: 700, color: '#ffffff' }}>
            🛰️ ORBITAL SATELLITE VECTORING → LOCKING ON {regionMeta.name.toUpperCase()}...
          </span>
        </div>
      )}

      {/* ── Top-Right Floating Google Earth & Tactical Switcher ────────────── */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          zIndex: 40,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.7rem',
        }}
      >
        {/* Basemap Switcher Palette */}
        <div
          style={{
            background: 'rgba(10, 12, 16, 0.90)',
            border: '1px solid rgba(255, 255, 255, 0.16)',
            borderRadius: '8px',
            padding: '6px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(14px)',
            display: 'flex',
            gap: '4px',
          }}
        >
          <button
            onClick={() => handleBasemapSelect('google-hybrid')}
            title="Google Earth Satellite Hybrid with landmarks, roads & infrastructure"
            style={{
              padding: '5px 10px',
              borderRadius: '5px',
              background:
                activeBasemap === 'google-hybrid'
                  ? 'linear-gradient(135deg, #1d4ed8, #3b82f6)'
                  : 'rgba(255, 255, 255, 0.06)',
              color: '#ffffff',
              border: activeBasemap === 'google-hybrid' ? '1px solid #93c5fd' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              transition: 'all 0.15s ease',
            }}
          >
            <span>🛰️</span> Google Earth HD
          </button>

          <button
            onClick={() => handleBasemapSelect('google-satellite')}
            title="Google Earth Clean Satellite Imagery"
            style={{
              padding: '5px 10px',
              borderRadius: '5px',
              background:
                activeBasemap === 'google-satellite'
                  ? 'linear-gradient(135deg, #047857, #10b981)'
                  : 'rgba(255, 255, 255, 0.06)',
              color: '#ffffff',
              border:
                activeBasemap === 'google-satellite' ? '1px solid #6ee7b7' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              transition: 'all 0.15s ease',
            }}
          >
            <span>🌍</span> Satellite Clean
          </button>

          <button
            onClick={() => handleBasemapSelect('carto-dark')}
            title="Tactical Dark Matrix Mode"
            style={{
              padding: '5px 10px',
              borderRadius: '5px',
              background:
                activeBasemap === 'carto-dark'
                  ? 'linear-gradient(135deg, #374151, #1f2937)'
                  : 'rgba(255, 255, 255, 0.06)',
              color: '#ffffff',
              border: activeBasemap === 'carto-dark' ? '1px solid #9ca3af' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              transition: 'all 0.15s ease',
            }}
          >
            <span>🌑</span> Tactical Dark
          </button>
        </div>

        {/* Tactical Layer Quick Toggles */}
        <div
          style={{
            background: 'rgba(10, 12, 16, 0.88)',
            border: '1px solid rgba(255, 255, 255, 0.14)',
            borderRadius: '8px',
            padding: '6px 8px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(12px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '6px',
            color: '#a0a6ae',
          }}
        >
          <button
            onClick={() => triggerCinematicFlyTo(region)}
            title="Replay Orbit Space-to-Ground Fly-In Animation"
            style={{
              background: 'linear-gradient(135deg, #7c3aed, #6366f1)',
              color: '#ffffff',
              border: '1px solid #a78bfa',
              padding: '3px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.65rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '3px',
            }}
          >
            <span>🚀</span> Fly-In
          </button>

          <button
            onClick={() => setShowHexGrid((v) => !v)}
            style={{
              background: showHexGrid ? 'rgba(59, 130, 246, 0.25)' : 'transparent',
              color: showHexGrid ? '#60a5fa' : '#6b7280',
              border: `1px solid ${showHexGrid ? 'rgba(59, 130, 246, 0.4)' : 'rgba(255, 255, 255, 0.08)'}`,
              padding: '3px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.65rem',
              fontWeight: 600,
            }}
          >
            H3 Grid
          </button>

          <button
            onClick={() => setShowLabels((v) => !v)}
            style={{
              background: showLabels ? 'rgba(16, 185, 129, 0.25)' : 'transparent',
              color: showLabels ? '#34d399' : '#6b7280',
              border: `1px solid ${showLabels ? 'rgba(16, 185, 129, 0.4)' : 'rgba(255, 255, 255, 0.08)'}`,
              padding: '3px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.65rem',
              fontWeight: 600,
            }}
          >
            Labels
          </button>

          <button
            onClick={() =>
              setViewState((v) => ({
                ...v,
                pitch: v.pitch > 10 ? 0 : 55,
              }))
            }
            style={{
              background: viewState.pitch > 10 ? 'rgba(245, 158, 11, 0.25)' : 'transparent',
              color: viewState.pitch > 10 ? '#fbbf24' : '#6b7280',
              border: `1px solid ${viewState.pitch > 10 ? 'rgba(245, 158, 11, 0.4)' : 'rgba(255, 255, 255, 0.08)'}`,
              padding: '3px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.65rem',
              fontWeight: 600,
            }}
          >
            {viewState.pitch > 10 ? '3D View (55°)' : '2D (0°)'}
          </button>
        </div>
      </div>

      {/* ── Bottom-Left Tactical Live Telemetry Watermark ─────────────────── */}
      <div
        style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          zIndex: 30,
          background: 'rgba(8, 10, 14, 0.88)',
          border: '1px solid rgba(255, 255, 255, 0.14)',
          borderRadius: '8px',
          padding: '8px 12px',
          backdropFilter: 'blur(12px)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.68rem',
          color: '#a0a6ae',
          display: 'flex',
          flexDirection: 'column',
          gap: '3px',
          pointerEvents: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#ef4444',
              boxShadow: '0 0 10px #ef4444',
              animation: 'pulse 1.5s infinite',
            }}
          />
          <span style={{ fontWeight: 700, color: '#f3f4f6', letterSpacing: '0.04em' }}>
            GOOGLE EARTH SATELLITE FEED · {region.toUpperCase()}
          </span>
        </div>
        <div style={{ fontSize: '0.62rem', color: '#9ca3af' }}>
          LIVE TILES · VIIRS 375m · VNF 1200K+ · SENTINEL-2 SWIR · H3 RES-8
        </div>
      </div>

      {/* ── Interactive Floating Tactical Hover Tooltip ──────────────────── */}
      {tooltip && (
        <div
          className="absolute pointer-events-none z-50 px-3.5 py-2.5 bg-[#0b0d11]/95 border border-white/25 rounded-lg shadow-2xl backdrop-blur-xl text-white text-xs font-mono"
          style={{
            left: `${tooltip.x + 16}px`,
            top: `${tooltip.y + 16}px`,
            minWidth: '235px',
            boxShadow: '0 12px 40px rgba(0, 0, 0, 0.85), 0 0 20px rgba(239, 68, 68, 0.25)',
          }}
        >
          <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-1.5 mb-2">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping" />
              <span className="font-bold text-[#f3f4f6] text-sm">{tooltip.cluster.cluster_id}</span>
            </div>
            <span
              className="px-2 py-0.5 rounded text-[10px] font-bold"
              style={{
                backgroundColor: `${getPriorityColor(tooltip.cluster.priority_tier)}25`,
                color: getPriorityColor(tooltip.cluster.priority_tier),
                border: `1px solid ${getPriorityColor(tooltip.cluster.priority_tier)}60`,
              }}
            >
              {tooltip.cluster.priority_tier} PRIORITY
            </span>
          </div>

          <div className="space-y-1.5 text-[#a0a6ae] text-[11px]">
            <div className="flex justify-between items-center">
              <span>Source Type:</span>
              <span
                className="font-bold px-1.5 py-0.5 rounded text-[10px]"
                style={{
                  backgroundColor: `${getCategoryColor(tooltip.cluster.classification)}25`,
                  color: getCategoryColor(tooltip.cluster.classification),
                  border: `1px solid ${getCategoryColor(tooltip.cluster.classification)}50`,
                }}
              >
                {tooltip.cluster.classification.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Fire Radiative Power:</span>
              <span className="font-bold text-[#f97316]">{tooltip.cluster.median_frp.toFixed(1)} MW</span>
            </div>
            {tooltip.cluster.vnf_temp_k && (
              <div className="flex justify-between">
                <span>Combustion Temp:</span>
                <span className="font-bold text-[#fbbf24]">{Math.round(tooltip.cluster.vnf_temp_k)} K</span>
              </div>
            )}
            <div className="flex justify-between">
              <span>Confidence:</span>
              <span className="text-[#34d399] font-bold">
                {(tooltip.cluster.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Coordinates:</span>
              <span className="text-[#9ca3af]">
                {tooltip.cluster.centroid_lat.toFixed(3)}°N, {tooltip.cluster.centroid_lon.toFixed(3)}°E
              </span>
            </div>
          </div>
          <div className="mt-2 text-[9.5px] text-[#9ca3af] italic border-t border-white/10 pt-1 text-center font-sans">
            ⚡ Click hotspot to load full 4-tab intelligence dossier
          </div>
        </div>
      )}
    </div>
  );
}
