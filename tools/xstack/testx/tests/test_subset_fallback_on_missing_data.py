"""FAST test: subset planner records deterministic fallback reason when impact graph coverage is incomplete."""

from __future__ import annotations

import os
import sys


TEST_ID = "testx.dev.subset_fallback_on_missing_data"
TEST_TAGS = ["smoke", "tools", "runner"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.runner import resolve_subset_selection

    temp_rel = "impact_subset_missing_data_probe.tmp"
    temp_abs = os.path.join(repo_root, temp_rel)
    open(temp_abs, "w", encoding="utf-8").write("subset missing-data probe\n")
    try:
        plan = resolve_subset_selection(repo_root=repo_root, profile="FAST", subset=None)
    finally:
        try:
            os.remove(temp_abs)
        except OSError:
            pass

    reason = str(plan.get("fallback_reason", ""))
    if str(plan.get("mode", "")) != "fallback_full":
        return {"status": "fail", "message": "expected fallback_full mode for missing graph coverage"}
    if reason != "impact_graph_incomplete_or_empty_subset":
        return {"status": "fail", "message": "unexpected fallback reason '{}'".format(reason)}
    return {"status": "pass", "message": "subset fallback reason behavior passed"}
