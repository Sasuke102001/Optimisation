# Module 3 Dashboard — Full Build Brief
**For: Antigravity**
**Date: 2026-05-28**

Work through every task in this brief in sequence. All work is in a single file:
`D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\dashboard\index.html`

Design direction reference: `dashboard_redesign_brief.md` (same folder)
Detailed task list reference: `antigravity_todo.md` (same folder)

---

## Ground Rules

- **CSS and HTML structure only** — do not modify any JS logic functions
- **Do not add new external dependencies** — use only what is already loaded (Inter, Space Grotesk, Clash Display fonts). Remove Three.js (see C.1).
- **Use existing CSS variables only** — all brand tokens (colours, fonts, RAG system) are defined at the top of the file. Do not introduce new ones.
- **Do not split into multiple files** — single `index.html` output only
- The one JS addition allowed: the "Quick environment check" inline prompt after interval submit (Section 2.3) — implement this

---

## Priority Order

Work in this sequence:

1. **C.1 — Remove Three.js** (do this first — it unblocks everything else visually)
2. **Screen 1 — Session Setup** (sections 1.1 → 1.5)
3. **Screen 2 — Floor Logger** (sections 2.1 → 2.3)
4. **Screen 3 — KPI Monitor** (sections 3.1 → 3.6)
5. **Cross-cutting** (C.2 → C.5)

---

## C.1 — Remove Three.js canvas background

Remove the `#three-canvas` element and its entire Three.js `<script>` block from the HTML.
The existing `body` radial gradient CSS background is sufficient — keep it.
This reduces page weight and removes the visual distraction.

---

## Screen 1 — Session Setup

### 1.1 Setup card visual polish
- Increase internal padding — the card needs more breathing room
- The `PN` logo mark at the top: style as a gold square with Clash Display font, matching the header mark
- Create clear visual separation between the title/subtitle block and the fields below

### 1.2 Table config steppers
- Larger, more tactile `+` and `−` buttons
- Count number between buttons: minimum 28–32px, Space Grotesk bold, prominent
- Column labels ("2-person", "4-person", "6-person"): small, uppercase, muted
- "Total: X tables" line updates live

### 1.3 Venue recall state
- When a saved table config loads: all three stepper columns briefly flash a green tint (~0.6s) to indicate they populated
- The existing green hint text below venue input is correct — keep it

### 1.4 Open Session button state
- Visually disabled (reduced opacity, no glow) when: venue name empty OR total tables = 0
- Fully active (gold glow) only when both conditions are met
- CSS/visual state only — JS validation already blocks the action

### 1.5 Field order
Ensure fields appear in this exact order:
1. Venue Name
2. Table Layout (3 steppers)
3. Session Mode
4. Logging Interval
5. Operator Name
6. Open Session button

---

## Screen 2 — Floor Logger

### 2.1 Door & Flow tab

**Counter cards (Entries and Exits):**
- `+` button: minimum 56×56px, high contrast, prominent — tapped rapidly during service
- `−` button: smaller, clearly secondary style
- Count number: 48–56px, Space Grotesk bold, centred
- The card itself is a dedicated tapping target — generous padding, clear boundary
- Mobile: entire right half of counter card is an increment tap zone

**Interval countdown:**
- Add a thin progress bar directly below the interval info bar — depletes as time passes
- Under 2 minutes remaining: bar and timer turn amber
- At 0: bar turns red and pulses

**Submit Interval button:**
- Already full-width gold — correct, keep it
- After submit: button briefly shows "✓ Logged 9:47pm" for 1.5 seconds then reverts

**Interval history:**
- Keep the collapsible history list
- Each row: time range | entries (green) | exits (muted) | net flow

### 2.2 Tables tab

**Table grid:**
- Desktop (≥1024px): 6 columns
- Tablet (768–1023px): 4 columns
- Mobile (<768px): 3 columns
- Each tile: minimum 100px height

**Empty tile:**
- Background: `var(--bg-card)`
- Border: `var(--border)` subtle
- Shows: table code (e.g. T7, large, Clash Display), capacity label ("Cap: 4", small, muted), faint `+` or circle icon

**Occupied tile:**
- Background: `rgba(34, 197, 94, 0.05)` (subtle green tint)
- Border: `rgba(34, 197, 94, 0.28)` (green)
- Shows: table code (green), people count ("4 ppl"), segment label ("College"), dwell timer ("0h 42m")
- Dwell timer updates every 5 seconds — already in JS, keep it

**Long-dwell tile (90 min+):**
- Border: amber, animated pulse (already in CSS as `.table-tile.warning`)
- Dwell timer text: amber and bold

**Table detail modal:**
- Desktop: centred overlay modal
- Tablet/mobile: bottom sheet that slides up from the bottom
- Modal header: Table code + capacity
- Headcount: segmented button row — 1 / 2 / 3 / 4 / 5 / 6+ — large enough to tap
- Segment: chip grid — Couple / Social Group / Family / College / Corporate / Solo / Mixed
  - Pill-shaped chips, one selectable at a time
  - Selected: gold text, gold border, subtle gold background tint
- Note field: single text input, optional, labelled "Behavioural note (optional)"
- Two buttons: "Clear Table" (ghost/secondary) and "Save" (gold, larger)
- After Save: tile updates immediately, toast "✓ T7 updated"
- After Clear Table: tile resets to empty, toast "✓ T7 cleared — 1h 12m dwell recorded"

### 2.3 Environment tab

Visual tasks only — do not change the structure:
- Each env-row-card: more vertical padding — currently cramped
- Segmented controls: equal width buttons, clear selected state (gold text + gold bottom border or tint)
- "Save Environment Snapshot →" button: sticky to bottom of container on mobile

**Quick environment check prompt (one JS addition allowed):**
After the operator hits "Submit Interval →" on Door & Flow, trigger a brief inline prompt:
> "Quick environment check?" with a single collapsed row showing the 4 env selectors (sound / temp / energy / queue) inline — not a full modal. Operator taps to update any that changed, or dismisses. This is a small JS addition — implement it.

After save: toast "✓ Environment snapshot logged — 10:15pm"

---

## Screen 3 — KPI Monitor

### 3.1 Zone tab bar
- Already a horizontal tab row — correct structure, keep it
- Each zone tab: add a status dot (coloured pip) reflecting worst-case KPI status in that zone
  - Green = all normal
  - Amber = at least one on Watch
  - Red = at least one on Alert
  - Grey = nothing logged yet
- Active tab: gold underline, gold text — already correct

### 3.2 KPI cards — two visual states

**State A — Logged (assessed this session):**
- Solid coloured dot per signal row (green / amber / red)
- Bottom timestamp: "Updated 9:47pm" or "Updated 12m ago"
- Top colour bar reflects overall card status

**State B — Unlogged (not yet assessed):**
- Signal dots: grey, soft pulse animation
- Bottom timestamp: "Not logged this session"
- Card border: faint dashed treatment instead of solid
- Subtle label/icon indicating attention needed

### 3.3 Manual vs auto-fed signals

Inside expanded card view:
- **Auto-fed signals**: small source badge on right side of signal row — `counter` / `derived` / `sensor` — update automatically
- **Manual signals**: small "Manual" badge in muted grey — show "Tap to assess" prompt when card is unlogged

### 3.4 Card update interaction

- Rename "Expand ↓" button to "Update" with a pencil/edit icon
- When expanded, manual signals appear as compact assessment rows:
  - Signal name left
  - Three small buttons right: `N` (Normal) | `W` (Watch) | `A` (Alert) — currently selected state highlighted
- Auto-fed signals in expanded view: read-only rows showing current value ("Entries: 183", "Tables: 12/22")
- One "Save" button at bottom of expanded section
- After save: card collapses, status badge updates, timestamp updates, toast "✓ Queue — Service updated"

### 3.5 Replace "Live Updated" label
- Remove "● Live Updated" text from card footers entirely
- Replace with: actual timestamp ("Updated 9:47pm") or "Not logged" if no assessment
- If last update was more than 15 minutes ago: timestamp in amber with a clock icon

### 3.6 Bottom summary strip
- Already present — make it sticky to bottom (always visible)
- Values update live as data is logged
- Three stats need slightly more visual separation (dividers or gap)

---

## Cross-Cutting Tasks

### C.2 Session mode badge
Header badge (BASELINE / ENGINEERED / FOLLOWUP) must be immediately readable on Screen 2 and Screen 3:
- BASELINE: grey/neutral badge
- ENGINEERED: gold badge
- FOLLOWUP: muted violet badge

### C.3 Toast confirmations
Every data entry action fires a toast. Ensure these all fire correctly:
- Submit Interval → "✓ Interval logged — 9:47pm"
- Save table update → "✓ T7 updated"
- Clear table → "✓ T7 cleared — 1h 12m dwell"
- Save environment snapshot → "✓ Environment logged — 10:15pm"
- Log complaint → "✓ Complaint logged"
- KPI card update → "✓ [Zone] — [Family] updated"

### C.4 Responsive layout

**Desktop (≥1024px):**
- All screens: single centred column, max-width constraint as currently set
- Table grid: 6 columns
- KPI grid: 3 columns

**Tablet (768–1023px):**
- Table grid: 4 columns
- KPI grid: 2 columns
- Table detail modal: bottom sheet

**Mobile (<768px):**
- Logger tabs: full-width at top, horizontally scrollable if needed
- Table grid: 3 columns
- KPI grid: 1 column
- Table detail modal: full-screen bottom sheet
- Counter `+` buttons: minimum 64px tap target
- Environment selectors: full-width stacked if they don't fit in one row

### C.5 No active session state
When setup screen is showing, the inactive banner should be:
- Clean, centred, with the PN mark
- "No active session" message
- Not an error state — just an idle/neutral state

---

## When Done

Confirm completion with a short list of what was done vs any items skipped (with reason).
The file to deliver is `index.html` in the same location — no new files.
