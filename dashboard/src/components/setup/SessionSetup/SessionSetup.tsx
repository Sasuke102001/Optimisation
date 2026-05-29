import { useState } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import { VenueInput } from '../VenueInput/VenueInput';
import { TableStepper } from '../TableStepper/TableStepper';
import { SegmentedControl } from '../../shared/SegmentedControl/SegmentedControl';
import { showToast } from '../../shared/Toast/ToastRack';
import styles from './SessionSetup.module.css';

export function SessionSetup() {
  const { session, tableConfig, pickSetupMode, pickSetupInterval, startSession } = useSessionStore();
  const [operator, setOperator] = useState('');

  const totalTables = tableConfig.two + tableConfig.four + tableConfig.six;
  const isButtonDisabled = !session.venue.trim() || totalTables === 0;

  const handleOpenSession = () => {
    if (!session.venue.trim()) {
      showToast('⚠ Enter a venue name to start', 'warn');
      return;
    }
    if (totalTables === 0) {
      showToast('⚠ Set the table layout before starting', 'warn');
      return;
    }

    const ok = startSession(operator);
    if (ok) {
      showToast(`Session opened at ${session.venue}`, 'ok');
    }
  };

  const modeOptions = [
    { label: 'Baseline', value: 'BASELINE' as const },
    { label: 'Engineered', value: 'ENGINEERED' as const },
    { label: 'Follow-up', value: 'FOLLOWUP' as const }
  ];

  const intervalOptions = [
    { label: '15 Min', value: 15 },
    { label: '30 Min', value: 30 }
  ];

  return (
    <div className={styles.setupScreen} id="screen-setup">
      <div className={styles.setupCard}>
        <div className={styles.setupCardHeader}>
          <div className={styles.setupLogo}>PN</div>
          <div className={styles.setupTitle}>Initialize Live Session</div>
          <div className={styles.setupSub}>Module 3 · Venue Behavioral Logging System</div>
        </div>

        <VenueInput />
        <TableStepper />

        <div className={styles.setupField}>
          <div className={styles.setupLbl}>Session Mode</div>
          <SegmentedControl
            options={modeOptions}
            value={session.mode}
            onChange={(val) => pickSetupMode(val)}
          />
        </div>

        <div className={styles.setupField}>
          <div className={styles.setupLbl}>Logging Interval</div>
          <SegmentedControl
            options={intervalOptions}
            value={session.interval}
            onChange={(val) => pickSetupInterval(val)}
          />
        </div>

        <div className={styles.setupField}>
          <div className={styles.setupLbl}>Operator Name</div>
          <input
            className={styles.setupInput}
            id="setup-operator-input"
            type="text"
            placeholder="Your name..."
            value={operator}
            onChange={(e) => setOperator(e.target.value)}
          />
        </div>

        <div className={styles.setupField} style={{ marginTop: '8px' }}>
          <button
            type="button"
            className={`btn btn-gold ${isButtonDisabled ? styles.disabledState : ''}`}
            id="open-session-btn"
            style={{ width: '100%', height: '44px', fontSize: '14px' }}
            onClick={handleOpenSession}
          >
            Open Session →
          </button>
        </div>
      </div>
    </div>
  );
}
