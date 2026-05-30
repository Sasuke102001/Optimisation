import { useSEStore } from '../store/seStore'
import type { AgentStatus } from '../store/seStore'
import './PlanGeneration.css'

export function PlanGeneration() {
  const {
    agents,
    generationStatus,
    resetGeneration,
    selectedVenue,
    planOutput,
  } = useSEStore()

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
          <p className="field-label" style={{ marginBottom: 14 }}>Synthesis Stream</p>
          {generationStatus === 'complete' && planOutput ? (
            <pre className="pg-stream-output fade-in">{planOutput.rawBrief}</pre>
          ) : generationStatus === 'error' ? (
            <div className="pg-stream-error fade-in" style={{ padding: '20px 0' }}>
              <p className="error-text" style={{ color: '#ef4444', fontSize: '13px', lineHeight: '1.5' }}>
                {planOutput?.rawBrief || 'An error occurred during plan generation.'}
              </p>
            </div>
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
