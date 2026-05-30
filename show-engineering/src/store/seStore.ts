import { create } from 'zustand'

// ─── Types ────────────────────────────────────────────────────────────────────

export type NavSection = 'plan' | 'history'

export type PlanScreen =
  | 'venue_selector'
  | 'plan_generation'
  | 'show_plan'
  | 'conversational'

export type HistoryScreen = 'post_show_review' | 'show_history'

export type GenerationStatus =
  | 'idle'
  | 'stage_1_running'
  | 'stage_2_running'
  | 'complete'
  | 'error'

export type AgentStatus = 'waiting' | 'running' | 'done'

export interface Venue {
  id: number
  name: string
  area: string
  city: string
  types: string[]
  display_tags: string[]
  primary_type: string | null
  cascade_types: string[]
}

export interface SessionContext {
  date: string
  startTime: string     // HH:MM 24h, e.g. "21:00"
  endTime: string       // HH:MM 24h, e.g. "00:00"
  phaseCount: number    // 2–5
  crowdSize: 'intimate' | 'medium' | 'large' | ''
  crowdType: 'regular' | 'corporate' | 'college' | 'mixed' | ''
  showType: 'dj_night' | 'live_band' | 'open_mic' | 'private_event' | ''
  notes: string
}

export interface AgentRow {
  id: number
  name: string
  role: string
  status: AgentStatus
}

export interface Phase {
  label: string
  startTimeStr: string  // HH:MM — for boundary input value
  endTimeStr: string
  timeRange: string     // "9 PM–12 AM"
  color: string
  goal: string
}

export interface PhasePresription {
  bpm: string
  chord: string
  key: string
  bass: string
  target: string
  brainwave: string
}

export interface PhaseLighting {
  intensity: string
  colour: string
  movement: string
}

// ─── Phase reference data ─────────────────────────────────────────────────────

const PHASE_PRESETS: Record<number, string[]> = {
  2: ['Opening', 'Wind Down'],
  3: ['Opening', 'Peak', 'Wind Down'],
  4: ['Opening', 'Build', 'Peak', 'Wind Down'],
  5: ['Opening', 'Warm Up', 'Build', 'Peak', 'Wind Down'],
}

export const PHASE_COLORS: Record<string, string> = {
  'Opening':   '#78716C',
  'Warm Up':   '#6366F1',
  'Build':     '#7C3AED',
  'Peak':      '#E6D3A3',
  'Wind Down': '#D97706',
}

const PHASE_GOALS: Record<string, string> = {
  'Opening':   'Warm entry — ambient social priming',
  'Warm Up':   'Energy onset — transitional momentum',
  'Build':     'Momentum shift — floor activation',
  'Peak':      'Full release — sustained energy plateau',
  'Wind Down': 'Graceful close — spend drive',
}

export const PHASE_PRESCRIPTIONS: Record<string, PhasePresription> = {
  'Opening':   { bpm: '105–112', chord: 'I–IV–V',                key: 'F major — Ionian',     bass: '55–70Hz · nominal',            target: 'Social priming, reduce inhibition threshold',        brainwave: 'Low-alpha 8–9Hz'    },
  'Warm Up':   { bpm: '112–118', chord: 'I–V–vi–IV',             key: 'C major — Ionian',     bass: '58–72Hz +1dB',                 target: 'Energy build, social engagement onset',              brainwave: 'Alpha 9–10Hz'        },
  'Build':     { bpm: '118–124', chord: 'i–VII–VI–VII',          key: 'A minor — Aeolian',    bass: '60–80Hz +2dB',                 target: 'Momentum, floor activation, social engagement',      brainwave: 'High-alpha 10–12Hz'  },
  'Peak':      { bpm: '128–134', chord: 'i–VII–VI–VII (8-bar)',  key: 'D minor — Dorian',     bass: '65–85Hz +3dB + 40Hz rumble',   target: 'Full motor activation, peak release, social proof', brainwave: 'Low-beta 14–16Hz'    },
  'Wind Down': { bpm: '110–116', chord: 'I–V–vi–IV',             key: 'G major — Mixolydian', bass: '55–65Hz · taper to nominal',   target: 'Graceful energy reduction, increase dwell + spend', brainwave: 'Alpha bridge 9–10Hz' },
}

export const PHASE_LIGHTING_DATA: Record<string, PhaseLighting> = {
  'Opening':   { intensity: '40%', colour: 'Warm white',            movement: 'Slow pulse'           },
  'Warm Up':   { intensity: '50%', colour: 'Cool white / soft blue', movement: 'Gentle sweep'        },
  'Build':     { intensity: '60%', colour: 'Blue / purple',          movement: 'Medium sweep'         },
  'Peak':      { intensity: '85%', colour: 'Multi-colour',           movement: 'Fast strobe on drops' },
  'Wind Down': { intensity: '30%', colour: 'Warm amber',             movement: 'Static'               },
}

// ─── Phase computation ────────────────────────────────────────────────────────

function timeStrToMins(t: string): number {
  const [h, m] = t.split(':').map(Number)
  return h * 60 + (m ?? 0)
}

function minsToLabel(totalMins: number): string {
  const m = ((totalMins % 1440) + 1440) % 1440
  const h = Math.floor(m / 60)
  const min = m % 60
  const period = h >= 12 ? 'PM' : 'AM'
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h
  return min === 0
    ? `${h12} ${period}`
    : `${h12}:${String(min).padStart(2, '0')} ${period}`
}

function minsToTimeStr(totalMins: number): string {
  const m = ((totalMins % 1440) + 1440) % 1440
  const h = Math.floor(m / 60)
  const min = m % 60
  return `${String(h).padStart(2, '0')}:${String(min).padStart(2, '0')}`
}

export function formatTimeStr(hhmm: string): string {
  const [hStr, mStr] = hhmm.split(':')
  const h = parseInt(hStr, 10)
  const min = parseInt(mStr ?? '0', 10)
  const period = h >= 12 ? 'PM' : 'AM'
  const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h
  return min === 0 ? `${h12} ${period}` : `${h12}:${String(min).padStart(2, '0')} ${period}`
}

export function buildPhases(
  startTime: string,
  endTime: string,
  phaseCount: number,
  manualBoundaries: string[] | null,
): Phase[] {
  const count = Math.max(2, Math.min(5, phaseCount))
  const labels = PHASE_PRESETS[count] ?? PHASE_PRESETS[3]
  const startMins = timeStrToMins(startTime)
  let endMins = timeStrToMins(endTime)
  if (endMins <= startMins) endMins += 1440

  const sliceMins = (endMins - startMins) / count
  const boundaries: number[] = [startMins]

  for (let i = 1; i < count; i++) {
    if (manualBoundaries && manualBoundaries.length === count - 1 && manualBoundaries[i - 1]) {
      let bMins = timeStrToMins(manualBoundaries[i - 1])
      if (bMins < startMins) bMins += 1440
      boundaries.push(bMins)
    } else {
      boundaries.push(Math.round(startMins + i * sliceMins))
    }
  }
  boundaries.push(endMins)

  return labels.map((label, i) => ({
    label,
    startTimeStr: minsToTimeStr(boundaries[i]),
    endTimeStr:   minsToTimeStr(boundaries[i + 1]),
    timeRange:    `${minsToLabel(boundaries[i])}–${minsToLabel(boundaries[i + 1])}`,
    color:        PHASE_COLORS[label] ?? '#78716C',
    goal:         PHASE_GOALS[label]  ?? '',
  }))
}

export function computeDurationHint(startTime: string, endTime: string, phaseCount: number): string {
  const startMins = timeStrToMins(startTime)
  let endMins = timeStrToMins(endTime)
  if (endMins <= startMins) endMins += 1440
  const totalMins = endMins - startMins
  const perPhase = Math.round(totalMins / phaseCount)
  const hrs = totalMins / 60
  const hoursLabel = hrs % 1 === 0 ? `${hrs} hr` : `${Math.round(hrs * 10) / 10} hrs`
  return `${hoursLabel} show · ${phaseCount} phases · ~${perPhase} min each`
}

// ─── State ────────────────────────────────────────────────────────────────────

interface SEState {
  navSection: NavSection
  planScreen: PlanScreen
  historyScreen: HistoryScreen

  venueSearch: string
  selectedVenue: Venue | null

  sessionContext: SessionContext

  // null = auto equal splits; string[] of length phaseCount-1 = manual overrides
  manualBoundaries: string[] | null

  generationStatus: GenerationStatus
  agents: AgentRow[]
  conversationalPanelOpen: boolean

  setNavSection: (s: NavSection) => void
  setPlanScreen: (s: PlanScreen) => void
  setHistoryScreen: (s: HistoryScreen) => void
  setVenueSearch: (q: string) => void
  selectVenue: (v: Venue) => void
  clearVenue: () => void
  setSessionContext: (patch: Partial<SessionContext>) => void
  setBoundary: (index: number, time: string) => void
  resetBoundaries: () => void
  startGeneration: () => void
  resetGeneration: () => void
  setConversationalPanel: (open: boolean) => void
  updateAgentStatus: (id: number, status: AgentStatus) => void
  setGenerationStatus: (s: GenerationStatus) => void
}

// ─── Mock venue list ──────────────────────────────────────────────────────────

export const MOCK_VENUES: Venue[] = [
  { id: 1,  name: 'Todi Mill Social',         area: 'Lower Parel',  city: 'Mumbai',      types: ['bar', 'restaurant'] },
  { id: 2,  name: 'Kitty Su',                 area: 'Lower Parel',  city: 'Mumbai',      types: ['nightclub'] },
  { id: 3,  name: 'Tryst',                    area: 'Juhu',         city: 'Mumbai',      types: ['nightclub', 'bar'] },
  { id: 4,  name: 'Aer',                      area: 'Worli',        city: 'Mumbai',      types: ['lounge', 'rooftop'] },
  { id: 5,  name: 'Blue Frog',                area: 'Lower Parel',  city: 'Mumbai',      types: ['live_music', 'bar'] },
  { id: 6,  name: 'The Korner House',         area: 'Bandra',       city: 'Mumbai',      types: ['bar', 'restaurant'] },
  { id: 7,  name: 'Hard Rock Cafe',           area: 'Andheri',      city: 'Mumbai',      types: ['bar', 'live_music'] },
  { id: 8,  name: 'Tresind',                  area: 'Vashi',        city: 'Navi Mumbai', types: ['restaurant'] },
  { id: 9,  name: 'Whisky Samba',             area: 'Andheri',      city: 'Mumbai',      types: ['bar', 'lounge'] },
  { id: 10, name: 'KOKO',                     area: 'Lower Parel',  city: 'Mumbai',      types: ['nightclub', 'bar'] },
  { id: 11, name: 'Dome at Intercontinental', area: 'Marine Lines', city: 'Mumbai',      types: ['rooftop', 'lounge'] },
  { id: 12, name: 'Bling - The Discotheque',  area: 'Juhu',         city: 'Mumbai',      types: ['nightclub'] },
]

// ─── Initial agents ───────────────────────────────────────────────────────────

const INITIAL_AGENTS: AgentRow[] = [
  { id: 1, name: 'Agent 1', role: 'Behavioral KAG',       status: 'waiting' },
  { id: 2, name: 'Agent 2', role: 'Behavioral RAG',       status: 'waiting' },
  { id: 3, name: 'Agent 3', role: 'Neuroacoustic KAG',    status: 'waiting' },
  { id: 4, name: 'Agent 4', role: 'Neuroacoustic RAG',    status: 'waiting' },
  { id: 5, name: 'Agent 5', role: 'Integrator',           status: 'waiting' },
  { id: 6, name: 'Agent 6', role: 'Prescriber',           status: 'waiting' },
  { id: 7, name: 'Agent 7', role: 'Conversational Guide', status: 'waiting' },
]

const DEFAULT_CONTEXT: SessionContext = {
  date: '',
  startTime: '21:00',
  endTime: '00:00',
  phaseCount: 3,
  crowdSize: '',
  crowdType: '',
  showType: '',
  notes: '',
}

// ─── Store ────────────────────────────────────────────────────────────────────

export const useSEStore = create<SEState>((set) => ({
  navSection: 'plan',
  planScreen: 'venue_selector',
  historyScreen: 'show_history',

  venueSearch: '',
  selectedVenue: null,

  sessionContext: { ...DEFAULT_CONTEXT },
  manualBoundaries: null,

  generationStatus: 'idle',
  agents: INITIAL_AGENTS,
  conversationalPanelOpen: false,

  setNavSection: (s) => set({ navSection: s }),
  setPlanScreen: (s) => set({ planScreen: s }),
  setHistoryScreen: (s) => set({ historyScreen: s }),
  setVenueSearch: (q) => set({ venueSearch: q }),
  selectVenue: (v) => set({ selectedVenue: v, venueSearch: '' }),
  clearVenue: () => set({
    selectedVenue: null,
    sessionContext: { ...DEFAULT_CONTEXT },
    manualBoundaries: null,
  }),
  setSessionContext: (patch) =>
    set((s) => ({
      sessionContext: { ...s.sessionContext, ...patch },
      // reset manual boundaries whenever phase count changes (presets shift)
      manualBoundaries: 'phaseCount' in patch ? null : s.manualBoundaries,
    })),
  setBoundary: (index, time) =>
    set((s) => {
      const count = s.sessionContext.phaseCount
      const base = buildPhases(s.sessionContext.startTime, s.sessionContext.endTime, count, null)
      const current = s.manualBoundaries ?? base.slice(0, -1).map((p) => p.endTimeStr)
      const next = [...current]
      next[index] = time
      return { manualBoundaries: next }
    }),
  resetBoundaries: () => set({ manualBoundaries: null }),
  startGeneration: () =>
    set({ generationStatus: 'stage_1_running', agents: INITIAL_AGENTS }),
  resetGeneration: () =>
    set({ generationStatus: 'idle', agents: INITIAL_AGENTS, planScreen: 'venue_selector', conversationalPanelOpen: false }),
  setConversationalPanel: (open) => set({ conversationalPanelOpen: open }),
  updateAgentStatus: (id, status) =>
    set((s) => ({
      agents: s.agents.map((a) => (a.id === id ? { ...a, status } : a)),
    })),
  setGenerationStatus: (status) => set({ generationStatus: status }),
}))
