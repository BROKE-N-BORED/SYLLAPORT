#!/bin/bash
# Syllaport test runner.
# Unit tests run plain. GUI unit tests run on the offscreen platform
# (no X server roundtrips, so they stay fast under load); the real
# Xvfb + xcb proof is verify/drive_r2.py, which drives the app like a
# user and screenshots it. Qt libs come from ~/workspace/qt-libs (see
# AGENTS.md: never override HOME for Qt/xcb).
# Usage: bash run_tests.sh [unittest args, e.g. tests.test_data]
set -e
cd "$(dirname "$0")"
PY="${PY:-$HOME/workspace/forge-v2-testenv/bin/python}"
if [ ! -x "$PY" ]; then PY="python3"; fi
export TMPDIR=/tmp
export LD_LIBRARY_PATH="$HOME/workspace/qt-libs/root/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export __EGL_VENDOR_LIBRARY_DIRS="$HOME/workspace/qt-libs/root/usr/share/glvnd/egl_vendor.d"
export QT_QPA_PLATFORM=offscreen
if [ $# -gt 0 ]; then
  exec timeout 280 "$PY" -u -m unittest "$@" -v
fi
# The full suite does not fit one 280 s run under sandbox load (the GUI
# tests build 8 windows per class), so it runs in phases, each under
# its own timeout. Phase 1 is the fast unit tests; phases 2 and 3 split
# the GUI classes. Every phase must pass.
timeout 120 "$PY" -u -m unittest tests.test_data tests.test_catalog tests.test_checklist tests.test_style || exit 1
timeout 280 "$PY" -u -m unittest tests.test_gui.ChecklistFlowTests tests.test_gui.CoursesTests tests.test_gui.DashboardTileTests tests.test_gui.HelpAndBackupTests tests.test_gui.NoAmpersandTests tests.test_gui.NoDefaultSelectionTests || exit 1
timeout 280 "$PY" -u -m unittest tests.test_gui.PresetTests tests.test_gui.WindowTests || exit 1
echo "ALL TESTS PASSED"
