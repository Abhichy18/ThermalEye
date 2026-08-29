'use client';

import React from 'react';
import Link from 'next/link';
import { RegionId } from '@/lib/types';
import { REGIONS } from '@/lib/constants';

interface Props {
  selectedRegion: RegionId;
  onSelectRegion: (region: RegionId) => void;
  is3d: boolean;
  onToggle3d: () => void;
  showWind: boolean;
  onToggleWind: () => void;
  totalClustersCount: number;
  criticalP1Count: number;
}

export default function HUDHeader({
  selectedRegion,
  onSelectRegion,
  is3d,
  onToggle3d,
  showWind,
  onToggleWind,
  totalClustersCount,
  criticalP1Count,
}: Props) {
  return (
    <header
      style={{
        width: '100%',
        height: '52px',
        background: 'var(--bg-glass)',
        borderBottom: '1px solid var(--border-default)',
        backdropFilter: 'blur(12px)',
        padding: '0 var(--space-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.75rem',
        color: 'var(--text-primary)',
        zIndex: 30,
        flexShrink: 0,
      }}
    >
      {/* Left: Brand & Problem Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
        <Link
          href="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            textDecoration: 'none',
            color: 'inherit',
          }}
        >
          <span
            style={{
              width: '24px',
              height: '24px',
              borderRadius: 'var(--radius-sm)',
              background: 'linear-gradient(135deg, #d97706, #ef4444)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '12px',
              boxShadow: '0 0 10px rgba(239, 68, 68, 0.4)',
            }}
          >
            🔥
          </span>
          <span
            style={{
              fontWeight: 700,
              fontSize: '0.9rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
            }}
          >
            THERMAL<span style={{ color: 'var(--accent)' }}>EYE</span>
          </span>
        </Link>

        <span
          style={{
            padding: '2px 8px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.65rem',
            color: 'var(--text-tertiary)',
          }}
        >
          SIH26162YELLOW · NTRO
        </span>
      </div>

      {/* Center: Sector Switcher */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <label style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)' }}>SECTOR:</label>
        <select
          value={selectedRegion}
          onChange={(e) => onSelectRegion(e.target.value as RegionId)}
          style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-strong)',
            color: 'var(--accent)',
            fontWeight: 650,
            fontSize: '0.75rem',
            fontFamily: 'var(--font-mono)',
            borderRadius: 'var(--radius-sm)',
            padding: '4px 10px',
            outline: 'none',
            cursor: 'pointer',
          }}
        >
          {Object.entries(REGIONS).map(([id, meta]) => (
            <option key={id} value={id}>
              {meta.name}
            </option>
          ))}
        </select>
      </div>

      {/* Right: Controls & Portal Link */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '3px 8px',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.7rem',
          }}
        >
          <span style={{ color: 'var(--text-tertiary)' }}>Active Sources:</span>
          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{totalClustersCount}</span>
          {criticalP1Count > 0 && (
            <span
              style={{
                marginLeft: '4px',
                padding: '1px 5px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--critical-soft)',
                color: 'var(--critical)',
                border: '1px solid var(--critical-line)',
                fontWeight: 700,
                fontSize: '0.65rem',
              }}
            >
              {criticalP1Count} P1
            </span>
          )}
        </div>

        {/* 3D Extrusion Toggle */}
        <button
          onClick={onToggle3d}
          style={{
            padding: '4px 10px',
            borderRadius: 'var(--radius-sm)',
            border: is3d ? '1px solid var(--accent)' : '1px solid var(--border-subtle)',
            background: is3d ? 'var(--accent-soft)' : 'var(--bg-secondary)',
            color: is3d ? 'var(--accent)' : 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            cursor: 'pointer',
          }}
        >
          {is3d ? '3D Height ON' : '2D Flat'}
        </button>

        {/* Wind Toggle */}
        <button
          onClick={onToggleWind}
          style={{
            padding: '4px 10px',
            borderRadius: 'var(--radius-sm)',
            border: showWind ? '1px solid var(--positive)' : '1px solid var(--border-subtle)',
            background: showWind ? 'var(--positive-soft)' : 'var(--bg-secondary)',
            color: showWind ? 'var(--positive)' : 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            cursor: 'pointer',
          }}
        >
          {showWind ? '💨 Wind ON' : '💨 Wind OFF'}
        </button>

        {/* Citizen Portal Link */}
        <Link
          href="/citizen"
          style={{
            padding: '4px 12px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--accent)',
            color: 'var(--accent-ink)',
            fontWeight: 650,
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <span>📱</span>
          <span>Field Portal</span>
        </Link>
      </div>
    </header>
  );
}
