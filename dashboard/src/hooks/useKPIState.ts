import { useSessionStore } from '../store/sessionStore';
import { ZONES, KPI_FAMILIES } from '../types/constants';
import type { RAGStatus } from '../types';

export function useKPIState() {
  const flow = useSessionStore((state) => state.flow);
  const tables = useSessionStore((state) => state.tables);
  const environment = useSessionStore((state) => state.environment);
  const loggedKpis = useSessionStore((state) => state.loggedKpis);
  const manualSignals = useSessionStore((state) => state.manualSignals);
  const kpiOverrides = useSessionStore((state) => state.kpiOverrides);

  const isKpiCardLogged = (zoneId: string, famId: string) => {
    const key = `${zoneId}_${famId}`;
    return !!loggedKpis[key];
  };

  const SIGNAL_OPTIONS: Record<string, { options: string[], rag: string[] }> = {
    is_anyone_dancing: { options: ['No', 'A few', 'Floor is alive'], rag: ['red', 'amber', 'green'] },
    room_energy_level: { options: ['Dead', 'Building', 'Peak'], rag: ['red', 'amber', 'green'] },
    groups_mixing: { options: ['No', 'Some', 'Yes'], rag: ['red', 'amber', 'green'] },
    sound_level_working: { options: ['Too quiet', 'Right', 'Too loud'], rag: ['amber', 'green', 'red'] },
    temperature_feeling: { options: ['Cold', 'Comfortable', 'Hot'], rag: ['amber', 'green', 'red'] },
    atmosphere_right: { options: ['Off', 'Building', 'On'], rag: ['red', 'amber', 'green'] },
    table_turnover: { options: ['Slow', 'Normal', 'Fast'], rag: ['red', 'amber', 'green'] },
    dwell_behaviour: { options: ['Leaving early', 'Normal dwell', 'Long stays'], rag: ['red', 'amber', 'green'] },
    bar_activity: { options: ['Dead', 'Active', 'Very busy'], rag: ['red', 'amber', 'green'] },
    fatigue_signs: { options: ['Yes, dying', 'Getting tired', 'Fresh'], rag: ['red', 'amber', 'green'] },
    overcrowding: { options: ['Yes, too packed', 'Busy', 'Fine'], rag: ['red', 'amber', 'green'] },
    visible_discomfort: { options: ['Yes, several', 'One or two', 'No'], rag: ['red', 'amber', 'green'] }
  };

  const getIndividualSignalStatus = (zoneId: string, kpiFamilyId: string, sigName: string): 'ok' | 'watch' | 'alert' => {
    const val = manualSignals[`${zoneId}_${kpiFamilyId}_${sigName}`];
    if (val) {
      const optInfo = SIGNAL_OPTIONS[sigName];
      const optIdx = optInfo ? optInfo.options.indexOf(val) : -1;
      const rag = optIdx !== -1 ? optInfo.rag[optIdx] : 'green';
      const ragMap: Record<string, 'ok' | 'watch' | 'alert'> = {
        green: 'ok',
        amber: 'watch',
        red: 'alert'
      };
      return ragMap[rag] || 'ok';
    }
    return 'ok';
  };

  const getCalculatedKpiStatus = (zoneId: string, kpiFamilyId: string): 'ok' | 'watch' | 'alert' => {
    const overrideKey = `${zoneId}_${kpiFamilyId}`;
    if (kpiOverrides[overrideKey]) return kpiOverrides[overrideKey] as 'ok' | 'watch' | 'alert';

    const fam = KPI_FAMILIES.find((f) => f.id === kpiFamilyId);
    let manualStatus: 'ok' | 'watch' | 'alert' = 'ok';

    if (fam) {
      for (const sig of fam.signals) {
        const val = manualSignals[`${zoneId}_${kpiFamilyId}_${sig}`];
        if (val) {
          const optInfo = SIGNAL_OPTIONS[sig];
          const optIdx = optInfo ? optInfo.options.indexOf(val) : -1;
          const rag = optIdx !== -1 ? optInfo.rag[optIdx] : 'green';
          if (rag === 'red') {
            manualStatus = 'alert';
          } else if (rag === 'amber' && manualStatus !== 'alert') {
            manualStatus = 'watch';
          }
        }
      }
    }

    let autoStatus: 'ok' | 'watch' | 'alert' = 'ok';
    const activeComplaints = environment.complaints.filter((c) => c.zone === zoneId);
    const occupiedCount = tables.filter((t) => t.occupied).length;

    if (kpiFamilyId === 'crowd_energy') {
      if (environment.energy === 'Flat') autoStatus = 'alert';
      else if (environment.energy === 'Relaxed') autoStatus = 'watch';
    } else if (kpiFamilyId === 'environment') {
      if (environment.sound === 'Very Loud') autoStatus = 'alert';
      else if (environment.temp === 'Hot' || environment.temp === 'Cold') autoStatus = 'watch';
    } else if (kpiFamilyId === 'commercial') {
      if (occupiedCount < 5) autoStatus = 'watch';
    } else if (kpiFamilyId === 'crowd_stress') {
      if (activeComplaints.length > 0) {
        const hasAlert = activeComplaints.some((c) => c.severity === 'alert');
        autoStatus = hasAlert ? 'alert' : 'watch';
      }
      if (environment.queue.includes('Long')) autoStatus = 'alert';
      else if (environment.queue.includes('Medium')) autoStatus = 'watch';
      
      if (zoneId === 'entrance' || zoneId === 'queue') {
        const netDiff = flow.totals.entries - flow.totals.exits;
        if (netDiff > 150) autoStatus = 'alert';
        else if (netDiff > 100) autoStatus = 'watch';
      }
      if (environment.sound === 'Very Loud') {
        if (autoStatus !== 'alert') autoStatus = 'watch';
      }
    }

    if (manualStatus === 'alert' || autoStatus === 'alert') return 'alert';
    if (manualStatus === 'watch' || autoStatus === 'watch') return 'watch';
    return 'ok';
  };

  const getCalculatedZoneHealth = (zoneId: string): RAGStatus => {
    const zone = ZONES.find((z) => z.id === zoneId);
    if (!zone) return 'none';

    let hasAnyLogged = false;
    let hasWatch = false;
    let hasAlert = false;

    zone.relevant.forEach((famId) => {
      const status = getCalculatedKpiStatus(zoneId, famId);
      if (status === 'alert') hasAlert = true;
      if (status === 'watch') hasWatch = true;

      if (isKpiCardLogged(zoneId, famId)) hasAnyLogged = true;
    });

    if (hasAlert) return 'alert';
    if (hasWatch) return 'watch';
    if (hasAnyLogged) return 'ok';
    return 'none';
  };

  return {
    isKpiCardLogged,
    getIndividualSignalStatus,
    getCalculatedKpiStatus,
    getCalculatedZoneHealth
  };
}
