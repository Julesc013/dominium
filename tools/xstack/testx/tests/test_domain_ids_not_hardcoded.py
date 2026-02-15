"""STRICT test: RepoX must not report hardcoded dom.domain.* tokens in code paths."""

from __future__ import annotations

import sys


TEST_ID = "testx.domain.ids_not_hardcoded"
TEST_TAGS = ["strict", "repox"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = list(result.get("findings") or [])
    hardcoded = [
        row
        for row in findings
        if isinstance(row, dict) and str(row.get("rule_id", "")) == "INV-NO-HARDCODED-DOMAIN-TOKENS"
    ]
    if hardcoded:
        return {"status": "fail", "message": "repox detected hardcoded domain tokens"}
    if str(result.get("status", "")) != "pass":
        return {"status": "fail", "message": "repox strict status is not pass"}
    return {"status": "pass", "message": "hardcoded domain token check passed"}
