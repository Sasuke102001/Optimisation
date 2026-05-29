import { useSessionStore } from '../store/sessionStore';
import { ZONES, KPI_FAMILIES, getSignalSource } from '../types/constants';
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

  const getIndividualSignalStatus = (zoneId: string, kpiFamilyId: string, sigName: string): 'ok' | 'watch' | 'alert' => {
    const source = getSignalSource(sigName);

    if (source === 'manual') {
      const val = manualSignals[`${zoneId}_${kpiFamilyId}_${sigName}`];
      return (val as 'ok' | 'watch' | 'alert') || 'ok';
    }

    if (sigName === 'Sound level suitability') {
      if (environment.sound === 'Very Loud') return 'watch';
      return 'ok';
    }
    if (sigName === 'Thermal comfort') {
      if (environment.temp === 'Hot' || environment.temp === 'Cold') return 'watch';
      return 'ok';
    }
    if (sigName === 'Complaint rate') {
      const count = environment.complaints.filter((c) => c.zone === zoneId).length;
      if (count > 0) return 'watch';
      return 'ok';
    }
    if (sigName === 'Incident clustering') {
      const count = environment.complaints.filter((c) => c.zone === zoneId).length;
      if (count > 1) return 'alert';
      return 'ok';
    }
    if (sigName === 'Crowd density comfort') {
      const net = flow.totals.entries - flow.totals.exits;
      if (net > 150) return 'alert';
      if (net > 100) return 'watch';
      return 'ok';
    }
    if (sigName === 'Queue spillback risk') {
      if (environment.queue.includes('Long')) return 'alert';
      if (environment.queue.includes('Medium')) return 'watch';
      return 'ok';
    }
    if (sigName === 'Table occupancy speed') {
      const occupied = tables.filter((t) => t.occupied).length;
      if (occupied < 5) return 'watch';
      return 'ok';
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
        if (getSignalSource(sig) === 'manual') {
          const val = manualSignals[`${zoneId}_${kpiFamilyId}_${sig}`];
          if (val === 'alert') {
            manualStatus = 'alert';
          } else if (val === 'watch' && manualStatus !== 'alert') {
            manualStatus = 'watch';
          }
        }
      }
    }

    let autoStatus: 'ok' | 'watch' | 'alert' = 'ok';
    const activeComplaints = environment.complaints.filter((c) => c.zone === zoneId);

    if (kpiFamilyId === 'complaints') {
      if (activeComplaints.length > 0) {
        const hasAlert = activeComplaints.some((c) => c.severity === 'alert');
        autoStatus = hasAlert ? 'alert' : 'watch';
      }
    } else if (kpiFamilyId === 'flow') {
      if (zoneId === 'entrance' || zoneId === 'queue') {
        const netDiff = flow.totals.entries - flow.totals.exits;
        if (netDiff > 150) autoStatus = 'alert';
        else if (netDiff > 100) autoStatus = 'watch';
      }
    } else if (kpiFamilyId === 'service') {
      if (zoneId === 'tables') {
        const occupied = tables.filter((t) => t.occupied).length;
        if (occupied >= 25) autoStatus = 'alert';
        else if (occupied >= 18) autoStatus = 'watch';
      }
      if (environment.queue.includes('Long')) autoStatus = 'alert';
      else if (environment.queue.includes('Medium')) autoStatus = 'watch';
    } else if (kpiFamilyId === 'engagement') {
      if (environment.energy === 'Flat') autoStatus = 'alert';
      else if (environment.energy === 'Relaxed') autoStatus = 'watch';
    } else if (kpiFamilyId === 'overload') {
      if (environment.sound === 'Very Loud') autoStatus = 'alert';
      else if (environment.temp === 'Hot' || environment.temp === 'Cold') autoStatus = 'watch';
      const longDwellers = tables.filter((t) => {
        if (!t.occupied || !t.seatedTime) return false;
        return Date.now() - t.seatedTime >= 90 * 60000;
      }).length;
      if (longDwellers >= 2) autoStatus = 'watch';
    } else if (kpiFamilyId === 'commercial') {
      const occupied = tables.filter((t) => t.occupied).length;
      if (occupied > 22) autoStatus = 'ok';
      else if (occupied < 5) autoStatus = 'watch';
    } else if (kpiFamilyId === 'environment') {
      if (environment.sound === 'Very Loud') autoStatus = 'watch';
      if (environment.temp === 'Hot') autoStatus = 'watch';
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
      // Always compute worst-case status regardless of logging state —
      // auto-derived signals (flow, environment, tables) are live and
      // should surface as amber/red even before the operator logs a KPI card.
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
