"""FAST test: optional capability mismatches produce a degrade plan."""

from __future__ import annotations


TEST_ID = "test_degrade_plan_generated"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate

    client, server = build_default_pair(repo_root)
    server["feature_capabilities"] = ["cap.ui.tui", "cap.worldgen.refinement_l3"]
    result = negotiate(repo_root, client, server)
    record = dict(result.get("negotiation_record") or {})
    degrade_plan = list(record.get("degrade_plan") or [])
    if str(record.get("compatibility_mode_id", "")) != "compat.degraded":
        return {"status": "fail", "message": "optional capability mismatch did not degrade"}
    if not degrade_plan:
        return {"status": "fail", "message": "degrade plan is missing"}
    return {"status": "pass", "message": "degrade plan generated for optional capability mismatch"}
