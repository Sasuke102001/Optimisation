import { create } from 'zustand';
import type { Table, IntervalRecord, Complaint } from '../types';
import { KPI_FAMILIES } from '../types/constants';
import { showToast } from '../components/shared/Toast/ToastRack';

interface SessionState {
  session: {
    active: boolean;
    venue: string;
    venueName: string;
    venueId: number | null;
    area: string;
    city: string;
    mode: 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP';
    interval: number;
    startTime: number | null;
    number: number;
    operator: string;
    sessionId: number | null;
    intervalCount: number;
  };
  tableConfig: { two: number; four: number; six: number };
  flow: {
    entries: number;
    exits: number;
    totals: { entries: number; exits: number };
    history: IntervalRecord[];
  };
  tables: Table[];
  environment: {
    sound: string;
    temp: string;
    energy: string;
    queue: string;
    complaints: Complaint[];
  };
  kpiOverrides: Record<string, string>;
  loggedKpis: Record<string, number>;
  lastIntervalSignals: Record<string, string>;
  manualSignals: Record<string, string>;
  currentScreen: 'setup' | 'logger' | 'monitor';
  currentLoggerTab: 'flow' | 'tables' | 'env';
  currentMonitorZone: string;
  venueRecallHint: string;
  venueRecallColor: string;
  intervalTimeRemaining: number;
  showQuickEnvCheck: boolean;

  // Actions
  onVenueNameInput: (venue: string) => void;
  selectVenue: (venueId: number, venueName: string, area: string, city: string) => void;
  adjustTableType: (type: 'two' | 'four' | 'six', delta: number) => void;
  pickSetupMode: (mode: 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP') => void;
  pickSetupInterval: (interval: number) => void;
  startSession: (operatorName: string) => Promise<boolean>;
  endSession: () => Promise<void>;
  switchScreen: (screen: 'setup' | 'logger' | 'monitor') => void;
  switchLoggerTab: (tab: 'flow' | 'tables' | 'env') => void;
  switchMonitorZone: (zone: string) => void;
  updateCounter: (type: 'entries' | 'exits', change: number) => void;
  submitInterval: (timeLabel: string) => Promise<void>;
  saveTableAction: (tableId: string, pplCount: number | '6+', custType: string, note: string) => void;
  clearTableAction: (tableId: string) => { tableId: string; dwellText: string } | null;
  pickEnvValue: (property: 'sound' | 'temp' | 'energy' | 'queue', value: string) => void;
  submitIncidentAction: (type: string, severity: 'watch' | 'alert', zone: string, note: string) => void;
  saveKpiCardUpdate: (zoneId: string, famId: string, signalsData: Record<string, string>) => void;
  overrideKpiStatus: (zoneId: string, famId: string, overrideValue: string) => void;
  decrementIntervalTime: () => void;
  resetIntervalTime: () => void;
  setShowQuickEnvCheck: (val: boolean) => void;
}

const FAMILY_ID_MAP: Record<string, number> = {
  crowd_energy: 1,
  environment: 2,
  commercial: 3,
  crowd_stress: 4
};

const SIGNAL_OPTIONS: Record<string, { options: string[], rag: string[], scores: number[] }> = {
  is_anyone_dancing: {
    options: ['No', 'A few', 'Floor is alive'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  room_energy_level: {
    options: ['Dead', 'Building', 'Peak'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  groups_mixing: {
    options: ['No', 'Some', 'Yes'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  sound_level_working: {
    options: ['Too quiet', 'Right', 'Too loud'],
    rag: ['amber', 'green', 'red'],
    scores: [0.5, 0.9, 0.1]
  },
  temperature_feeling: {
    options: ['Cold', 'Comfortable', 'Hot'],
    rag: ['amber', 'green', 'red'],
    scores: [0.5, 0.9, 0.1]
  },
  atmosphere_right: {
    options: ['Off', 'Building', 'On'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  table_turnover: {
    options: ['Slow', 'Normal', 'Fast'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  dwell_behaviour: {
    options: ['Leaving early', 'Normal dwell', 'Long stays'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  bar_activity: {
    options: ['Dead', 'Active', 'Very busy'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  fatigue_signs: {
    options: ['Yes, dying', 'Getting tired', 'Fresh'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  overcrowding: {
    options: ['Yes, too packed', 'Busy', 'Fine'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  },
  visible_discomfort: {
    options: ['Yes, several', 'One or two', 'No'],
    rag: ['red', 'amber', 'green'],
    scores: [0.1, 0.5, 0.9]
  }
};

export const useSessionStore = create<SessionState>((set, get) => ({
  session: {
    active: false,
    venue: '',
    venueName: '',
    venueId: null,
    area: '',
    city: '',
    mode: 'ENGINEERED',
    interval: 15,
    startTime: null,
    number: 3,
    operator: '',
    sessionId: null,
    intervalCount: 1
  },
  tableConfig: { two: 0, four: 0, six: 0 },
  flow: {
    entries: 0,
    exits: 0,
    totals: { entries: 0, exits: 0 },
    history: []
  },
  tables: [],
  environment: {
    sound: 'Medium',
    temp: 'Comfortable',
    energy: 'Active',
    queue: 'None',
    complaints: []
  },
  kpiOverrides: {},
  loggedKpis: {},
  lastIntervalSignals: {},
  manualSignals: {},
  currentScreen: 'setup',
  currentLoggerTab: 'flow',
  currentMonitorZone: 'entrance',
  venueRecallHint: '',
  venueRecallColor: 'var(--text-disabled)',
  intervalTimeRemaining: 0,
  showQuickEnvCheck: false,

  onVenueNameInput: (venue: string) => {
    const key = venue.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    let config = { two: 0, four: 0, six: 0 };
    let hint = '';
    let color = 'var(--text-disabled)';

    if (venue.trim()) {
      try {
        const all = JSON.parse(localStorage.getItem('pn_venue_configs') || '{}');
        if (all[key]) {
          config = all[key];
          const tot = config.two + config.four + config.six;
          hint = `✓ Table layout loaded — ${tot} tables remembered from last session`;
          color = 'var(--ok)';
        } else {
          hint = 'New venue — set table layout below';
        }
      } catch (e) {
        hint = 'New venue — set table layout below';
      }
    }

    set((state) => ({
      session: {
        ...state.session,
        venue,
        venueName: venue,
        venueId: null,
        area: '',
        city: ''
      },
      tableConfig: config.two + config.four + config.six > 0 ? config : state.tableConfig,
      venueRecallHint: hint,
      venueRecallColor: color
    }));
  },

  selectVenue: (venueId: number, venueName: string, area: string, city: string) => {
    const key = venueName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    let config = { two: 0, four: 0, six: 0 };
    let hint = '';
    let color = 'var(--text-disabled)';

    try {
      const all = JSON.parse(localStorage.getItem('pn_venue_configs') || '{}');
      if (all[key]) {
        config = all[key];
        const tot = config.two + config.four + config.six;
        hint = `✓ Table layout loaded — ${tot} tables remembered from last session`;
        color = 'var(--ok)';
      } else {
        hint = 'New venue — set table layout below';
      }
    } catch (e) {
      hint = 'New venue — set table layout below';
    }

    set((state) => ({
      session: {
        ...state.session,
        venue: venueName,
        venueName,
        venueId,
        area,
        city
      },
      tableConfig: config.two + config.four + config.six > 0 ? config : state.tableConfig,
      venueRecallHint: hint,
      venueRecallColor: color
    }));
  },

  adjustTableType: (type: 'two' | 'four' | 'six', delta: number) => {
    set((state) => {
      const val = Math.max(0, (state.tableConfig[type] || 0) + delta);
      return {
        tableConfig: { ...state.tableConfig, [type]: val }
      };
    });
  },

  pickSetupMode: (mode: 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP') => {
    set((state) => ({
      session: { ...state.session, mode }
    }));
  },

  pickSetupInterval: (interval: number) => {
    set((state) => ({
      session: { ...state.session, interval }
    }));
  },

  startSession: async (operatorName: string) => {
    const { session, tableConfig } = get();
    if (!session.venue.trim()) return false;
    const totalTables = tableConfig.two + tableConfig.four + tableConfig.six;
    if (totalTables === 0) return false;

    // Save venue config
    const key = session.venue.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    try {
      const all = JSON.parse(localStorage.getItem('pn_venue_configs') || '{}');
      all[key] = tableConfig;
      localStorage.setItem('pn_venue_configs', JSON.stringify(all));
    } catch (e) {}

    // Generate tables
    const newTables: Table[] = [];
    let tNum = 1;
    const makeTable = (cap: number): Table => ({
      id: `T${tNum++}`,
      cap,
      occupied: false,
      pplCount: null,
      custType: null,
      note: '',
      seatedTime: null
    });
    for (let i = 0; i < tableConfig.two; i++) newTables.push(makeTable(2));
    for (let i = 0; i < tableConfig.four; i++) newTables.push(makeTable(4));
    for (let i = 0; i < tableConfig.six; i++) newTables.push(makeTable(6));

    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://20.219.216.138';
    const modeMap: Record<string, string> = {
      BASELINE: 'observation_only',
      ENGINEERED: 'engineering_active',
      FOLLOWUP: 'post_intervention'
    };

    try {
      const res = await fetch(`${BASE_URL}/api/kpi/session/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          venue_id: session.venueId || 1,
          venue_name: session.venueName,
          area: session.area,
          city: session.city,
          session_number: session.number || 1,
          session_mode: modeMap[session.mode] || 'observation_only',
          table_config: {
            two_person: tableConfig.two,
            four_person: tableConfig.four,
            six_person: tableConfig.six
          },
          notes: `Operator: ${operatorName}`
        })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to start session on backend');
      }

      const data = await res.json();
      const sessionId = data.session_id;

      set((state) => ({
        session: {
          ...state.session,
          active: true,
          operator: operatorName || 'Operator',
          startTime: Date.now(),
          sessionId,
          intervalCount: 1
        },
        tables: newTables,
        currentScreen: 'logger',
        intervalTimeRemaining: state.session.interval * 60
      }));

      return true;
    } catch (err: any) {
      showToast(`Setup failed: ${err.message || err}`, 'warn');
      return false;
    }
  },

  endSession: async () => {
    const { session } = get();
    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://20.219.216.138';

    if (session.sessionId) {
      try {
        const res = await fetch(`${BASE_URL}/api/kpi/session/${session.sessionId}/end`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        if (!res.ok) {
          throw new Error('Failed to end session on server');
        }
      } catch (err: any) {
        showToast(`Failed to close session on server: ${err.message || err}`, 'warn');
        return; // DO NOT clear session on error
      }
    }

    set({
      session: {
        active: false,
        venue: '',
        venueName: '',
        venueId: null,
        area: '',
        city: '',
        mode: 'ENGINEERED',
        interval: 15,
        startTime: null,
        number: 3,
        operator: '',
        sessionId: null,
        intervalCount: 1
      },
      tableConfig: { two: 0, four: 0, six: 0 },
      flow: {
        entries: 0,
        exits: 0,
        totals: { entries: 0, exits: 0 },
        history: []
      },
      tables: [],
      environment: {
        sound: 'Medium',
        temp: 'Comfortable',
        energy: 'Active',
        queue: 'None',
        complaints: []
      },
      kpiOverrides: {},
      loggedKpis: {},
      lastIntervalSignals: {},
      manualSignals: {},
      currentScreen: 'setup',
      currentLoggerTab: 'flow',
      currentMonitorZone: 'entrance',
      venueRecallHint: '',
      venueRecallColor: 'var(--text-disabled)',
      intervalTimeRemaining: 0,
      showQuickEnvCheck: false
    });
  },

  switchScreen: (screen: 'setup' | 'logger' | 'monitor') => {
    set({ currentScreen: screen });
  },

  switchLoggerTab: (tab: 'flow' | 'tables' | 'env') => {
    set({ currentLoggerTab: tab });
  },

  switchMonitorZone: (zone: string) => {
    set({ currentMonitorZone: zone });
  },

  updateCounter: (type: 'entries' | 'exits', change: number) => {
    set((state) => {
      const val = Math.max(0, state.flow[type] + change);
      return {
        flow: { ...state.flow, [type]: val }
      };
    });
  },

  submitInterval: async (timeLabel: string) => {
    const { session, loggedKpis, manualSignals, flow } = get();
    const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://20.219.216.138';

    if (!session.sessionId) {
      showToast('No active session. Offline interval submit.', 'warn');
    }

    try {
      if (session.sessionId) {
        const keys = Object.keys(loggedKpis).filter(k => loggedKpis[k]);
        
        const promises = keys.map(async (key) => {
          const suffixes = ['crowd_energy', 'environment', 'commercial', 'crowd_stress'];
          let zoneId = '';
          let famId = '';
          for (const suf of suffixes) {
            if (key.endsWith(`_${suf}`)) {
              famId = suf;
              zoneId = key.substring(0, key.length - suf.length - 1);
              break;
            }
          }

          const famObj = KPI_FAMILIES.find((f) => f.id === famId);
          if (!famObj) return;

          let overallRag = 'green';
          const readings = famObj.signals.map((sigName) => {
            const val = manualSignals[`${zoneId}_${famId}_${sigName}`];
            const optInfo = SIGNAL_OPTIONS[sigName];
            const optIdx = optInfo ? optInfo.options.indexOf(val) : -1;
            const rag = optIdx !== -1 ? optInfo.rag[optIdx] : 'green';
            const score = optIdx !== -1 ? optInfo.scores[optIdx] : 0.9;

            if (rag === 'red') overallRag = 'red';
            else if (rag === 'amber' && overallRag !== 'red') overallRag = 'amber';

            return {
              signal_label: sigName,
              value_numeric: score,
              value_text: val || 'No input'
            };
          });

          const res = await fetch(`${BASE_URL}/api/kpi/session/${session.sessionId}/assessment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              family_id: FAMILY_ID_MAP[famId],
              zone: zoneId,
              rag_status: overallRag,
              notes: `Interval ${session.intervalCount} assessment`,
              readings
            })
          });
          if (!res.ok) {
            throw new Error(`Failed to submit assessment for ${zoneId} - ${famId}`);
          }
        });

        await Promise.all(promises);
      }

      const ent = flow.entries;
      const ex = flow.exits;
      const newHistory = [
        { time: timeLabel, entries: ent, exits: ex },
        ...flow.history
      ].slice(0, 5);

      set((state) => ({
        flow: {
          entries: 0,
          exits: 0,
          totals: {
            entries: state.flow.totals.entries + ent,
            exits: state.flow.totals.exits + ex
          },
          history: newHistory
        },
        session: {
          ...state.session,
          intervalCount: state.session.intervalCount + 1
        },
        loggedKpis: {},
        lastIntervalSignals: { ...state.manualSignals },
        manualSignals: {},
        intervalTimeRemaining: state.session.interval * 60
      }));
      showToast('Interval submitted successfully', 'ok');
    } catch (err: any) {
      showToast(`Submit failed: ${err.message || err}`, 'warn');
      throw err;
    }
  },

  saveTableAction: (tableId: string, pplCount: number | '6+', custType: string, note: string) => {
    set((state) => {
      const list = state.tables.map(t => {
        if (t.id === tableId) {
          const isNewSeat = !t.occupied;
          return {
            ...t,
            occupied: true,
            pplCount,
            custType,
            note,
            seatedTime: isNewSeat ? Date.now() : t.seatedTime
          };
        }
        return t;
      });
      return { tables: list };
    });
  },

  clearTableAction: (tableId: string) => {
    let dwellText = '';
    const { tables } = get();
    const table = tables.find(t => t.id === tableId);
    if (!table || !table.seatedTime) return null;

    const m = Math.floor((Date.now() - table.seatedTime) / 60000);
    const hrs = Math.floor(m / 60);
    const mins = m % 60;
    dwellText = `${hrs}h ${mins}m`;

    set((state) => {
      const list = state.tables.map(t => {
        if (t.id === tableId) {
          return {
            ...t,
            occupied: false,
            pplCount: null,
            custType: null,
            note: '',
            seatedTime: null
          };
        }
        return t;
      });
      return { tables: list };
    });

    return { tableId, dwellText };
  },

  pickEnvValue: (property: 'sound' | 'temp' | 'energy' | 'queue', value: string) => {
    set((state) => ({
      environment: { ...state.environment, [property]: value }
    }));
  },

  submitIncidentAction: (type: string, severity: 'watch' | 'alert', zone: string, note: string) => {
    const complaint: Complaint = {
      type,
      severity,
      zone,
      note,
      timestamp: Date.now()
    };
    set((state) => ({
      environment: {
        ...state.environment,
        complaints: [...state.environment.complaints, complaint]
      }
    }));
  },

  saveKpiCardUpdate: (zoneId: string, famId: string, signalsData: Record<string, string>) => {
    const key = `${zoneId}_${famId}`;
    set((state) => {
      const newManualSignals = { ...state.manualSignals };
      Object.keys(signalsData).forEach(sig => {
        newManualSignals[`${key}_${sig}`] = signalsData[sig];
      });

      const famObj = KPI_FAMILIES.find((f) => f.id === famId);
      const allSelected = famObj ? famObj.signals.every(sig => newManualSignals[`${key}_${sig}`]) : false;

      const newLogged = { ...state.loggedKpis };
      if (allSelected) {
        newLogged[key] = Date.now();
      } else {
        delete newLogged[key];
      }

      return {
        loggedKpis: newLogged,
        manualSignals: newManualSignals
      };
    });
  },

  overrideKpiStatus: (zoneId: string, famId: string, overrideValue: string) => {
    const key = `${zoneId}_${famId}`;
    set((state) => ({
      kpiOverrides: { ...state.kpiOverrides, [key]: overrideValue }
    }));
  },

  decrementIntervalTime: () => {
    set((state) => ({
      intervalTimeRemaining: Math.max(0, state.intervalTimeRemaining - 1)
    }));
  },

  resetIntervalTime: () => {
    const { session } = get();
    set({ intervalTimeRemaining: session.interval * 60 });
  },

  setShowQuickEnvCheck: (val: boolean) => {
    set({ showQuickEnvCheck: val });
  }
}));
