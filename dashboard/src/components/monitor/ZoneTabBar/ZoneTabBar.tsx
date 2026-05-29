import { useSessionStore } from '../../../store/sessionStore';
import { useKPIState } from '../../../hooks/useKPIState';
import { ZONES } from '../../../types/constants';
import styles from './ZoneTabBar.module.css';

export function ZoneTabBar() {
  const { currentMonitorZone, switchMonitorZone } = useSessionStore();
  const { getCalculatedZoneHealth } = useKPIState();

  return (
    <nav className={styles.monitorTabs} id="monitor-tabs-container">
      {ZONES.map((zone) => {
        const health = getCalculatedZoneHealth(zone.id);
        const isActive = zone.id === currentMonitorZone;

        return (
          <button
            key={zone.id}
            type="button"
            className={`${styles.mtab} ${isActive ? styles.active : ''}`}
            onClick={() => switchMonitorZone(zone.id)}
          >
            <div className={`${styles.mtabPip} ${styles[health]}`} />
            <span>{zone.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
