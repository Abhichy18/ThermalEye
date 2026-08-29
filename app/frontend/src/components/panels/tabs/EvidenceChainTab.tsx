'use client';

import React from 'react';
import { ThermalCluster } from '@/lib/types';
import { getCategoryColor, getPriorityColor } from '@/lib/colors';

interface Props {
  cluster: ThermalCluster;
}

export default function EvidenceChainTab({ cluster }: Props) {
  const catColor = getCategoryColor(cluster.classification);
  const priColor = getPriorityColor(cluster.priority_tier);

  return (
    <div className="space-y-4 font-mono text-xs text-[#e7e9ec]">
      {/* Executive Classification Header */}
      <div className="p-3 bg-white/5 border border-white/10 rounded-md flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: catColor }}
          />
          <span className="font-bold text-sm" style={{ color: catColor }}>
            {cluster.classification.replace('_', ' ').toUpperCase()}
          </span>
          <span className="text-[#a0a6ae]">({(cluster.confidence * 100).toFixed(1)}% Confidence)</span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className="px-2 py-0.5 rounded text-[11px] font-bold"
            style={{
              backgroundColor: `${priColor}20`,
              color: priColor,
              border: `1px solid ${priColor}50`,
            }}
          >
            {cluster.priority_tier} · {cluster.priority_label}
          </span>
          <span className="text-[#a0a6ae]">EPS: <b className="text-white">{cluster.eps_score}</b>/100</span>
        </div>
      </div>

      {/* LLM Grounded Briefing */}
      <div className="p-3 bg-[#7a9ce0]/10 border border-[#7a9ce0]/30 rounded-md">
        <div className="text-[10px] text-[#7a9ce0] uppercase tracking-wider font-bold mb-1">
          ✦ Autonomous Intelligence Briefing
        </div>
        <p className="text-[#e7e9ec] leading-relaxed text-[11.5px] font-sans">
          {cluster.grounded_briefing}
        </p>
      </div>

      {/* 4-Pillar Mathematical Evidence Trail */}
      <div>
        <div className="text-[11px] text-[#a0a6ae] uppercase tracking-wider font-bold mb-2">
          Deterministic 4-Pillar Evidence Trail
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div className="p-2.5 bg-white/5 border border-white/10 rounded">
            <div className="text-[#7a9ce0] text-[10px] uppercase font-bold mb-1">1. Temporal Profile</div>
            <div className="text-[#a0a6ae] text-[11px] leading-normal">{cluster.evidence_chain.temporal}</div>
          </div>
          <div className="p-2.5 bg-white/5 border border-white/10 rounded">
            <div className="text-[#f59e0b] text-[10px] uppercase font-bold mb-1">2. Thermal Physics</div>
            <div className="text-[#a0a6ae] text-[11px] leading-normal">{cluster.evidence_chain.thermal}</div>
          </div>
          <div className="p-2.5 bg-white/5 border border-white/10 rounded">
            <div className="text-[#5ea88a] text-[10px] uppercase font-bold mb-1">3. Spatial / OSM Proximity</div>
            <div className="text-[#a0a6ae] text-[11px] leading-normal">{cluster.evidence_chain.spatial}</div>
          </div>
          <div className="p-2.5 bg-white/5 border border-white/10 rounded">
            <div className="text-[#c0705b] text-[10px] uppercase font-bold mb-1">4. Statutory Jurisdiction</div>
            <div className="text-[#a0a6ae] text-[11px] leading-normal">{cluster.evidence_chain.contextual}</div>
          </div>
        </div>
      </div>

      {/* Alternative Hypotheses Rejected (Anti-Hallucination Guard) */}
      <div>
        <div className="text-[11px] text-[#a0a6ae] uppercase tracking-wider font-bold mb-2 flex items-center gap-1.5">
          <span>🛡️ Alternative Hypotheses Rejected</span>
          <span className="text-[10px] text-[#6d737b] font-normal">(Anti-Hallucination Verification)</span>
        </div>
        <div className="space-y-1.5">
          {cluster.alternative_hypotheses_rejected && cluster.alternative_hypotheses_rejected.length > 0 ? (
            cluster.alternative_hypotheses_rejected.map((hyp, idx) => (
              <div
                key={idx}
                className="p-2 bg-red-500/10 border border-red-500/20 rounded flex items-start gap-2 text-[11px]"
              >
                <span className="text-red-400 font-bold">❌</span>
                <div>
                  <span className="font-bold text-red-300 mr-1.5 uppercase">
                    Rejected: {hyp.hypothesis.replace('_', ' ')}
                  </span>
                  <span className="text-[#cbd5e1]">{hyp.reason}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="p-2 bg-white/5 border border-white/10 rounded text-[#a0a6ae] text-[11px]">
              No competing ambiguous hypothesis detected for this signature.
            </div>
          )}
        </div>
      </div>

      {/* Regulatory Action Recommendation */}
      <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded">
        <div className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-1">
          Regulatory Action Mandate
        </div>
        <div className="text-[#e7e9ec] font-semibold text-[11.5px]">
          {cluster.regulatory_recommendation}
        </div>
      </div>
    </div>
  );
}
