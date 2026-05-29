# Antigravity — Module 3 Dashboard To-Do

## Context

The dashboard is a single HTML file (`index.html`) with three screens:
- Screen 1: Session Setup
- Screen 2: Floor Logger (3 tabs — Door & Flow, Tables, Environment)
- Screen 3: KPI Monitor

The JS logic for the setup screen is already written and working.
Do not touch the JS logic — only handle the visual and UX tasks listed below.
All brand tokens (colours, fonts, RAG system) are already defined in CSS variables at the top of the file. Use them, do not introduce new ones.

---

## What Is Already Done (Do Not Redo)

- Venue name text input with localStorage memory per venue
- Table config steppers (2-person / 4-person / 6-person) generating the table array dynamically
- Session validation (blocks start if no venue name or 0 tables)
- All hardcoded venue names (Circus, Eclipse, South Hall) removed
- All hardcoded `/30` table counts replaced with dynamic `state.tables.length`
- Fake pre-populated session data cleared
- Operator name default cleared

---

## Screen 1 — Session Setup

### 1.1 Setup card visual polish
The setup card currently looks like a login screen. It needs to feel like a proper configuration tool.
- Give the card more breathing room — increase internal padding
- The `PN` logo mark at the top should match the header mark style (gold square, Clash Display font)
- The title "Initialize Live Session" and subtitle should be clearly separated from the fields below

### 1.2 Table config steppers
This is the most important visual element on this screen.
- The three columns (2-person / 4-person / 6-person) need larger, more tactile `+` and `−` buttons
- The count number between the buttons should be large and prominent (at least 28–32px, Space Grotesk bold)
- The column labels ("2-person", "4-person", "6-person") should be small, uppercase, muted
- The "Total: X tables" line below should update live as buttons are tapped

### 1.3 Venue recall state
When a venue name is recognised and a saved table config is loaded:
- The three stepper columns should have a brief highlight/flash (green tint for ~0.6s) to draw attention to the fact they populated
- The hint text below the venue input already turns green — that is correct, keep it

### 1.4 Open Session button state
- The "Open Session →" button should appear visually disabled (reduced opacity, no glow) when:
  - Venue name input is empty
  - OR total tables is 0
- It should become fully active (gold glow) only when both conditions are met
- This is a CSS/visual state only — the JS validation already blocks the action

### 1.5 Field order
Ensure the fields appear in this order:
1. Venue Name (text input)
2. Table Layout (3 steppers)
3. Session Mode (Baseline / Engineered / Follow-up)
4. Logging Interval (15 Min / 30 Min)
5. Operator Name (text input)
6. Open Session button

---

## Screen 2 — Floor Logger

### 2.1 Door & Flow tab

**Counter cards (Entries and Exits):**
- The `+` button must be significantly larger than the `−` button
  - `+` button: minimum 56×56px, high contrast, prominent — this is tapped rapidly during service
  - `−` button: smaller, secondary style — this is only for corrections
- The count number in the centre should be very large (48–56px, Space Grotesk bold)
- The card itself should feel like a dedicated tapping target — generous padding, clear visual boundary
- On mobile: consider making the entire right half of the counter card tappable as an increment zone

**Interval countdown:**
- The "15:00 remaining" text timer is not visually prominent enough
- Add a thin progress bar directly below the interval info bar that depletes as time passes
- When under 2 minutes remaining, the bar and timer turn amber
- When at 0, the bar turns red and pulses

**Submit Interval button:**
- Already full-width and gold — correct
- After submit: button briefly shows "✓ Logged 9:47pm" text for 1.5 seconds before reverting

**Interval history:**
- The collapsible history list is correct — keep as is
- Each history row should show: time range | entries (green) | exits (muted) | net flow

---

### 2.2 Tables tab

**Table grid:**
- Responsive column count:
  - Desktop (≥1024px): 6 columns
  - Tablet (768–1023px): 4 columns
  - Mobile (<768px): 3 columns
- Each tile should have a minimum height of 100px

**Empty tile:**
- Dark background (`var(--bg-card)`)
- Subtle border (`var(--border)`)
- Shows: table code (e.g. T7, large, Clash Display), capacity label (e.g. "Cap: 4", small, muted)
- A faint `+` or circle icon to invite a tap

**Occupied tile:**
- Background: subtle green tint (`rgba(34, 197, 94, 0.05)`)
- Border: green (`rgba(34, 197, 94, 0.28)`)
- Shows: table code (green), people count (e.g. "4 ppl"), segment label (e.g. "College"), dwell timer (e.g. "0h 42m")
- Dwell timer updates every 5 seconds — already handled in JS

**Long-dwell tile (90 minutes+):**
- Border: amber, animated pulse (already in CSS as `.table-tile.warning`)
- Dwell timer text turns amber and bold
- This is a visual signal to the operator: "this table has been here a long time"

**Table detail modal:**
- On desktop: centred overlay modal — keep current structure
- On tablet/mobile: bottom sheet that slides up from the bottom of the screen
- Modal header: Table code + capacity (already correct)
- Headcount row: segmented button row with options 1 / 2 / 3 / 4 / 5 / 6+ — each button should be large enough to tap easily
- Segment row: chip grid (Couple / Social Group / Family / College / Corporate / Solo / Mixed)
  - Chips should be pill-shaped, clearly selectable, one at a time
  - Selected chip: gold text, gold border, subtle gold background
- Note field: single text input, optional, labelled "Behavioural note (optional)"
- Two buttons at bottom: "Clear Table" (ghost/secondary) and "Save" (gold, larger)
- After Save: tile updates immediately, toast appears "✓ T7 updated"
- After Clear Table: tile resets to empty, toast appears "✓ T7 cleared — 1h 12m dwell recorded"

---

### 2.3 Environment tab

This tab stays as-is structurally. Visual tasks only:

- Each env-row-card needs more vertical padding — currently feels cramped
- The segmented control buttons for each row (Low / Medium / Loud / Very Loud etc.) should be equal width and clearly show which is selected
- Selected state: gold text, gold bottom border or gold background tint — match the segmented control style used elsewhere
- The "Save Environment Snapshot →" button must always be visible without scrolling — stick it to the bottom of the container on mobile if needed
- After save: toast "✓ Environment snapshot logged — 10:15pm"

**Connection to interval submit (important):**
When the operator hits "Submit Interval →" on the Door & Flow tab, after the interval data is saved, show a brief inline prompt:
> "Quick environment check?" with a collapsed row of the 4 env selectors (sound / temp / energy / queue) inline — not a full modal. One row, tap to update any that changed, or skip. This connects the two actions.

---

## Screen 3 — KPI Monitor

This is the most significant visual rework needed.

### 3.1 Zone tab bar
- Already present as a horizontal tab row — correct structure
- Each zone tab must show a status dot (coloured pip) reflecting the worst-case status of any KPI family in that zone
  - Green dot = all normal
  - Amber dot = at least one on Watch
  - Red dot = at least one on Alert
  - Grey dot = nothing logged yet
- Active zone tab: gold underline, gold text — already correct

### 3.2 KPI card — two visual states

Every card must visually communicate one of two states:

**State A — Logged (has been assessed this session):**
- Solid coloured dot per signal row (green / amber / red)
- Timestamp at bottom: "Updated 9:47pm" or "Updated 12m ago"
- Top colour bar reflects the card's overall status

**State B — Unlogged (not yet assessed this session):**
- Signal dots are grey and pulsing (soft pulse animation)
- Bottom timestamp shows: "Not logged this session"
- The card has a faint dashed border treatment instead of solid
- A subtle label or icon signals that this card needs attention

The operator needs to see at a glance which cards still need their input.

### 3.3 Manual vs. auto-fed signals

Inside the expanded card view, signal rows must show their source:

**Auto-fed signals** (data comes from Floor Logger):
- Show a small source badge on the right side of the signal row: `counter` / `derived` / `sensor`
- These update automatically — no tap needed

**Manual signals** (operator must assess by walking the zone):
- Show a small "Manual" badge in muted grey
- When the card is unlogged, these rows show a faint "Tap to assess" prompt
- These are the signals that require the operator's eyes: Engagement level, Dancefloor activation, Fatigue signals, Service speed etc.

### 3.4 Card update interaction

**Current:** "Expand ↓" button opens a large expansion with many controls.

**Required change:** Make the tap-to-update flow faster and clearer.
- The "Expand ↓" button should be relabelled "Update" with a pencil or edit icon
- When expanded, the manual signals appear as a compact assessment row each:
  - Signal name on the left
  - Three small buttons on the right: `N` (Normal) | `W` (Watch) | `A` (Alert)
  - Currently selected state is highlighted
- Auto-fed signals in the expanded view show their current value (e.g. "Entries: 183", "Tables: 12/22") as read-only rows
- One "Save" button at the bottom of the expanded section confirms the update
- After save: card collapses, status badge updates, timestamp updates, toast "✓ Queue — Service updated"

### 3.5 Replace "Live Updated" label
- Remove the "● Live Updated" text from card footers entirely
- Replace with: actual timestamp ("Updated 9:47pm") or "Not logged" if no assessment yet
- If last update was more than 15 minutes ago, show timestamp in amber with a clock icon

### 3.6 Bottom summary strip
Already present with Total Entries / Occupied Tables / Complaints Logged.
- This strip should always be visible (sticky to bottom)
- Values should update live as data is logged
- The three stats need slightly more visual separation (dividers or gap)

---

## Cross-Cutting Tasks

### C.1 Remove Three.js canvas background
The `#three-canvas` element and its Three.js script block should be removed entirely.
It adds significant page weight and visual distraction. The existing `body` radial gradient background is sufficient.

### C.2 Session mode badge — always readable
The header badge (BASELINE / ENGINEERED / FOLLOWUP) must be immediately readable on both Screen 2 and Screen 3.
- BASELINE: grey/neutral badge
- ENGINEERED: gold badge
- FOLLOWUP: muted violet badge

### C.3 Toast confirmations — every logged action
Every data entry action must produce a toast. The toast rack already exists in the HTML.
Ensure these fire correctly for:
- Submit Interval → "✓ Interval logged — 9:47pm"
- Save table update → "✓ T7 updated"
- Clear table → "✓ T7 cleared — 1h 12m dwell"
- Save environment snapshot → "✓ Environment logged — 10:15pm"
- Log complaint → "✓ Complaint logged"
- KPI card update → "✓ [Zone] — [Family] updated"

### C.4 Responsive layout

**Desktop (≥1024px):**
- All three screens: single centred column with max-width constraint (already set to 1024px for logger, 1200px for monitor)
- Table grid: 6 columns
- KPI grid: 3 columns (already `auto-fill minmax(330px, 1fr)`)

**Tablet (768–1023px):**
- Table grid: 4 columns
- KPI grid: 2 columns
- Table detail modal: bottom sheet (slides up)

**Mobile (<768px):**
- Logger tabs: stay at top, full width, horizontally scrollable if needed
- Table grid: 3 columns
- KPI grid: 1 column
- Table detail modal: full-screen bottom sheet
- Counter `+` buttons: minimum 64px tap target
- Environment selectors: full-width stacked if they don't fit in one row

### C.5 No active session state
When no session is open (setup screen is showing), the header is hidden and an "inactive banner" is shown. This is already handled in JS. Visually:
- The banner should be clean, centred, with the PN mark and a "No active session" message
- Should not look like an error state — just an idle state

---

## File Reference

All work is in a single file:
`D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\dashboard\index.html`

Do not split into multiple files. Do not add new external dependencies beyond what is already loaded (Inter, Space Grotesk, Clash Display fonts, Three.js can be removed).

Do not modify any JS logic functions. Visual and CSS changes only, except for:
- Removing the Three.js canvas element and its script block (Section C.1)
- Adding the "Quick environment check" inline prompt triggered after interval submit (Section 2.3) — this requires a small JS addition but should be discussed before implementing
