import { useEffect, useState } from 'react'
import { useSEStore } from '../store/seStore'
import './ShowHistory.css'

type OutcomeKey = 'exceeded' | 'met' | 'below' | 'no_review'

interface ShowRun {
  id: number
  venue_id: number
  venue_name: string
  area: string
  city: string
  plan_date: string | null
  version: number
  phase_count: number
  start_time: string
  end_time: string
  show_type: string | null
  generated_at: string | null
  finalized: boolean
  outcome: OutcomeKey
}

const OUTCOME_BADGE: Record<OutcomeKey, { label: string; cls: string }> = {
  exceeded:  { label: 'Exceeded',   cls: 'badge badge-ok' },
  met:       { label: 'Met plan',   cls: 'badge badge-watch' },
  below:     { label: 'Below plan', cls: 'badge badge-alert' },
  no_review: { label: 'No review',  cls: 'badge badge-stale' },
}

const SHOW_TYPE_DISPLAY: Record<string, string> = {
  dj_night:      'DJ night',
  live_band:     'Live band',
  open_mic:      'Open mic',
  private_event: 'Private event',
}

const SHOW_TYPE_OPTIONS = ['All types', 'DJ night', 'Live band', 'Open mic', 'Private event']
const OUTCOME_OPTIONS: Array<{ value: string; label: string }> = [
  { value: 'all',       label: 'All outcomes' },
  { value: 'exceeded',  label: 'Exceeded' },
  { value: 'met',       label: 'Met plan' },
  { value: 'below',     label: 'Below plan' },
  { value: 'no_review', label: 'No review' },
]

function formatPlanDate(isoDate: string | null): string {
  if (!isoDate) return '—'
  const d = new Date(isoDate + 'T00:00:00')
  return d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
}

function formatTime(hhmm: string): string {
  if (!hhmm) return ''
  const [hStr, mStr] = hhmm.split(':')
  const h = parseInt(hStr, 10)
  const m = parseInt(mStr ?? '0', 10)
  const period = h >= 12 ? 'PM' : 'AM'
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h
  return m === 0 ? `${h12} ${period}` : `${h12}:${String(m).padStart(2, '0')} ${period}`
}

function planSummary(run: ShowRun): string {
  const timeStr = `${formatTime(run.start_time)}–${formatTime(run.end_time)}`
  const phases = `${run.phase_count} phases`
  const type = run.show_type ? SHOW_TYPE_DISPLAY[run.show_type] ?? run.show_type : null
  return [type, phases, timeStr].filter(Boolean).join(' · ')
}

export function ShowHistory() {
  const { setNavSection, setPlanScreen, setHistoryScreen } = useSEStore()

  const [runs, setRuns] = useState<ShowRun[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [filterType, setFilterType] = useState('All types')
  const [filterOutcome, setFilterOutcome] = useState('all')

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetch('/api/show/runs')
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}: ${r.statusText}`)
        return r.json() as Promise<ShowRun[]>
      })
      .then((data) => { setRuns(data); setLoading(false) })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err)
        setError(msg)
        setLoading(false)
      })
  }, [])

  const filtered = runs.filter((e) => {
    const displayType = e.show_type ? SHOW_TYPE_DISPLAY[e.show_type] ?? e.show_type : null
    const typeOk = filterType === 'All types' || displayType === filterType
    const outcomeOk = filterOutcome === 'all' || e.outcome === filterOutcome
    return typeOk && outcomeOk
  })

  function handleNewPlan() {
    setNavSection('plan')
    setPlanScreen('venue_selector')
  }

  function handleLogReview() {
    setHistoryScreen('post_show_review')
  }

  return (
    <div className="sh-root fade-in">
      <div className="sh-header">
        <div>
          <h1 className="sh-title clash">Prior Shows</h1>
          <p className="sh-subtitle">Per-venue history of show plans and post-show outcomes.</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button id="log-review-standalone-btn" className="btn btn-ghost" onClick={handleLogReview}>
            + Log Post-Show Review
          </button>
          <button id="new-plan-from-history-btn" className="btn btn-gold" onClick={handleNewPlan}>
            + New Plan
          </button>
        </div>
      </div>

      {/* Filter bar */}
      <div className="card sh-filters">
        <div className="sh-filter-group">
          <span className="field-label" style={{ marginBottom: 0 }}>Show type</span>
          <div className="seg-control">
            {SHOW_TYPE_OPTIONS.map((t) => (
              <button
                key={t}
                id={`filter-type-${t.toLowerCase().replace(' ', '-')}`}
                className={`seg-btn${filterType === t ? ' active' : ''}`}
                onClick={() => setFilterType(t)}
              >{t}</button>
            ))}
          </div>
        </div>
        <div className="sh-filter-group">
          <span className="field-label" style={{ marginBottom: 0 }}>Outcome</span>
          <div className="seg-control">
            {OUTCOME_OPTIONS.map((o) => (
              <button
                key={o.value}
                id={`filter-outcome-${o.value}`}
                className={`seg-btn${filterOutcome === o.value ? ' active' : ''}`}
                onClick={() => setFilterOutcome(o.value)}
              >{o.label}</button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="sh-list">
        {loading && (
          <div className="sh-empty">Loading show history…</div>
        )}
        {!loading && error && (
          <div className="sh-empty" style={{ color: '#f87171' }}>
            Could not load history: {error}
          </div>
        )}
        {!loading && !error && runs.length === 0 && (
          <div className="sh-empty">
            No show plans yet.{' '}
            <button className="btn btn-gold" style={{ marginLeft: 8 }} onClick={handleNewPlan}>
              Generate your first plan →
            </button>
          </div>
        )}
        {!loading && !error && runs.length > 0 && filtered.length === 0 && (
          <div className="sh-empty">No sessions match the current filters.</div>
        )}
        {filtered.map((entry) => {
          const badge = OUTCOME_BADGE[entry.outcome]
          const isOpen = expandedId === entry.id
          return (
            <div key={entry.id} className={`card sh-entry${isOpen ? ' sh-entry--open' : ''}`}>
              <button
                id={`history-entry-${entry.id}`}
                className="sh-entry-header"
                onClick={() => setExpandedId(isOpen ? null : entry.id)}
              >
                <div className="sh-entry-left">
                  <div className="sh-entry-date">{formatPlanDate(entry.plan_date)}</div>
                  <div className="sh-entry-venue">{entry.venue_name}</div>
                  <div className="sh-entry-meta">
                    {[entry.area, entry.city].filter(Boolean).join(', ')}
                    {entry.show_type ? ` · ${SHOW_TYPE_DISPLAY[entry.show_type] ?? entry.show_type}` : ''}
                  </div>
                </div>
                <div className="sh-entry-right">
                  <span className={badge.cls}>{badge.label}</span>
                  <span className="sh-chevron">{isOpen ? '▲' : '▼'}</span>
                </div>
              </button>

              {isOpen && (
                <div className="sh-entry-body fade-in">
                  <div className="sh-entry-section">
                    <p className="sh-entry-k">Plan Summary</p>
                    <p className="sh-entry-v">{planSummary(entry)}</p>
                  </div>
                  {entry.outcome === 'no_review' && (
                    <div className="sh-entry-section">
                      <button
                        id={`log-review-btn-${entry.id}`}
                        className="btn btn-gold"
                        style={{ fontSize: 12 }}
                        onClick={handleLogReview}
                      >
                        + Log Post-Show Review
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
