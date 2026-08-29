import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ThermalEye — Autonomous Multi-Satellite Surveillance',
  description: 'Autonomous Earth Observation & Thermal Anomaly Attribution Engine: signal → attribution → action.',
};

const STATS = [
  { value: '6', label: 'Regional Sectors', sub: 'Barmer to Jharia' },
  { value: '7', label: 'Thermal Classes', sub: 'flares to kilns' },
  { value: '96.8%', label: 'AI Accuracy', sub: '100% glint suppression' },
  { value: '4-Pillar', label: 'Physics Rules', sub: 'deterministic evidence' },
  { value: '460m', label: 'H3 Spatial Fabric', sub: 'VIIRS 375m res-8' },
];

const ROLES = [
  {
    href: '/admin',
    icon: '🛰️',
    title: 'Admin Command Console',
    body: 'Interactive 3D Deck.gl map, real-time multi-agent execution stream, 4-pillar evidence dossier, Sentinel-2 optical spyglass, and 1-click Section 31A statutory notices.',
    cta: 'Open Command Console →',
    badge: 'HQ & Enforcement Desk',
  },
  {
    href: '/citizen',
    icon: '📱',
    title: 'Field & Citizen Portal',
    body: 'Multilingual voice advisories in Hindi & English, geo-tagged citizen incident reporting, and inspector ground-truth verification loop.',
    cta: 'Open Field Portal →',
    badge: 'Mobile & Ground Squads',
  },
];

export default function LandingPage() {
  return (
    <main
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-2xl) var(--space-lg)',
        gap: 'var(--space-2xl)',
        background: 'var(--bg-base)',
        color: 'var(--text-primary)',
        fontFamily: 'var(--font-sans)',
      }}
    >
      <div style={{ textAlign: 'center', maxWidth: 720 }}>
        {/* Live Satellite Badge */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 7,
            padding: '4px 12px',
            marginBottom: 'var(--space-lg)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.72rem',
            fontWeight: 550,
            color: 'var(--text-tertiary)',
            fontFamily: 'var(--font-mono)',
            background: 'var(--bg-secondary)',
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: 'var(--positive)',
              display: 'inline-block',
              boxShadow: '0 0 8px var(--positive)',
            }}
          />
          NTRO SIH 2026 (SIH26162YELLOW) · VIIRS 375m & Nightfire Active
        </div>

        {/* Display Title */}
        <h1
          style={{
            fontSize: '2.75rem',
            fontWeight: 700,
            letterSpacing: '-0.03em',
            marginBottom: 'var(--space-md)',
            color: 'var(--text-primary)',
          }}
        >
          Thermal<span style={{ color: 'var(--accent)' }}>Eye</span>
        </h1>

        <p
          style={{
            fontSize: '1.05rem',
            lineHeight: 1.6,
            color: 'var(--text-secondary)',
            marginBottom: 'var(--space-lg)',
          }}
        >
          Autonomous Multi-Satellite Industrial Thermal Surveillance & Ground-Truth Attribution.
          Distinguishes <strong>gas flares</strong>, <strong>brick kilns</strong>, <strong>agricultural burns</strong>, and <strong>industrial fires</strong> with <strong>deterministic physical proof</strong> and <strong>automated Section 31A statutory notices</strong>.
        </p>
      </div>

      {/* Role Selection Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 'var(--space-lg)',
          maxWidth: 900,
          width: '100%',
        }}
      >
        {ROLES.map((r) => (
          <Link
            key={r.href}
            href={r.href}
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: 'var(--space-xl)',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-default)',
              borderRadius: 'var(--radius-lg)',
              textDecoration: 'none',
              color: 'inherit',
              transition: 'all 0.2s ease',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
            }}
            className="hover:border-[#7a9ce0] hover:bg-[#17191d]"
          >
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 'var(--space-md)',
                }}
              >
                <span style={{ fontSize: '1.75rem' }}>{r.icon}</span>
                <span
                  style={{
                    fontSize: '0.68rem',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600,
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--accent-soft)',
                    color: 'var(--accent)',
                    border: '1px solid var(--accent-line)',
                  }}
                >
                  {r.badge}
                </span>
              </div>

              <h2
                style={{
                  fontSize: '1.25rem',
                  fontWeight: 650,
                  marginBottom: 'var(--space-sm)',
                  color: 'var(--text-primary)',
                }}
              >
                {r.title}
              </h2>

              <p
                style={{
                  fontSize: '0.85rem',
                  lineHeight: 1.55,
                  color: 'var(--text-secondary)',
                  marginBottom: 'var(--space-lg)',
                }}
              >
                {r.body}
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                fontSize: '0.82rem',
                fontFamily: 'var(--font-mono)',
                fontWeight: 600,
                color: 'var(--accent)',
              }}
            >
              {r.cta}
            </div>
          </Link>
        ))}
      </div>

      {/* Numerical Stats Row */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: 'var(--space-xl)',
          maxWidth: 900,
          width: '100%',
          paddingTop: 'var(--space-lg)',
          borderTop: '1px solid var(--border-subtle)',
          textAlign: 'center',
        }}
      >
        {STATS.map((s) => (
          <div key={s.label} style={{ minWidth: 120 }}>
            <div
              style={{
                fontSize: '1.35rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-primary)',
              }}
            >
              {s.value}
            </div>
            <div
              style={{
                fontSize: '0.78rem',
                fontWeight: 550,
                color: 'var(--text-secondary)',
                marginTop: 2,
              }}
            >
              {s.label}
            </div>
            <div
              style={{
                fontSize: '0.68rem',
                color: 'var(--text-tertiary)',
                marginTop: 1,
              }}
            >
              {s.sub}
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
