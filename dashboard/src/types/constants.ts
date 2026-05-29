export const ZONES = [
  { id: 'entrance',    label: 'Entrance',    icon: '🚪', desc: 'Arrival, first impressions, initial flow',   relevant: ['flow', 'engagement', 'environment'] },
  { id: 'queue',       label: 'Queue',       icon: '🚶', desc: 'Queue management, wait behaviour, pressure', relevant: ['flow', 'service', 'complaints'] },
  { id: 'main_bar',    label: 'Main Bar',    icon: '🥃', desc: 'Primary service, ordering, throughput',      relevant: ['service', 'commercial', 'complaints'] },
  { id: 'dancefloor',  label: 'Dancefloor',  icon: '🎵', desc: 'Focal energy zone, engagement epicentre',    relevant: ['engagement', 'overload', 'environment'] },
  { id: 'circulation', label: 'Corridor',    icon: '↔',  desc: 'Circulation flow, connector zones',          relevant: ['flow', 'overload'] },
  { id: 'exits',       label: 'Exits',       icon: '🚪', desc: 'Exit behaviour, egress flow, drift signals', relevant: ['flow', 'engagement'] },
  { id: 'quiet',       label: 'Quiet Zone',  icon: '🌙', desc: 'Recovery, decompression, low-stimulus',      relevant: ['overload', 'environment'] },
  { id: 'tables',      label: 'Seating',     icon: '🪑', desc: 'Tables, dwell behaviour, table spend',       relevant: ['commercial', 'service', 'overload'] }
];

export const KPI_FAMILIES = [
  { id: 'flow',        name: 'Flow',               icon: '🌊', desc: 'Movement, density, congestion',           signals: ['Crowd density comfort', 'Queue spillback risk', 'Directional flow stability'] },
  { id: 'service',     name: 'Service',             icon: '⚡', desc: 'Speed, load, throughput, friction',       signals: ['Service speed', 'Queue pressure', 'Staff load pressure'] },
  { id: 'engagement',  name: 'Engagement',          icon: '🔥', desc: 'Energy, participation, momentum',         signals: ['Engagement level', 'Dancefloor activation', 'Social energy'] },
  { id: 'overload',    name: 'Overload / Recovery', icon: '⚠️', desc: 'Fatigue, sensory load, overstimulation',  signals: ['Fatigue signals', 'Sensory load pressure', 'Overstimulation risk'] },
  { id: 'complaints',  name: 'Complaints & Risk',   icon: '🚨', desc: 'Issues, contradictions, friction hotspots',signals: ['Complaint rate', 'Incident clustering', 'Hotspot intensity'] },
  { id: 'commercial',  name: 'Commercial',          icon: '💠', desc: 'Spend intent, conversion, retention',     signals: ['Commercial momentum', 'Table occupancy speed', 'Abandonment behaviour'] },
  { id: 'environment', name: 'Environment',         icon: '🌡️', desc: 'Sound, temperature, atmosphere',         signals: ['Sound level suitability', 'Thermal comfort', 'Atmosphere coherence'] }
];
export function getSignalSource(name: string): 'manual' | 'sensor' | 'derived' {
  const manuals = [
    'Crowd density comfort', 'Engagement level', 'Dancefloor activation', 'Social energy',
    'Service speed', 'Queue pressure', 'Staff load pressure', 'Fatigue signals',
    'Sensory load pressure', 'Overstimulation risk', 'Hotspot intensity',
    'Commercial momentum', 'Abandonment behaviour', 'Atmosphere coherence'
  ];
  const sensors = ['Sound level suitability', 'Thermal comfort'];
  if (manuals.includes(name)) return 'manual';
  if (sensors.includes(name)) return 'sensor';
  return 'derived';
}
