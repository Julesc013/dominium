"""FAST test: retro-consistency flow duplication rule remains clean for canonical repo."""

from __future__ import annotations

import sys


TEST_ID = "test_no_duplicate_flow_logic"
TEST_TAGS = ["fast", "repox", "architecture"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = list(result.get("findings") or [])
    hits = [row for row in findings if str(row.get("rule_id", "")).strip() == "INV-NO-DUPLICATE-FLOW"]
    if hits:
        return {"status": "fail", "message": "flow duplication invariant triggered: {}".format(len(hits))}
    return {"status": "pass", "message": "No duplicate flow logic detected"}
