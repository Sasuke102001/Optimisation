import { useSessionStore } from '../../../store/sessionStore';
import { useKPIState } from '../../../hooks/useKPIState';
import { Badge } from '../../shared/Badge/Badge';
import type { KPIFamily } from '../../../types';
import styles from './KPICard.module.css';

interface KPICardProps {
  family: KPIFamily;
  zoneId: string;
}

const SIGNALS_LOOKUP: Record<string, { question: string; options: string[] }> = {
  is_anyone_dancing: {
    question: 'Is anyone dancing?',
    options: ['No', 'A few', 'Floor is alive']
  },
  room_energy_level: {
    question: 'How is the room energy?',
    options: ['Dead', 'Building', 'Peak']
  },
  groups_mixing: {
    question: 'Are groups mixing and socializing?',
    options: ['No', 'Some', 'Yes']
  },
  sound_level_working: {
    question: 'Is the sound level working for the crowd?',
    options: ['Too quiet', 'Right', 'Too loud']
  },
  temperature_feeling: {
    question: 'How is the temperature feeling?',
    options: ['Cold', 'Comfortable', 'Hot']
  },
  atmosphere_right: {
    question: 'Is the atmosphere feeling right?',
    options: ['Off', 'Building', 'On']
  },
  table_turnover: {
    question: 'Are tables turning over?',
    options: ['Slow', 'Normal', 'Fast']
  },
  dwell_behaviour: {
    question: 'Are people staying or leaving early?',
    options: ['Leaving early', 'Normal dwell', 'Long stays']
  },
  bar_activity: {
    question: 'How is bar activity?',
    options: ['Dead', 'Active', 'Very busy']
  },
  fatigue_signs: {
    question: 'Is the crowd showing fatigue signs?',
    options: ['Yes, dying', 'Getting tired', 'Fresh']
  },
  overcrowding: {
    question: 'Is the venue feeling overcrowded?',
    options: ['Yes, too packed', 'Busy', 'Fine']
  },
  visible_discomfort: {
    question: 'Is anyone visibly uncomfortable?',
    options: ['Yes, several', 'One or two', 'No']
  }
};

export function KPICard({ family, zoneId }: KPICardProps) {
  const { manualSignals, loggedKpis, lastIntervalSignals, saveKpiCardUpdate } = useSessionStore();
  const { isKpiCardLogged, getCalculatedKpiStatus } = useKPIState();

  const isLogged = isKpiCardLogged(zoneId, family.id);
  const status = getCalculatedKpiStatus(zoneId, family.id);
  const displayStatus = isLogged ? status : 'none';

  const keyPrefix = `${zoneId}_${family.id}_`;

  const handleSelectOption = (sigSlug: string, optionLabel: string) => {
    // Construct updated signals mapping
    const currentCardData: Record<string, string> = {};
    family.signals.forEach(sig => {
      const val = manualSignals[`${keyPrefix}${sig}`];
      if (val) currentCardData[sig] = val;
    });
    currentCardData[sigSlug] = optionLabel;

    saveKpiCardUpdate(zoneId, family.id, currentCardData);
  };

  const getFooterText = () => {
    const key = `${zoneId}_${family.id}`;
    const timestamp = loggedKpis[key];
    if (timestamp) {
      const date = new Date(timestamp);
      let hours = date.getHours();
      const mins = String(date.getMinutes()).padStart(2, '0');
      const ampm = hours >= 12 ? 'PM' : 'AM';
      hours = hours % 12;
      hours = hours ? hours : 12;
      return `Logged at ${hours}:${mins} ${ampm}`;
    }

    // Check if at least one is tapped
    const anyTapped = family.signals.some(sig => manualSignals[`${keyPrefix}${sig}`]);
    if (anyTapped) {
      return 'Logging in progress...';
    }

    return 'Not logged this session';
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
        {family.signals.map((sigSlug) => {
          const sigInfo = SIGNALS_LOOKUP[sigSlug];
          if (!sigInfo) return null;

          const currentSel = manualSignals[`${keyPrefix}${sigSlug}`] || '';
          const lastIntervalVal = lastIntervalSignals[`${keyPrefix}${sigSlug}`];

          return (
            <div key={sigSlug} className={styles.sigRowLayout}>
              <div className={styles.questionCol}>
                <span className={styles.questionText}>{sigInfo.question}</span>
                {lastIntervalVal && (
                  <span className={styles.lastValLabel}>
                    Last interval: {lastIntervalVal}
                  </span>
                )}
              </div>
              <div className={styles.tapSelector}>
                {sigInfo.options.map((opt) => {
                  const isActive = currentSel === opt;
                  const isDimmed = currentSel && currentSel !== opt;
                  return (
                    <button
                      key={opt}
                      type="button"
                      className={`${styles.tapOption} ${isActive ? styles.active : ''} ${isDimmed ? styles.dimmed : ''}`}
                      onClick={() => handleSelectOption(sigSlug, opt)}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className={styles.cardFoot}>
        <div className={styles.cardTs}>{getFooterText()}</div>
      </div>
    </div>
  );
}
