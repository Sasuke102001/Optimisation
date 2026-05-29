import { useSessionStore } from '../../../../store/sessionStore';
import { SegmentedControl } from '../../../shared/SegmentedControl/SegmentedControl';
import { showToast } from '../../../shared/Toast/ToastRack';
import styles from './QuickEnvCheck.module.css';

export function QuickEnvCheck() {
  const { environment, pickEnvValue, showQuickEnvCheck, setShowQuickEnvCheck } = useSessionStore();

  if (!showQuickEnvCheck) return null;

  const soundOptions = ['Low', 'Medium', 'Loud', 'Very Loud'];
  const tempOptions = ['Cold', 'Comfortable', 'Warm', 'Hot'];
  const energyOptions = ['Flat', 'Relaxed', 'Active', 'High Energy'];
  const queueOptions = [
    { label: 'None', value: 'None' },
    { label: 'Short (<5)', value: 'Short (<5)' },
    { label: 'Medium (5–15)', value: 'Medium (5–15)' },
    { label: 'Long (15+)', value: 'Long (15+)' }
  ];

  const handleSave = () => {
    setShowQuickEnvCheck(false);
    const now = new Date();
    let hours = now.getHours();
    const mins = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const timeStr = `${hours}:${mins} ${ampm}`.toLowerCase();
    showToast(`Environment logged — ${timeStr}`, 'ok');
  };

  const handleSkip = () => {
    setShowQuickEnvCheck(false);
  };

  return (
    <div className={styles.quickEnvContainer} id="quick-env-check-container">
      <div className={styles.quickEnvHeader}>
        <span className={styles.quickEnvTitle}>⚡ Quick Environment Check?</span>
        <button type="button" className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: '11px', borderRadius: '4px' }} onClick={handleSkip}>
          Skip
        </button>
      </div>
      <div className={styles.quickEnvGrid}>
        {/* Sound */}
        <div className={styles.quickEnvCol}>
          <span className={styles.quickEnvLbl}>Sound</span>
          <SegmentedControl
            options={soundOptions}
            value={environment.sound}
            onChange={(val) => pickEnvValue('sound', val)}
            className={styles.compactControl}
          />
        </div>
        {/* Temp */}
        <div className={styles.quickEnvCol}>
          <span className={styles.quickEnvLbl}>Temp</span>
          <SegmentedControl
            options={tempOptions}
            value={environment.temp}
            onChange={(val) => pickEnvValue('temp', val)}
            className={styles.compactControl}
          />
        </div>
        {/* Energy */}
        <div className={styles.quickEnvCol}>
          <span className={styles.quickEnvLbl}>Energy</span>
          <SegmentedControl
            options={energyOptions}
            value={environment.energy}
            onChange={(val) => pickEnvValue('energy', val)}
            className={styles.compactControl}
          />
        </div>
        {/* Queue */}
        <div className={styles.quickEnvCol}>
          <span className={styles.quickEnvLbl}>Queue</span>
          <SegmentedControl
            options={queueOptions}
            value={environment.queue}
            onChange={(val) => pickEnvValue('queue', val)}
            className={styles.compactControl}
          />
        </div>
      </div>
      <button
        type="button"
        className="btn btn-gold"
        style={{ width: '100%', padding: '10px', fontSize: '12px', fontWeight: 700, height: '38px' }}
        onClick={handleSave}
      >
        Save &amp; Complete
      </button>
    </div>
  );
}
