'use client';

import React, { useState, useEffect } from 'react';
import { ThermalCluster, SentinelSpyglassData } from '@/lib/types';
import { fetchSentinelSpyglass } from '@/lib/api';

interface Props {
  cluster: ThermalCluster;
}

export default function OpticalSpyglassTab({ cluster }: Props) {
  const [sliderPos, setSliderPos] = useState<number>(50); // percentage (0 - 100)
  const [spyglassData, setSpyglassData] = useState<SentinelSpyglassData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchSentinelSpyglass(cluster.cluster_id, cluster.region).then((data) => {
      if (mounted) {
        setSpyglassData(data);
        setLoading(false);
      }
    });
    return () => {
      mounted = false;
    };
  }, [cluster]);

  const trueColorUrl = spyglassData?.spyglass_metadata.true_color_url || '';
  const swirUrl = spyglassData?.spyglass_metadata.swir_thermal_url || '';

  return (
    <div className="space-y-3 font-mono text-xs text-[#e7e9ec]">
      {/* Header Info */}
      <div className="flex items-center justify-between p-2.5 bg-white/5 border border-white/10 rounded">
        <div>
          <div className="font-bold text-[#7a9ce0] text-[11px]">Sentinel-2 MSI 10-Meter Optical Resolution</div>
          <div className="text-[10px] text-[#a0a6ae]">
            Acquisition: {spyglassData?.spyglass_metadata.acquisition_date || '2025-11-12'} · Cloud: {spyglassData?.spyglass_metadata.cloud_coverage_pct || 1.8}%
          </div>
        </div>
        <span className="px-2 py-0.5 bg-[#5ea88a]/20 border border-[#5ea88a]/50 text-[#5ea88a] text-[10px] font-bold rounded">
          {spyglassData?.verification_status || 'FACILITY_VERIFIED'}
        </span>
      </div>

      {/* Interactive Split-Screen Spyglass Slider */}
      <div className="relative w-full h-[280px] rounded-lg border border-white/20 overflow-hidden bg-black select-none">
        {/* Layer A: Right Image (SWIR Band 12 Infrared Thermal Bloom) */}
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('${swirUrl}')`,
            backgroundColor: '#17191d',
          }}
        >
          {/* Simulated SWIR Heat Bloom Flare representation if image offline */}
          <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-amber-950/40 via-red-950/30 to-black/80">
            <div className="w-16 h-16 rounded-full bg-red-500/30 blur-md border border-amber-400/60 animate-pulse flex items-center justify-center">
              <div className="w-6 h-6 rounded-full bg-amber-300 blur-xs" />
            </div>
            <span className="mt-2 text-[10px] text-amber-300 font-bold bg-black/60 px-2 py-0.5 rounded">
              SWIR 2.2μm Band 12 Heat Bloom
            </span>
          </div>
        </div>

        {/* Layer B: Left Image (True Color RGB 10m Optical) */}
        <div
          className="absolute inset-y-0 left-0 overflow-hidden bg-cover bg-center border-r-2 border-[#7a9ce0]"
          style={{
            width: `${sliderPos}%`,
            backgroundImage: `url('${trueColorUrl}')`,
            backgroundColor: '#111316',
          }}
        >
          {/* Simulated Satellite True Color Optical Texture */}
          <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900/60 to-zinc-950/80">
            <div className="p-2 border border-white/30 rounded bg-black/40 text-[10px] text-white font-mono text-center">
              <div className="font-bold">Ground Target Perimeter</div>
              <div className="text-[9px] text-[#a0a6ae]">({cluster.centroid_lat.toFixed(4)}°N, {cluster.centroid_lon.toFixed(4)}°E)</div>
              <div className="mt-1 text-cyan-400 font-bold">10m Optical Base</div>
            </div>
          </div>
        </div>

        {/* Floating Split Slider Handle */}
        <div
          className="absolute inset-y-0 flex items-center justify-center pointer-events-none"
          style={{ left: `calc(${sliderPos}% - 12px)` }}
        >
          <div className="w-6 h-6 rounded-full bg-[#7a9ce0] text-black font-bold flex items-center justify-center shadow-lg text-[10px]">
            ↔
          </div>
        </div>

        {/* Invisible Range Input for Dragging */}
        <input
          type="range"
          min="0"
          max="100"
          value={sliderPos}
          onChange={(e) => setSliderPos(Number(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
        />

        {/* Labels Overlay */}
        <div className="absolute top-2 left-2 px-2 py-0.5 bg-black/70 border border-white/20 rounded text-[9px] font-bold text-white z-10 pointer-events-none">
          ◀ TRUE COLOR (RGB)
        </div>
        <div className="absolute top-2 right-2 px-2 py-0.5 bg-black/70 border border-amber-500/50 rounded text-[9px] font-bold text-amber-400 z-10 pointer-events-none">
          SWIR INFRARED (BAND 12) ▶
        </div>
      </div>

      <p className="text-[10px] text-[#6d737b] text-center italic">
        Drag the split slider horizontally to compare physical optical infrastructure against thermal bloom.
      </p>
    </div>
  );
}
