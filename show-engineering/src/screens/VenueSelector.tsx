import { useMemo, useState, useEffect } from 'react'
import { useSEStore, computeDurationHint } from '../store/seStore'
import type { Venue } from '../store/seStore'
import './VenueSelector.css'

const PHASE_COUNTS = [2, 3, 4, 5] as const

const CROWD_SIZES = [
  { value: 'intimate', label: 'Intimate (<50)' },
  { value: 'medium',   label: 'Medium (50–150)' },
  { value: 'large',    label: 'Large (150+)' },
] as const

const CROWD_TYPES = [
  { value: 'regular',   label: 'Regular crowd' },
  { value: 'corporate', label: 'Corporate event' },
  { value: 'college',   label: 'College crowd' },
  { value: 'mixed',     label: 'Mixed' },
] as const

const SHOW_TYPES = [
  { value: 'dj_night',      label: 'DJ night' },
  { value: 'live_band',     label: 'Live band' },
  { value: 'open_mic',      label: 'Open mic' },
  { value: 'private_event', label: 'Private event' },
] as const

export function VenueSelector() {
  const {
    venueSearch, setVenueSearch,
    selectedVenue, selectVenue, clearVenue,
    sessionContext, setSessionContext,
    setPlanScreen, startGeneration,
  } = useSEStore()

  const [venues, setVenues] = useState<Venue[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    fetch('/api/venues')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch')
        return res.json()
      })
      .then((data) => {
        if (active) {
          setVenues(data)
          setLoading(false)
        }
      })
      .catch(() => {
        if (active) {
          setError('Could not load venues')
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [])

  const filtered = useMemo(() => {
    if (!venueSearch.trim()) return venues
    const q = venueSearch.toLowerCase()
    return venues.filter(
      (v) => v.name.toLowerCase().includes(q) || v.area.toLowerCase().includes(q) || v.city.toLowerCase().includes(q)
    )
  }, [venueSearch, venues])

  const canGenerate = !!(selectedVenue && sessionContext.date)

  const durationHint = useMemo(
    () => computeDurationHint(sessionContext.startTime, sessionContext.endTime, sessionContext.phaseCount),
    [sessionContext.startTime, sessionContext.endTime, sessionContext.phaseCount],
  )

  function handleGenerate() {
    if (!canGenerate) return
    startGeneration()
    setPlanScreen('plan_generation')
  }

  return (
    <div className="vs-root fade-in">
      <div className="vs-header">
        <h1 className="vs-title clash">Show Engineering</h1>
        <p className="vs-subtitle">Select a venue and configure session context to generate your show plan.</p>
      </div>

      <div className="vs-body">
        {/* ── Venue selector column ── */}
        <div className="vs-left">
          <div className="card vs-search-card">
            <label className="field-label">Venue</label>

            {selectedVenue ? (
              <SelectedVenueBanner venue={selectedVenue} onClear={clearVenue} />
            ) : (
              <>
                <div className="vs-search-wrap">
                  <span className="vs-search-icon">🔍</span>
                  <input
                    id="venue-search-input"
                    className="field-input vs-search-input"
                    placeholder="Search venue by name or area…"
                    value={venueSearch}
                    onChange={(e) => setVenueSearch(e.target.value)}
                    autoComplete="off"
                  />
                </div>
                <div className="vs-venue-list">
                  {loading ? (
                    <p className="vs-empty">Loading venues...</p>
                  ) : error ? (
                    <p className="vs-empty" style={{ color: '#ef4444' }}>{error}</p>
                  ) : filtered.length === 0 ? (
                    <p className="vs-empty">No venues match "{venueSearch}"</p>
                  ) : (
                    filtered.map((v) => (
                      <VenueCard key={v.id} venue={v} onSelect={selectVenue} />
                    ))
                  )}
                </div>
              </>
            )}
          </div>
        </div>

        {/* ── Context form column ── */}
        <div className="vs-right">
          {selectedVenue && (
            <div className="card vs-context-card fade-in">
              <p className="field-label" style={{ marginBottom: 16 }}>Session Context</p>

              {/* Date */}
              <div className="vs-field">
                <label className="field-label" htmlFor="show-date">Show Date</label>
                <input
                  id="show-date"
                  type="date"
                  className="field-input"
                  value={sessionContext.date}
                  onChange={(e) => setSessionContext({ date: e.target.value })}
                />
              </div>

              {/* Show times */}
              <div className="vs-field">
                <label className="field-label">Show Times</label>
                <div className="vs-time-row">
                  <div className="vs-time-field">
                    <span className="vs-time-label">Start</span>
                    <input
                      id="show-start-time"
                      type="time"
                      className="field-input"
                      value={sessionContext.startTime}
                      onChange={(e) => setSessionContext({ startTime: e.target.value })}
                    />
                  </div>
                  <span className="vs-time-sep">→</span>
                  <div className="vs-time-field">
                    <span className="vs-time-label">End</span>
                    <input
                      id="show-end-time"
                      type="time"
                      className="field-input"
                      value={sessionContext.endTime}
                      onChange={(e) => setSessionContext({ endTime: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              {/* Phase count */}
              <div className="vs-field">
                <label className="field-label">Phases</label>
                <div className="seg-control" style={{ width: '100%' }}>
                  {PHASE_COUNTS.map((n) => (
                    <button
                      key={n}
                      id={`phase-count-${n}`}
                      className={`seg-btn${sessionContext.phaseCount === n ? ' active' : ''}`}
                      style={{ flex: 1 }}
                      onClick={() => setSessionContext({ phaseCount: n })}
                    >{n}</button>
                  ))}
                </div>
                <p className="vs-duration-hint">{durationHint}</p>
              </div>

              {/* Crowd size */}
              <div className="vs-field">
                <label className="field-label">Expected Crowd Size</label>
                <div className="seg-control" style={{ width: '100%', justifyContent: 'stretch' }}>
                  {CROWD_SIZES.map((o) => (
                    <button
                      key={o.value}
                      id={`crowd-size-${o.value}`}
                      className={`seg-btn${sessionContext.crowdSize === o.value ? ' active' : ''}`}
                      style={{ flex: 1 }}
                      onClick={() => setSessionContext({ crowdSize: o.value })}
                    >{o.label}</button>
                  ))}
                </div>
              </div>

              {/* Crowd type */}
              <div className="vs-field">
                <label className="field-label">Crowd Type</label>
                <div className="seg-control" style={{ width: '100%' }}>
                  {CROWD_TYPES.map((o) => (
                    <button
                      key={o.value}
                      id={`crowd-type-${o.value}`}
                      className={`seg-btn${sessionContext.crowdType === o.value ? ' active' : ''}`}
                      style={{ flex: 1 }}
                      onClick={() => setSessionContext({ crowdType: o.value })}
                    >{o.label}</button>
                  ))}
                </div>
              </div>

              {/* Show type */}
              <div className="vs-field">
                <label className="field-label">Show Type</label>
                <div className="seg-control" style={{ width: '100%' }}>
                  {SHOW_TYPES.map((o) => (
                    <button
                      key={o.value}
                      id={`show-type-${o.value}`}
                      className={`seg-btn${sessionContext.showType === o.value ? ' active' : ''}`}
                      style={{ flex: 1 }}
                      onClick={() => setSessionContext({ showType: o.value })}
                    >{o.label}</button>
                  ))}
                </div>
              </div>

              {/* Notes */}
              <div className="vs-field">
                <label className="field-label" htmlFor="show-notes">Notes <span style={{ opacity: 0.5, fontWeight: 400 }}>(optional)</span></label>
                <textarea
                  id="show-notes"
                  className="field-textarea"
                  placeholder="e.g. Tonight skews older, corporate crowd…"
                  value={sessionContext.notes}
                  onChange={(e) => setSessionContext({ notes: e.target.value })}
                />
              </div>

              <button
                id="generate-plan-btn"
                className="btn btn-gold"
                style={{ width: '100%', marginTop: 8, fontSize: 13.5, padding: '11px 0' }}
                disabled={!canGenerate}
                onClick={handleGenerate}
              >
                ✦ Generate Show Plan
              </button>
              {!sessionContext.date && (
                <p className="vs-hint">Set a show date to enable generation.</p>
              )}
            </div>
          )}

          {!selectedVenue && (
            <div className="vs-empty-right">
              <div className="vs-empty-glyph">✦</div>
              <p>Select a venue to configure your session context.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function VenueCard({ venue, onSelect }: { venue: Venue; onSelect: (v: Venue) => void }) {
  return (
    <button
      id={`venue-card-${venue.id}`}
      className="vs-venue-card"
      onClick={() => onSelect(venue)}
    >
      <div className="vs-venue-name">{venue.name}</div>
      <div className="vs-venue-meta">
        {venue.area} · {venue.city}
        <span className="vs-venue-types">
          {(venue.display_tags ?? venue.types).map((t) => (
            <span key={t} className="vs-type-chip">{t.replace(/_/g, ' ')}</span>
          ))}
        </span>
      </div>
    </button>
  )
}

function SelectedVenueBanner({ venue, onClear }: { venue: Venue; onClear: () => void }) {
  return (
    <div className="vs-selected-banner">
      <div className="vs-selected-glyph">●</div>
      <div className="vs-selected-info">
        <div className="vs-selected-name">{venue.name}</div>
        <div className="vs-selected-area">{venue.area} · {venue.city}</div>
      </div>
      <button id="clear-venue-btn" className="btn btn-ghost" style={{ padding: '6px 12px', fontSize: 12 }} onClick={onClear}>
        Change
      </button>
    </div>
  )
}
