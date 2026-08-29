'use client';

import React, { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';

import { ThermalCluster, RegionId, ExecutiveSummaryStats } from '@/lib/types';
import { fetchClusters, fetchClustersSummary } from '@/lib/api';
import { DEFAULT_REGION, REGIONS } from '@/lib/constants';

import HUDHeader from '@/components/HUDHeader';
import AgentProgressStrip from '@/components/agents/AgentProgressStrip';
import TriageSidebar from '@/components/panels/TriageSidebar';
import CaseFileDrawer from '@/components/panels/CaseFileDrawer';

// Dynamically import DeckMap with SSR disabled (Deck.gl requires client DOM)
const ThermalDeckMap = dynamic(() => import('@/components/map/ThermalDeckMap'), {
  ssr: false,
  loading: () => (
    <div
      style={{
        width: '100%',
        height: '100%',
        background: 'var(--bg-base)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.75rem',
        color: 'var(--text-tertiary)',
        gap: '8px',
      }}
    >
      <div
        style={{
          width: '24px',
          height: '24px',
          border: '2px solid var(--accent)',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <span>INITIALIZING 3D EARTH OBSERVATION DECK...</span>
    </div>
  ),
});

export default function AdminConsolePage() {
  const [region, setRegion] = useState<RegionId>(DEFAULT_REGION);
  const [clusters, setClusters] = useState<ThermalCluster[]>([]);
  const [summary, setSummary] = useState<ExecutiveSummaryStats | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<ThermalCluster | null>(null);
  const [is3dExtruded, setIs3dExtruded] = useState<boolean>(true);
  const [showWindVectors, setShowWindVectors] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = useCallback((targetRegion: RegionId) => {
    setLoading(true);
    Promise.all([
      fetchClusters(targetRegion),
      fetchClustersSummary(targetRegion),
    ]).then(([cls, sum]) => {
      setClusters(cls);
      setSummary(sum);
      if (cls.length > 0) {
        setSelectedCluster(cls[0]);
      } else {
        setSelectedCluster(null);
      }
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    loadData(region);
  }, [region, loadData]);

  const handleSelectRegion = (newRegion: RegionId) => {
    setRegion(newRegion);
    setSelectedCluster(null);
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        width: '100vw',
        overflow: 'hidden',
        background: 'var(--bg-base)',
        color: 'var(--text-primary)',
        userSelect: 'none',
      }}
    >
      {/* Top HUD Header */}
      <HUDHeader
        selectedRegion={region}
        onSelectRegion={handleSelectRegion}
        is3d={is3dExtruded}
        onToggle3d={() => setIs3dExtruded((prev) => !prev)}
        showWind={showWindVectors}
        onToggleWind={() => setShowWindVectors((prev) => !prev)}
        totalClustersCount={clusters.length}
        criticalP1Count={summary?.critical_p1_count || 0}
      />

      {/* Real-time Multi-Agent Progress Strip */}
      <AgentProgressStrip region={region} onPipelineComplete={() => loadData(region)} />

      {/* Main Workspace Area (Sidebar + 3D Deck Map + Case File Drawer) */}
      <div
        style={{
          position: 'relative',
          flex: 1,
          display: 'flex',
          overflow: 'hidden',
        }}
      >
        {/* Left Triage Sidebar */}
        <TriageSidebar
          clusters={clusters}
          selectedClusterId={selectedCluster?.cluster_id || null}
          onSelectCluster={(c) => setSelectedCluster(c)}
        />

        {/* Center 3D Deck.gl Map Canvas */}
        <main
          style={{
            flex: 1,
            position: 'relative',
            height: '100%',
            width: '100%',
            overflow: 'hidden',
          }}
        >
          <ThermalDeckMap
            region={region}
            clusters={clusters}
            selectedClusterId={selectedCluster?.cluster_id || null}
            onSelectCluster={(c) => setSelectedCluster(c)}
            is3dExtruded={is3dExtruded}
            showWindVectors={showWindVectors}
          />
        </main>

        {/* Right / Bottom Case File Drawer (4-Tab Intelligence Suite) */}
        {selectedCluster && (
          <CaseFileDrawer
            cluster={selectedCluster}
            onClose={() => setSelectedCluster(null)}
          />
        )}
      </div>
    </div>
  );
}
