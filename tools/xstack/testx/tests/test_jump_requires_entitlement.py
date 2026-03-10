"""FAST test: EMB-2 jump requires the explicit entitlement surface."""

from __future__ import annotations

import sys


TEST_ID = "test_jump_requires_entitlement"
TEST_TAGS = ["fast", "embodiment", "locomotion", "authority"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.emb2_testlib import jump_entitlement_report

    report = jump_entitlement_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EMB-2 entitlement probe did not complete"}
    if str(report.get("jump_result", "")).strip() != "refused":
        return {"status": "fail", "message": "EMB-2 jump should refuse when ent.move.jump is missing"}
    reason_code = str(report.get("reason_code", "")).strip()
    if reason_code not in {"ENTITLEMENT_MISSING", "refusal.control.entitlement_missing"}:
        return {"status": "fail", "message": "EMB-2 jump refusal should identify missing entitlement"}
    return {"status": "pass", "message": "EMB-2 jump correctly requires entitlement"}
