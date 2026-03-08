"""STRICT test: LOGIC-10 stress envelope prefers compiled execution under pressure."""

from __future__ import annotations

import sys


TEST_ID = "test_compiled_preference_under_pressure"
TEST_TAGS = ["strict", "logic", "envelope", "compile", "stress"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.logic.tool_run_logic_stress import run_logic_stress

    report = run_logic_stress(
        repo_root=repo_root,
        seed=1010,
        tick_count=4,
        network_count=4,
        mega_node_count=1_000_000,
        thread_count_labels=(1, 8),
    )
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "logic stress envelope did not complete for compiled-preference fixture"}
    if not bool(dict(report.get("assertions") or {}).get("compiled_preference_under_pressure", False)):
        return {"status": "fail", "message": "logic stress envelope failed compiled-preference assertion"}
    ratio = float(dict(report.get("metrics") or {}).get("compiled_execution_ratio", 0.0) or 0.0)
    if ratio <= 0.0:
        return {"status": "fail", "message": "logic stress envelope observed zero compiled execution ratio"}
    return {"status": "pass", "message": "logic stress envelope prefers compiled execution under pressure"}
