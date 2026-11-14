# Syllaport

Free university workstation. Pick free classes from a verified catalog,
build your own schedule, and track your pace, notes, and progress.
Everything lives on this computer.

Syllaport is the universal portal version of Study Shell: anyone
downloads it, creates a local profile, picks their own free classes,
and gets the same dashboard, pace engine, notebook, and progress
tracking. Downloadable program first: native Qt desktop app, Windows
build and Linux build, every release.

## Status

R2 (scaffold plus first run), version 0.1.0. What works today:

- Eight windows, one per job: Dashboard, Courses, Schedule, Notebook,
  Work Log, Account, Backup, Settings. Real menu bar, left nav rail,
  status bar, single instance, geometry memory.
- First run: a five step setup checklist on the Dashboard. Every step
  is real and saves: profile, first class, weekly pace, start date,
  tour. Dismissible, gone when done, reopenable from Settings.
- Courses: empty state teaches by playing with three working choices:
  browse the catalog, add a class you already know, start with a
  guided pick. The catalog holds 19 verified free sources and 44
  named courses, all free to learn from, no card, no phone check.
- Presets: larger text, reduced motion, high contrast. In the View
  menu and in Settings, applied at once.
- Help menu: How to Use index with real content for every window,
  plus About.
- File menu: Backup Now, Download Backup, Restore from Backup (with
  a confirm step), Export Notes (.md), Export Work Log (.csv).
- Tools menu: Debug Report with real facts and a copy button.

Coming next (R3 to R9): full accounts and class picker (R3), bento
dashboard rebuild (R4), per-course units and progress (R5), schedule
builder (R6), live pace graphs (R7), notebooks (R8), work log (R9).
Windows for those jobs already open and say plainly what arrives.

## Run it

Needs Python 3.10 or newer and PySide6:

    pip install -r requirements.txt
    python main.py

Your data lives in the platform app data folder
(Windows: %APPDATA%/Syllaport, Linux: ~/.local/share/Syllaport).
Use `python main.py --data-dir DIR` to point it elsewhere.

## Tests

    bash run_tests.sh

Unit tests plus offscreen GUI tests (windows open, checklist
completes, presets apply). The GUI tests need a display or Xvfb;
run_tests.sh handles that.

## Rules this build follows

- Real function only: every control does something real. No
  placeholder buttons, no fake data, no dead ends.
- Syllaport never asks for or stores any course password. You sign
  in on the provider's own site; Syllaport only links out.
- No em-dashes in visible text. No default selections. Every field
  explains itself in plain words underneath it.
- Secrets are never in code. They live in gitignored files only;
  see .gitignore.
- Design spec: ../universal-portal/design-spec.md (R1). Rules:
  the BNB UI Design Source File Library repo, design-rules.md
  (U1-U39, D1-D3). Catalog source:
  ../research_notes/free-colleges-master-list/report.md.

## Layout

    main.py               Entry point, single instance
    syllaport.svg         Icon source (paper, ink, highlighter)
    icons/                Rendered icon PNGs (16, 32, 48, 256 px)
    syllaport/
      data.py             Data model, storage, pace engine (stdlib only)
      store.py            Data file plus change signals (Qt side)
      catalog.py          Verified $0 catalog (19 sources, 44 courses)
      checklist.py        First-run checklist model
      dialogs.py          Profile, pace, start date, pickers
      tour.py             Guided tour
      windows.py          Window framework, menu bar, rail, manager
      dashboard.py        Dashboard window (bento plus checklist hero)
      courses.py          Courses window (teach-by-playing empty state)
      other_windows.py    Schedule, Notebook, Work Log, Account,
                          Backup, Settings
      howto.py            How to Use index
      style.py            The one stylesheet plus presets
      anim.py             Small motion helpers (opacity only, under 300 ms)
      debuglog.py         Debug log layer (U12, minimal R2 version)
    tests/                unittest suite
    verify/               GUI drive script (screenshots + user-flow proof)
