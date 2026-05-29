import { useEffect, useRef } from 'react'
import { useSEStore } from '../store/seStore'
import type { AgentStatus } from '../store/seStore'
import './PlanGeneration.css'

// Simulated timing for each agent (ms from start)
const STAGE1_DELAYS: Record<number, number> = { 1: 800, 2: 1100, 3: 900, 4: 1300 }
const STAGE2_DELAYS: Record<number, number> = { 5: 1800, 6: 2600 }

const MOCK_PLAN_FRAGMENT = `
## Night Arc — Todi Mill Social · Saturday, 21 Jun 2025

**Opening Phase** (9:00–10:00 PM) — Warm entry, ambient social priming
- BPM: 105–112 · Key: F major · Mode: Ionian
- Sub-bass: 55–70Hz at nominal, no boost
- Brainwave target: Low-alpha 8–9Hz (relaxed, aware)

**Build Phase** (10:00–11:00 PM) — Momentum shift, floor activation
- BPM: 118–124 · Key: A minor · Mode: Aeolian
- Sub-bass: 60–80Hz +2dB
- Brainwave target: High-alpha 10–12Hz (socially engaged)

**Peak Phase** (11:00 PM–1:00 AM) — Full release, sustained energy
- BPM: 128–134 · Key: D minor · Mode: Dorian
- Sub-bass: 65–85Hz +3dB, stacked with 40Hz rumble
- Brainwave target: Low-beta 14–16Hz (motor priming)
- Chord structure: i–VII–VI–VII cycling 8-bar phrases

**Wind Down Phase** (1:00–2:00 AM) — Graceful close
- BPM: 110–116 · Key: G major · Mode: Mixolydian
- Sub-bass: taper to 55–65Hz, nominal
- Brainwave target: Alpha bridge 9–10Hz
`.trim()

export function PlanGeneration() {
  const {
    agents, updateAgentStatus,
    generationStatus, setGenerationStatus,
    setPlanScreen, resetGeneration, selectedVenue,
  } = useSEStore()

  const ranRef = useRef(false)

  useEffect(() => {
    if (ranRef.current) return
    ranRef.current = true

    // Stage 1 — agents 1–4 run in parallel
    ;[1, 2, 3, 4].forEach((id) => {
      updateAgentStatus(id, 'running')
      setTimeout(() => updateAgentStatus(id, 'done'), STAGE1_DELAYS[id])
    })

    // After stage 1 completes → start stage 2
    const stage1Done = Math.max(...Object.values(STAGE1_DELAYS))
    setTimeout(() => {
      setGenerationStatus('stage_2_running')
      ;[5, 6].forEach((id) => {
        setTimeout(() => updateAgentStatus(id, 'running'), 0)
        setTimeout(
          () => updateAgentStatus(id, 'done'),
          STAGE2_DELAYS[id] - STAGE1_DELAYS[4]
        )
      })
    }, stage1Done)

    // Complete
    const total = stage1Done + STAGE2_DELAYS[6]
    setTimeout(() => {
      setGenerationStatus('complete')
      setTimeout(() => setPlanScreen('show_plan'), 600)
    }, total)

  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="pg-root fade-in">
      <div className="pg-header">
        <div className="pg-header-left">
          <h1 className="pg-title clash">Generating Plan</h1>
          <p className="pg-subtitle">
            {selectedVenue?.name} — 7 agents deliberating
          </p>
        </div>
        <button
          id="cancel-generation-btn"
          className="btn btn-danger"
          onClick={resetGeneration}
        >
          ✕ Cancel
        </button>
      </div>

      <div className="pg-body">
        {/* Agent progress list */}
        <div className="card pg-agent-card">
          <p className="field-label" style={{ marginBottom: 14 }}>Agent Progress</p>
          <div className="pg-agent-list">
            {agents.map((a, i) => (
              <div
                key={a.id}
                className={`pg-agent-row${a.status !== 'waiting' ? ' pg-agent-row--active' : ''}`}
                style={{ animationDelay: `${i * 0.04}s` }}
              >
                <AgentStatusDot status={a.status} />
                <div className="pg-agent-info">
                  <span className="pg-agent-name">{a.name}</span>
                  <span className="pg-agent-role">{a.role}</span>
                </div>
                <span className="pg-agent-status-label">
                  {a.status === 'waiting' ? '◌ waiting' : a.status === 'running' ? '● running' : '✓ done'}
                </span>
              </div>
            ))}
          </div>

          <div className="pg-stage-info">
            <div className={`pg-stage${generationStatus === 'stage_1_running' ? ' pg-stage--active' : generationStatus !== 'idle' ? ' pg-stage--done' : ''}`}>
              <span className="pg-stage-dot" />
              Stage 1 — Parallel KAG/RAG
            </div>
            <div className="pg-stage-arrow">→</div>
            <div className={`pg-stage${generationStatus === 'stage_2_running' ? ' pg-stage--active' : generationStatus === 'complete' ? ' pg-stage--done' : ''}`}>
              <span className="pg-stage-dot" />
              Stage 2 — Integration + Prescription
            </div>
          </div>
        </div>

        {/* Synthesis stream area */}
        <div className="card pg-stream-card">
          <p className="field-label" style={{ marginBottom: 14 }}>Synthesis Stream</p>
          {generationStatus === 'complete' ? (
            <pre className="pg-stream-output fade-in">{MOCK_PLAN_FRAGMENT}</pre>
          ) : (
            <div className="pg-stream-placeholder">
              <div className="pg-stream-spinner" />
              <p>
                {generationStatus === 'stage_1_running'
                  ? 'Agents 1–4 gathering behavioral and neuroacoustic context…'
                  : 'Agents 5–6 integrating and prescribing show plan…'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Dot component ─────────────────────────────────────────────────────────────

function AgentStatusDot({ status }: { status: AgentStatus }) {
  return (
    <span
      className={`pg-dot pg-dot--${status}`}
      aria-label={status}
    />
  )
}
