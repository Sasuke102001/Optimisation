import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { useSessionStore } from '../../../store/sessionStore';
import { useKPIState } from '../../../hooks/useKPIState';
import { useTableState } from '../../../hooks/useTableState';
import { SignalRow } from '../SignalRow/SignalRow';
import { Badge } from '../../shared/Badge/Badge';
import { showToast } from '../../shared/Toast/ToastRack';
import { getSignalSource } from '../../../types/constants';
import type { KPIFamily } from '../../../types';
import styles from './KPICard.module.css';

interface KPICardProps {
  family: KPIFamily;
  zoneId: string;
}

export function KPICard({ family, zoneId }: KPICardProps) {
  const { flow, environment, manualSignals, loggedKpis, saveKpiCardUpdate } = useSessionStore();
  const { isKpiCardLogged, getCalculatedKpiStatus } = useKPIState();
  const { occupiedCount, totalCount } = useTableState();

  const [isExpanded, setIsExpanded] = useState(false);
  const [tempManualSignals, setTempManualSignals] = useState<Record<string, string>>({});

  const isLogged = isKpiCardLogged(zoneId, family.id);
  const status = getCalculatedKpiStatus(zoneId, family.id);
  const displayStatus = isLogged ? status : 'none';

  const hasManualSignals = family.signals.some((sig) => getSignalSource(sig) === 'manual');

  // Sync manual signals when family, zone, or manualSignals updates
  useEffect(() => {
    const initial: Record<string, string> = {};
    family.signals.forEach((sig) => {
      if (getSignalSource(sig) === 'manual') {
        const key = `${zoneId}_${family.id}_${sig}`;
        initial[sig] = manualSignals[key] || 'ok';
      }
    });
    setTempManualSignals(initial);
  }, [family, zoneId, manualSignals]);

  const handleManualSelect = (sig: string, val: string) => {
    setTempManualSignals((prev) => ({
      ...prev,
      [sig]: val
    }));
  };

  const handleSave = () => {
    saveKpiCardUpdate(zoneId, family.id, tempManualSignals);
    setIsExpanded(false);
    showToast('Changes saved', 'ok');
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    let hours = date.getHours();
    const mins = String(date.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12;
    return `${hours}:${mins} ${ampm}`;
  };

  const renderTimestamp = () => {
    const key = `${zoneId}_${family.id}`;
    const timestamp = loggedKpis[key];

    if (!timestamp) {
      return <span style={{ color: 'var(--text-disabled)' }}>Not logged this session</span>;
    }

    const diffMs = Date.now() - timestamp;
    const timeStr = formatTime(timestamp);

    if (diffMs > 15 * 60 * 1000) {
      return (
        <span className={styles.timeWarning}>
          <span style={{ marginRight: '4px' }}>🕒</span>Updated {timeStr}
        </span>
      );
    }

    return <span>Updated {timeStr}</span>;
  };

  // Support Statistics Calculations
  const renderSupportData = () => {
    // raw & derived IDs for each family
    const supportMap: Record<string, { raw: string[]; derived: string[] }> = {
      flow: {
        raw: ['entry_count', 'exit_count', 'door_queue'],
        derived: ['ingress_rate', 'net_change']
      },
      service: {
        raw: ['table_occupancy', 'bar_queue'],
        derived: ['seated_ratio']
      },
      engagement: {
        raw: ['crowd_energy'],
        derived: ['energy_index']
      },
      overload: {
        raw: ['sound_level', 'temp_comfort'],
        derived: ['fatigue_risk']
      },
      complaints: {
        raw: ['complaints_count'],
        derived: ['ingress_rate'] // incident rate maps here
      },
      commercial: {
        raw: ['table_occupancy'],
        derived: ['seated_ratio']
      },
      environment: {
        raw: ['sound_level', 'temp_comfort'],
        derived: ['comfort_coherence']
      }
    };

    const map = supportMap[family.id];
    if (!map) return <div className={styles.scoreRow}>No mapped signal data</div>;

    const rawLabels: Record<string, string> = {
      entry_count: 'Total entries',
      exit_count: 'Total exits',
      door_queue: 'At door now',
      table_occupancy: 'Tables occupied',
      sound_level: 'Sound level',
      temp_comfort: 'Temperature',
      crowd_energy: 'Crowd energy',
      bar_queue: 'Bar queue',
      complaints_count: 'Complaints'
    };

    const derivedLabels: Record<string, string> = {
      ingress_rate: 'Entries this interval',
      net_change: 'Net flow',
      seated_ratio: 'Tables filled',
      energy_index: 'Energy level',
      fatigue_risk: 'Fatigue risk',
      comfort_coherence: 'Comfort score'
    };

    const list: ReactNode[] = [];

    // Render Raw
    map.raw.forEach((rid) => {
      let label = rawLabels[rid] || rid;
      let val: string | number = 'N/A';
      let src = 'manual';

      if (rid === 'entry_count') {
        val = flow.totals.entries;
        src = 'counter';
      } else if (rid === 'exit_count') {
        val = flow.totals.exits;
        src = 'counter';
      } else if (rid === 'door_queue') {
        val = flow.entries;
        src = 'counter';
      } else if (rid === 'table_occupancy') {
        val = `${occupiedCount}/${totalCount}`;
        src = 'counter';
      } else if (rid === 'sound_level') {
        val = environment.sound;
        src = 'sensor';
      } else if (rid === 'temp_comfort') {
        val = environment.temp;
        src = 'sensor';
      } else if (rid === 'crowd_energy') {
        val = environment.energy;
        src = 'manual';
      } else if (rid === 'bar_queue') {
        val = environment.queue;
        src = 'manual';
      } else if (rid === 'complaints_count') {
        val = environment.complaints.length;
        src = 'manual';
      }

      const isManual = src === 'manual';
      list.push(
        <div key={rid} className={styles.scoreRow}>
          <span className={styles.scoreLbl}>{label}</span>
          <span className={styles.scoreVal}>
            {val}{' '}
            <span className={`${styles.srcBadge} ${isManual ? styles.manualBadge : styles.autoBadge}`}>
              {isManual ? 'manual' : 'auto'}
            </span>
          </span>
        </div>
      );
    });

    // Render Derived
    map.derived.forEach((did) => {
      let label = derivedLabels[did] || did;
      let val: string | number = 'N/A';

      if (did === 'ingress_rate') {
        if (family.id === 'complaints') {
          val = `${environment.complaints.length} active`;
        } else {
          val = `+${flow.entries}/int`;
        }
      } else if (did === 'net_change') {
        val = flow.totals.entries - flow.totals.exits;
      } else if (did === 'seated_ratio') {
        const ratio = totalCount > 0 ? Math.round((occupiedCount / totalCount) * 100) : 0;
        val = `${ratio}%`;
      } else if (did === 'energy_index') {
        val = environment.energy === 'High Energy' ? 'Strong' : 'Stable';
      } else if (did === 'fatigue_risk') {
        val = environment.energy === 'Flat' ? 'Elevated' : 'Low';
      } else if (did === 'comfort_coherence') {
        val = environment.temp === 'Comfortable' ? 'High' : 'Friction';
      }

      list.push(
        <div key={did} className={styles.scoreRow}>
          <span className={styles.scoreLbl}>{label}</span>
          <span className={styles.scoreVal} style={{ color: 'var(--gold)' }}>
            {val}{' '}
            <span className={`${styles.srcBadge} ${styles.autoBadge}`}>
              auto
            </span>
          </span>
        </div>
      );
    });

    return list;
  };

  return (
    <div
      className={`${styles.kpiCard} ${styles[`st-${displayStatus}`]} ${!isLogged ? styles.unlogged : ''}`}
      id={`kpi-card-${family.id}`}
    >
      <div className={styles.cardHead}>
        <div className={styles.cardFamily}>
          <span className={styles.cardFi}>{family.icon}</span>
          <span className={styles.cardFn}>{family.name}</span>
        </div>
        <Badge type="status" value={isLogged ? status : 'none'} />
      </div>

      <div className={styles.cardSignals}>
        {family.signals.map((sigName) => (
          <SignalRow
            key={sigName}
            signalName={sigName}
            zoneId={zoneId}
            familyId={family.id}
            isLogged={isLogged}
          />
        ))}
      </div>

      <div className={`${styles.cardExpand} ${isExpanded ? styles.open : ''}`} id={`mon-expand-${family.id}`}>
        <div className={styles.expandSection}>
          <div className={styles.expandLbl}>Auto-tracked data</div>
          {renderSupportData()}
        </div>

        {hasManualSignals && (
          <div className={styles.cardOverrideSection}>
            <div className={styles.expandLbl} style={{ marginBottom: '6px' }}>
              Your assessment
            </div>
            {family.signals.map((sig) => {
              if (getSignalSource(sig) === 'manual') {
                const currentVal = tempManualSignals[sig] || 'ok';
                return (
                  <div key={sig} className={styles.manualSigRow}>
                    <span className={styles.manualSigName}>{sig}</span>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <button
                        type="button"
                        className={`${styles.manualSigBtn} ${styles.btnN} ${currentVal === 'ok' ? styles.active : ''}`}
                        onClick={() => handleManualSelect(sig, 'ok')}
                      >
                        N
                      </button>
                      <button
                        type="button"
                        className={`${styles.manualSigBtn} ${styles.btnW} ${currentVal === 'watch' ? styles.active : ''}`}
                        onClick={() => handleManualSelect(sig, 'watch')}
                      >
                        W
                      </button>
                      <button
                        type="button"
                        className={`${styles.manualSigBtn} ${styles.btnA} ${currentVal === 'alert' ? styles.active : ''}`}
                        onClick={() => handleManualSelect(sig, 'alert')}
                      >
                        A
                      </button>
                    </div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        )}

        <div style={{ padding: '10px 16px 14px' }}>
          <button
            type="button"
            className="btn btn-gold"
            style={{ width: '100%', height: '36px', fontSize: '12px', fontWeight: 700 }}
            onClick={handleSave}
          >
            Save Changes
          </button>
        </div>
      </div>

      <div className={styles.cardFoot}>
        <div className={styles.cardTs}>{renderTimestamp()}</div>
        <button
          type="button"
          className={styles.cardBtnAction}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '✕ Close' : '✏️ Update'}
        </button>
      </div>
    </div>
  );
}
