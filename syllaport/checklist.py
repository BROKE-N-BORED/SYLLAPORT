"""First-run setup checklist (entry 020, Design Spec section 6.2).

Five steps, each one real: completing a step does something and saves
it. Checklist state lives in the data file, so completed steps stay
completed across restarts. The checklist is dismissible and gone when
done (020); a dismissed checklist can be reopened from Settings.
"""

from __future__ import annotations

STEP_ORDER = ["profile", "first_class", "pace", "start_date", "tour"]

STEPS = {
    "profile": {
        "title": "Create your profile",
        "detail": "Your name and the day you started. This profile lives "
                  "on this computer only.",
        "button": "Create profile",
    },
    "first_class": {
        "title": "Pick your first class",
        "detail": "Choose from the verified free catalog. Every class "
                  "here is free to learn from.",
        "button": "Pick a class",
    },
    "pace": {
        "title": "Set your weekly pace",
        "detail": "How many units a week you aim to finish. You can "
                  "change this any time in Settings.",
        "button": "Set pace",
    },
    "start_date": {
        "title": "Choose your start date",
        "detail": "The first day of your study plan. Your schedule is "
                  "built from this date.",
        "button": "Choose date",
    },
    "tour": {
        "title": "Take the tour",
        "detail": "A short walk through the eight windows, so you know "
                  "where everything lives.",
        "button": "Start tour",
    },
}


def checklist_state(data):
    """The checklist dict with every step present (old files fill in)."""
    state = dict(data.get("checklist") or {})
    for step in STEP_ORDER:
        state.setdefault(step, False)
    return state


def done_count(data):
    state = checklist_state(data)
    return sum(1 for step in STEP_ORDER if state.get(step))


def is_complete(data):
    return done_count(data) == len(STEP_ORDER)


def is_dismissed(data):
    return bool(data.get("checklist_dismissed"))


def mark_done(data, step):
    """Mark one step done. Returns True when the step was newly completed."""
    if step not in STEP_ORDER:
        return False
    state = data.setdefault("checklist", {})
    if state.get(step):
        return False
    state[step] = True
    return True


def show_checklist(data):
    """True when the Dashboard hero should show the checklist."""
    return not is_complete(data) and not is_dismissed(data)
