"""Small motion helpers (Design Spec section 5, entries 001 and 002).

Cheap motion only: opacity, never layout properties. Every animation
stays under 300 ms. When reduced motion is on, the state change still
happens and the motion is skipped entirely (Spec section 5.4).
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect

TICK_MS = 150  # micro feedback (001: 100 to 150 ms)


def reduced_motion_on(store):
    """True when the user's reduced-motion preset is on."""
    return bool(store.data.get("presets", {}).get("reduced_motion"))


def fade_in(widget, store, duration_ms=TICK_MS):
    """Fade a widget in over duration_ms, or show it at once when reduced
    motion is on. Returns the animation (or None when skipped)."""
    if reduced_motion_on(store):
        effect = widget.graphicsEffect()
        if effect is not None:
            effect.setOpacity(1.0)
        widget.show()
        return None
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(0.0)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    widget.show()
    return anim
