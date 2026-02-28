"""STRICT test: RepoX type-branching invariant reports no gameplay violations."""

from __future__ import annotations

import sys


TEST_ID = "test_no_type_branching_detected"
TEST_TAGS = ["strict", "repox", "capability"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = [
        dict(row)
        for row in list(result.get("findings") or [])
        if isinstance(row, dict) and str(row.get("rule_id", "")) == "INV-NO-TYPE-BRANCHING"
    ]
    if findings:
        first = dict(findings[0])
        return {
            "status": "fail",
            "message": "type-branching invariant violation detected at {}:{}".format(
                str(first.get("file_path", "")),
                int(first.get("line_number", 0) or 0),
            ),
        }
    return {"status": "pass", "message": "no type-branching invariant violations detected"}

