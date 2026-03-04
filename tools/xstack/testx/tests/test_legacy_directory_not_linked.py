"""FAST test: production/runtime code paths do not reference legacy quarantine directory."""

from __future__ import annotations

import sys


TEST_ID = "test_legacy_directory_not_linked"
TEST_TAGS = ["fast", "repox", "architecture", "legacy"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = list(result.get("findings") or [])
    hits = [row for row in findings if str(row.get("rule_id", "")).strip() == "INV-NO-LEGACY-REFERENCE"]
    if hits:
        return {"status": "fail", "message": "legacy reference invariant triggered: {}".format(len(hits))}
    return {"status": "pass", "message": "Legacy quarantine is not linked from runtime paths"}
