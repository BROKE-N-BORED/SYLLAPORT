# Syllaport — Design Foundation + Identity Spec

- **Task:** R1 of the UI redesign task list (`ui-audit-and-redesign-task-list.md` §5)
- **Date:** 2026-11-13
- **Status:** Design spec only. No code, no build, no push. Every later task (R2–R14) cites this file.
- **Product:** Syllaport — the universal portal version of Study Shell. Anyone downloads it, creates an account, picks their own free classes from a verified $0 catalog, builds their own schedule, and gets the same dashboard, pace engine, notebook, and progress tracking. Downloadable program first: native Qt desktop app, Windows build AND Linux build, every release.
- **Repo:** https://github.com/BROKE-N-BORED/SYLLAPORT (exists, empty)

## Sources (all cited by number in this spec)

- `ui-audit-and-redesign-task-list.md` — the audit of Study Shell v1.5 UI + the R1 task definition. Section references below ("Audit §2", "R5", etc.) point there.
- `~/workspace/bnb-ui-design-library/design-rules.md` — the immutable rules (U1–U39, D1–D3), Part 1 philosophy, Part 3 techniques drawer. This repo file is the source of truth. The workspace copy (`~/workspace/design-rules.md`) is stale (U1–U33 only) and was NOT used.
- Library entries: 005 Bento grids, 023 Focus-first navigation, 001 Micro-interactions. Spring physics (002) lives in design-rules.md Part 3. Entry 021 is cited for minimum target size only.
- The library is a living repo (36 entries as of Drop 3, 2026-11-13). R1 cites only the entries named in its definition; later tasks may pull from newer drops through the repo filter.

## How to cite this spec

Later tasks cite sections by number (e.g. "per Design Spec §2, hero tile spans the full grid"). If a later task needs something this spec does not define, it defines it in its own task and cites the rule or entry it comes from. Nothing in this spec overrides a rule in design-rules.md: if this spec ever conflicts with a rule, the rule wins.

---

## 1. Identity — paper, ink, and highlighter

### 1.1 The material (U15)

Syllaport looks like a study desk, not a classroom and not generic SaaS. Its material is **paper, ink, and highlighter**: cream paper surfaces, near-black ink for structure and text, lime highlighter for the marks that matter (progress, the thing to do now, the thing just finished). This is Study Shell's identity carried over, not invented fresh (Audit §2, Strengths: "Real identity, not generic SaaS"). Pro software with a real identity (U15). Nothing here looks like a game.

### 1.2 Palette (exact values, carried from Study Shell `app.py` CSS)

| Role | Name | Hex | Used for |
|---|---|---|---|
| Background | Cream | `#f7f1e3` | Window background, page surfaces |
| Card | Card cream | `#fffdf6` | Cards, tiles, panels |
| Text / structure | Ink | `#141414` | Text, borders, header/rail, buttons |
| Accent | Lime | `#b6e61e` | Progress fills, highlights, "do this now" marks, focus glow |
| Line | Line | `#d8d0ba` | Table borders, dividers, hairlines |
| Nav dark | Rail | `#222222` | Left nav rail background (carried from Study Shell `nav`) |

**Pairing rules (contrast, spec decision grounded in U19/U34 readability):**
- Allowed: ink text on cream, ink text on card cream, cream text on ink, ink text on lime.
- Forbidden: lime text on cream, lime text on card cream, cream text on lime, lime text on white. Lime is never body text. Lime is a fill, a highlight, or a progress color, always with ink text on top of it or beside it.
- Pure white `#FFFFFF` is not used as a surface (023: avoid pure white, it glows and blooms). The lightest surface is card cream `#fffdf6`. Input fields use `#ffffff` for the field interior only (carried from Study Shell), with a 2 px ink border so the field reads as a field.

### 1.3 What stays from Study Shell

- The palette above, exact hexes (U15).
- Hard-shadow cards: 2 px ink border, 4 px hard offset shadow in ink, 0 blur (carried from Study Shell CSS). The shadow has no blur, so it costs nothing to render on weak hardware (repo filter: cheap motion and cheap paint only).
- Buttons: ink background, cream text, 8 px radius, bold; hover goes black background with lime text (carried).
- Inputs: 2 px ink border, 8 px radius, 8 px padding, full width in forms (carried).
- Progress bar: 18 px tall, 2 px ink border, 9 px radius, lime fill, centered bold label (carried).
- Big numbers: 30 px bold for the numbers that matter (pace, streak, time in) (carried from `.big`).
- Plain-words copy voice (U9): his words or plain facts only. If it sounds like an ad, it goes.
- The password rule, generalized: Syllaport never asks for or stores any course-provider password. Users sign in on the provider's own site; Syllaport only links out (Study Shell security rule, Audit §2).
- Single instance (U27), double-click install + icon + menu entry (U3, D2, D3), atomic local data with automatic backups (carried behavior, not visual identity, but part of what the product feels like: nothing is ever lost).

### 1.4 What changes for everyone (Syllaport is a product for any user, not Joshua's personal program)

- **Name and header.** The header reads **Syllaport**, subtitle **Free university workstation** (plain facts, U9). No "STUDY SHELL", no "BROKE N' BORED STUDIO" header. Version lives in Help → About, not in the header.
- **No hardcoded person.** No "Joshua Lofland", no "SpaceWok", no pre-seeded CS50x enrollment. The Account window shows the signed-in user's own profile (R3).
- **No Broke n' Bored framing.** The "Apply-It" field becomes neutral: label **Apply it**, explanation directly underneath (U20): "How will you use what you learned today?" (Audit F10).
- **No hardcoded journey.** CS50 and MIT are catalog entries, not the default. A new user starts with no classes until they pick some (R2, R3). The prep banner, term dates, and lanes all come from the user's own setup (Audit F8).
- **No provider-specific top level.** There is no "edX Account" window. The Account window is generic: the user's profile, their provider links, their certificates (R3).
- **No em-dashes in any visible UI text** (U33). Use plain words or commas. Empty values read as "None yet" or "Not set", never "—" (Audit F1).
- **No bare `&` in any visible label** (U11). Use "and". (Qt mnemonic markers are covered in §4.4; they are not visible text.)
- **No default selections anywhere** (U6). Every picker, list, and choice starts unselected (Audit F2).

### 1.5 Icon brief (D3: creative and beautiful, not a placeholder)

- The Syllaport mark: paper, ink, and highlighter. Ink mark on cream, lime as the one accent.
- Must read at 16, 32, 48, and 256 px. Test at 16 px first: if it does not read small, it does not ship.
- Ships with every release as the desktop icon, menu icon, and installer icon (D2, D3).
- The artwork itself is produced with the build, not in this spec. This brief is the constraint it must meet.

### 1.6 Copy rules (apply to every string in the app)

- Plain words or plain facts only (U9). No ad-speak, no coined brand copy.
- Tell the truth about real limits (U17). If the app cannot check something, say so in the UI ("Syllaport can't check this for you").
- Every field explains itself in plain words directly underneath it (U20). No field without its explanation.
- No em-dashes (U33). No bare `&` in visible labels (U11).
- No third-party brands in documentation (U10). Course providers are named only as the user's own courses (content, not branding).
- Destructive actions say exactly what they undo, in plain words, before the user confirms (U31; Audit §2, Strengths: the delete confirm names what else it undoes).

---

## 2. Bento grid spec (entry 005)

The dashboard — and any screen that must show many things at once — is a bento grid. Size is the hierarchy: the bigger tile is the more important content, and the layout itself tells the user where to look first (005).

### 2.1 Numbers (all from entry 005 unless marked spec decision)

| Item | Spec |
|---|---|
| Columns (desktop) | 4 columns at the default window size. 3 columns below 900 px width, 5 columns above 1400 px width (breakpoints: spec decision; range 3–5 is from 005) |
| Hero tile | Exactly one per layout. Spans all 4 columns, 2 rows tall (005: hero 4–6 columns wide, 2 rows tall) |
| Gaps | 20 px uniform on desktop (005 range: 16–24 px). 12 px on narrow layouts (005 range: 8–16 px) |
| Corner radius | Standard tiles 16 px, hero tile 20 px (005 range: 12–24 px; square corners read as a table) |
| Cells per layout | 5–10 (005). Dashboard: 6 tiles (see §2.2). More than 10 and it stops being scannable |
| Outer margin | 20 px, matching the gap (spec decision: one rhythm for gaps and margins) |
| Restack | On narrow widths, tiles restack into a single column ordered by priority, not by original position (005) |

### 2.2 Dashboard tile map (R4 builds this; R1 defines the layout)

| Tile | Size | Contents |
|---|---|---|
| Do this now (hero) | 4 cols × 2 rows | Today's lane + next unit + the one primary action button |
| Your pace | 1 col × 1 row | Measured pace, big number (30 px) |
| Journey progress | 1 col × 1 row | Progress bar + courses/units done |
| Streak | 1 col × 1 row | Day streak, big number |
| Next milestone | 1 col × 1 row | Next course boundary or certificate |
| Time in | 1 col × 1 row | Total + this week |

Six tiles: inside the 5–10 cell budget (005). The hero answers "what do I do today" before a word is read (005: spatial weight pre-answers "what matters here").

### 2.3 Watch-outs (005)

- Bento fails when every box is the same size or the hierarchy is unclear. Symmetric grids look like spreadsheets. If the sizes do not mean something, it is just a wall of boxes. Enforcement: exactly one hero per layout; no two tiles share the hero's size.
- Every tile is self-contained and has exactly one job (005). A tile that needs two jobs is two tiles (or a window, per U1).

---

## 3. Type scale and spacing

### 3.1 Type scale (sizes carried from Study Shell CSS unless marked spec decision)

| Role | Size | Weight | Used for |
|---|---|---|---|
| Big number | 30 px | Bold | Pace, streak, time-in totals (`.big`) |
| Window title | 24 px | Bold | Window titles, header (Study Shell `h1`) |
| Card title | 19 px | Bold | Tile and card titles (`h2`) |
| Section head | 16 px | Bold | Sub-sections inside a card (spec decision: between card title and body) |
| Body | 14 px | Regular | Body text, table text, nav |
| Small / helper | 13 px | Regular | Explanations under fields (U20), helper text (`.small`) |
| Caption / tag | 11 px | Bold | Tags, status chips (`.tag`) |

- **Line height:** 1.2 for headings and big numbers, 1.4 for body and helper text (spec decision: standard readable leading).
- **Font stack:** Verdana, DejaVu Sans, Segoe UI, sans-serif (carried from Study Shell `Verdana,Geneva,sans-serif`, extended with per-platform fallbacks — see §7). One family everywhere; no second display font.
- **Minimum body size is 14 px.** Nothing the user must read goes below 13 px helper text, and helper text is never the only place a fact lives.
- **Note on entry 023's type numbers:** 023's point sizes (Body 29 pt, headlines 38 pt+) are 10-foot TV UI at 1920×1080. They do NOT port to a desktop app and are not used here. The desktop scale above derives from Study Shell's proven sizes.

### 3.2 Spacing (4 px base unit, spec decision)

| Item | Value | Source |
|---|---|---|
| Base unit | 4 px | Spec decision |
| Scale | 4 / 8 / 12 / 16 / 20 / 24 / 32 px | Spec decision |
| Card / tile padding | 16 px | Carried from Study Shell |
| Tile gap | 20 px desktop, 12 px narrow | §2.1 (005) |
| Outer margin | 20 px | §2.1 (spec decision) |
| Section gap (between card groups) | 24 px | Spec decision |
| Button padding | 9 px vertical, 14 px horizontal | Carried from Study Shell |
| Input padding | 8 px | Carried from Study Shell |
| Nav rail width | 200 px, collapsible to 56 px icon-only | Spec decision (see §6.3) |

### 3.3 Minimum target size (entry 021)

- Every clickable control is at least **44 × 44 px** (021: 44 × 44 pt iOS, 48 × 48 dp Android — 44 px is the floor). Where a visible control is smaller, the clickable area grows invisibly around it (transparent padding, visible control pixel-identical).
- A 2 × 2 tile gets a single trigger, not a button matrix (021).

---

## 4. Focus ring + keyboard navigation (entry 023, entry 001)

### 4.1 Focus ring spec (023: unmistakable, not 1 px dotted)

- **The ring:** 2 px solid ink outline on the focused widget, plus an outer soft lime glow at ~10% opacity (001: "a soft glow at about 10 percent opacity, colored border plus ring").
- **Why two signals:** the ink outline reads on cream and card surfaces; the lime glow reads on ink and dark surfaces. One of the two always shows, whatever the widget sits on.
- **What it is not:** not the browser/Qt default 1 px dotted line. 023 is explicit: "A weak focus style (1 px outline, no scale) fails from across the room, and it fails a tired user at a desk too."
- **No size change on focus.** 023's tvOS scaling (focused element scales up with parallax) is a 10-foot pattern. On desktop Qt it would shift layouts, so focus is ring + glow only, no scaling (spec decision; also honors 001's rule against layout-affecting animation).
- **The ring applies to every focusable family:** buttons, inputs, checkboxes, tiles, list rows, menu items, rail entries. No focusable control ships without the ring.

### 4.2 Focus behavior (023)

- **Focus is never lost.** No focus traps, no dead ends, no diagonal-only paths.
- **On a window change, focus lands on the most likely next action** (023). Opening Courses lands focus on the current course. Opening Notebook lands focus on the open note.
- **On return, focus restores the prior position** (023). Going back to a window puts focus where it was.
- **Back retreats one level** (023). Esc closes a dialog or retreats one level, leaving things untouched (U31 clean escape).
- **Arrow keys move within grids and lists** (023, adapted from TV shelves): Left/Right move within a row and wrap at the row ends; Up/Down move between rows and keep the column. In the bento grid, arrows move between tiles by position.
- **Tab walks in visual order** (spec decision grounded in 023's "focus is never lost" + U19/U34). Tab order follows the layout top-to-bottom, left-to-right, never the order widgets happened to be created.

### 4.3 Keyboard principles

- **The whole app is usable by keyboard alone** (U19 teenager-or-grandparent bar, U34 toy rule). No mouse-only action exists.
- **Enter activates, Esc retreats.** Space toggles checkboxes. Arrows navigate grids, lists, and shelves.
- **Window switching:** Ctrl+1 through Ctrl+8 focus the eight windows in rail order (spec decision; see §6.2). Alt+letter menu mnemonics per Qt convention (§4.4).
- **Minimize typing** (023: "treat every required keystroke as a design failure"). Pickers, chips, and lists beat free-text entry wherever the choices are known. Free text stays only where the user is genuinely writing (notes, note fields).
- **No keyboard shortcut is the only way to do anything.** Every shortcut has a visible menu item, button, or rail entry that does the same thing (U19).

### 4.4 Mnemonics and U11

- Menu mnemonics use Qt's `&` marker (the standard mechanism: `&File` underlines F). This is what `&` is FOR in menus, and the `&` itself never displays.
- Visible label TEXT must never contain a bare `&` (U11). Write "and", never "&", in any label, button, tab, or menu text. The MIMIK failure was a bare `&` in a tab label rendering as a mnemonic ("Hosts & Learn" became "Hosts_Learn"); the rule exists because the string check stays green while the label renders wrong.

---

## 5. Motion budget (entries 001, 002)

Cheap motion only: transform and opacity, never layout properties, or the frame rate dies (001). The target machine is 8 GB RAM, no GPU, spinning hard drive (repo filter).

### 5.1 Timing (001, capped by Part 3)

| Motion | Duration | Easing (001) |
|---|---|---|
| Micro feedback (press, hover, ripple) | 100–150 ms | Ease-out for entering, ease-in for leaving |
| Small UI actions (panel open, toggle, tick) | 150–250 ms | Ease-out for entering, ease-in for leaving |
| Context changes (view switch, card expand) | 250–300 ms | Ease-out for entering, ease-in for leaving |
| Loops (only where a loop is genuinely needed) | Ease-in-out | Rare; default is no loops (§5.4) |

- **The 300 ms cap:** entry 001 allows context changes up to 400 ms, but the Part 3 file-level budget caps functional animation at under 300 ms ("Anything longer feels slow, not delightful"). The stricter cap wins: context changes are 250–300 ms in this spec.
- **Functional animation stays under 300 ms, always** (Part 3). Anything longer feels slow, not delightful.

### 5.2 Measured patterns (001, exact numbers)

- **Button press:** scale to 0.97 (3% smaller) over 150 ms. Smaller than 2% is invisible; bigger than 5% looks cartoonish (001).
- **Card/tile hover:** lift 4 px, over 200 ms, ease-out (001). Enough to feel tangible, not enough to look like a toy popping off the screen.
- **Focus ring:** soft glow at ~10% opacity, colored border plus ring (001; see §4.1).
- **Checkmark:** draws itself when a task finishes (001). In Syllaport: the unit tick (R5) and the checklist tick (R2).

### 5.3 Springs (002, Part 3)

- **Where springs live in Syllaport: exactly two places.** Card expand (a tile growing into its detail window) and checklist tick settle (R2). Springs are earned, not defaulted (002, from Material 3 Expressive): they belong on content and interactive surfaces that reward attention, not on chrome and utility controls.
- **Numbers:** a snappy toggle is stiffness ~500, damping ~30 — quick movement, slight overshoot, fast settle (002).
- **Rules:** springs are for motion the USER causes (taps, drags, expands). For things that happen on their own (a loading fade), plain easing is better (002). Feed the release velocity into the spring; a spring that restarts from zero when the user lets go feels disconnected from the hand (002). Transitions must be interruptible: if the user grabs something mid-flight, it retargets smoothly instead of finishing the old animation first (002).
- **In Qt:** `QPropertyAnimation` with `QEasingCurve::OutBack` gives the overshoot (the cheap version that already feels good); `OutElastic` gives the bounce. For true velocity-aware springs, a small custom animator integrates stiffness and damping per frame (Part 3 Qt note). R1 specifies OutBack as the default spring curve; a custom animator is allowed only if OutBack cannot express the motion.

### 5.4 Reduced motion + prohibitions

- **Respect reduced-motion settings** (Part 3; 015 reduced-motion preset). When reduced motion is on, all animation becomes an instant state change: no motion, no fade, no spring. The state change still happens; only the motion is removed. Nothing may depend on an animation to be understood.
- **Every animation needs a purpose.** If you cannot say why it helps, remove it (001). Never animate to cover up slowness; fix the slowness (001).
- **No idle or looping animation.** The UI rests when idle (003 calm technology: the interface recedes; a good tool disappears through use). No ambient loops, no idle timers animating anything.
- **No layout animation.** Animate transform and opacity only, never layout properties (001). A hover lift is a transform; a panel opening animates opacity/transform, never width/height.

---

## 6. Menu bar + window plan (U38, U1)

### 6.1 Menu bar (U38: real Windows-style menus)

A proper Qt menu bar on every window. Real drop-down menus, collapsible headers in panels (Part 1 philosophy: "Real Windows-style menus and drop-down menus. Collapsible headers in panels. Proper navigation, not a flat wall of controls").

| Menu | Items |
|---|---|
| File | Backup Now · Download Backup... · Restore from Backup... · Export Notes (.md) · Export Work Log (.csv) · — · Quit |
| View | Dashboard · Courses · Schedule · Notebook · Work Log · Account · Backup · Settings (each opens/focuses its window; the active window carries a checkmark) |
| Tools | Debug Report... (U12) |
| Help | How to Use Index (U22) · About Syllaport |

- Menu items use plain words (U9), no em-dashes (U33), "and" never "&" in visible text (U11). Mnemonics via Qt `&` per §4.4.
- The View menu is the window switcher: it mirrors the rail (§6.3) and the Ctrl+1..8 shortcuts (§4.3). Three ways to the same windows, all consistent.

### 6.2 Window plan (U1: one function, one window)

Every function gets its own closable window. Never cram everything into one window (U1). Syllaport has eight windows, one per function, mirroring Study Shell's eight pages — but as native windows, not browser tabs (U2):

| # | Window | One function | Contents (summary; the owning task defines the detail) |
|---|---|---|---|
| 1 | Dashboard | What do I do today | Bento grid (§2.2). The home window. Opened at launch. (R4) |
| 2 | Courses | My classes + progress | Course list, one course open, unit checks (R5) |
| 3 | Schedule | My week + my journey | Schedule builder, This Week strip, seed-vs-live timeline (R6) |
| 4 | Notebook | My notes | One notebook open, save + restore (R8) |
| 5 | Work Log | What I did + my pace | Log form, filters, entries, totals (R9) |
| 6 | Account | Who I am + my providers | Profile, provider links, certificates (R3) |
| 7 | Backup | My data, safe | Download, auto-backups, restore (carried behavior) |
| 8 | Settings | How it behaves | Seed pace, term dates, skip courses, accessibility presets (R2/R12) |

- **The Dashboard is the home window.** It opens at launch. Closing a secondary window returns focus to the Dashboard (or the last active window, if the Dashboard is closed — closing the Dashboard quits the app only if it is the last window; otherwise the next window takes focus).
- **Never remove anything — reorganize only** (U1). Every Study Shell function survives into Syllaport as a window or a menu item. If a function does not fit a window, it lives in the menu bar, never deleted.
- **First-run checklist** (R2) appears as the Dashboard hero tile state, not as a ninth window. One hero, one job (§2.3).

### 6.3 Window chrome (shared by all eight windows)

- **Menu bar** (§6.1) on every window.
- **Left nav rail:** the eight windows as rail entries (label + icon), current window highlighted. Rail is 200 px wide, collapsible to 56 px icon-only via a toggle (spec decision; U1: organize with tabs, burger buttons, and collapsible sections). Rail order matches View menu order and Ctrl+1..8 order.
- **Status bar:** a light plus small status text, always visible (U16: "Always show what it's doing"). Idle reads as quiet status ("Saved", "Ready"), never blank, never a modal.
- **Default size:** 1100 × 700 (U5: ACR 1100×700 default; fits the 1366×768 screen). Geometry is remembered between runs via QSettings (U5). First run opens centered.
- **Single instance** (U27): re-clicking the icon focuses the running app; it never starts a second copy.
- **Dialogs:** modal dialogs never stack (U18) — one in flight; others queue behind it with an honest message about what they are waiting for. Destructive confirmations default to No (U23). Every dialog has a clean escape: Esc or tap-outside leaves things untouched (U31).

### 6.4 What a window is not

- Not a browser tab. Not a page in a single scrolling view. Not a crowded single window holding every function (the core rule: NO one-window crowded builds ever).
- Not a modal for routine work. Routine work happens in windows; dialogs are for confirmations and short interruptions only (U18, U31).

---

## 7. Platform notes (Windows + Linux, portal rule)

- **Stack:** PySide6, Qt Widgets (the house stack; Part 3's Qt note cites `QPropertyAnimation` and `QEasingCurve`, the Widgets animation framework). Native Qt desktop windows (U2). No web UI for the downloadable shape.
- **One stylesheet, both platforms.** The same Qt stylesheet renders on Windows and Linux. No per-platform visual branches. Verify both (U13: verify the way the user will use it).
- **Fonts:** Verdana, DejaVu Sans, Segoe UI, sans-serif (§3.1). Verdana is native on Windows; on Linux it resolves if MS core fonts are installed, otherwise DejaVu Sans carries the same metrics class. Never bundle a font file without a reason (U7: default is no limit, but a bundled font is weight; the stack covers both platforms without one).
- **Every release ships both builds** (portal rule: "It needs a windows build and a Linux build fyi"). Each build carries the icon + double-click installer (D2, D3). The installer installs or updates ALL dependencies for the project (D3). The menu launcher must actually launch: bake the app dir in at install (U4 — the `%k` pattern fails).
- **The machine configures itself** (U35): the app measures the PC's specs silently and sets the right settings under the hood. Settings that do not change do not appear (U36): only show a setting if the user would ever change it for a real reason.
- **Long work runs in worker threads; the UI never blocks** (U30). Long operations show progress and offer cancel (U26). Heavy background work leaves the desktop usable (U25: cap parallelism to the machine).

---

## 8. Rule trace (what this spec honors, and where)

| Rule / entry | Honored in |
|---|---|
| Core rule (no one-window crowded builds) | §6.2, §6.4 |
| U1 one function, one window | §6.2, §6.3 |
| U2 native Qt desktop windows | §7 |
| U3 double-click install + launch | §7, §1.3 |
| U4 launcher bakes app dir | §7 |
| U5 fit 1366×768, geometry memory | §6.3 (1100×700, QSettings) |
| U6 select nothing by default | §1.4 |
| U7 default is no limit | §7 (no bundled font without reason) |
| U9 copy is plain facts | §1.6, §1.4 |
| U10 no third-party brands in docs | §1.6 |
| U11 "and", never bare "&" | §1.4, §1.6, §4.4, §6.1 |
| U12 debug log layer | §6.1 (Tools → Debug Report) |
| U15 pro software, real identity | §1.1, §1.2 |
| U16 always show what it's doing | §6.3 (status bar) |
| U17 copy tells the truth about limits | §1.6 |
| U18 modal dialogs never stack | §6.3 |
| U19 teenager-or-grandparent bar | §4.3, §3.1 |
| U20 field explains itself underneath | §1.4, §1.6 |
| U21 ask for the minimum up front | §6.2 (R2 owns first run; this spec reserves the hero tile) |
| U22 How to Use index in the menu | §6.1 (Help menu) |
| U23 destructive confirmations default to No | §6.3 |
| U25/U26/U30 background work + progress + threads | §7 |
| U27 single instance | §6.3 |
| U28 actions preserve UI state | §4.2 (focus restore), §6.2 |
| U31 confirm destructive, clean escape | §6.3, §4.2 |
| U33 no em-dashes in visible UI text | §1.4, §1.6, §6.1 |
| U34 toy rule (child could use it) | §4.3, §3.1, §1.1 |
| U35 backend configures itself | §7 |
| U36 settings that don't change don't appear | §7 |
| U37 real measurements, science software | §2.2 (pace/progress tiles carry the numbers; R7 builds the graphs) |
| U38 real Windows-style menus | §6.1 |
| U39 guided choices | §1.4 (R3 builds the picker; this spec reserves the pattern) |
| D1 GitHub-only ship | §7 (process; binds the build) |
| D2/D3 icon + installer + dependencies | §1.5, §7 |
| Portal rule: Windows + Linux builds | §7 |
| 001 Micro-interactions | §5.1, §5.2, §4.1 |
| 002 Spring physics (Part 3) | §5.3 |
| 005 Bento grids | §2 |
| 021 Glanceable surfaces (target size only) | §3.3 |
| 023 Focus-first navigation | §4 |
| Part 1 philosophy (complex underneath, simple on top; toy bar; real menus) | §1.1, §6.1, §4.3 |
| Part 3 (300 ms budget; reduced motion; Qt OutBack) | §5.1, §5.3, §5.4 |

Rules not traced here are owned by later tasks (U13 verify-like-the-user is R14; U20/U21/U22/U37/U39 get their full build in R2–R11) or do not apply to a design spec (U8 surgical edits, U13 process, U14 phone-first web — R13, hosted phase, deferred).

---

## 9. Out of scope (this spec does not cover)

- **R2–R14.** First run (R2), accounts + class picker (R3), dashboard build (R4), courses (R5), schedule builder (R6), graphs (R7), notebook (R8), work log (R9), feedback pass (R10), navigation build (R11), compliance sweep (R12), hosted shape (R13, deferred), verification (R14). Each cites this spec and adds its own detail.
- **Code.** No widgets, no stylesheets, no files. This is the spec the build follows.
- **Icon artwork.** The brief is §1.5; the artwork is produced with the build.
- **Packaging mechanics.** Installer internals, Windows/Linux build tooling, and Release process belong to the build, not to R1. The requirements they must meet are §7 + D2/D3.
- **The hosted shape.** R13 is deferred to a later hosted phase. Nothing in this spec assumes a server. Where a choice differs by shape (accounts in R3), this spec notes it and moves on.

---

## Acceptance (from the R1 task definition)

- Spec written in the portal folder: this file, `~/workspace/universal-portal/design-spec.md`.
- Every later task cites it: §2–§6 give R2–R12 concrete numbers to build against, and §8 traces every rule and entry to its section.
- Toy-test read-through: a child could follow the spec's own test — one hero tile that says what to do, one function per window, plain words everywhere. If a later task finds a section a child could not follow, the section is wrong, not the test.
