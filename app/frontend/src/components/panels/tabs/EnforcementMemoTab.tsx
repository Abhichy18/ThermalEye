'use client';

import React, { useState } from 'react';
import { ThermalCluster } from '@/lib/types';

interface Props {
  cluster: ThermalCluster;
}

export default function EnforcementMemoTab({ cluster }: Props) {
  const [selectedLang, setSelectedLang] = useState<'hi' | 'en'>('hi');
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const [dispatchedSuccess, setDispatchedSuccess] = useState<boolean>(false);

  const memoPdfUrl = `http://localhost:8000/api/memos/${cluster.cluster_id}/pdf?region=${cluster.region}`;
  const audioUrl = `http://localhost:8000/api/audio/${cluster.cluster_id}/${selectedLang}?region=${cluster.region}`;

  const handleSimulateDispatch = () => {
    setDispatchedSuccess(true);
    setTimeout(() => setDispatchedSuccess(false), 4000);
  };

  return (
    <div className="space-y-3.5 font-mono text-xs text-[#e7e9ec]">
      {/* Target Authority Banner */}
      <div className="p-3 bg-white/5 border border-white/10 rounded-md">
        <div className="text-[10px] text-[#7a9ce0] uppercase tracking-wider font-bold mb-1">
          Responsible Statutory Authority
        </div>
        <div className="text-sm font-bold text-white">
          {cluster.jurisdiction_dispatch?.target_agency || 'State Pollution Control Board (Regional Office)'}
        </div>
        <div className="text-[10.5px] text-[#a0a6ae] mt-0.5">
          Mandate: {cluster.jurisdiction_dispatch?.legal_jurisdiction || 'Section 31A, Air (Prevention & Control of Pollution) Act 1981'}
        </div>
      </div>

      {/* 1-Click PDF Download Section */}
      <div className="p-3 bg-slate-900/80 border border-white/15 rounded-md flex flex-col md:flex-row items-center justify-between gap-3">
        <div>
          <div className="font-bold text-white text-xs">Official Show-Cause Statutory Notice</div>
          <div className="text-[10px] text-[#a0a6ae]">
            Pre-filled with telemetry evidence, GPS coordinates & 72-hour compliance mandate.
          </div>
        </div>

        <a
          href={memoPdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-3.5 py-1.5 bg-[#7a9ce0] hover:bg-[#93b0ea] active:bg-[#5b7cb8] text-black font-bold text-xs rounded flex items-center gap-1.5 transition-all shadow-md shrink-0 cursor-pointer"
        >
          <span>📄</span>
          <span>Download PDF Notice</span>
        </a>
      </div>

      {/* Multilingual Voice Advisory Player */}
      <div className="p-3 bg-white/5 border border-white/10 rounded-md space-y-2">
        <div className="flex items-center justify-between">
          <div className="font-bold text-xs text-white">Multilingual Field Voice Advisory</div>
          <div className="flex rounded border border-white/15 overflow-hidden text-[10px]">
            <button
              onClick={() => setSelectedLang('hi')}
              className={`px-2 py-0.5 font-bold transition-all ${
                selectedLang === 'hi' ? 'bg-[#7a9ce0] text-black' : 'bg-transparent text-[#a0a6ae]'
              }`}
            >
              हिन्दी (Hindi)
            </button>
            <button
              onClick={() => setSelectedLang('en')}
              className={`px-2 py-0.5 font-bold transition-all ${
                selectedLang === 'en' ? 'bg-[#7a9ce0] text-black' : 'bg-transparent text-[#a0a6ae]'
              }`}
            >
              English
            </button>
          </div>
        </div>

        <audio controls className="w-full h-8 mt-1 rounded bg-black/40 border border-white/10" src={audioUrl}>
          Your browser does not support the audio element.
        </audio>
        <div className="text-[10px] text-[#6d737b] italic">
          Synthesized broadcast note for district control room & patrol squads.
        </div>
      </div>

      {/* WhatsApp / Telegram Automated Emergency Dispatch Button */}
      <div className="pt-1">
        <button
          onClick={handleSimulateDispatch}
          className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-bold text-xs rounded-md shadow-lg flex items-center justify-center gap-2 transition-all cursor-pointer"
        >
          <span>📱</span>
          <span>Dispatch Emergency Alert to Regional Inspector Squad</span>
        </button>

        {dispatchedSuccess && (
          <div className="mt-2 p-2 bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 rounded text-center text-[11px] font-bold animate-fadeIn">
            ✓ Alert successfully routed to {cluster.jurisdiction_dispatch?.recipient_role || 'Field Officer'}! Recorded in Intervention Ledger.
          </div>
        )}
      </div>
    </div>
  );
}
