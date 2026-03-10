"""FAST test: EMB-2 jump is only allowed while grounded."""

from __future__ import annotations

import sys


TEST_ID = "test_jump_only_when_grounded"
TEST_TAGS = ["fast", "embodiment", "locomotion", "collision"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.emb2_testlib import jump_grounded_report

    report = jump_grounded_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "EMB-2 grounded jump probe did not complete"}
    if str(report.get("airborne_result", "")).strip() != "refused":
        return {"status": "fail", "message": "EMB-2 airborne jump should refuse"}
    if str(report.get("airborne_reason_code", "")).strip() != "refusal.move.jump_not_grounded":
        return {"status": "fail", "message": "EMB-2 airborne jump refusal should use refusal.move.jump_not_grounded"}
    if str(report.get("grounded_result", "")).strip() != "complete":
        return {"status": "fail", "message": "EMB-2 grounded jump should complete"}
    if int(report.get("velocity_z_after_jump", 0) or 0) <= 0:
        return {"status": "fail", "message": "EMB-2 grounded jump should apply an upward velocity"}
    if bool(report.get("grounded_after_jump", True)):
        return {"status": "fail", "message": "EMB-2 jump should clear grounded state until next terrain contact"}
    return {"status": "pass", "message": "EMB-2 jump grounding behavior is deterministic"}
