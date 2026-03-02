"""FAST test: SIG knowledge receipt mutation stays on allowed process/transport paths."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.no_direct_knowledge_mutation"
TEST_TAGS = ["fast", "signals", "repox", "auditx"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = [
        row
        for row in list(result.get("findings") or [])
        if str(row.get("rule_id", "")).strip() == "INV-NO-DIRECT-KNOWLEDGE-TRANSFER"
    ]
    if findings:
        first = dict(findings[0] or {})
        path = str(first.get("file_path", "unknown")).strip() or "unknown"
        line = int(first.get("line_number", 0) or 0)
        return {
            "status": "fail",
            "message": "knowledge bypass smell detected at {}:{}".format(path, line),
        }
    return {"status": "pass", "message": "no direct knowledge mutation patterns detected"}
