import { useSessionStore } from '../../../store/sessionStore';
import { useKPIState } from '../../../hooks/useKPIState';
import { useTableState } from '../../../hooks/useTableState';
import { ZoneTabBar } from '../ZoneTabBar/ZoneTabBar';
import { KPICard } from '../KPICard/KPICard';
import { Badge } from '../../shared/Badge/Badge';
import { ZONES, KPI_FAMILIES } from '../../../types/constants';
import styles from './KPIMonitor.module.css';

export function KPIMonitor() {
  const { currentMonitorZone, flow, environment } = useSessionStore();
  const { getCalculatedZoneHealth } = useKPIState();
  const { occupiedCount, totalCount } = useTableState();

  const activeZone = ZONES.find((z) => z.id === currentMonitorZone) || ZONES[0];
  const health = getCalculatedZoneHealth(activeZone.id);

  // Sort relevant families first
  const orderedFamilies = [...KPI_FAMILIES].sort((a, b) => {
    const aRel = activeZone.relevant.includes(a.id);
    const bRel = activeZone.relevant.includes(b.id);
    if (aRel && !bRel) return -1;
    if (!aRel && bRel) return 1;
    return 0;
  });

  return (
    <div className={styles.monitorScreen} id="screen-monitor">
      <ZoneTabBar />

      <div className={styles.monitorWorkspace}>
        <div className={styles.monitorHeaderRow}>
          <div className={styles.monZoneTitleBlock}>
            <span className={styles.monZoneIcon} id="mon-zone-icon">
              {activeZone.icon}
            </span>
            <div>
              <div className={styles.monZoneName} id="mon-zone-name">
                {activeZone.label}
              </div>
              <div className={styles.monZoneDesc} id="mon-zone-desc">
                {activeZone.desc}
              </div>
            </div>
          </div>
          <div>
            <Badge type="status" value={health} />
          </div>
        </div>

        <div className={styles.kpiGrid} id="kpi-grid">
          {orderedFamilies.map((fam) => (
            <KPICard key={fam.id} family={fam} zoneId={activeZone.id} />
          ))}
        </div>
      </div>

      {/* Bottom summary strip */}
      <div className={styles.bottomSummaryBar}>
        <div className={styles.summaryStat}>
          Total Entries: <span>{flow.totals.entries}</span>
        </div>
        <div className={styles.summaryDivider}></div>
        <div className={styles.summaryStat}>
          Occupied Tables: <span>{occupiedCount}/{totalCount}</span>
        </div>
        <div className={styles.summaryDivider}></div>
        <div className={styles.summaryStat}>
          Complaints Logged: <span>{environment.complaints.length}</span>
        </div>
      </div>
    </div>
  );
}
