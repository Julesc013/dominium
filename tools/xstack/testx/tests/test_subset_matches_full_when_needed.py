"""FAST test: subset planner switches to full execution when safe fallback is required."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.dev.subset_matches_full_when_needed"
TEST_TAGS = ["smoke", "tools", "runner"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.runner import resolve_subset_selection

    temp_rel = "impact_subset_fallback_marker.tmp"
    temp_abs = os.path.join(repo_root, temp_rel)
    open(temp_abs, "w", encoding="utf-8").write("subset fallback probe\n")
    try:
        plan = resolve_subset_selection(repo_root=repo_root, profile="FAST", subset=None)
    finally:
        try:
            os.remove(temp_abs)
        except OSError:
            pass

    if str(plan.get("mode", "")) != "fallback_full":
        return {"status": "fail", "message": "expected fallback_full mode when coverage is incomplete"}
    if not bool(plan.get("run_all", False)):
        return {"status": "fail", "message": "fallback_full mode must set run_all=true"}
    return {"status": "pass", "message": "subset planner full-fallback behavior passed"}
