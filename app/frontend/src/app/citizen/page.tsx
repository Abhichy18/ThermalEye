'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ThermalCluster, RegionId } from '@/lib/types';
import { fetchClusters, submitCitizenReport, submitInspectorFeedback } from '@/lib/api';
import { REGIONS } from '@/lib/constants';

export default function CitizenPortalPage() {
  const [region, setRegion] = useState<RegionId>('barmer');
  const [clusters, setClusters] = useState<ThermalCluster[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<ThermalCluster | null>(null);
  const [activeLang, setActiveLang] = useState<'hi' | 'en'>('hi');

  // Citizen Complaint Form State
  const [citizenDesc, setCitizenDesc] = useState('');
  const [citizenCat, setCitizenCat] = useState('agricultural_burn');
  const [citizenSubmitted, setCitizenSubmitted] = useState(false);

  // Inspector Ground-Truth Form State
  const [inspectorName, setInspectorName] = useState('Officer R.K. Sharma');
  const [badgeNo, setBadgeNo] = useState('SPCB-RAJ-409');
  const [confirmedCat, setConfirmedCat] = useState('gas_flare');
  const [inspectorNotes, setInspectorNotes] = useState('Physical site perimeter verified.');
  const [inspectorSubmitted, setInspectorSubmitted] = useState(false);

  useEffect(() => {
    fetchClusters(region).then((data) => {
      setClusters(data);
      if (data.length > 0) setSelectedCluster(data[0]);
    });
  }, [region]);

  const handleCitizenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitCitizenReport({
      lat: 26.5612,
      lon: 73.834,
      description: citizenDesc,
      category_reported: citizenCat,
      region,
    });
    setCitizenSubmitted(true);
    setTimeout(() => setCitizenSubmitted(false), 4000);
    setCitizenDesc('');
  };

  const handleInspectorSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCluster) return;
    await submitInspectorFeedback({
      cluster_id: selectedCluster.cluster_id,
      confirmed_category: confirmedCat as any,
      original_category: selectedCluster.classification,
      inspector_name: inspectorName,
      badge_number: badgeNo,
      field_notes: inspectorNotes,
      region,
    });
    setInspectorSubmitted(true);
    setTimeout(() => setInspectorSubmitted(false), 4000);
  };

  return (
    <div className="min-h-screen bg-[#0b0c0e] text-[#e7e9ec] font-mono select-none">
      {/* Mobile-first Header */}
      <header className="sticky top-0 z-30 bg-[#111316]/95 border-b border-white/10 px-4 py-3 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-2">
          <Link href="/" className="text-[#7a9ce0] text-xs font-bold hover:underline">
            ← Back to HQ Dashboard
          </Link>
          <span className="text-white/20">|</span>
          <span className="text-xs font-bold text-white uppercase">FIELD & CITIZEN PORTAL</span>
        </div>

        <select
          value={region}
          onChange={(e) => setRegion(e.target.value as RegionId)}
          className="bg-[#17191d] border border-white/20 text-[#7a9ce0] font-bold text-xs rounded px-2 py-1 outline-none"
        >
          {Object.entries(REGIONS).map(([id, meta]) => (
            <option key={id} value={id}>
              {meta.name}
            </option>
          ))}
        </select>
      </header>

      {/* Main Container */}
      <main className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Section 1: Active Regional Hazard Advisories & Voice Player */}
        <section className="bg-[#111316] border border-white/10 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-white/10 pb-2">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-1.5">
                <span>🔊</span>
                <span>Active Regional Thermal Hazard Broadcast</span>
              </h2>
              <p className="text-[11px] text-[#a0a6ae]">
                Automated multi-satellite hazard advisory for local residents and panchayat officers.
              </p>
            </div>

            <div className="flex rounded border border-white/15 overflow-hidden text-[10px]">
              <button
                onClick={() => setActiveLang('hi')}
                className={`px-2 py-0.5 font-bold ${activeLang === 'hi' ? 'bg-[#7a9ce0] text-black' : 'text-[#a0a6ae]'}`}
              >
                हिन्दी
              </button>
              <button
                onClick={() => setActiveLang('en')}
                className={`px-2 py-0.5 font-bold ${activeLang === 'en' ? 'bg-[#7a9ce0] text-black' : 'text-[#a0a6ae]'}`}
              >
                English
              </button>
            </div>
          </div>

          {selectedCluster && (
            <div className="p-3 bg-white/5 border border-white/8 rounded-lg space-y-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-bold text-amber-400">
                  Target Anomaly: {selectedCluster.cluster_id} · {selectedCluster.classification.toUpperCase()}
                </span>
                <span className="text-[10px] text-[#a0a6ae]">{selectedCluster.district_name}, {selectedCluster.state}</span>
              </div>

              <p className="text-[#cbd5e1] font-sans text-xs leading-relaxed">
                {activeLang === 'hi'
                  ? `सावधान: ${selectedCluster.district_name} में ${selectedCluster.classification} थर्मल गतिविधि उपग्रह द्वारा सत्यापित की गई है। विकिरण ऊर्जा ${selectedCluster.median_frp.toFixed(0)} मेगावाट है।`
                  : selectedCluster.grounded_briefing}
              </p>

              <audio
                controls
                className="w-full h-8 mt-2 rounded bg-black/40 border border-white/10"
                src={`http://localhost:8000/api/audio/${selectedCluster.cluster_id}/${activeLang}?region=${region}`}
              >
                Audio not supported
              </audio>
            </div>
          )}
        </section>

        {/* Section 2: Two-Sided Grid (Citizen Intake + Inspector Closure) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Citizen Geo-Tagged Report Form */}
          <section className="bg-[#111316] border border-white/10 rounded-xl p-4 space-y-3">
            <h2 className="text-sm font-bold text-[#7a9ce0] flex items-center gap-1.5 border-b border-white/10 pb-2">
              <span>📸</span>
              <span>Report Unidentified Fire / Smoke</span>
            </h2>
            <p className="text-[10.5px] text-[#a0a6ae]">
              Residents can submit GPS-tagged reports of illegal garbage burning, brick kiln emissions, or farm fires.
            </p>

            <form onSubmit={handleCitizenSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-[11px] text-[#a0a6ae] mb-1">Observed Incident Type:</label>
                <select
                  value={citizenCat}
                  onChange={(e) => setCitizenCat(e.target.value)}
                  className="w-full bg-[#17191d] border border-white/15 rounded p-2 text-white outline-none"
                >
                  <option value="agricultural_burn">Crop Stubble / Farm Residue Fire</option>
                  <option value="brick_kiln">Unauthorized Brick Kiln Smoke</option>
                  <option value="industrial_fire">Industrial Chemical Smoke / Factory Flare</option>
                  <option value="waste_burning">Municipal Waste / Landfill Burning</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] text-[#a0a6ae] mb-1">Incident Description & Landmark:</label>
                <textarea
                  required
                  rows={3}
                  value={citizenDesc}
                  onChange={(e) => setCitizenDesc(e.target.value)}
                  placeholder="Describe location, smoke density, duration..."
                  className="w-full bg-[#17191d] border border-white/15 rounded p-2 text-white placeholder-[#6d737b] outline-none"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded shadow-md cursor-pointer transition-all"
              >
                Submit Citizen Report
              </button>

              {citizenSubmitted && (
                <div className="p-2 bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 rounded text-center text-[11px] font-bold">
                  ✓ Report registered with District Magistrate Environmental Desk.
                </div>
              )}
            </form>
          </section>

          {/* Inspector Ground-Truth Calibration Form */}
          <section className="bg-[#111316] border border-white/10 rounded-xl p-4 space-y-3">
            <h2 className="text-sm font-bold text-amber-400 flex items-center gap-1.5 border-b border-white/10 pb-2">
              <span>👮</span>
              <span>Inspector Ground-Truth Verification Loop</span>
            </h2>
            <p className="text-[10.5px] text-[#a0a6ae]">
              Field officers conduct physical site audits to confirm or correct satellite AI predictions.
            </p>

            <form onSubmit={handleInspectorSubmit} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[10px] text-[#a0a6ae] mb-1">Officer Name:</label>
                  <input
                    type="text"
                    value={inspectorName}
                    onChange={(e) => setInspectorName(e.target.value)}
                    className="w-full bg-[#17191d] border border-white/15 rounded p-1.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-[#a0a6ae] mb-1">Badge ID:</label>
                  <input
                    type="text"
                    value={badgeNo}
                    onChange={(e) => setBadgeNo(e.target.value)}
                    className="w-full bg-[#17191d] border border-white/15 rounded p-1.5 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] text-[#a0a6ae] mb-1">Confirmed Physical Ground Category:</label>
                <select
                  value={confirmedCat}
                  onChange={(e) => setConfirmedCat(e.target.value)}
                  className="w-full bg-[#17191d] border border-white/15 rounded p-2 text-white outline-none"
                >
                  <option value="gas_flare">Industrial Gas Flare (Confirmed)</option>
                  <option value="industrial_fire">Acute Industrial Fire / Spill</option>
                  <option value="brick_kiln">Brick Kiln (FCK / Zig-Zag)</option>
                  <option value="agricultural_burn">Agricultural Stubble Burning</option>
                  <option value="mining">Mining / Quarry Fire</option>
                  <option value="wildfire">Forest Wildfire</option>
                  <option value="sun_glint">False Alarm (Solar Roof Reflection)</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] text-[#a0a6ae] mb-1">Field Audit Notes:</label>
                <input
                  type="text"
                  value={inspectorNotes}
                  onChange={(e) => setInspectorNotes(e.target.value)}
                  className="w-full bg-[#17191d] border border-white/15 rounded p-1.5 text-white"
                />
              </div>

              <button
                type="submit"
                className="w-full py-2 bg-amber-600 hover:bg-amber-500 text-black font-bold rounded shadow-md cursor-pointer transition-all"
              >
                Submit Ground Verification & Close Case
              </button>

              {inspectorSubmitted && (
                <div className="p-2 bg-emerald-500/20 border border-emerald-500/50 text-emerald-300 rounded text-center text-[11px] font-bold">
                  ✓ Ground verification recorded! Intervention Ledger updated and response stopwatch stopped.
                </div>
              )}
            </form>
          </section>
        </div>
      </main>
    </div>
  );
}
