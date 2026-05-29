import { useState } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import { useInterval } from '../../../hooks/useInterval';
import { QuickEnvCheck } from './QuickEnvCheck/QuickEnvCheck';
import { showToast } from '../../shared/Toast/ToastRack';
import styles from './DoorFlow.module.css';

export function DoorFlow() {
  const { flow, session, updateCounter, submitInterval } = useSessionStore();
  const { formatted, pct, status } = useInterval();
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
  const [submittingFeedback, setSubmittingFeedback] = useState<string | null>(null);

  const formatTime = (dateObj: Date) => {
    let hours = dateObj.getHours();
    const mins = String(dateObj.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${hours}:${mins} ${ampm}`;
  };

  const handleSubmitInterval = () => {
    const now = new Date();
    const start = new Date(now.getTime() - session.interval * 60 * 1000);
    const timeStr = `${formatTime(start)}–${formatTime(now)}`;
    const timeLabel = formatTime(now).toLowerCase();

    submitInterval(timeStr);
    showToast(`Interval logged — ${timeLabel}`, 'ok');

    // Trigger feedback on button
    setSubmittingFeedback(`✓ Logged ${timeLabel}`);
    setTimeout(() => {
      setSubmittingFeedback(null);
    }, 1500);

    // Show inline quick check
    useSessionStore.setState({ showQuickEnvCheck: true });
  };

  const netTotal = flow.totals.entries - flow.totals.exits;
  const netSign = netTotal >= 0 ? '+' : '';

  return (
    <div className={styles.doorFlowTab}>
      <div className={styles.flowInfoBarWrapper}>
        <div className={styles.flowInfoBar}>
          <div className={styles.flowInfoLabel}>{session.interval} Min Interval</div>
          <div className={`${styles.flowInfoTime} ${styles[status]}`}>
            {formatted} remaining
          </div>
        </div>
        <div className={styles.countdownProgressContainer}>
          <div
            className={`${styles.countdownProgressBar} ${styles[status]}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className={styles.counterBlockContainer}>
        {/* Entries Counter Card */}
        <div
          className={styles.counterCard}
          id="counter-card-entries"
          onClick={() => updateCounter('entries', 1)}
        >
          <div className={styles.counterCardHeader}>
            <div className={styles.counterCardTitleBlock}>
              <div className={styles.counterCardTitle}>ENTRIES</div>
              <div className={styles.counterCardDesc}>Tap card to increment</div>
            </div>
          </div>
          <div className={styles.counterBodyRow} onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className={styles.btnCounterMinus}
              onClick={(e) => {
                updateCounter('entries', -1);
                e.stopPropagation();
              }}
              title="Correction"
            >
              −
            </button>
            <div className={styles.counterValGiant}>{flow.entries}</div>
            <button
              type="button"
              className={styles.btnCounterPlus}
              onClick={(e) => {
                updateCounter('entries', 1);
                e.stopPropagation();
              }}
            >
              +
            </button>
          </div>
        </div>

        {/* Exits Counter Card */}
        <div
          className={styles.counterCard}
          id="counter-card-exits"
          onClick={() => updateCounter('exits', 1)}
        >
          <div className={styles.counterCardHeader}>
            <div className={styles.counterCardTitleBlock}>
              <div className={styles.counterCardTitle}>EXITS</div>
              <div className={styles.counterCardDesc}>Tap card to increment</div>
            </div>
          </div>
          <div className={styles.counterBodyRow} onClick={(e) => e.stopPropagation()}>
            <button
              type="button"
              className={styles.btnCounterMinus}
              onClick={(e) => {
                updateCounter('exits', -1);
                e.stopPropagation();
              }}
              title="Correction"
            >
              −
            </button>
            <div className={styles.counterValGiant}>{flow.exits}</div>
            <button
              type="button"
              className={styles.btnCounterPlus}
              onClick={(e) => {
                updateCounter('exits', 1);
                e.stopPropagation();
              }}
            >
              +
            </button>
          </div>
        </div>
      </div>

      <button
        type="button"
        className="btn btn-gold"
        id="submit-interval-btn"
        style={{ width: '100%', height: '46px', fontSize: '14px', marginTop: '4px' }}
        onClick={handleSubmitInterval}
        disabled={submittingFeedback !== null}
      >
        {submittingFeedback || 'Submit Interval →'}
      </button>

      {/* Inline Quick Environment Check prompt */}
      <QuickEnvCheck />

      <div className={styles.totalsBar}>
        <div className={styles.totalStat}>
          Entries Today: <span>{flow.totals.entries}</span>
        </div>
        <div className={styles.totalStat}>
          Exits Today: <span>{flow.totals.exits}</span>
        </div>
        <div className={styles.totalStat}>
          Net: <span>{netSign}{netTotal}</span>
        </div>
      </div>

      <div className={styles.historyCard}>
        <div
          className={styles.historyHeader}
          onClick={() => setIsHistoryCollapsed(!isHistoryCollapsed)}
        >
          <span>Interval History (Last 5 Entries)</span>
          <span>{isHistoryCollapsed ? '▼' : '▲'}</span>
        </div>
        <div className={`${styles.historyList} ${isHistoryCollapsed ? styles.collapsed : ''}`}>
          {flow.history.length === 0 ? (
            <div className={styles.historyEmpty}>No intervals logged yet.</div>
          ) : (
            flow.history.map((item, idx) => (
              <div key={idx} className={styles.historyItem}>
                <span className={styles.histTime}>{item.time}</span>
                <span className={styles.histData}>
                  +{item.entries} / -{item.exits}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
