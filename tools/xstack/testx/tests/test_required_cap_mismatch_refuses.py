"""FAST test: required capability mismatches refuse negotiation."""

from __future__ import annotations


TEST_ID = "test_required_cap_mismatch_refuses"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate

    client, server = build_default_pair(repo_root)
    client["required_capabilities"] = ["cap.ui.rendered"]
    server["feature_capabilities"] = ["cap.ui.tui"]
    result = negotiate(repo_root, client, server)
    refusal = dict(result.get("refusal") or {})
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "required capability mismatch did not refuse"}
    if str(refusal.get("reason_code", "")) != "refusal.compat.missing_required_cap":
        return {"status": "fail", "message": "unexpected refusal code for required capability mismatch"}
    return {"status": "pass", "message": "required capability mismatches refuse deterministically"}
