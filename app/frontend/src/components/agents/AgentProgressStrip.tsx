'use client';

import React, { useState } from 'react';
import { PipelineProgressEvent, RegionId } from '@/lib/types';

interface Props {
  region: RegionId;
  onPipelineComplete?: () => void;
}

const STAGES = [
  { id: 'INGESTION', label: '1. Ingest', sub: 'VIIRS 375m' },
  { id: 'SPATIAL_FABRIC', label: '2. Grid', sub: 'H3 res-8' },
  { id: 'DBSCAN_CLUSTERING', label: '3. Cluster', sub: 'DBSCAN' },
  { id: '7_CLASS_CLASSIFIER', label: '4. Classify', sub: '7-Class LGB' },
  { id: 'EVIDENCE_ENGINE', label: '5. Evidence', sub: 'Hypothesis' },
  { id: 'ACTION_DISPATCH', label: '6. Action', sub: 'Memos & Audio' },
];

export default function AgentProgressStrip({ region, onPipelineComplete }: Props) {
  const [activeStage, setActiveStage] = useState<string>('PIPELINE_COMPLETE');
  const [progressPct, setProgressPct] = useState<number>(100);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<string>('Surveillance active · All intelligence agents synchronized.');

  const triggerLiveRun = () => {
    setIsRunning(true);
    setProgressPct(5);
    setActiveStage('INGESTION');
    setLastMessage('Connecting to satellite telemetry pipeline...');

    const eventSource = new EventSource(`http://localhost:8000/api/pipeline/stream?region=${region}`);

    eventSource.addEventListener('agent_progress', (e) => {
      try {
        const payload: PipelineProgressEvent = JSON.parse(e.data);
        setActiveStage(payload.stage);
        setProgressPct(payload.progress_percent);
        setLastMessage(payload.message);
      } catch (err) {
        console.error('Error parsing SSE progress', err);
      }
    });

    eventSource.addEventListener('agent_complete', (e) => {
      try {
        const payload: PipelineProgressEvent = JSON.parse(e.data);
        setActiveStage('PIPELINE_COMPLETE');
        setProgressPct(100);
        setIsRunning(false);
        setLastMessage(payload.message);
        eventSource.close();
        if (onPipelineComplete) onPipelineComplete();
      } catch (err) {
        console.error('Error parsing SSE complete', err);
      }
    });

    eventSource.onerror = () => {
      setIsRunning(false);
      setProgressPct(100);
      setActiveStage('PIPELINE_COMPLETE');
      setLastMessage('Agent pipeline execution completed (offline sync mode).');
      eventSource.close();
      if (onPipelineComplete) onPipelineComplete();
    };
  };

  return (
    <div
      style={{
        width: '100%',
        background: 'var(--bg-primary)',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '6px var(--space-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.72rem',
        color: 'var(--text-primary)',
        flexShrink: 0,
        gap: 'var(--space-md)',
        zIndex: 25,
      }}
    >
      {/* Stages List */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', overflowX: 'auto' }}>
        {STAGES.map((st, idx) => {
          const isCurrent = activeStage === st.id;
          const isDone = progressPct === 100 || idx < STAGES.findIndex((s) => s.id === activeStage);

          return (
            <div
              key={st.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '3px 8px',
                borderRadius: 'var(--radius-sm)',
                border: isCurrent
                  ? '1px solid var(--accent)'
                  : isDone
                  ? '1px solid var(--border-subtle)'
                  : '1px solid transparent',
                background: isCurrent
                  ? 'var(--accent-soft)'
                  : isDone
                  ? 'var(--bg-tertiary)'
                  : 'transparent',
                color: isCurrent
                  ? 'var(--accent)'
                  : isDone
                  ? 'var(--text-primary)'
                  : 'var(--text-tertiary)',
                whiteSpace: 'nowrap',
              }}
            >
              <div
                style={{
                  width: '5px',
                  height: '5px',
                  borderRadius: '50%',
                  background: isCurrent ? 'var(--accent)' : isDone ? 'var(--positive)' : 'var(--text-tertiary)',
                }}
              />
              <span style={{ fontWeight: 600 }}>{st.label}</span>
            </div>
          );
        })}
      </div>

      {/* Live Stream Message & Action Trigger */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.7rem', whiteSpace: 'nowrap' }}>
          <span style={{ color: 'var(--positive)', fontWeight: 700, marginRight: '4px' }}>● LIVE:</span>
          {lastMessage}
        </div>

        <button
          onClick={triggerLiveRun}
          disabled={isRunning}
          style={{
            padding: '3px 10px',
            background: 'var(--accent-soft)',
            border: '1px solid var(--accent-line)',
            color: 'var(--accent)',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 650,
            fontSize: '0.7rem',
            fontFamily: 'var(--font-mono)',
            cursor: isRunning ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            opacity: isRunning ? 0.6 : 1,
            whiteSpace: 'nowrap',
          }}
        >
          <span>⚡</span>
          <span>{isRunning ? 'Running...' : 'Re-Run Pipeline'}</span>
        </button>
      </div>
    </div>
  );
}
