#!/usr/bin/env python3
"""Compatibility wrapper for SOL-1 illumination replay determinism."""

from __future__ import annotations

import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.abspath(THIS_DIR)
for _repo_root_probe_depth in range(16):
    if os.path.exists(os.path.join(REPO_ROOT_HINT, "AGENTS.md")):
        break
    parent = os.path.dirname(REPO_ROOT_HINT)
    if parent == REPO_ROOT_HINT:
        REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
        break
    REPO_ROOT_HINT = parent
REPO_ROOT_HINT = os.path.normpath(REPO_ROOT_HINT)
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.domain.astronomy.tool_replay_illumination_view import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
