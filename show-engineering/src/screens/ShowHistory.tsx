import { useState } from 'react'
import { useSEStore } from '../store/seStore'
import './ShowHistory.css'

type OutcomeKey = 'exceeded' | 'met' | 'below' | 'no_review'

interface HistoryEntry {
  id: number
  date: string
  venue: string
  area: string
  showType: string
  outcome: OutcomeKey
  planSummary: string
  outcomeNotes: string
}

const MOCK_HISTORY: HistoryEntry[] = [
  {
    id: 1,
    date: 'Sat 21 Jun 2025',
    venue: 'Todi Mill Social',
    area: 'Lower Parel, Mumbai',
    showType: 'DJ night',
    outcome: 'exceeded',
    planSummary: 'BPM arc 105→134→110. Peak phase sustained from 11 PM–1 AM. Sub-bass stack deployed at 11:40 PM. Floor occupancy exceeded projections by ~18% at peak.',
    outcomeNotes: 'Corporate group arrived at 11 PM — seated near floor per staff notes. Worked well. Will replicate seating strategy.',
  },
  {
    id: 2,
    date: 'Fri 14 Jun 2025',
    venue: 'Kitty Su',
    area: 'Lower Parel, Mumbai',
    showType: 'Private event',
    outcome: 'met',
    planSummary: 'Private corporate event. BPM arc capped at 126 (corporate preset). Chord structure shifted to major modes throughout.',
    outcomeNotes: 'Client was satisfied. Bar spend above average. Floor not heavily used — expected for corporate format.',
  },
  {
    id: 3,
    date: 'Sat 7 Jun 2025',
    venue: 'Todi Mill Social',
    area: 'Lower Parel, Mumbai',
    showType: 'DJ night',
    outcome: 'below',
    planSummary: 'Intervention 1 triggered at 10:40 PM (floor < 30%). Recovery partial — floor reached ~45% peak occupancy vs 70% target.',
    outcomeNotes: 'Competing venue had a big event same night. External crowd draw reduced walk-in flow. Note for future: check city event calendar.',
  },
  {
    id: 4,
    date: 'Fri 30 May 2025',
    venue: 'Aer',
    area: 'Worli, Mumbai',
    showType: 'Live band',
    outcome: 'no_review',
    planSummary: 'Live band set with BPM arc 100–120. Chord structure advisory only — band played own set.',
    outcomeNotes: '',
  },
]

const OUTCOME_BADGE: Record<OutcomeKey, { label: string; cls: string }> = {
  exceeded:  { label: 'Exceeded',  cls: 'badge badge-ok' },
  met:       { label: 'Met plan',  cls: 'badge badge-watch' },
  below:     { label: 'Below plan', cls: 'badge badge-alert' },
  no_review: { label: 'No review', cls: 'badge badge-stale' },
}

const SHOW_TYPE_OPTIONS = ['All types', 'DJ night', 'Private event', 'Live band', 'Open mic']
const OUTCOME_OPTIONS: Array<{ value: string; label: string }> = [
  { value: 'all',       label: 'All outcomes' },
  { value: 'exceeded',  label: 'Exceeded' },
  { value: 'met',       label: 'Met plan' },
  { value: 'below',     label: 'Below plan' },
  { value: 'no_review', label: 'No review' },
]

export function ShowHistory() {
  const { setNavSection, setPlanScreen } = useSEStore()
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [filterType, setFilterType] = useState('All types')
  const [filterOutcome, setFilterOutcome] = useState('all')

  const filtered = MOCK_HISTORY.filter((e) => {
    const typeOk = filterType === 'All types' || e.showType === filterType
    const outcomeOk = filterOutcome === 'all' || e.outcome === filterOutcome
    return typeOk && outcomeOk
  })

  function handleNewPlan() {
    setNavSection('plan')
    setPlanScreen('venue_selector')
  }

  return (
    <div className="sh-root fade-in">
      <div className="sh-header">
        <div>
          <h1 className="sh-title clash">Prior Shows</h1>
          <p className="sh-subtitle">Per-venue history of show plans and post-show outcomes.</p>
        </div>
        <button id="new-plan-from-history-btn" className="btn btn-gold" onClick={handleNewPlan}>
          + New Plan
        </button>
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

      {/* Session list */}
      <div className="sh-list">
        {filtered.length === 0 && (
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
                  <div className="sh-entry-date">{entry.date}</div>
                  <div className="sh-entry-venue">{entry.venue}</div>
                  <div className="sh-entry-meta">{entry.area} · {entry.showType}</div>
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
                    <p className="sh-entry-v">{entry.planSummary}</p>
                  </div>
                  {entry.outcomeNotes && (
                    <div className="sh-entry-section">
                      <p className="sh-entry-k">Outcome Notes</p>
                      <p className="sh-entry-v">{entry.outcomeNotes}</p>
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
