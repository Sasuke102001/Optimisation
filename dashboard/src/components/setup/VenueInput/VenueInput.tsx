import { useState, useEffect, useRef } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import styles from './VenueInput.module.css';

interface Venue {
  id: number;
  name: string;
  area: string;
  city: string;
  types: string[];
}

export function VenueInput() {
  const { session, venueRecallHint, venueRecallColor, onVenueNameInput, selectVenue } = useSessionStore();
  const [venues, setVenues] = useState<Venue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://20.219.216.138';
    let active = true;
    fetch(`${BASE_URL}/api/venues`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(data => {
        if (active) {
          setVenues(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (active) {
          setError('Could not load venues — type manually');
          setLoading(false);
        }
      });

    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      active = false;
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInputChange = (val: string) => {
    onVenueNameInput(val);
    setIsOpen(true);
  };

  const handleSelectVenue = (v: Venue) => {
    selectVenue(v.id, v.name, v.area, v.city);
    setIsOpen(false);
  };

  const handleClearVenue = () => {
    onVenueNameInput('');
  };

  const filteredVenues = venues.filter(v =>
    v.name.toLowerCase().includes(session.venue.toLowerCase()) ||
    v.area.toLowerCase().includes(session.venue.toLowerCase())
  );

  return (
    <div className={styles.setupField} ref={containerRef}>
      <div className={styles.setupLbl}>Venue Name</div>
      
      {session.venueId ? (
        <div className={styles.selectedChip} id="selected-venue-chip">
          <span>📍 {session.venueName} · <small>{session.area}, {session.city}</small></span>
          <button type="button" className={styles.clearChipBtn} onClick={handleClearVenue} id="clear-venue-btn">✕</button>
        </div>
      ) : (
        <div style={{ position: 'relative' }}>
          <input
            className={styles.setupInput}
            id="setup-venue-input"
            type="text"
            placeholder={loading ? "Loading venues..." : "Type venue name to search..."}
            value={session.venue}
            onChange={(e) => handleInputChange(e.target.value)}
            onFocus={() => setIsOpen(true)}
            autoComplete="off"
            disabled={loading && !error}
          />
          {error && (
            <div style={{ fontSize: '10.5px', marginTop: '5px', color: 'var(--danger)' }}>
              {error}
            </div>
          )}
          {isOpen && session.venue.trim().length > 0 && filteredVenues.length > 0 && (
            <div className={styles.dropdownList} id="venue-search-results">
              {filteredVenues.map(v => {
                const isSelected = session.venueId === v.id;
                return (
                  <div
                    key={v.id}
                    className={`${styles.dropdownItem} ${isSelected ? styles.active : ''}`}
                    onClick={() => handleSelectVenue(v)}
                    id={`venue-option-${v.id}`}
                  >
                    <div className={styles.dropdownName}>{v.name}</div>
                    <div className={styles.dropdownMeta}>{v.area} · {v.city}</div>
                  </div>
                );
              })}
            </div>
          )}
          <div
            style={{ fontSize: '10.5px', marginTop: '5px', minHeight: '16px', color: venueRecallColor }}
            id="venue-recall-hint"
          >
            {venueRecallHint}
          </div>
        </div>
      )}
    </div>
  );
}
