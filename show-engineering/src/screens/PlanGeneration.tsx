import { useEffect, useRef } from 'react'
import { useSEStore } from '../store/seStore'
import type { AgentStatus, StreamEntry } from '../store/seStore'
import './PlanGeneration.css'

export function PlanGeneration() {
  const {
    agents,
    generationStatus,
    resetGeneration,
    selectedVenue,
    streamLog,
    synthesisBuf,
  } = useSEStore()

  const streamEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll stream area as content arrives
  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [streamLog, synthesisBuf])

  const hasStream = streamLog.length > 0 || synthesisBuf.length > 0

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
            <div className={`pg-stage${generationStatus === 'stage_1_running' ? ' pg-stage--active' : generationStatus !== 'idle' && generationStatus !== 'error' ? ' pg-stage--done' : ''}`}>
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
          <p className="field-label" style={{ marginBottom: 14 }}>Council Stream</p>

          {generationStatus === 'error' && !hasStream ? (
            <p className="error-text" style={{ color: '#ef4444', fontSize: '13px' }}>
              An error occurred during plan generation.
            </p>
          ) : hasStream ? (
            <div className="pg-stream-log">
              {streamLog.map((entry, i) => (
                <StreamLogEntry key={i} entry={entry} />
              ))}
              {synthesisBuf && (
                <div className="pg-stream-synthesis">
                  <span className="pg-stream-label pg-stream-label--synthesis">SYNTHESIS</span>
                  <div className="pg-synthesis-generating">
                    <div className="pg-stream-spinner" />
                    <span>Generating show plan…</span>
                  </div>
                </div>
              )}
              <div ref={streamEndRef} />
            </div>
          ) : (
            <div className="pg-stream-placeholder">
              <div className="pg-stream-spinner" />
              <p>Connecting to Council…</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Stream log entry ──────────────────────────────────────────────────────────

function StreamLogEntry({ entry }: { entry: StreamEntry }) {
  if (entry.type === 'status') {
    return (
      <div className="pg-stream-entry pg-stream-entry--status">
        <span className="pg-stream-dot" />
        <span>{entry.text}</span>
      </div>
    )
  }

  if (entry.type === 'r1') {
    return (
      <div className="pg-stream-entry pg-stream-entry--r1">
        <div className="pg-stream-entry-header">
          <span className="pg-stream-label pg-stream-label--r1">R1 PROPOSAL</span>
          {entry.meta && (
            <span className="pg-stream-badge">{entry.meta}</span>
          )}
        </div>
        <p className="pg-stream-entry-text">{entry.text}</p>
      </div>
    )
  }

  if (entry.type === 'r2') {
    return (
      <div className="pg-stream-entry pg-stream-entry--r2">
        <div className="pg-stream-entry-header">
          <span className="pg-stream-label pg-stream-label--r2">R2 CHALLENGE</span>
          {entry.meta && (
            <span className={`pg-stream-badge pg-stream-badge--${entry.meta.toLowerCase()}`}>
              {entry.meta}
            </span>
          )}
        </div>
        <p className="pg-stream-entry-text">{entry.text}</p>
      </div>
    )
  }

  if (entry.type === 'synthesis_start') {
    return (
      <div className="pg-stream-entry pg-stream-entry--status">
        <span className="pg-stream-dot pg-stream-dot--gold" />
        <span>{entry.text}</span>
      </div>
    )
  }

  return null
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
