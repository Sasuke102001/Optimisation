-- Run on Azure PostgreSQL polynovea_m3 database
-- Replaces existing 7-family seed with 4 rationalized families

TRUNCATE m3_kpi_signals CASCADE;
TRUNCATE m3_kpi_families RESTART IDENTITY CASCADE;

INSERT INTO m3_kpi_families (slug, label, description, zone, layer) VALUES
  ('crowd_energy',  'Crowd Energy',       'Energy level, dancefloor activation, social mixing', NULL, 'A'),
  ('environment',   'Environment',        'Sound level, temperature, atmosphere coherence',     NULL, 'A'),
  ('commercial',    'Commercial Signal',  'Table turnover, dwell behaviour, bar activity',      NULL, 'A'),
  ('crowd_stress',  'Crowd Stress',       'Fatigue signs, overcrowding, comfort signals',       NULL, 'A');

INSERT INTO m3_kpi_signals (family_id, slug, label, source_type) VALUES
  -- Crowd Energy
  ((SELECT id FROM m3_kpi_families WHERE slug = 'crowd_energy'), 'is_anyone_dancing', 'Is anyone dancing?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'crowd_energy'), 'room_energy_level', 'How is the room energy?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'crowd_energy'), 'groups_mixing', 'Are groups mixing and socializing?', 'manual'),
  -- Environment
  ((SELECT id FROM m3_kpi_families WHERE slug = 'environment'), 'sound_level_working', 'Is the sound level working for the crowd?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'environment'), 'temperature_feeling', 'How is the temperature feeling?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'environment'), 'atmosphere_right', 'Is the atmosphere feeling right?', 'manual'),
  -- Commercial Signal
  ((SELECT id FROM m3_kpi_families WHERE slug = 'commercial'), 'table_turnover', 'Are tables turning over?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'commercial'), 'dwell_behaviour', 'Are people staying or leaving early?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'commercial'), 'bar_activity', 'How is bar activity?', 'manual'),
  -- Crowd Stress
  ((SELECT id FROM m3_kpi_families WHERE slug = 'crowd_stress'), 'fatigue_signs', 'Is the crowd showing fatigue signs?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'crowd_stress'), 'overcrowding', 'Is the venue feeling overcrowded?', 'manual'),
  ((SELECT id FROM m3_kpi_families WHERE slug = 'crowd_stress'), 'visible_discomfort', 'Is anyone visibly uncomfortable?', 'manual');
