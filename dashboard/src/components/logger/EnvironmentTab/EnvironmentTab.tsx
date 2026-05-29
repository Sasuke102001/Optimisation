import { useState } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import { SegmentedControl } from '../../shared/SegmentedControl/SegmentedControl';
import { IncidentDrawer } from './IncidentDrawer/IncidentDrawer';
import { showToast } from '../../shared/Toast/ToastRack';
import styles from './EnvironmentTab.module.css';

export function EnvironmentTab() {
  const { environment, pickEnvValue } = useSessionStore();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const soundOptions = ['Low', 'Medium', 'Loud', 'Very Loud'];
  const tempOptions = ['Cold', 'Comfortable', 'Warm', 'Hot'];
  const energyOptions = ['Flat', 'Relaxed', 'Active', 'High Energy'];
  const queueOptions = [
    { label: 'None', value: 'None' },
    { label: 'Short (<5)', value: 'Short (<5)' },
    { label: 'Medium (5–15)', value: 'Medium (5–15)' },
    { label: 'Long (15+)', value: 'Long (15+)' }
  ];

  const handleSaveSnapshot = () => {
    const now = new Date();
    let hours = now.getHours();
    const mins = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    const timeStr = `${hours}:${mins} ${ampm}`.toLowerCase();
    showToast(`Environment logged — ${timeStr}`, 'ok');
  };

  const complaintsCount = environment.complaints.length;

  return (
    <div className={styles.envTab} id="logger-panel-env">
      <div className={styles.envContainer}>
        <div className={styles.envRowCard}>
          <div className={styles.envRowTitle}>Sound Level</div>
          <SegmentedControl
            options={soundOptions}
            value={environment.sound}
            onChange={(val) => pickEnvValue('sound', val)}
            id="env-sound-ctrl"
          />
        </div>

        <div className={styles.envRowCard}>
          <div className={styles.envRowTitle}>Temperature Comfort</div>
          <SegmentedControl
            options={tempOptions}
            value={environment.temp}
            onChange={(val) => pickEnvValue('temp', val)}
            id="env-temp-ctrl"
          />
        </div>

        <div className={styles.envRowCard}>
          <div className={styles.envRowTitle}>Crowd Energy</div>
          <SegmentedControl
            options={energyOptions}
            value={environment.energy}
            onChange={(val) => pickEnvValue('energy', val)}
            id="env-energy-ctrl"
          />
        </div>

        <div className={styles.envRowCard}>
          <div className={styles.envRowTitle}>Queue at Bar</div>
          <SegmentedControl
            options={queueOptions}
            value={environment.queue}
            onChange={(val) => pickEnvValue('queue', val)}
            id="env-queue-ctrl"
          />
        </div>

        <div className={`${styles.envRowCard} ${styles.incidentRow}`}>
          <div>
            <div className={styles.envRowTitle} style={{ marginBottom: '2px' }}>
              Complaints &amp; Incidents
            </div>
            <div className={styles.envIncidentStat} id="env-incident-stat">
              {complaintsCount} logged in this session
            </div>
          </div>
          <button
            type="button"
            className="btn btn-danger"
            onClick={() => setIsDrawerOpen(true)}
          >
            + Log Complaint
          </button>
        </div>

        <div className={styles.envActionStickyContainer}>
          <button
            type="button"
            className="btn btn-gold"
            style={{ width: '100%', height: '46px', fontSize: '14px' }}
            onClick={handleSaveSnapshot}
          >
            Save Environment Snapshot →
          </button>
        </div>
      </div>

      {isDrawerOpen && <IncidentDrawer onClose={() => setIsDrawerOpen(false)} />}
    </div>
  );
}
