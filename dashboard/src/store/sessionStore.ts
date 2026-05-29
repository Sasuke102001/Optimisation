import { create } from 'zustand';
import type { Table, IntervalRecord, Complaint } from '../types';

interface SessionState {
  session: {
    active: boolean;
    venue: string;
    mode: 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP';
    interval: number;
    startTime: number | null;
    number: number;
    operator: string;
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
  adjustTableType: (type: 'two' | 'four' | 'six', delta: number) => void;
  pickSetupMode: (mode: 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP') => void;
  pickSetupInterval: (interval: number) => void;
  startSession: (operatorName: string) => boolean;
  endSession: () => void;
  switchScreen: (screen: 'setup' | 'logger' | 'monitor') => void;
  switchLoggerTab: (tab: 'flow' | 'tables' | 'env') => void;
  switchMonitorZone: (zone: string) => void;
  updateCounter: (type: 'entries' | 'exits', change: number) => void;
  submitInterval: (timeLabel: string) => void;
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

export const useSessionStore = create<SessionState>((set, get) => ({
  session: {
    active: false,
    venue: '',
    mode: 'ENGINEERED',
    interval: 15,
    startTime: null,
    number: 3,
    operator: ''
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
      session: { ...state.session, venue },
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

  startSession: (operatorName: string) => {
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

    set((state) => ({
      session: {
        ...state.session,
        active: true,
        operator: operatorName || 'Operator',
        startTime: Date.now()
      },
      tables: newTables,
      currentScreen: 'logger',
      intervalTimeRemaining: state.session.interval * 60
    }));

    return true;
  },

  endSession: () => {
    set({
      session: {
        active: false,
        venue: '',
        mode: 'ENGINEERED',
        interval: 15,
        startTime: null,
        number: 3,
        operator: ''
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

  submitInterval: (timeLabel: string) => {
    const { flow } = get();
    const ent = flow.entries;
    const ex = flow.exits;

    const newHistory = [
      {
        time: timeLabel,
        entries: ent,
        exits: ex
      },
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
      intervalTimeRemaining: state.session.interval * 60
    }));
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
      return {
        loggedKpis: { ...state.loggedKpis, [key]: Date.now() },
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
