import { useState } from 'react'
import { useSEStore } from '../store/seStore'
import { ConversationalPanel } from './ConversationalPanel'
import './ShowPlan.css'

// ── Mock data ────────────────────────────────────────────────────────────────

const PHASES = [
  { id: 'opening',   label: 'Opening',   time: '9–10 PM',    color: '#78716C', goal: 'Warm entry — ambient social priming' },
  { id: 'build',     label: 'Build',     time: '10–11 PM',   color: '#7C3AED', goal: 'Momentum shift — floor activation' },
  { id: 'peak',      label: 'Peak',      time: '11 PM–1 AM', color: '#E6D3A3', goal: 'Full release — sustained energy plateau' },
  { id: 'winddown',  label: 'Wind Down', time: '1–2 AM',     color: '#D97706', goal: 'Graceful close — spend drive' },
]

const PHASE_DETAIL = [
  {
    phase: 'Opening',
    bpm: '105–112',
    chord: 'I–IV–V',
    key: 'F major — Ionian',
    bass: '55–70Hz · nominal',
    target: 'Social priming, reduce inhibition threshold',
    brainwave: 'Low-alpha 8–9Hz',
  },
  {
    phase: 'Build',
    bpm: '118–124',
    chord: 'i–VII–VI–VII',
    key: 'A minor — Aeolian',
    bass: '60–80Hz +2dB',
    target: 'Momentum, floor activation, social engagement',
    brainwave: 'High-alpha 10–12Hz',
  },
  {
    phase: 'Peak',
    bpm: '128–134',
    chord: 'i–VII–VI–VII (8-bar cycles)',
    key: 'D minor — Dorian',
    bass: '65–85Hz +3dB + 40Hz rumble stack',
    target: 'Full motor activation, peak release, social proof lock-in',
    brainwave: 'Low-beta 14–16Hz',
  },
  {
    phase: 'Wind Down',
    bpm: '110–116',
    chord: 'I–V–vi–IV',
    key: 'G major — Mixolydian',
    bass: '55–65Hz · taper to nominal',
    target: 'Graceful energy reduction, increase dwell + spend',
    brainwave: 'Alpha bridge 9–10Hz',
  },
]

const INTERVENTIONS = [
  {
    id: 1,
    trigger: 'Dance floor occupancy < 30% after 30 mins into Build phase',
    action: 'Queue 2–3 familiar tracks in minor key at 124 BPM, 8-bar phrases',
    watch: 'First 2–3 movers step onto floor — hold steady, don\'t escalate yet',
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

const LIGHTING = [
  { phase: 'Opening',   intensity: '40%',  colour: 'Warm white',   movement: 'Slow pulse' },
  { phase: 'Build',     intensity: '60%',  colour: 'Blue / purple', movement: 'Medium sweep' },
  { phase: 'Peak',      intensity: '85%',  colour: 'Multi-colour',  movement: 'Fast strobe on drops' },
  { phase: 'Wind Down', intensity: '30%',  colour: 'Warm amber',    movement: 'Static' },
]

const STAFF_NOTES = [
  'Position 2 staff near the floor entrance during Build — creates social proof for reluctant dancers.',
  'Brief bar staff: upsell doubles and cocktails from 11 PM; peak phase correlates with peak spend intent.',
  'Increase table service pace during Wind Down — encourage spend before close.',
  'If a large group arrives during Peak, seat them near (not on) the dance floor — not at the back.',
  'Do not use over-the-mic announcements during Build or Peak — disrupts neuroacoustic continuity.',
]

// ── Component ─────────────────────────────────────────────────────────────────

export function ShowPlan() {
  const { selectedVenue, sessionContext, resetGeneration, setConversationalPanel, conversationalPanelOpen } = useSEStore()
  const [expandedIntervention, setExpandedIntervention] = useState<number | null>(null)

  const dateLabel = sessionContext.date
    ? new Date(sessionContext.date).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
    : ''

  function handlePrint() {
    window.print()
  }

  return (
    <div className="sp-root fade-in">
      {/* ── Header ── */}
      <div className="sp-header">
        <div className="sp-header-meta">
          <h1 className="sp-title clash">{selectedVenue?.name}</h1>
          <p className="sp-subtitle">{dateLabel} · {selectedVenue?.area}, {selectedVenue?.city}</p>
        </div>
        <div className="sp-header-actions">
          <button id="refine-plan-btn" className="btn btn-ghost" onClick={() => setConversationalPanel(true)}>
            ✦ Refine with Agent 7
          </button>
          <button id="print-plan-btn" className="btn btn-ghost" onClick={handlePrint}>
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

      {/* 3a — Night Arc Overview */}
      <section className="sp-section">
        <h2 className="sp-section-title clash">Night Arc</h2>
        <div className="sp-arc-strip">
          {PHASES.map((p, i) => (
            <div key={p.id} className="sp-arc-phase" style={{ '--phase-color': p.color } as React.CSSProperties}>
              <div className="sp-arc-time">{p.time}</div>
              <div className="sp-arc-label">{p.label}</div>
              <div className="sp-arc-goal">{p.goal}</div>
              {i < PHASES.length - 1 && <div className="sp-arc-arrow">→</div>}
            </div>
          ))}
        </div>
      </section>

      {/* 3b — BPM + Chord Arc */}
      <section className="sp-section">
        <h2 className="sp-section-title clash">BPM + Chord Arc</h2>
        <div className="sp-phase-grid">
          {PHASE_DETAIL.map((p) => (
            <div key={p.phase} className="card sp-phase-card">
              <div className="sp-phase-header">{p.phase}</div>
              <div className="sp-phase-bpm">{p.bpm} BPM</div>
              <div className="sp-kv">
                <span className="sp-k">Chord</span>
                <span className="sp-v">{p.chord}</span>
              </div>
              <div className="sp-kv">
                <span className="sp-k">Key</span>
                <span className="sp-v">{p.key}</span>
              </div>
              <div className="sp-kv">
                <span className="sp-k">Sub-bass</span>
                <span className="sp-v">{p.bass}</span>
              </div>
              <div className="sp-kv sp-kv--target">
                <span className="sp-k">Target</span>
                <span className="sp-v sp-v--target">{p.target}</span>
              </div>
              <div className="sp-kv">
                <span className="sp-k">Brainwave</span>
                <span className="sp-v sp-v--brain">{p.brainwave}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 3c — Intervention Decision Tree */}
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

      {/* 3d — Lighting Arc */}
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
              {LIGHTING.map((row) => (
                <tr key={row.phase}>
                  <td className="sp-td-phase">{row.phase}</td>
                  <td>{row.intensity}</td>
                  <td>{row.colour}</td>
                  <td>{row.movement}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 3e — Staff Notes */}
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

      {/* Conversational panel overlay */}
      {conversationalPanelOpen && <ConversationalPanel />}
    </div>
  )
}
