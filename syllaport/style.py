"""The one stylesheet (Design Spec section 1, 3, 4).

Palette (exact, carried from Study Shell): cream #f7f1e3, card cream
#fffdf6, ink #141414, lime #b6e61e, line #d8d0ba, rail #222222.

Focus ring (Spec section 4.1, entry 023): 2 px solid, never 1 px
dotted. Qt stylesheets have no box-shadow, so the lime glow is
expressed as a lime ring on dark widgets and a light lime tint behind
focused fields; the two signals still hold (one always shows, whatever
the widget sits on). Every focusable family gets a transparent 2 px
baseline border so focusing never shifts layout.

Presets (entry 015): larger text scales the whole type scale; high
contrast swaps the palette to black on white. Both rebuild the same
stylesheet, so the app never carries two visual branches.
"""

from __future__ import annotations

CREAM = "#f7f1e3"
CARD = "#fffdf6"
INK = "#141414"
LIME = "#b6e61e"
LINE = "#d8d0ba"
RAIL = "#222222"
FIELD = "#ffffff"
FOCUS_TINT = "#f4f9d2"   # very light lime behind a focused field
MUTED = "#6b6552"        # secondary text on cream (readable, not greyed out)

# High contrast palette (preset): black on white, lime kept as the mark.
HC_BG = "#ffffff"
HC_CARD = "#ffffff"
HC_INK = "#000000"
HC_LINE = "#000000"
HC_RAIL = "#000000"
HC_FOCUS_TINT = "#ffffcc"


def _sizes(larger_text):
    """Type scale (Spec section 3.1). Larger text scales it by 5/4."""
    scale = 1.25 if larger_text else 1.0
    raw = {"bignum": 30, "title": 24, "cardtitle": 19, "section": 16,
           "body": 14, "small": 13, "tag": 11}
    return {k: int(round(v * scale)) for k, v in raw.items()}


def build_stylesheet(presets=None):
    """The full app stylesheet for the given preset state."""
    presets = presets or {}
    larger = bool(presets.get("larger_text"))
    high_contrast = bool(presets.get("high_contrast"))
    s = _sizes(larger)
    if high_contrast:
        bg, card, ink, line, rail = HC_BG, HC_CARD, HC_INK, HC_LINE, HC_RAIL
        focus_tint, muted = HC_FOCUS_TINT, HC_INK
        field = HC_BG
    else:
        bg, card, ink, line, rail = CREAM, CARD, INK, LINE, RAIL
        focus_tint, muted = FOCUS_TINT, MUTED
        field = FIELD
    return """
QMainWindow, QDialog { background: %(bg)s; }
QWidget { color: %(ink)s; font-family: Verdana, "DejaVu Sans", "Segoe UI", sans-serif; font-size: %(body)spx; }
QLabel { background: transparent; }
QLabel[role="title"] { font-size: %(title)spx; font-weight: bold; }
QLabel[role="cardtitle"] { font-size: %(cardtitle)spx; font-weight: bold; }
QLabel[role="section"] { font-size: %(section)spx; font-weight: bold; }
QLabel[role="small"] { font-size: %(small)spx; }
QLabel[role="muted"] { font-size: %(small)spx; color: %(muted)s; }
QLabel[role="bignum"] { font-size: %(bignum)spx; font-weight: bold; }
QLabel[role="tag"] { font-size: %(tag)spx; font-weight: bold; }

QPushButton { background: %(ink)s; color: %(bg)s; border: 2px solid transparent; border-radius: 8px; padding: 9px 14px; font-weight: bold; min-height: 26px; }
QPushButton:hover { background: #000000; color: %(lime)s; }
QPushButton:pressed { background: #000000; }
QPushButton:focus { border: 2px solid %(lime)s; }
QPushButton:disabled { background: %(line)s; color: %(muted)s; }
QPushButton[role="quiet"] { background: transparent; color: %(ink)s; border: 2px solid %(ink)s; }
QPushButton[role="quiet"]:hover { background: %(ink)s; color: %(lime)s; }
QPushButton[role="quiet"]:focus { border: 2px solid %(ink)s; background: %(focus_tint)s; }
QPushButton[role="link"] { background: transparent; color: %(ink)s; border: 2px solid transparent; text-decoration: underline; font-weight: normal; padding: 4px 6px; min-height: 20px; }
QPushButton[role="link"]:hover { background: transparent; color: %(ink)s; }
QPushButton[role="link"]:focus { border: 2px solid %(ink)s; }

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit { background: %(field)s; color: %(ink)s; border: 2px solid %(ink)s; border-radius: 8px; padding: 8px; }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus { background: %(focus_tint)s; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background: %(field)s; color: %(ink)s; border: 2px solid %(ink)s; selection-background-color: %(lime)s; selection-color: %(ink)s; }

QCheckBox, QRadioButton { border: 2px solid transparent; spacing: 8px; }
QCheckBox:focus, QRadioButton:focus { border: 2px solid %(ink)s; border-radius: 4px; }
QCheckBox::indicator { width: 20px; height: 20px; border: 2px solid %(ink)s; border-radius: 4px; background: %(field)s; }
QCheckBox::indicator:checked { background: %(lime)s; }
QRadioButton::indicator { width: 20px; height: 20px; border: 2px solid %(ink)s; border-radius: 11px; background: %(field)s; }
QRadioButton::indicator:checked { background: %(lime)s; }

QListWidget { background: %(card)s; border: 2px solid %(ink)s; border-radius: 8px; }
QListWidget::item { padding: 8px; border: 2px solid transparent; }
QListWidget::item:selected { background: %(lime)s; color: %(ink)s; }
QListWidget::item:hover { background: %(focus_tint)s; }

QGroupBox { border: 2px solid %(ink)s; border-radius: 8px; margin-top: 12px; padding-top: 12px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }

QMenuBar { background: %(ink)s; color: %(bg)s; }
QMenuBar::item { padding: 6px 12px; background: transparent; }
QMenuBar::item:selected { background: #000000; color: %(lime)s; }
QMenu { background: %(card)s; color: %(ink)s; border: 2px solid %(ink)s; }
QMenu::item { padding: 6px 24px 6px 12px; }
QMenu::item:selected { background: %(lime)s; color: %(ink)s; }
QMenu::separator { height: 1px; background: %(line)s; margin: 4px 0px; }

QStatusBar { background: %(bg)s; color: %(ink)s; border-top: 1px solid %(line)s; }
QStatusBar::item { border: none; }

QScrollArea { border: none; background: %(bg)s; }
QScrollBar:vertical { background: %(bg)s; width: 14px; }
QScrollBar::handle:vertical { background: %(line)s; border-radius: 6px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: %(ink)s; }
QScrollBar:horizontal { background: %(bg)s; height: 14px; }
QScrollBar::handle:horizontal { background: %(line)s; border-radius: 6px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: %(ink)s; }

QToolTip { background: %(ink)s; color: %(bg)s; border: 1px solid %(ink)s; padding: 4px 8px; }

QFrame#rail { background: %(rail)s; }
QPushButton[role="rail"] { background: transparent; color: %(bg)s; border: 2px solid transparent; border-left: 4px solid transparent; border-radius: 0px; text-align: left; font-weight: bold; padding: 10px 12px; min-height: 24px; }
QPushButton[role="rail"]:hover { background: #333333; color: %(lime)s; }
QPushButton[role="rail"]:focus { border: 2px solid %(lime)s; }
QPushButton[role="rail"][current="true"] { background: #333333; color: %(lime)s; border-left: 4px solid %(lime)s; }
""" % {"bg": bg, "card": card, "ink": ink, "lime": LIME, "line": line,
       "rail": rail, "field": field, "focus_tint": focus_tint,
       "muted": muted, "body": s["body"], "title": s["title"],
       "cardtitle": s["cardtitle"], "section": s["section"],
       "small": s["small"], "bignum": s["bignum"], "tag": s["tag"]}


def apply_presets(app, presets):
    """Apply the preset state to the running app (stylesheet rebuild)."""
    app.setStyleSheet(build_stylesheet(presets))
