'use client';

import React, { useState } from 'react';
import { ThermalCluster } from '@/lib/types';
import EvidenceChainTab from './tabs/EvidenceChainTab';
import OpticalSpyglassTab from './tabs/OpticalSpyglassTab';
import FRPSparklineTab from './tabs/FRPSparklineTab';
import EnforcementMemoTab from './tabs/EnforcementMemoTab';
import { getCategoryColor, getPriorityColor } from '@/lib/colors';

interface Props {
  cluster: ThermalCluster | null;
  onClose: () => void;
}

type TabType = 'evidence' | 'spyglass' | 'sparkline' | 'memo';

export default function CaseFileDrawer({ cluster, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<TabType>('evidence');

  if (!cluster) return null;

  const catColor = getCategoryColor(cluster.classification);
  const priColor = getPriorityColor(cluster.priority_tier);

  return (
    <aside
      style={{
        position: 'absolute',
        bottom: 0,
        right: 0,
        width: '460px',
        maxHeight: 'calc(100vh - 110px)',
        background: 'var(--bg-glass)',
        borderLeft: '1px solid var(--border-default)',
        borderTop: '1px solid var(--border-default)',
        backdropFilter: 'blur(16px)',
        boxShadow: '-8px 0 30px rgba(0, 0, 0, 0.5)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 40,
        userSelect: 'none',
        borderRadius: 'var(--radius-md) 0 0 0',
      }}
    >
      {/* Drawer Header */}
      <div
        style={{
          padding: '10px 14px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'var(--bg-secondary)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: catColor,
              boxShadow: `0 0 8px ${catColor}`,
            }}
          />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.85rem' }}>
                {cluster.cluster_id}
              </span>
              <span
                style={{
                  padding: '1px 5px',
                  borderRadius: 'var(--radius-sm)',
                  background: `${priColor}25`,
                  color: priColor,
                  border: `1px solid ${priColor}50`,
                  fontSize: '0.62rem',
                  fontFamily: 'var(--font-mono)',
                  fontWeight: 700,
                }}
              >
                {cluster.priority_tier}
              </span>
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-tertiary)', fontFamily: 'var(--font-mono)' }}>
              {cluster.district_name}, {cluster.state} · ({cluster.centroid_lat.toFixed(4)}°N, {cluster.centroid_lon.toFixed(4)}°E)
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-tertiary)',
            fontSize: '1rem',
            cursor: 'pointer',
            padding: '4px 8px',
          }}
          title="Close Case File"
        >
          ✕
        </button>
      </div>

      {/* Tab Navigation Strip */}
      <div
        style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'var(--bg-primary)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.72rem',
        }}
      >
        {[
          { id: 'evidence', label: '📋 Evidence' },
          { id: 'spyglass', label: '🛰️ Spyglass' },
          { id: 'sparkline', label: '📈 Sparkline' },
          { id: 'memo', label: '⚖️ Legal Memo' },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id as TabType)}
            style={{
              flex: 1,
              padding: '8px 4px',
              textAlign: 'center',
              fontWeight: 650,
              border: 'none',
              borderBottom: activeTab === t.id ? '2px solid var(--accent)' : '2px solid transparent',
              background: activeTab === t.id ? 'var(--bg-tertiary)' : 'transparent',
              color: activeTab === t.id ? 'var(--accent)' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.7rem',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab Content Area */}
      <div
        style={{
          padding: '14px',
          overflowY: 'auto',
          maxHeight: 'calc(100vh - 220px)',
        }}
      >
        {activeTab === 'evidence' && <EvidenceChainTab cluster={cluster} />}
        {activeTab === 'spyglass' && <OpticalSpyglassTab cluster={cluster} />}
        {activeTab === 'sparkline' && <FRPSparklineTab cluster={cluster} />}
        {activeTab === 'memo' && <EnforcementMemoTab cluster={cluster} />}
      </div>
    </aside>
  );
}
