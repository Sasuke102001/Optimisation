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
}

export interface SessionContext {
  date: string
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

// ─── State ────────────────────────────────────────────────────────────────────

interface SEState {
  // Navigation
  navSection: NavSection
  planScreen: PlanScreen
  historyScreen: HistoryScreen

  // Venue selection
  venueSearch: string
  selectedVenue: Venue | null

  // Session context
  sessionContext: SessionContext

  // Plan generation
  generationStatus: GenerationStatus
  agents: AgentRow[]
  conversationalPanelOpen: boolean

  // Actions
  setNavSection: (s: NavSection) => void
  setPlanScreen: (s: PlanScreen) => void
  setHistoryScreen: (s: HistoryScreen) => void
  setVenueSearch: (q: string) => void
  selectVenue: (v: Venue) => void
  clearVenue: () => void
  setSessionContext: (patch: Partial<SessionContext>) => void
  startGeneration: () => void
  resetGeneration: () => void
  setConversationalPanel: (open: boolean) => void
  updateAgentStatus: (id: number, status: AgentStatus) => void
  setGenerationStatus: (s: GenerationStatus) => void
}

// ─── Mock venue list (static until backend wired) ─────────────────────────────

export const MOCK_VENUES: Venue[] = [
  { id: 1,  name: 'Todi Mill Social',       area: 'Lower Parel',    city: 'Mumbai',      types: ['bar', 'restaurant'] },
  { id: 2,  name: 'Kitty Su',               area: 'Lower Parel',    city: 'Mumbai',      types: ['nightclub'] },
  { id: 3,  name: 'Tryst',                  area: 'Juhu',           city: 'Mumbai',      types: ['nightclub', 'bar'] },
  { id: 4,  name: 'Aer',                    area: 'Worli',          city: 'Mumbai',      types: ['lounge', 'rooftop'] },
  { id: 5,  name: 'Blue Frog',              area: 'Lower Parel',    city: 'Mumbai',      types: ['live_music', 'bar'] },
  { id: 6,  name: 'The Korner House',       area: 'Bandra',         city: 'Mumbai',      types: ['bar', 'restaurant'] },
  { id: 7,  name: 'Hard Rock Cafe',         area: 'Andheri',        city: 'Mumbai',      types: ['bar', 'live_music'] },
  { id: 8,  name: 'Tresind',               area: 'Vashi',          city: 'Navi Mumbai', types: ['restaurant'] },
  { id: 9,  name: 'Whisky Samba',          area: 'Andheri',        city: 'Mumbai',      types: ['bar', 'lounge'] },
  { id: 10, name: 'KOKO',                  area: 'Lower Parel',    city: 'Mumbai',      types: ['nightclub', 'bar'] },
  { id: 11, name: 'Dome at Intercontinental', area: 'Marine Lines', city: 'Mumbai',     types: ['rooftop', 'lounge'] },
  { id: 12, name: 'Bling - The Discotheque', area: 'Juhu',         city: 'Mumbai',      types: ['nightclub'] },
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

// ─── Store ────────────────────────────────────────────────────────────────────

export const useSEStore = create<SEState>((set) => ({
  navSection: 'plan',
  planScreen: 'venue_selector',
  historyScreen: 'show_history',

  venueSearch: '',
  selectedVenue: null,

  sessionContext: {
    date: '',
    crowdSize: '',
    crowdType: '',
    showType: '',
    notes: '',
  },

  generationStatus: 'idle',
  agents: INITIAL_AGENTS,
  conversationalPanelOpen: false,

  setNavSection: (s) => set({ navSection: s }),
  setPlanScreen: (s) => set({ planScreen: s }),
  setHistoryScreen: (s) => set({ historyScreen: s }),
  setVenueSearch: (q) => set({ venueSearch: q }),
  selectVenue: (v) => set({ selectedVenue: v, venueSearch: '' }),
  clearVenue: () => set({ selectedVenue: null, sessionContext: { date: '', crowdSize: '', crowdType: '', showType: '', notes: '' } }),
  setSessionContext: (patch) =>
    set((s) => ({ sessionContext: { ...s.sessionContext, ...patch } })),
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
