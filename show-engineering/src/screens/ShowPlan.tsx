import { useState } from 'react'
import {
  useSEStore,
  buildPhases,
  formatTimeStr,
  PHASE_PRESCRIPTIONS,
  PHASE_LIGHTING_DATA,
} from '../store/seStore'
import { ConversationalPanel } from './ConversationalPanel'
import './ShowPlan.css'

// ─── Static mock data ──────────────────────────────────────────────────────────

const INTERVENTIONS = [
  {
    id: 1,
    trigger: 'Dance floor occupancy < 30% after 30 mins into Build phase',
    action: 'Queue 2–3 familiar tracks in minor key at 124 BPM, 8-bar phrases',
    watch: "First 2–3 movers step onto floor — hold steady, don't escalate yet",
  },
  {
    id: 2,
    trigger: 'Crowd energy signal drops ≥ 15% in Peak phase',
    action: 'Introduce a crowd-familiar track with strong sub-bass hook at +3dB',
    watch: 'Monitor for 2 tracks before further intervention — allow reset time',
  },
  {
    id: 3,
    trigger: 'Bar/table service stalls during Wind Down (queue visible)',
    action: 'Drop BPM by 4–6 from current, shift to major key feel',
    watch: 'Table conversations should increase — signal that people are settling',
  },
]

const STAFF_NOTES = [
  'Position 2 staff near the floor entrance during Build — creates social proof for reluctant dancers.',
  'Brief bar staff: upsell doubles and cocktails from 11 PM; peak phase correlates with peak spend intent.',
  'Increase table service pace during Wind Down — encourage spend before close.',
  'If a large group arrives during Peak, seat them near (not on) the dance floor — not at the back.',
  'Do not use over-the-mic announcements during Build or Peak — disrupts neuroacoustic continuity.',
]

// ─── Part 1: Quick Reference action lines ─────────────────────────────────────

const QR_ACTION: Record<string, string> = {
  'Opening':   'Hold energy low. Let room fill naturally.',
  'Warm Up':   'Introduce rhythmic familiarity. Watch for shoulder movement.',
  'Build':     'Escalate every 2 tracks. Watch for first floor movers.',
  'Peak':      'Lock in and hold. Don\'t second-guess the room.',
  'Wind Down': 'Slow BPM gradually. Cue bar staff to increase table rounds.',
}

// ─── Part 2: Watch for signals ────────────────────────────────────────────────

const PHASE_WATCH_SIGNALS: Record<string, string[]> = {
  'Opening':   ['Guests clustering at the bar — room not ready', 'Conversations louder than music — hold BPM', 'First small group settles near floor — green light to start nudging'],
  'Warm Up':   ['Shoulders moving at tables — social priming working', 'Bar queue forming — energy rising', 'People looking toward the floor — ready to escalate'],
  'Build':     ['First 2–3 people step onto floor — hold steady, let contagion work', 'Dance floor occupancy below 30% after 30 min — trigger intervention', 'Crowd facing the DJ — momentum locked'],
  'Peak':      ['Energy plateau — normal, hold prescription', 'Energy drop >15% — trigger intervention immediately', 'Groups leaving floor — check volume, consider familiar track'],
  'Wind Down': ['Conversations at tables increasing — good signal', 'Bar spend visibly rising — Wind Down working', 'Crowd thinning faster than expected — accelerate to close'],
}

// ─── Part 3: Energy values per phase ─────────────────────────────────────────

const PHASE_ENERGY: Record<string, number> = {
  'Opening':   30,
  'Warm Up':   50,
  'Build':     72,
  'Peak':      95,
  'Wind Down': 45,
}

// ─── Part 4: Transition cards ─────────────────────────────────────────────────

const PHASE_TRANSITIONS: Record<string, string[]> = {
  'Opening→Warm Up':   ['Drop 1 track with +2 BPM nudge', 'Keep key consistent — no jarring shifts', 'Watch shoulders before escalating further'],
  'Opening→Build':     ['Run 2 bridge tracks at 114–116 BPM', 'Shift to minor key feel on track 2', 'Wait for first floor movers before full Build energy'],
  'Opening→Peak':      ['Rare direct jump — only if room is already hot', 'Use a crowd-familiar anthem as the bridge', 'Full sub-bass in immediately'],
  'Warm Up→Build':     ['One track overlap in BPM range (118)', 'Introduce minor chord feel', "Don't announce the transition — let it happen"],
  'Warm Up→Peak':      ['2 escalating bridge tracks', 'Sub-bass +1dB then +2dB across tracks', 'Confirm floor occupancy >40% before committing to Peak'],
  'Build→Peak':        ['Single high-energy pivot track', 'Sub-bass to full prescription in one step', 'Hold for 2 full tracks before reading crowd response'],
  'Peak→Wind Down':    ['Avoid hard BPM drop — step down over 3 tracks', 'Shift to major key on track 2 of Wind Down', 'Signal bar staff as you enter Wind Down'],
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function phaseDuration(startStr: string, endStr: string): string {
  const toMins = (t: string) => {
    const [h, m] = t.split(':').map(Number)
    return h * 60 + (m ?? 0)
  }
  let diff = toMins(endStr) - toMins(startStr)
  if (diff <= 0) diff += 1440
  const h = Math.floor(diff / 60)
  const m = diff % 60
  if (h === 0) return `${m} min`
  if (m === 0) return `${h} hr`
  return `${h} hr ${m} min`
}

// ─── Energy Curve SVG ─────────────────────────────────────────────────────────

function EnergyCurve({ labels }: { labels: string[] }) {
  const W = 1000 // viewBox width
  const H = 56
  const PAD = 16

  const n = labels.length
  // One point per phase, evenly spaced horizontally
  const pts = labels.map((label, i) => ({
    x: PAD + (i / (n - 1 || 1)) * (W - PAD * 2),
    y: H - PAD - ((PHASE_ENERGY[label] ?? 50) / 100) * (H - PAD * 2),
  }))

  // Build smooth bezier path
  let d = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1]
    const cur = pts[i]
    const cpX = (prev.x + cur.x) / 2
    d += ` C ${cpX} ${prev.y} ${cpX} ${cur.y} ${cur.x} ${cur.y}`
  }

  // Phase separator x positions (between phases)
  const sepXs = labels.slice(0, -1).map((_, i) =>
    PAD + ((i + 0.5) / (n - 1 || 1)) * (W - PAD * 2)
  )

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      preserveAspectRatio="none"
      width="100%"
      height={H}
      className="sp-energy-curve"
      aria-hidden="true"
    >
      {/* Vertical separator lines */}
      {sepXs.map((x, i) => (
        <line
          key={i}
          x1={x} y1={4} x2={x} y2={H - 4}
          stroke="var(--border)"
          strokeWidth="1"
          strokeDasharray="4 4"
        />
      ))}

      {/* Curve */}
      <path
        d={d}
        fill="none"
        stroke="var(--gold-muted)"
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />

      {/* Dots */}
      {pts.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r="4" fill="var(--gold)" />
      ))}
    </svg>
  )
}

// ─── Main component ───────────────────────────────────────────────────────────

export function ShowPlan() {
  const {
    selectedVenue, sessionContext,
    manualBoundaries, setBoundary, resetBoundaries,
    resetGeneration, setConversationalPanel, conversationalPanelOpen,
  } = useSEStore()

  const [expandedIntervention, setExpandedIntervention] = useState<number | null>(null)
  const [editingBoundary, setEditingBoundary] = useState<number | null>(null)
  const [refOpen, setRefOpen] = useState(false)

  const phases = buildPhases(
    sessionContext.startTime,
    sessionContext.endTime,
    sessionContext.phaseCount,
    manualBoundaries,
  )

  const dateLabel = sessionContext.date
    ? new Date(sessionContext.date).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
    : ''

  function handleBoundaryCommit(index: number, value: string) {
    if (value) setBoundary(index, value)
    setEditingBoundary(null)
  }

  return (
    <div className="sp-root fade-in">

      {/* ── Header (unchanged) ── */}
      <div className="sp-header">
        <div className="sp-header-meta">
          <h1 className="sp-title clash">{selectedVenue?.name}</h1>
          <p className="sp-subtitle">{dateLabel} · {selectedVenue?.area}, {selectedVenue?.city}</p>
        </div>
        <div className="sp-header-actions">
          <button id="refine-plan-btn" className="btn btn-ghost" onClick={() => setConversationalPanel(true)}>
            ✦ Refine with Agent 7
          </button>
          <button id="print-plan-btn" className="btn btn-ghost" onClick={() => window.print()}>
            ⎙ Print / Screenshot
          </button>
          <button id="save-plan-btn" className="btn btn-ghost" style={{ opacity: 0.5, cursor: 'not-allowed' }}>
            ↓ Save Plan
          </button>
          <button id="new-plan-btn" className="btn btn-gold" onClick={resetGeneration}>
            + New Plan
          </button>
        </div>
      </div>

      {/* ── Part 1: Quick Reference Strip ── */}
      <section className="sp-section">
        <h2 className="sp-section-title clash">Tonight at a Glance</h2>
        <div className="sp-qr-strip">
          {phases.map((p) => (
            <div key={p.label} className="sp-qr-cell">
              <div className="sp-qr-cell-top">
                <span className="sp-qr-dot" style={{ background: p.color }} />
                <span className="sp-qr-name">{p.label}</span>
                <span className="sp-qr-time">{p.timeRange}</span>
              </div>
              <div className="sp-qr-action">{QR_ACTION[p.label] ?? '—'}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Part 2 + 3: Phase Arc (replaces Night Arc + BPM sections) ── */}
      <section className="sp-section sp-phase-arc">
        <div className="sp-section-header">
          <h2 className="sp-section-title clash">Phase Arc</h2>
          {manualBoundaries && (
            <button className="sp-reset-btn" onClick={resetBoundaries}>Reset to equal splits</button>
          )}
        </div>

        {/* Energy Curve */}
        <div className="sp-curve-wrap">
          <EnergyCurve labels={phases.map(p => p.label)} />
        </div>

        {/* Phase cards + transition cards */}
        <div className="sp-phase-row">
          {phases.map((p, i) => {
            const rx = PHASE_PRESCRIPTIONS[p.label]
            const signals = PHASE_WATCH_SIGNALS[p.label] ?? []
            const dur = phaseDuration(p.startTimeStr, p.endTimeStr)
            const transKey = i < phases.length - 1 ? `${p.label}→${phases[i + 1].label}` : null
            const transList = transKey ? (PHASE_TRANSITIONS[transKey] ?? []) : null

            return (
              <div key={p.label} className="sp-phase-col">
                {/* Phase card */}
                <div
                  className="sp-phase-card-v2"
                  style={{ '--phase-color': p.color } as React.CSSProperties}
                >
                  {/* Color bar */}
                  <div className="sp-pc-bar" />

                  {/* Phase name + time */}
                  <div className="sp-pc-header">
                    <span className="sp-pc-name clash">{p.label}</span>
                    <span className="sp-pc-timerange">{p.timeRange}</span>
                  </div>
                  <span className="sp-pc-dur">{dur}</span>

                  <div className="sp-pc-divider" />

                  {/* BPM + music prescription */}
                  {rx ? (
                    <>
                      <div className="sp-pc-bpm">{rx.bpm} <span className="sp-pc-bpm-unit">BPM</span></div>
                      <div className="sp-pc-row"><span className="sp-pc-k">Chord</span><span className="sp-pc-v">{rx.chord}</span></div>
                      <div className="sp-pc-row"><span className="sp-pc-k">Key</span><span className="sp-pc-v">{rx.key}</span></div>
                      <div className="sp-pc-row"><span className="sp-pc-k">Sub-bass</span><span className="sp-pc-v">{rx.bass}</span></div>
                    </>
                  ) : (
                    <p className="sp-pc-v" style={{ opacity: 0.4 }}>No prescription</p>
                  )}

                  <div className="sp-pc-divider" />

                  {/* Watch For signals */}
                  <div className="sp-watch-label">WATCH FOR</div>
                  <ul className="sp-watch-list">
                    {signals.map((s, si) => (
                      <li key={si} className="sp-watch-item">{s}</li>
                    ))}
                  </ul>

                  {/* Boundary pill */}
                  {i < phases.length - 1 && (
                    <div className="sp-boundary-wrap">
                      {editingBoundary === i ? (
                        <input
                          type="time"
                          className="sp-boundary-input"
                          defaultValue={p.endTimeStr}
                          autoFocus
                          onBlur={(e) => handleBoundaryCommit(i, e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleBoundaryCommit(i, e.currentTarget.value)
                            if (e.key === 'Escape') setEditingBoundary(null)
                          }}
                        />
                      ) : (
                        <button
                          className="sp-boundary-btn"
                          title="Click to adjust boundary"
                          onClick={() => setEditingBoundary(i)}
                        >
                          {formatTimeStr(p.endTimeStr)} ▾
                        </button>
                      )}
                    </div>
                  )}
                </div>

                {/* Transition card — between this phase and next */}
                {transList && (
                  <div className="sp-transition-card">
                    <div className="sp-tc-top">
                      <span className="sp-tc-arrow">→</span>
                      <span className="sp-tc-label">TRANSITION</span>
                    </div>
                    <ul className="sp-tc-list">
                      {transList.map((t, ti) => (
                        <li key={ti} className="sp-tc-item">· {t}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </section>

      {/* ── 3c Intervention Decision Tree (unchanged) ── */}
      <section className="sp-section">
        <h2 className="sp-section-title clash">Intervention Decision Tree</h2>
        <div className="sp-interventions">
          {INTERVENTIONS.map((iv) => (
            <div key={iv.id} className="card sp-iv-card">
              <button
                id={`intervention-${iv.id}-toggle`}
                className="sp-iv-header"
                onClick={() => setExpandedIntervention(expandedIntervention === iv.id ? null : iv.id)}
              >
                <span className="sp-iv-label">
                  <span className="sp-iv-tag">IF</span>
                  {iv.trigger}
                </span>
                <span className="sp-iv-chevron">{expandedIntervention === iv.id ? '▲' : '▼'}</span>
              </button>
              {expandedIntervention === iv.id && (
                <div className="sp-iv-body fade-in">
                  <div className="sp-iv-row">
                    <span className="sp-iv-tag sp-iv-tag--do">DO</span>
                    <span>{iv.action}</span>
                  </div>
                  <div className="sp-iv-row">
                    <span className="sp-iv-tag sp-iv-tag--watch">WATCH</span>
                    <span>{iv.watch}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ── 3d Lighting Arc (unchanged) ── */}
      <section className="sp-section">
        <h2 className="sp-section-title clash">Lighting Arc</h2>
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="sp-table">
            <thead>
              <tr>
                <th>Phase</th>
                <th>Intensity</th>
                <th>Colour</th>
                <th>Movement</th>
              </tr>
            </thead>
            <tbody>
              {phases.map((p) => {
                const lt = PHASE_LIGHTING_DATA[p.label]
                if (!lt) return null
                return (
                  <tr key={p.label}>
                    <td className="sp-td-phase">{p.label}</td>
                    <td>{lt.intensity}</td>
                    <td>{lt.colour}</td>
                    <td>{lt.movement}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── 3e Staff Notes (unchanged) ── */}
      <section className="sp-section">
        <h2 className="sp-section-title clash">Staff Notes</h2>
        <div className="card sp-staff-card">
          <ul className="sp-staff-list">
            {STAFF_NOTES.map((note, i) => (
              <li key={i} className="sp-staff-item">{note}</li>
            ))}
          </ul>
        </div>
      </section>

      {/* ── Part 5: Prescription Reference (collapsed) ── */}
      <section className="sp-section">
        <button
          id="prescription-ref-toggle"
          className="sp-ref-toggle"
          onClick={() => setRefOpen(!refOpen)}
        >
          {refOpen ? '▼ Hide' : '▶ Show'} prescription reference
        </button>
        {refOpen && (
          <div className="card fade-in" style={{ padding: 0, overflow: 'hidden', marginTop: 10 }}>
            <table className="sp-table">
              <thead>
                <tr>
                  <th>Phase</th>
                  <th>Behavioral Target</th>
                  <th>Brainwave</th>
                </tr>
              </thead>
              <tbody>
                {phases.map((p) => {
                  const rx = PHASE_PRESCRIPTIONS[p.label]
                  if (!rx) return null
                  return (
                    <tr key={p.label}>
                      <td className="sp-td-phase">{p.label}</td>
                      <td style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>{rx.target}</td>
                      <td style={{ fontSize: 12.5, color: 'var(--src-counter)' }}>{rx.brainwave}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {conversationalPanelOpen && <ConversationalPanel />}
    </div>
  )
}
