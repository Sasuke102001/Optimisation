import { useState } from 'react'
import { useSEStore } from '../store/seStore'
import './ConversationalPanel.css'

const MOCK_AGENT7_RESPONSE = {
  heard: [
    'Crowd type → Corporate / older demographic',
    'Energy target → Moderate (not high-energy peak)',
    'Chord preference → likely major keys, less dissonant structures',
  ],
  summary:
    'This will adjust the BPM arc (peak capped at 126), chord choices (shift towards I–IV–V and major modes), and tone down strobe prescription.',
}

export function ConversationalPanel() {
  const { setConversationalPanel, setPlanScreen, startGeneration } = useSEStore()
  const [input, setInput] = useState('')
  const [submitted, setSubmitted] = useState(false)

  function handleSend() {
    if (!input.trim()) return
    setSubmitted(true)
  }

  function handleRegenerate() {
    setConversationalPanel(false)
    startGeneration()
    setPlanScreen('plan_generation')
  }

  function handleKeepCurrent() {
    setConversationalPanel(false)
  }

  return (
    <div className="cp-overlay">
      <div className="cp-backdrop" onClick={handleKeepCurrent} />

      <div className="cp-panel">
        {/* ── Panel header ── */}
        <div className="cp-header">
          <div>
            <p className="cp-label">Agent 7 — Conversational Guide</p>
            <p className="cp-hint">Type a refinement in natural language. Agent 7 will interpret and confirm before regenerating.</p>
          </div>
          <button id="close-conversational-panel-btn" className="btn btn-ghost cp-close" onClick={handleKeepCurrent}>
            ✕
          </button>
        </div>

        {/* ── Response card ── */}
        {submitted && (
          <div className="cp-response-card fade-in">
            <div className="cp-response-header">
              <span className="cp-agent-dot" />
              <span className="cp-agent-label">I heard:</span>
            </div>
            <ul className="cp-heard-list">
              {MOCK_AGENT7_RESPONSE.heard.map((h, i) => (
                <li key={i} className="cp-heard-item">• {h}</li>
              ))}
            </ul>
            <p className="cp-response-summary">{MOCK_AGENT7_RESPONSE.summary}</p>
            <p className="cp-response-cta">Regenerate plan with these changes?</p>
            <div className="cp-response-actions">
              <button id="confirm-regenerate-btn" className="btn btn-gold" onClick={handleRegenerate}>
                Yes, regenerate
              </button>
              <button id="keep-current-btn" className="btn btn-ghost" onClick={handleKeepCurrent}>
                No, keep current
              </button>
            </div>
          </div>
        )}

        {/* ── Input strip ── */}
        {!submitted && (
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
