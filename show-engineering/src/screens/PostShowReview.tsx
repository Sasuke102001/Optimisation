import { useState } from 'react'
import './PostShowReview.css'

const MOCK_SESSIONS = [
  { id: 1, label: 'Todi Mill Social — Sat 21 Jun 2025 (DJ night)' },
  { id: 2, label: 'Kitty Su — Fri 14 Jun 2025 (Private event)' },
]

const PHASES = ['Opening', 'Build', 'Peak', 'Wind Down']

const INTERVENTIONS_LIST = [
  'Queued familiar tracks — floor occupancy < 30%',
  'Introduced sub-bass hook during energy dip',
  'Dropped BPM during Wind Down to drive settle',
]

export function PostShowReview() {
  const [selectedSession, setSelectedSession] = useState('')
  const [phaseSignals, setPhaseSignals] = useState<Record<string, string>>({})
  const [deployedInterventions, setDeployedInterventions] = useState<Set<number>>(new Set())
  const [signalConfirmed, setSignalConfirmed] = useState<Record<string, string>>({})
  const [overallRating, setOverallRating] = useState('')
  const [notes, setNotes] = useState('')

  function toggleIntervention(i: number) {
    setDeployedInterventions((prev) => {
      const next = new Set(prev)
      if (next.has(i)) next.delete(i); else next.add(i)
      return next
    })
  }

  const hasSession = !!selectedSession

  return (
    <div className="psr-root fade-in">
      <div className="psr-header">
        <h1 className="psr-title clash">Post-Show Review</h1>
        <p className="psr-subtitle">Compare plan vs actual KPI data and log outcome for the M3 database.</p>
      </div>

      {/* Session selector */}
      <div className="card psr-session-select">
        <label className="field-label" htmlFor="session-select">Session</label>
        <select
          id="session-select"
          className="field-select"
          value={selectedSession}
          onChange={(e) => setSelectedSession(e.target.value)}
        >
          <option value="">— Select a session —</option>
          {MOCK_SESSIONS.map((s) => (
            <option key={s.id} value={String(s.id)}>{s.label}</option>
          ))}
        </select>
      </div>

      {hasSession && (
        <div className="psr-body fade-in">
          {/* Comparison columns */}
          <div className="psr-cols">
            <div className="psr-col-header psr-col-plan">Plan</div>
            <div className="psr-col-header psr-col-actual">Actual</div>
          </div>

          {PHASES.map((phase) => (
            <div key={phase} className="card psr-phase-row">
              <div className="psr-phase-label">{phase}</div>
              <div className="psr-phase-cols">
                {/* Plan side */}
                <div className="psr-plan-side">
                  <div className="psr-kv">
                    <span className="psr-k">BPM Range</span>
                    <span className="psr-v">{phase === 'Opening' ? '105–112' : phase === 'Build' ? '118–124' : phase === 'Peak' ? '128–134' : '110–116'}</span>
                  </div>
                  <div className="psr-kv">
                    <span className="psr-k">Crowd target</span>
                    <span className="psr-v">{phase === 'Opening' ? 'Social priming' : phase === 'Build' ? 'Floor activation' : phase === 'Peak' ? 'Peak release' : 'Dwell + spend'}</span>
                  </div>
                </div>

                {/* Actual side */}
                <div className="psr-actual-side">
                  <div className="psr-kv">
                    <span className="psr-k">Observed energy signal</span>
                    <select
                      id={`phase-signal-${phase.toLowerCase().replace(' ', '-')}`}
                      className="field-select"
                      value={phaseSignals[phase] || ''}
                      onChange={(e) => setPhaseSignals((prev) => ({ ...prev, [phase]: e.target.value }))}
                    >
                      <option value="">— Select —</option>
                      <option value="above">Above plan</option>
                      <option value="on_plan">On plan</option>
                      <option value="below">Below plan</option>
                    </select>
                  </div>
                  <div className="psr-kv">
                    <span className="psr-k">Signal confirmed plan?</span>
                    <div className="seg-control">
                      {['Yes', 'Partially', 'No'].map((v) => (
                        <button
                          key={v}
                          id={`confirm-${phase.toLowerCase().replace(' ', '-')}-${v.toLowerCase()}`}
                          className={`seg-btn${signalConfirmed[phase] === v ? ' active' : ''}`}
                          onClick={() => setSignalConfirmed((prev) => ({ ...prev, [phase]: v }))}
                        >{v}</button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Interventions deployed */}
          <div className="card psr-interventions">
            <p className="field-label" style={{ marginBottom: 12 }}>Interventions Deployed</p>
            {INTERVENTIONS_LIST.map((label, i) => (
              <label key={i} id={`intervention-deployed-${i}`} className="psr-check-row">
                <input
                  type="checkbox"
                  className="psr-checkbox"
                  checked={deployedInterventions.has(i)}
                  onChange={() => toggleIntervention(i)}
                />
                <span>{label}</span>
              </label>
            ))}
          </div>

          {/* Overall rating */}
          <div className="card psr-outcome">
            <p className="field-label" style={{ marginBottom: 12 }}>Overall Outcome</p>
            <div className="seg-control psr-seg">
              {(['Exceeded plan', 'Met plan', 'Below plan'] as const).map((r) => (
                <button
                  key={r}
                  id={`outcome-${r.toLowerCase().replace(' ', '-')}`}
                  className={`seg-btn${overallRating === r ? ' active' : ''}`}
                  onClick={() => setOverallRating(r)}
                >{r}</button>
              ))}
            </div>
          </div>

          {/* Notes */}
          <div className="card">
            <label className="field-label" htmlFor="review-notes">Notes</label>
            <textarea
              id="review-notes"
              className="field-textarea"
              placeholder="Any observations, anomalies, or context for this session…"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              style={{ minHeight: 100 }}
            />
          </div>

          <button
            id="save-outcome-btn"
            className="btn btn-gold"
            style={{ opacity: 0.5, cursor: 'not-allowed', width: '100%', padding: '12px 0' }}
          >
            ↓ Save Outcome (backend not wired)
          </button>
        </div>
      )}
    </div>
  )
}
