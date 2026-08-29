'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';
import DeckGL from '@deck.gl/react';
import { ColumnLayer, ScatterplotLayer, TextLayer, PathLayer } from '@deck.gl/layers';
import { H3HexagonLayer } from '@deck.gl/geo-layers';
import Map from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

import { ThermalCluster, RegionId } from '@/lib/types';
import { REGIONS } from '@/lib/constants';
import { getCategoryRgb, getFrpColorScale, getPriorityColor, getCategoryColor } from '@/lib/colors';

const CARTO_DARK_BASEMAP = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

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
}

export default function ThermalDeckMap({
  region,
  clusters,
  selectedClusterId,
  onSelectCluster,
  is3dExtruded = true,
  showWindVectors = true,
}: Props) {
  const regionMeta = REGIONS[region] || REGIONS.barmer;

  const [viewState, setViewState] = useState({
    longitude: regionMeta.lon,
    latitude: regionMeta.lat,
    zoom: regionMeta.zoom,
    pitch: regionMeta.pitch,
    bearing: regionMeta.bearing,
  });

  // Re-centre when region changes
  useEffect(() => {
    const meta = REGIONS[region] || REGIONS.barmer;
    setViewState({
      longitude: meta.lon,
      latitude: meta.lat,
      zoom: meta.zoom,
      pitch: is3dExtruded ? meta.pitch : 0,
      bearing: meta.bearing,
    });
  }, [region, is3dExtruded]);

  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);

  // Generate synthetic wind streamlines around region center
  const windStreamlines = useMemo(() => {
    if (!showWindVectors) return [];
    const lines = [];
    const baseLat = regionMeta.lat;
    const baseLon = regionMeta.lon;
    // South-Westerly wind field
    for (let i = -6; i <= 6; i++) {
      for (let j = -6; j <= 6; j++) {
        const startLat = baseLat + i * 0.15;
        const startLon = baseLon + j * 0.15;
        const endLat = startLat + 0.08;
        const endLon = startLon + 0.12;
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

  // Deck.gl Layers
  const layers = useMemo(() => {
    return [
      // 1. Wind Vector Streamlines
      new PathLayer({
        id: 'wind-vector-layer',
        data: windStreamlines,
        getPath: (d: any) => d.path,
        getColor: [122, 156, 224, 60],
        getWidth: 1.5,
        widthUnits: 'pixels',
        pickable: false,
        visible: showWindVectors,
      }),

      // 2. Extruded 3D Thermal Columns (Height proportional to FRP Megawatts)
      new ColumnLayer({
        id: 'thermal-columns-layer',
        data: clusters,
        diskResolution: 12,
        radius: 400,
        extruded: is3dExtruded,
        elevationScale: is3dExtruded ? 80 : 0,
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getElevation: (d: ThermalCluster) => Math.max(20, d.median_frp || 10),
        getFillColor: (d: ThermalCluster) => {
          const rgb = getCategoryRgb(d.classification);
          const isSelected = d.cluster_id === selectedClusterId;
          return [rgb[0], rgb[1], rgb[2], isSelected ? 255 : 200];
        },
        getLineColor: [255, 255, 255, 120],
        lineWidthMinPixels: 1,
        pickable: true,
        autoHighlight: true,
        highlightColor: [255, 255, 255, 80],
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

      // 3. Hotspot Glowing Beacon Rings (Pulsing around high FRP sources)
      new ScatterplotLayer({
        id: 'thermal-beacons-layer',
        data: clusters,
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getRadius: (d: ThermalCluster) => (d.priority_tier === 'P1' ? 1200 : 700),
        getFillColor: (d: ThermalCluster) => {
          const rgb = getCategoryRgb(d.classification);
          return [rgb[0], rgb[1], rgb[2], 40];
        },
        getLineColor: (d: ThermalCluster) => {
          const rgb = getCategoryRgb(d.classification);
          return [rgb[0], rgb[1], rgb[2], 220];
        },
        stroked: true,
        filled: true,
        lineWidthMinPixels: 2,
        pickable: false,
      }),

      // 4. Cluster ID & FRP Badges
      new TextLayer({
        id: 'thermal-labels-layer',
        data: clusters,
        getPosition: (d: ThermalCluster) => [d.centroid_lon, d.centroid_lat],
        getText: (d: ThermalCluster) => `${d.cluster_id} · ${Math.round(d.median_frp)}MW`,
        getSize: 12,
        getColor: [255, 255, 255, 240],
        getAngle: 0,
        getTextAnchor: 'start',
        getAlignmentBaseline: 'center',
        pixelOffset: [16, -16],
        fontFamily: 'var(--font-mono, monospace)',
        fontWeight: 'bold',
        outlineWidth: 2,
        outlineColor: [11, 12, 14, 255],
        pickable: false,
      }),
    ];
  }, [clusters, selectedClusterId, is3dExtruded, showWindVectors, windStreamlines, onSelectCluster]);

  return (
    <div className="relative w-full h-full bg-[#0b0c0e] overflow-hidden select-none">
      <DeckGL
        viewState={viewState}
        onViewStateChange={(e: any) => setViewState(e.viewState)}
        controller={{ doubleClickZoom: false, dragRotate: true }}
        layers={layers}
        getCursor={({ isHovering }) => (isHovering ? 'pointer' : 'crosshair')}
      >
        <Map mapStyle={CARTO_DARK_BASEMAP} reuseMaps />
      </DeckGL>

      {/* Interactive Floating Hover Tooltip */}
      {tooltip && (
        <div
          className="absolute pointer-events-none z-50 px-3 py-2 bg-[#111316]/95 border border-white/20 rounded-md shadow-2xl backdrop-blur-md text-white text-xs font-mono"
          style={{
            left: `${tooltip.x + 15}px`,
            top: `${tooltip.y + 15}px`,
            minWidth: '220px',
          }}
        >
          <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-1.5 mb-1.5">
            <span className="font-bold text-[#e7e9ec]">{tooltip.cluster.cluster_id}</span>
            <span
              className="px-1.5 py-0.5 rounded text-[10px] font-bold"
              style={{
                backgroundColor: `${getPriorityColor(tooltip.cluster.priority_tier)}25`,
                color: getPriorityColor(tooltip.cluster.priority_tier),
                border: `1px solid ${getPriorityColor(tooltip.cluster.priority_tier)}50`,
              }}
            >
              {tooltip.cluster.priority_tier}
            </span>
          </div>

          <div className="space-y-1 text-[#a0a6ae]">
            <div className="flex justify-between">
              <span>Classification:</span>
              <span
                className="font-semibold"
                style={{ color: getCategoryColor(tooltip.cluster.classification) }}
              >
                {tooltip.cluster.classification.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Radiative Power:</span>
              <span className="font-bold text-[#e7e9ec]">{tooltip.cluster.median_frp.toFixed(1)} MW</span>
            </div>
            {tooltip.cluster.vnf_temp_k && (
              <div className="flex justify-between">
                <span>Combustion Temp:</span>
                <span className="font-bold text-[#f59e0b]">{Math.round(tooltip.cluster.vnf_temp_k)} K</span>
              </div>
            )}
            <div className="flex justify-between">
              <span>Confidence:</span>
              <span className="text-[#5ea88a]">{(tooltip.cluster.confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span>Duration:</span>
              <span>{Math.round(tooltip.cluster.duration_hours)} hrs</span>
            </div>
          </div>
          <div className="mt-2 text-[10px] text-[#6d737b] italic border-t border-white/10 pt-1">
            Click to inspect 4-tab case file
          </div>
        </div>
      )}
    </div>
  );
}
