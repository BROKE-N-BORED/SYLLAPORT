"""Syllaport data model, storage, and pace engine (stdlib only, no Qt).

Derived from Study Shell v1.5's model (read-only reference at
~/workspace/study-shell/app.py): one JSON file, atomic writes, five
rotating auto-backups, seed-vs-measured pace. Differences from Study
Shell: no hardcoded person, no hardcoded courses, no hardcoded dates.
Courses come from the user's own picks (see catalog.py); the pace engine
works against whatever courses the user has.

Nothing in this module touches the network or any provider password.
Syllaport never asks for or stores any course-provider password.
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import shutil
import tempfile
from datetime import date, datetime, timedelta

DATA_VERSION = 1
BACKUP_KEEP = 5
SEED_PACE = 1.0


def default_data():
    """A brand new user's data: nothing pre-seeded, nothing assumed."""
    return {
        "version": DATA_VERSION,
        "profile": {"name": "", "start_date": ""},
        "courses": [],       # my classes: {id, title, source_id, source_name,
                             #  url, added, certificate, blurb, units, final}
        "completions": [],   # work log entries; unit completions live here too
        "notes": {},         # course_id -> text ; "_general" -> general notebook
        "note_history": {},  # scope -> previous version of that note (one deep)
        "pace_history": [],  # weekly snapshots: {week, pace, units}
        "settings": {"seed_pace": SEED_PACE, "term_start": "", "skipped": []},
        "checklist": {"profile": False, "first_class": False, "pace": False,
                      "start_date": False, "tour": False},
        "checklist_dismissed": False,
        "presets": {"larger_text": False, "reduced_motion": False,
                    "high_contrast": False},
        "sessions": [],      # study sessions: {id, date, lane, minutes, apply_it}
        "certificates": {},  # course id -> ISO date the certificate was earned
        "enrolled": {},      # course id -> ISO date enrolled (provider side)
    }


def normalize_data(obj):
    """Fill any missing keys of a data dict from the defaults.

    Used by load_data and by restore: an older or partial file keeps
    working instead of crashing startup.
    """
    base = default_data()
    if not isinstance(obj, dict):
        return base
    for key in base:
        if key in obj:
            base[key] = obj[key]
    # Nested dicts merge key by key so an old file keeps working.
    for key in ("profile", "settings", "checklist", "presets"):
        merged = dict(default_data()[key])
        if isinstance(obj.get(key), dict):
            merged.update(obj[key])
        base[key] = merged
    return base


def load_data(path):
    """Load data from path, filling any missing keys from the defaults.

    A corrupt or unreadable file yields fresh defaults rather than a
    crash; the corrupt file is left alone so it can be recovered by hand.
    """
    if not path or not os.path.exists(path):
        return default_data()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, ValueError):
        return default_data()
    return normalize_data(data)


def rotate_backups(path):
    """Keep the last BACKUP_KEEP copies of path as path.bak1..bakN."""
    try:
        if not os.path.exists(path):
            return
        for n in range(BACKUP_KEEP, 1, -1):
            src, dst = "%s.bak%d" % (path, n - 1), "%s.bak%d" % (path, n)
            if os.path.exists(src):
                os.replace(src, dst)
        shutil.copyfile(path, "%s.bak1" % path)
    except OSError:
        pass  # backups must never break a save


def list_backups(path):
    """[(filename, size, mtime)] of existing auto-backups, newest first."""
    out = []
    for n in range(1, BACKUP_KEEP + 1):
        bak = "%s.bak%d" % (path, n)
        if os.path.exists(bak):
            try:
                st = os.stat(bak)
                out.append((os.path.basename(bak), st.st_size, st.st_mtime))
            except OSError:
                pass
    return out


def save_data(data, path):
    """Atomic write: temp file in the same directory, then rename."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    rotate_backups(path)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".data-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def backup_now(data, path):
    """Write a timestamped copy of the current data next to the data file.

    Returns the backup file path, or None if the write failed.
    """
    directory = os.path.dirname(os.path.abspath(path))
    backup_dir = os.path.join(directory, "backups")
    try:
        os.makedirs(backup_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = os.path.join(backup_dir, "syllaport-%s.json" % stamp)
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return dest
    except OSError:
        return None


def validate_backup(obj):
    """(ok, reason): True when a parsed JSON object looks like Syllaport data."""
    if not isinstance(obj, dict):
        return False, "The file is not a Syllaport data file."
    if obj.get("version") not in (1,):
        return False, "The file is not a Syllaport data file."
    if not isinstance(obj.get("courses"), list):
        return False, "The file is missing the class list."
    if not isinstance(obj.get("completions"), list):
        return False, "The file is missing the work log."
    if not isinstance(obj.get("notes"), dict):
        return False, "The file is missing the notebooks."
    return True, ""


# ---------------------------------------------------------------------------
# Courses (the user's own picks)
# ---------------------------------------------------------------------------

def course_by_id(data, course_id):
    for course in data.get("courses", []):
        if course.get("id") == course_id:
            return course
    return None


def add_course(data, title, source_id, source_name, url="", certificate="",
               blurb="", added=None):
    """Append a class to the user's list. Returns the new course dict."""
    added = added or date.today().isoformat()
    course_id = "course-%d" % (len(data.get("courses", [])) + 1)
    while course_by_id(data, course_id) is not None:
        course_id = "course-%d" % (int(course_id.split("-")[1]) + 1)
    course = {
        "id": course_id,
        "title": title,
        "source_id": source_id,
        "source_name": source_name,
        "url": url,
        "certificate": certificate,
        "blurb": blurb,
        "added": added,
        "units": None,   # unit count is set when the course is studied (R5)
        "final": False,
    }
    data.setdefault("courses", []).append(course)
    return course


def remove_course(data, course_id):
    """Remove a class from the list. Its log entries stay as work history."""
    data["courses"] = [c for c in data.get("courses", [])
                       if c.get("id") != course_id]


# ---------------------------------------------------------------------------
# Pace engine (ported from Study Shell; generic over the user's courses)
# ---------------------------------------------------------------------------

def unit_key(course_id, unit_index):
    """unit_index: 1..N for content units, 'final' for the final project."""
    return "%s:%s" % (course_id, unit_index)


def valid_unit_key(data, course_id, key):
    """True when a unit_key names a real unit of a course the user has.

    Courses without a known unit count have no countable units yet, so
    their keys never count (R5 sets unit counts when study starts).
    """
    course = course_by_id(data, course_id)
    if course is None or not key:
        return False
    _cid, _, idx = key.partition(":")
    if idx == "final":
        return bool(course.get("final"))
    if idx.isdigit():
        units = course.get("units")
        return bool(units) and 1 <= int(idx) <= units
    return False


def active_unit_entries(data):
    """Log entries that count toward progress: linked to a unit and active.

    Entries without a unit_key are time-only work. Entries with
    active == False were unchecked and are kept for their minutes/note.
    """
    return [e for e in data.get("completions", [])
            if e.get("unit_key") and e.get("active", True)
            and valid_unit_key(data, e.get("course_id"), e.get("unit_key"))]


def completed_unit_keys(data):
    keys = set()
    for e in active_unit_entries(data):
        keys.add(e["unit_key"])
    return keys


def count_completed_units(data):
    """Units completed = distinct checked (active, unit-linked) units only."""
    return len(completed_unit_keys(data))


def get_settings(data):
    """Settings with defaults filled in (old data files lack the key)."""
    s = dict(data.get("settings") or {})
    s.setdefault("seed_pace", SEED_PACE)
    s.setdefault("term_start", "")
    s.setdefault("skipped", [])
    return s


def seed_pace(data):
    try:
        pace = float(get_settings(data)["seed_pace"])
        return pace if pace > 0 else SEED_PACE
    except (TypeError, ValueError):
        return SEED_PACE


def term_start(data):
    """The user's study start date, or None when not set yet."""
    raw = get_settings(data).get("term_start", "")
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except (TypeError, ValueError):
        return None


def compute_pace(data, today=None):
    """
    Returns dict(seed, measured, effective, total_units, first_date,
    elapsed_weeks).
    - Seed pace = the Settings value (default 1.0 units/week).
    - Measured pace = total units completed / weeks elapsed since first
      log entry. Weeks elapsed is floored at 1 week so a fast first
      week doesn't explode.
    - Effective pace = measured once >= 2 units are logged, else the seed.
    """
    today = today or date.today()
    seed = seed_pace(data)
    entries = active_unit_entries(data)
    total = count_completed_units(data)
    if not entries or total == 0:
        return {"seed": seed, "measured": None, "effective": seed,
                "total_units": 0, "first_date": None, "elapsed_weeks": 0.0}
    dates = []
    for e in entries:
        try:
            dates.append(date.fromisoformat(e["date"]))
        except (KeyError, ValueError):
            pass
    if not dates:
        return {"seed": seed, "measured": None, "effective": seed,
                "total_units": total, "first_date": None, "elapsed_weeks": 0.0}
    first = min(dates)
    elapsed_weeks = max((today - first).days / 7.0, 1.0)
    measured = total / elapsed_weeks
    effective = measured if total >= 2 else seed
    return {"seed": seed, "measured": measured, "effective": effective,
            "total_units": total, "first_date": first,
            "elapsed_weeks": elapsed_weeks}


def projected_finish(remaining_units, pace, today=None):
    """today + ceil(remaining / pace) weeks. None when nothing remains."""
    today = today or date.today()
    if remaining_units <= 0:
        return today
    weeks = math.ceil(remaining_units / pace)
    return today + timedelta(weeks=weeks)


def recent_pace(data, today=None, weeks=4):
    """(units in the last N weeks, units/week): recent form, not lifetime."""
    today = today or date.today()
    cutoff = (today - timedelta(days=7 * weeks)).isoformat()
    units = sum(1 for e in active_unit_entries(data)
                if e.get("date", "") >= cutoff)
    return units, units / float(weeks)


def snapshot_pace(data, today=None):
    """Record this ISO week's pace once; returns True when a snapshot is new."""
    today = today or date.today()
    iso = today.isocalendar()
    week = "%d-W%02d" % (iso[0], iso[1])
    hist = data.setdefault("pace_history", [])
    if any(h.get("week") == week for h in hist):
        return False
    pace = compute_pace(data, today)
    hist.append({"week": week, "pace": round(pace["effective"], 2),
                 "units": pace["total_units"]})
    return True


# ---------------------------------------------------------------------------
# Time, streak, exports
# ---------------------------------------------------------------------------

def fmt_minutes(m):
    """120 -> '2h', 95 -> '1h 35m', 45 -> '45 min'."""
    m = int(m or 0)
    if m < 60:
        return "%d min" % m
    h, rest = divmod(m, 60)
    return "%dh" % h if not rest else "%dh %dm" % (h, rest)


def minutes_total(data, course_id=None, since=None):
    """Minutes across work-log entries + sessions, optionally filtered."""
    total = 0
    for e in data.get("completions", []):
        if course_id and e.get("course_id") != course_id:
            continue
        if since and e.get("date", "") < since.isoformat():
            continue
        total += e.get("minutes") or 0
    if not course_id:
        for s in data.get("sessions", []):
            if since and s.get("date", "") < since.isoformat():
                continue
            total += s.get("minutes") or 0
    return total


def minutes_this_week(data, today=None):
    today = today or date.today()
    monday = today - timedelta(days=today.weekday())
    return minutes_total(data, since=monday)


def active_days(data):
    """Dates with any work logged (entries + sessions)."""
    days = set()
    for e in data.get("completions", []):
        if e.get("date"):
            days.add(e["date"])
    for s in data.get("sessions", []):
        if s.get("date"):
            days.add(s["date"])
    return days


def streak(data, today=None):
    """Consecutive logged days ending today (or yesterday if not yet today)."""
    today = today or date.today()
    days = active_days(data)
    if not days:
        return 0
    cur = today if today.isoformat() in days else today - timedelta(days=1)
    n = 0
    while cur.isoformat() in days:
        n += 1
        cur -= timedelta(days=1)
    return n


def notes_markdown(data):
    """All notebooks as one Markdown document (empty notebooks say so)."""
    lines = ["# Syllaport notes", ""]
    notes = data.get("notes", {}) or {}
    if not any(text.strip() for text in notes.values()):
        lines.append("No notes yet.")
        lines.append("")
        return "\n".join(lines)
    for scope in sorted(notes):
        title = "General" if scope == "_general" else scope
        course = course_by_id(data, scope)
        if course is not None:
            title = course.get("title", scope)
        lines.append("## %s" % title)
        lines.append("")
        lines.append(notes[scope] or "No notes yet.")
        lines.append("")
    return "\n".join(lines)


def log_csv(data):
    """The work log (entries + sessions) as CSV text."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["date", "course", "unit", "minutes", "note"])
    rows = []
    for e in data.get("completions", []):
        course = course_by_id(data, e.get("course_id"))
        rows.append((e.get("date", ""), course.get("title", "") if course else "",
                     e.get("unit_label", ""), e.get("minutes") or "",
                     e.get("note", "")))
    for s in data.get("sessions", []):
        rows.append((s.get("date", ""), "",
                     "%s session" % s.get("lane", ""),
                     s.get("minutes") or "", s.get("apply_it", "")))
    rows.sort(key=lambda r: r[0])
    w.writerows(rows)
    return buf.getvalue()
