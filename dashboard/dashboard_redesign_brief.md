# Dashboard Redesign Brief — Polynovea Module 3

## What This Document Is

Design direction for Antigravity to redesign the Module 3 operator dashboard.
The current `index.html` was a strong first pass at the KPI monitoring layer
but missed the core data capture experience entirely.

This brief defines what to build and how to approach it.

---

## Two Separate Screens, Not One

The current design tries to be both a data entry tool and a KPI monitor at the same time.
That makes it complex and hard to follow.

Split into two distinct screens:

### Screen 1 — Floor Logger
What the floor operator uses during a live session.
Primary job: log data quickly and accurately.
User: operator (possibly non-technical, possibly the founder during early sessions).
Device: laptop-first, must also work on tablet and mobile.

### Screen 2 — KPI Monitor
What the supervisor/manager uses to read venue state.
Primary job: see what's happening, flag what needs attention.
User: manager or analyst.
Device: laptop/desktop.

This brief focuses on Screen 1 (Floor Logger) and the simplification of Screen 2 (KPI Monitor).
Both share the same visual language and brand tokens from the current design.

---

## Screen 1 — Floor Logger

### Top-Level Layout

```
[ Header: Venue name | Session mode badge | Live timer | Submit Interval button ]

[ Tab Nav: Door & Flow  |  Tables  |  Environment ]

[ Tab Content Area ]
```

Header is always visible.
Tab navigation switches the main content area.
No sidebars, no right panels, no zone rail on this screen.
Clean, single-column or two-column max.

---

### Header

Left side:
- Venue name (prominent, e.g., "Circus")
- Session mode badge — one of: `BASELINE` (grey) / `ENGINEERED` (gold) / `FOLLOWUP` (muted)
- Session number: "Session 3"

Centre:
- Live session timer (counting up from session start)

Right side:
- Operator name chip (small, avatar + name)
- **Submit Interval** button (gold, prominent) — this is the most important action on the screen

The Submit Interval button submits the current Door & Flow interval.
It should feel important. When pressed it confirms with "✓ Logged 9:47pm".

---

### Tab 1 — Door & Flow

Purpose: log how many people entered and exited in the current interval.

Layout:
```
[ Interval selector: 15 min / 30 min ]   [ Interval progress: 12 min remaining ]

[ ENTRIES block ]          [ EXITS block ]
  Big number display          Big number display
  [ − ]  [ 47 ]  [ + ]       [ − ]  [ 12 ]  [ + ]
  Tap + each time someone    Tap + each time someone
  enters                     exits

[ Submit Interval → ] (large gold button)

──────────────────────────────────
Session Totals (small, below)
Entries: 183  |  Exits: 47  |  Net: +136
──────────────────────────────────

[ Interval History (last 5 entries, collapsible) ]
  9:30–9:45   +32 in  /  −8 out
  9:15–9:30   +41 in  /  −5 out
  ...
```

Input type: large tap targets for + and −.
Numbers display prominently in the centre.
No text input required at all.

When Submit is tapped:
- Timestamp is recorded automatically
- Counters reset to 0
- History row appears above
- Toast confirmation: "✓ Interval logged — 9:47pm"

---

### Tab 2 — Tables

Purpose: track which tables are occupied, who is sitting there, and how long they've been there.

This is the most important tab. The operator will return to this every 15–30 minutes.

#### Table Grid

Displays all configured tables for the venue as a visual tile grid.
Tables are pre-configured per venue (30 tables, some 2-top, some 4-top, some 6-top).
The grid should feel like a simple floor map, not a data table.

**Empty table tile:**
```
┌───────────┐
│    T7     │
│  ○ Empty  │
│  Cap: 4   │
└───────────┘
```
Dark background. Subtle border. Table code + capacity.

**Occupied table tile:**
```
┌───────────┐
│    T7     │
│  ● 4 ppl  │
│  college  │
│  0h 42m   │
└───────────┘
```
Slightly lighter background (subtle green tint). Segment label. Dwell timer counting up.

**Long-dwell table tile (90min+):**
Same as occupied but with amber border. Signals the operator to notice this table.

**Tile tap behaviour:**
Tapping any tile opens a bottom sheet (mobile/tablet) or a compact modal (laptop).

#### Table Detail Modal / Bottom Sheet

```
Table T7  ·  Cap: 4
──────────────────────────────

How many people?
[ 1 ]  [ 2 ]  [ 3 ]  [ 4 ]  [ 5 ]  [ 6+ ]
(segmented button row, one tap)

Customer type?
[ Couple ]  [ Social Group ]  [ Family ]
[ College ]  [ Corporate ]   [ Solo ]
[ Mixed ]
(chip selection, one tap)

Note (optional):
[ _________________________________ ]

──────────────────────────────
[ Clear Table ]          [ Save ]
```

Rules for this modal:
- Headcount = segmented button row (not a number input, not a stepper — buttons are fastest)
- Segment = chips (one tap, visually selected)
- Note = only optional text field on this screen
- Save closes the modal, updates the tile, starts the dwell timer if newly seated
- Clear Table marks the table as empty, logs the dwell duration, tile resets

When saved:
- Tile updates immediately (optimistic update)
- Toast: "✓ T7 updated"

No dropdowns anywhere on this screen. Dropdowns are slow and require precise tapping.

---

### Tab 3 — Environment

Purpose: log environmental and operational observations during the session.
These are not counted (like entries) and not selected from a table (like segments).
They are periodic qualitative snapshots.

Layout: a set of simple card rows, each with a label and a selector.

```
Sound Level
[ Low ]  [ Medium ]  [ Loud ]  [ Very Loud ]

Temperature Comfort
[ Cold ]  [ Comfortable ]  [ Warm ]  [ Hot ]

Crowd Energy
[ Flat ]  [ Relaxed ]  [ Active ]  [ High Energy ]

Queue at Bar
[ None ]  [ Short (<5) ]  [ Medium (5–15) ]  [ Long (15+) ]

Complaints / Incidents
[ + Log Complaint ]
(opens a small modal: type selector + note)

[ Save Environment Snapshot → ]
```

Input type: segmented button rows for everything measurable on a scale.
Tap one, it highlights. Then hit Save.
No free text except for complaint notes.

Operator does this once per interval or whenever something changes.

---

## Screen 2 — KPI Monitor (simplified)

The current design is correct in concept but too complex in execution.

Simplification direction:

### Remove
- The zone rail sidebar — replace with a horizontal tab row at the top
- The right panel (Actions / Activity / Flags) — condense Activity into a bottom drawer or a simple "Recent" section
- The Three.js canvas background — too heavy, slows the page, distracts

### Keep
- Dark brand system (bg-primary, gold, RAG colours)
- RAG status per KPI family (ok / watch / alert / stale)
- Zone-by-zone KPI cards
- The layer label system (Layer A · Raw Signal, Layer B · Derived Metric, Layer C · KPI)

### Restructure
- Top: horizontal zone tabs (Entrance / Queue / Bar / Dancefloor / etc.)
- Main area: KPI family cards for the selected zone, in a 2 or 3 column grid
- Each card: clean RAG badge, last updated timestamp, expand to see supporting signals
- Bottom strip: session summary (entries today, tables occupied now, complaints logged)

### Input simplification on the KPI monitor
The KPI monitor should not require complex inputs.
By the time someone is on the KPI monitor screen, data has already been logged
via the Floor Logger. The monitor reads that data and shows derived state.

Manual override is still possible (operator can set a KPI family to watch or alert)
but this should be a secondary action, not the primary one.

---

## Input Type Rules (applies to both screens)

| Data type | Input control |
|-----------|--------------|
| Counting something (entries, exits, complaints) | Large counter with + / − tap targets |
| Choosing one of 4–6 options (segment, sound level, crowd energy) | Segmented button row or chip grid |
| Number from a known set (headcount 1–6+) | Segmented button row |
| True/false or yes/no | Toggle or two-button row |
| Free text note | Text area — only when no structured option exists |
| Never | Dropdowns, number spinners, sliders |

---

## Confirmation Feedback Rules

Every logged action must confirm clearly.

- Submit interval → toast: "✓ Interval logged — 9:47pm"
- Save table update → toast: "✓ T7 updated"
- Clear table → toast: "✓ T7 cleared — 1h 12m dwell recorded"
- Save environment snapshot → toast: "✓ Environment logged — 10:15pm"
- Log complaint → toast: "✓ Complaint logged"

Toast style: appears bottom-centre, 2.5s duration, ok/warn/alert colour variant.

The operator must always know:
- What they just submitted
- When it was submitted
- Whether it was successful

If the session is not active (no session opened), all log buttons are disabled
and a banner shows: "No active session — open a session to start logging."

---

## Responsive Behaviour

### Laptop (≥1024px)
- Floor Logger: Two-column layout on Door & Flow tab (entries left, exits right)
- Table grid: 5–6 columns of tiles
- Modal: centred overlay

### Tablet (768–1023px)
- Floor Logger: Single column, tabs at top
- Table grid: 3–4 columns of tiles
- Modal: bottom sheet (slides up from bottom)

### Mobile (<768px)
- Floor Logger: Single column
- Bottom navigation bar instead of top tabs (easier thumb reach)
- Table grid: 2 columns of tiles
- Modal: full-screen bottom sheet

---

## What Antigravity Should NOT Change

- Brand tokens (colours, typography, gold/RAG system) — keep exactly as is
- The fact that the KPI monitor and Floor Logger are separate screens
- The Layer A / B / C distinction in the KPI monitor's supporting data
- The zone-based navigation concept in the KPI monitor

---

## Deliverable Sequence

1. Floor Logger screen (this is the priority — this is what gets used on Day 1)
   - Door & Flow tab
   - Tables tab
   - Environment tab

2. KPI Monitor screen (simplified rebuild of current index.html)
   - Zone tab navigation
   - KPI family cards with RAG status
   - Supporting data drill-down

3. Session setup screen (separate, simple)
   - Select venue
   - Select session mode (Baseline / Engineered / Followup)
   - Set interval (15 min / 30 min)
   - Open session → goes to Floor Logger
