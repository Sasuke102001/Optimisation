import { useState } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import { useSession } from '../../../hooks/useSession';
import { Badge } from '../Badge/Badge';
import { showToast } from '../Toast/ToastRack';
import styles from './Header.module.css';

export function Header() {
  const { session, currentScreen, switchScreen, endSession, submitInterval } = useSessionStore();
  const { timerText } = useSession();
  const [submittingFeedback, setSubmittingFeedback] = useState<string | null>(null);

  const getInitials = (name: string) => {
    if (!name) return 'OP';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return parts[0].substring(0, 2).toUpperCase();
  };

  const handleEndSession = () => {
    if (window.confirm('Are you sure you want to end this logging session? All unsaved data will be cleared.')) {
      endSession();
      showToast('Session closed', 'warn');
    }
  };

  const handleToggleView = () => {
    if (currentScreen === 'logger') {
      switchScreen('monitor');
    } else {
      switchScreen('logger');
    }
  };

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

    // Trigger store interval submission
    submitInterval(timeStr);
    showToast(`Interval logged — ${timeLabel}`, 'ok');

    // Trigger feedback on button
    setSubmittingFeedback(`✓ Logged ${timeLabel}`);
    setTimeout(() => {
      setSubmittingFeedback(null);
    }, 1500);

    // Trigger QuickEnvCheck in DoorFlow tab (if active) via shared store flag
    useSessionStore.setState({ showQuickEnvCheck: true });
  };

  return (
    <header className={styles.globalHeader} id="global-header">
      <div className={styles.hdBrand}>
        <div className={styles.hdLogo}>PN</div>
        <div>
          <div className={styles.hdTitle} id="header-venue-display">
            {session.venue.toUpperCase()}
          </div>
          <div className={styles.hdSub}>Live Ops Module 3</div>
        </div>
      </div>
      <div className={styles.hdSessionInfo}>
        <Badge type="mode" value={session.mode} />
        <span className={styles.sessionNum} id="header-session-num">
          Session {session.number}
        </span>
        <div className={styles.hdTimer} id="session-timer">
          {timerText}
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div className={styles.hdOperator}>
          <div className={styles.hdAvatar}>{getInitials(session.operator)}</div>
          <div className={styles.hdOpName} id="header-operator-display">
            {session.operator || '—'}
          </div>
        </div>

        {currentScreen === 'logger' && (
          <button
            className="btn btn-gold"
            id="header-submit-interval-btn"
            onClick={handleSubmitInterval}
            disabled={submittingFeedback !== null}
            style={{ minWidth: '120px' }}
          >
            {submittingFeedback || 'Submit Interval'}
          </button>
        )}

        <button
          className="btn btn-ghost"
          id="header-switch-view-btn"
          onClick={handleToggleView}
        >
          {currentScreen === 'logger' ? '📊 Monitor View' : '✏️ Logger View'}
        </button>

        <button
          className="btn btn-danger"
          onClick={handleEndSession}
          style={{ padding: '8px 12px', fontSize: '11px' }}
        >
          End
        </button>
      </div>
    </header>
  );
}
