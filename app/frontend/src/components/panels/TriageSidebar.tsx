'use client';

import React, { useState, useMemo } from 'react';
import { ThermalCluster, ThermalCategory } from '@/lib/types';
import { getCategoryColor, getPriorityColor, getPriorityBgSoft } from '@/lib/colors';

interface Props {
  clusters: ThermalCluster[];
  selectedClusterId: string | null;
  onSelectCluster: (cluster: ThermalCluster) => void;
}

export default function TriageSidebar({ clusters, selectedClusterId, onSelectCluster }: Props) {
  const [filterCat, setFilterCat] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredClusters = useMemo(() => {
    return clusters.filter((c) => {
      if (filterCat !== 'ALL' && c.classification.toLowerCase() !== filterCat.toLowerCase()) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchId = c.cluster_id.toLowerCase().includes(q);
        const matchDist = c.district_name.toLowerCase().includes(q);
        const matchOsm = c.closest_osm_name.toLowerCase().includes(q);
        const matchCat = c.classification.toLowerCase().includes(q);
        if (!matchId && !matchDist && !matchOsm && !matchCat) return false;
      }
      return true;
    });
  }, [clusters, filterCat, searchQuery]);

  return (
    <aside
      style={{
        width: '320px',
        height: '100%',
        background: 'var(--bg-glass)',
        borderRight: '1px solid var(--border-default)',
        backdropFilter: 'blur(12px)',
        display: 'flex',
        flexDirection: 'column',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.75rem',
        flexShrink: 0,
        zIndex: 20,
      }}
    >
      {/* Header & Filter Controls */}
      <div
        style={{
          padding: 'var(--space-sm) var(--space-md)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          background: 'var(--bg-secondary)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-primary)', fontSize: '0.72rem' }}>
            Tactical Triage Queue
          </span>
          <span style={{ color: 'var(--text-tertiary)', fontSize: '0.68rem' }}>{filteredClusters.length} Sources</span>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Filter ID, district, facility..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            width: '100%',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-sm)',
            padding: '5px 8px',
            color: 'var(--text-primary)',
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            outline: 'none',
          }}
        />

        {/* Category Pills Strip */}
        <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', paddingBottom: '2px' }}>
          {['ALL', 'gas_flare', 'industrial_fire', 'brick_kiln', 'agricultural_burn', 'mining', 'wildfire'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCat(cat)}
              style={{
                padding: '2px 7px',
                borderRadius: 'var(--radius-sm)',
                border: filterCat === cat ? '1px solid var(--accent)' : '1px solid var(--border-subtle)',
                background: filterCat === cat ? 'var(--accent)' : 'var(--bg-tertiary)',
                color: filterCat === cat ? 'var(--accent-ink)' : 'var(--text-secondary)',
                fontSize: '0.65rem',
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {cat === 'ALL' ? 'All Types' : cat.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Cluster List */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 'var(--space-sm)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}
      >
        {filteredClusters.length === 0 ? (
          <div style={{ padding: 'var(--space-lg)', textAlign: 'center', color: 'var(--text-tertiary)' }}>
            No thermal sources match filter.
          </div>
        ) : (
          filteredClusters.map((c) => {
            const isSelected = c.cluster_id === selectedClusterId;
            const catColor = getCategoryColor(c.classification);
            const priColor = getPriorityColor(c.priority_tier);

            return (
              <div
                key={c.cluster_id}
                onClick={() => onSelectCluster(c)}
                style={{
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-sm)',
                  border: isSelected ? '1px solid var(--accent)' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'var(--bg-active)' : 'var(--bg-primary)',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  boxShadow: isSelected ? '0 0 10px rgba(122, 156, 224, 0.2)' : 'none',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <div
                      style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        background: catColor,
                      }}
                    />
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.75rem' }}>
                      {c.cluster_id}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span
                      style={{
                        padding: '1px 5px',
                        borderRadius: 'var(--radius-sm)',
                        background: getPriorityBgSoft(c.priority_tier),
                        color: priColor,
                        border: `1px solid ${priColor}40`,
                        fontSize: '0.62rem',
                        fontWeight: 700,
                      }}
                    >
                      {c.priority_tier}
                    </span>
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-secondary)' }}>{c.eps_score} EPS</span>
                  </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: catColor, fontSize: '0.7rem' }}>
                    {c.classification.replace('_', ' ').toUpperCase()}
                  </span>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.72rem' }}>
                    {c.median_frp.toFixed(1)} MW
                  </span>
                </div>

                <div
                  style={{
                    fontSize: '0.65rem',
                    color: 'var(--text-tertiary)',
                    marginTop: '4px',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}
                >
                  {c.closest_osm_name} ({c.district_name})
                </div>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}
