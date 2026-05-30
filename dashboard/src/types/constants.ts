export const ZONES = [
  { id: 'entrance',    label: 'Entrance',    icon: '🚪', desc: 'Arrival, first impressions, initial flow',   relevant: ['crowd_energy', 'environment', 'crowd_stress'] },
  { id: 'queue',       label: 'Queue',       icon: '🚶', desc: 'Queue management, wait behaviour, pressure', relevant: ['crowd_stress', 'commercial'] },
  { id: 'main_bar',    label: 'Main Bar',    icon: '🥃', desc: 'Primary service, ordering, throughput',      relevant: ['commercial', 'crowd_stress'] },
  { id: 'dancefloor',  label: 'Dancefloor',  icon: '🎵', desc: 'Focal energy zone, engagement epicentre',    relevant: ['crowd_energy', 'environment', 'crowd_stress'] },
  { id: 'circulation', label: 'Corridor',    icon: '↔',  desc: 'Circulation flow, connector zones',          relevant: ['crowd_stress'] },
  { id: 'exits',       label: 'Exits',       icon: '🚪', desc: 'Exit behaviour, egress flow, drift signals', relevant: ['crowd_energy', 'crowd_stress'] },
  { id: 'quiet',       label: 'Quiet Zone',  icon: '🌙', desc: 'Recovery, decompression, low-stimulus',      relevant: ['crowd_stress', 'environment'] },
  { id: 'tables',      label: 'Seating',     icon: '🪑', desc: 'Tables, dwell behaviour, table spend',       relevant: ['commercial', 'crowd_stress'] }
];

export const KPI_FAMILIES = [
  { id: 'crowd_energy',  name: 'Crowd Energy',       icon: '⚡', desc: 'Energy level, dancefloor activation, social mixing', signals: ['is_anyone_dancing', 'room_energy_level', 'groups_mixing'] },
  { id: 'environment',   name: 'Environment',        icon: '🌡️', desc: 'Sound level, temperature, atmosphere coherence',     signals: ['sound_level_working', 'temperature_feeling', 'atmosphere_right'] },
  { id: 'commercial',    name: 'Commercial Signal',  icon: '💰', desc: 'Table turnover, dwell behaviour, bar activity',      signals: ['table_turnover', 'dwell_behaviour', 'bar_activity'] },
  { id: 'crowd_stress',  name: 'Crowd Stress',       icon: '⚠️', desc: 'Fatigue signs, overcrowding, comfort signals',       signals: ['fatigue_signs', 'overcrowding', 'visible_discomfort'] }
];

export function getSignalSource(name: string): 'manual' | 'sensor' | 'derived' {
  const manuals = [
    'is_anyone_dancing', 'room_energy_level', 'groups_mixing',
    'sound_level_working', 'temperature_feeling', 'atmosphere_right',
    'table_turnover', 'dwell_behaviour', 'bar_activity',
    'fatigue_signs', 'overcrowding', 'visible_discomfort'
  ];
  if (manuals.includes(name)) return 'manual';
  return 'derived';
}
