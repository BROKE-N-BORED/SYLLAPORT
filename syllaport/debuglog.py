"""Debug log layer (U12, minimal R2 version).

Rotating timestamped log file next to the data file, plus a scrubbed
report for Tools > Debug Report. The full BNB S61+T21 layer (ring
buffer, traceback capture) is R12 work; this version logs honestly and
reports real facts today.

Nothing secret is ever logged: Syllaport holds no passwords, tokens, or
keys, and the report lists only version, platform, paths, sizes, and
the recent log tail.
"""

from __future__ import annotations

import logging
import os
import platform
import sys
from logging.handlers import RotatingFileHandler

from syllaport import __version__

LOGGER_NAME = "syllaport"
MAX_BYTES = 200 * 1024
BACKUP_COUNT = 3
TAIL_LINES = 50


def setup_logging(log_path):
    """Attach the rotating file handler. Safe to call twice."""
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logger.propagate = False
    try:
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
        handler = RotatingFileHandler(log_path, maxBytes=MAX_BYTES,
                                      backupCount=BACKUP_COUNT,
                                      encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    except OSError:
        pass  # logging must never break startup
    return logger


def log():
    return logging.getLogger(LOGGER_NAME)


def _log_tail(log_path, lines=TAIL_LINES):
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()[-lines:]
    except OSError:
        return []


def build_report(data_path, log_path):
    """The debug report text: facts only, no secrets exist to scrub."""
    import PySide6

    def _size(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return None

    data_size = _size(data_path)
    lines = [
        "Syllaport debug report",
        "Version: %s" % __version__,
        "Platform: %s %s (%s)" % (platform.system(), platform.release(),
                                  platform.machine()),
        "Python: %s" % sys.version.split()[0],
        "PySide6: %s" % PySide6.__version__,
        "Data file: %s" % (data_path or "Not set"),
        "Data size: %s" % ("Not saved yet" if data_size is None
                           else "%d bytes" % data_size),
        "Log file: %s" % (log_path or "Not set"),
        "",
        "Recent log (last %d lines):" % TAIL_LINES,
    ]
    tail = _log_tail(log_path) if log_path else []
    if tail:
        lines.extend(line.rstrip("\n") for line in tail)
    else:
        lines.append("No log lines yet.")
    return "\n".join(lines) + "\n"
