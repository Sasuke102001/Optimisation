import { useSessionStore } from '../../../store/sessionStore';
import styles from './VenueInput.module.css';

export function VenueInput() {
  const { session, venueRecallHint, venueRecallColor, onVenueNameInput } = useSessionStore();

  return (
    <div className={styles.setupField}>
      <div className={styles.setupLbl}>Venue Name</div>
      <input
        className={styles.setupInput}
        id="setup-venue-input"
        type="text"
        placeholder="Type venue name, e.g. Eclipse, Mango, 1000 Nights..."
        value={session.venue}
        onChange={(e) => onVenueNameInput(e.target.value)}
      />
      <div
        style={{ fontSize: '10.5px', marginTop: '5px', minHeight: '16px', color: venueRecallColor }}
        id="venue-recall-hint"
      >
        {venueRecallHint}
      </div>
    </div>
  );
}
