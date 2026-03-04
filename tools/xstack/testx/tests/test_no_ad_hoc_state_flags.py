"""FAST test: retro-consistency state transition logic remains on canonical state-machine substrate."""

from __future__ import annotations

import sys


TEST_ID = "test_no_ad_hoc_state_flags"
TEST_TAGS = ["fast", "repox", "architecture"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = list(result.get("findings") or [])
    hits = [row for row in findings if str(row.get("rule_id", "")).strip() == "INV-NO-ADHOC-STATE-FLAG"]
    if hits:
        return {"status": "fail", "message": "ad-hoc state flag invariant triggered: {}".format(len(hits))}
    return {"status": "pass", "message": "No ad-hoc state flag transitions detected"}
