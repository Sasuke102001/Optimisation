import { useState } from 'react'
import { useSEStore } from '../store/seStore'
import './ConversationalPanel.css'

export function ConversationalPanel() {
  const {
    setConversationalPanel, setPlanScreen, startGeneration,
    sendToAgent7, applyAgent7Patch, clearAgent7,
    agent7Response, agent7Loading,
    selectedVenue,
  } = useSEStore()

  const [input, setInput] = useState('')

  function handleSend() {
    if (!input.trim() || agent7Loading) return
    sendToAgent7(input.trim())
  }

  function handleRegenerate() {
    applyAgent7Patch()
    setConversationalPanel(false)
    startGeneration()
    setPlanScreen('plan_generation')
  }

  function handleKeepCurrent() {
    clearAgent7()
    setConversationalPanel(false)
  }

  const response = agent7Response
  const showInput = !response && !agent7Loading

  return (
    <div className="cp-overlay">
      <div className="cp-backdrop" onClick={handleKeepCurrent} />

      <div className="cp-panel">
        {/* ── Header ── */}
        <div className="cp-header">
          <div>
            <p className="cp-label">Conversational Guide</p>
            <p className="cp-hint">
              {selectedVenue?.name} — type a refinement in plain language. The guide will
              interpret and confirm before regenerating.
            </p>
          </div>
          <button
            id="close-conversational-panel-btn"
            className="btn btn-ghost cp-close"
            onClick={handleKeepCurrent}
          >
            ✕
          </button>
        </div>

        {/* ── Loading state ── */}
        {agent7Loading && (
          <div className="cp-loading fade-in">
            <div className="cp-loading-spinner" />
            <span>Interpreting…</span>
          </div>
        )}

        {/* ── Response card ── */}
        {response && (
          <div className="cp-response-card fade-in">
            {response.explanation_only ? (
              <>
                <div className="cp-response-header">
                  <span className="cp-agent-dot" />
                  <span className="cp-agent-label">Agent 7</span>
                  <span className="cp-confidence-badge cp-confidence-badge--{response.confidence.toLowerCase()}">{response.confidence}</span>
                </div>
                <p className="cp-response-summary" style={{ borderTop: 'none', paddingTop: 0 }}>
                  {response.summary}
                </p>
                <div className="cp-response-actions">
                  <button id="keep-current-btn" className="btn btn-ghost" onClick={handleKeepCurrent}>
                    Close
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="cp-response-header">
                  <span className="cp-agent-dot" />
                  <span className="cp-agent-label">I heard:</span>
                  <span className={`cp-confidence-badge cp-confidence-badge--${response.confidence.toLowerCase()}`}>
                    {response.confidence}
                  </span>
                </div>
                {response.heard.length > 0 && (
                  <ul className="cp-heard-list">
                    {response.heard.map((h, i) => (
                      <li key={i} className="cp-heard-item">• {h}</li>
                    ))}
                  </ul>
                )}
                <p className="cp-response-summary">{response.summary}</p>
                {response.requires_regeneration ? (
                  <>
                    <p className="cp-response-cta">Regenerate plan with these changes?</p>
                    <div className="cp-response-actions">
                      <button id="confirm-regenerate-btn" className="btn btn-gold" onClick={handleRegenerate}>
                        Yes, regenerate
                      </button>
                      <button id="keep-current-btn" className="btn btn-ghost" onClick={handleKeepCurrent}>
                        No, keep current
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="cp-response-actions">
                    <button id="keep-current-btn" className="btn btn-ghost" onClick={handleKeepCurrent}>
                      Close
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ── Input strip ── */}
        {showInput && (
          <div className="cp-input-strip fade-in">
            <textarea
              id="agent7-input"
              className="field-textarea cp-textarea"
              placeholder='e.g. "Tonight skews older, more corporate crowd, less energetic"'
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSend()
              }}
            />
            <button
              id="agent7-send-btn"
              className="btn btn-gold"
              disabled={!input.trim()}
              onClick={handleSend}
            >
              Send ↵
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
