# Module 3 Dashboard — React Migration Brief
**For: Antigravity**
**Date: 2026-05-29**

Migrate the existing `index.html` dashboard into a proper React + Vite + TypeScript application.
The design is done. The logic is done. This is a componentisation job, not a redesign.

Base path: `D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\dashboard\`

---

## What This Is

The current `index.html` (3185 lines) is a fully working single-file dashboard.
Everything in it — CSS tokens, brand system, HTML structure, JS logic — is correct and stays.
The job is to lift it into a proper React component tree so the backend can be wired later
without touching any component internals.

**No redesign. No new features (except the two fixes listed at the end).
Exact same visual output. Same behaviour. Just componentised.**

---

## Step 1 — Scaffold the project

Inside `dashboard\`, initialise:

```bash
npm create vite@latest . -- --template react-ts
npm install zustand
npm install -D @types/node
```

Delete the Vite boilerplate: `src/App.css`, `src/assets/`, `src/index.css` content (keep the file, it will hold tokens).

Keep: `index.html` (Vite's entry point — replace its body with `<div id="root"></div>`), `vite.config.ts`, `tsconfig.json`, `package.json`.

The old `index.html` stays in the repo as `index.html.legacy` for reference during migration. Delete it once migration is confirmed working.

---

## Step 2 — Extract CSS tokens

Create `src/styles/tokens.css`.

Copy the entire `:root { ... }` block from `index.html` verbatim — every CSS variable, every colour token, every glow, every radius. Do not change a single value.

Copy all global base styles (`*, *::before, *::after`, `body`, `body::before`, utility classes, scrollbar styles) into `src/styles/globals.css`.

Import both in `src/main.tsx`:
```tsx
import './styles/tokens.css'
import './styles/globals.css'
```

The Google Fonts and Fontshare `<link>` tags move into the new `index.html` `<head>`.

---

## Step 3 — Zustand store

Create `src/store/sessionStore.ts`.

This replaces all `window.state`, `localStorage`, and global variable usage in the current JS.
The store shape mirrors the existing state object exactly:

```ts
interface SessionState {
  // Session config
  isSessionActive: boolean
  venueName: string
  sessionMode: 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP'
  loggingInterval: 15 | 30
  operatorName: string
  sessionNumber: number
  sessionStartTime: number | null

  // Table config
  tableConfig: { two: number; four: number; six: number }
  tables: Table[]  // generated from tableConfig on session open

  // Door & Flow
  currentEntries: number
  currentExits: number
  intervalHistory: IntervalRecord[]
  sessionTotalEntries: number
  sessionTotalExits: number
  intervalStartTime: number | null

  // Environment
  environment: {
    sound: string
    temp: string
    energy: string
    queue: string
  }

  // KPI state
  kpiData: Record<string, KPIFamily>  // keyed by familyId

  // Show engineering suggestions (read from API later)
  suggestions: Suggestion[]
}
```

Define all actions (setVenueName, adjustTableType, openSession, submitInterval, updateTable,
clearTable, saveEnvironment, updateKPI, etc.) as Zustand actions inside the store.

All `localStorage` reads/writes stay — Zustand `persist` middleware handles this.
When the FastAPI backend is ready, actions get extended to also call `fetch()` — the component
API does not change.

---

## Step 4 — Types

Create `src/types/index.ts`. Define all interfaces:

```ts
export interface Table {
  code: string          // e.g. "T7"
  capacity: 2 | 4 | 6
  status: 'empty' | 'occupied' | 'warning'
  segment?: string
  headcount?: number
  seatedAt?: number     // timestamp
  note?: string
}

export interface IntervalRecord {
  startTime: string
  endTime: string
  entries: number
  exits: number
  net: number
}

export interface KPIFamily {
  familyId: string
  familyName: string
  zone: string
  layer: 'A' | 'B' | 'C'
  overallStatus: 'ok' | 'watch' | 'alert' | 'stale'
  isLogged: boolean
  lastAssessedAt: number | null
  signals: KPISignal[]
}

export interface KPISignal {
  signalId: string
  signalName: string
  sourceType: 'manual' | 'counter' | 'derived' | 'sensor'
  status: 'normal' | 'watch' | 'alert'
  value?: string | number
}

export interface Suggestion {
  id: string
  title: string
  body: string
  priority: 1 | 2 | 3 | 4 | 5
  status: 'pending' | 'shown' | 'acted' | 'dismissed' | 'expired'
  generatedAt: number
}

export type SessionMode = 'BASELINE' | 'ENGINEERED' | 'FOLLOWUP'
export type RAGStatus = 'ok' | 'watch' | 'alert' | 'stale'
```

---

## Step 5 — Component tree

Build exactly this structure. CSS for each component lives in a `.module.css` file alongside it,
extracted from the relevant CSS in `index.html`. No styled-components, no Tailwind.

```
src/
├── main.tsx
├── App.tsx
│
├── components/
│   │
│   ├── shared/
│   │   ├── Header/
│   │   │   ├── Header.tsx          ← venue name, session timer, mode badge, submit interval btn
│   │   │   └── Header.module.css
│   │   ├── Toast/
│   │   │   ├── ToastRack.tsx       ← toast container + showToast() exported util
│   │   │   └── Toast.module.css
│   │   ├── Badge/
│   │   │   ├── Badge.tsx           ← BASELINE/ENGINEERED/FOLLOWUP + RAG badges
│   │   │   └── Badge.module.css
│   │   └── SegmentedControl/
│   │       ├── SegmentedControl.tsx  ← reusable segmented button row (used in setup + env + monitor)
│   │       └── SegmentedControl.module.css
│   │
│   ├── setup/
│   │   ├── SessionSetup/
│   │   │   ├── SessionSetup.tsx    ← screen-setup wrapper
│   │   │   └── SessionSetup.module.css
│   │   ├── VenueInput/
│   │   │   ├── VenueInput.tsx      ← venue name input + recall hint
│   │   │   └── VenueInput.module.css
│   │   └── TableStepper/
│   │       ├── TableStepper.tsx    ← 3-column stepper grid + flash animation
│   │       └── TableStepper.module.css
│   │
│   ├── logger/
│   │   ├── FloorLogger/
│   │   │   ├── FloorLogger.tsx     ← screen-logger wrapper + tab nav
│   │   │   └── FloorLogger.module.css
│   │   ├── DoorFlow/
│   │   │   ├── DoorFlow.tsx        ← entries/exits counters + progress bar + history
│   │   │   ├── DoorFlow.module.css
│   │   │   └── QuickEnvCheck/
│   │   │       ├── QuickEnvCheck.tsx   ← inline prompt after submit interval
│   │   │       └── QuickEnvCheck.module.css
│   │   ├── TablesTab/
│   │   │   ├── TablesTab.tsx       ← table grid wrapper
│   │   │   ├── TablesTab.module.css
│   │   │   ├── TableTile/
│   │   │   │   ├── TableTile.tsx   ← empty / occupied / warning tile
│   │   │   │   └── TableTile.module.css
│   │   │   └── TableModal/
│   │   │       ├── TableModal.tsx  ← overlay modal + bottom-sheet-mode on mobile
│   │   │       └── TableModal.module.css
│   │   └── EnvironmentTab/
│   │       ├── EnvironmentTab.tsx  ← env snapshot form
│   │       └── EnvironmentTab.module.css
│   │
│   └── monitor/
│       ├── KPIMonitor/
│       │   ├── KPIMonitor.tsx      ← screen-monitor wrapper
│       │   └── KPIMonitor.module.css
│       ├── ZoneTabBar/
│       │   ├── ZoneTabBar.tsx      ← zone tabs + status dot per tab
│       │   └── ZoneTabBar.module.css
│       ├── KPICard/
│       │   ├── KPICard.tsx         ← logged / unlogged states + expand/collapse
│       │   └── KPICard.module.css
│       └── SignalRow/
│           ├── SignalRow.tsx       ← individual signal with source badge (manual/counter/derived/sensor)
│           └── SignalRow.module.css
│
├── hooks/
│   ├── useSession.ts       ← session open/close, timer
│   ├── useTableState.ts    ← table tile state, dwell timer
│   ├── useKPIState.ts      ← KPI assessment, auto-feed updates
│   └── useInterval.ts      ← interval countdown, progress bar
│
├── store/
│   └── sessionStore.ts
│
├── types/
│   └── index.ts
│
└── styles/
    ├── tokens.css
    └── globals.css
```

---

## Step 6 — App.tsx routing

No router library needed. Screen switching is state-driven, same as the current JS:

```tsx
function App() {
  const { isSessionActive, currentScreen } = useSessionStore()

  return (
    <>
      {isSessionActive && <Header />}
      {currentScreen === 'setup'   && <SessionSetup />}
      {currentScreen === 'logger'  && <FloorLogger />}
      {currentScreen === 'monitor' && <KPIMonitor />}
      <ToastRack />
    </>
  )
}
```

---

## Step 7 — Two fixes to implement during migration (not in previous pass)

### Fix A — QuickEnvCheck: dropdowns → segmented buttons
The current `index.html` quick-env-check (line 1511) uses `<select>` dropdowns for
sound / temp / energy / queue. Replace with `<SegmentedControl>` matching the Environment tab style.
Same options, same values — just no dropdowns.

### Fix B — ZoneTabBar: status dots
Each zone tab in the KPI Monitor needs a coloured pip to the right of (or below) the zone label:
- Green dot = all signals normal in that zone
- Amber dot = at least one signal on Watch
- Red dot = at least one on Alert
- Grey dot = zone not yet logged this session

Compute the dot colour from the `kpiData` store slice filtered by zone.

---

## What NOT to change

- Brand tokens — copy verbatim from index.html, do not adjust any value
- Logic behaviour — every interaction works identically to the current index.html
- Visual output — pixel-for-pixel the same (tokens + component CSS extracted from index.html)
- No new external libraries beyond what is listed in Step 1 (Vite, React, TypeScript, Zustand)
- No UI library (no MUI, no shadcn, no Radix) — the design system already exists in the CSS

---

## Deliverable

A working React + Vite + TypeScript app in `dashboard\` that:
- `npm run dev` serves the full dashboard locally
- `npm run build` produces a deployable `dist\` folder
- All three screens work identically to the current `index.html`
- `index.html.legacy` kept for reference until confirmed working, then deleted

Confirm when done with:
- Component list (what was built)
- Any logic that needed adjustment during migration (flag, don't silently change)
- Any items skipped with reason
