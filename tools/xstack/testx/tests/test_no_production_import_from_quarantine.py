"""FAST test: production/runtime modules do not import/reference legacy/quarantine paths."""

from __future__ import annotations

import sys


TEST_ID = "test_no_production_import_from_quarantine"
TEST_TAGS = ["fast", "architecture", "deprecation", "quarantine"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.repox.check import run_repox_check

    result = run_repox_check(repo_root=repo_root, profile="STRICT")
    findings = list(result.get("findings") or [])
    hits = [
        row
        for row in findings
        if str((dict(row or {})).get("rule_id", "")).strip() == "INV-NO-PRODUCTION-LEGACY-IMPORT"
    ]
    if hits:
        return {
            "status": "fail",
            "message": "production legacy/quarantine import invariant triggered: {}".format(len(hits)),
        }
    return {"status": "pass", "message": "production runtime quarantine boundary verified"}

