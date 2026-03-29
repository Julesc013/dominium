from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_source_pocket_policy, recompute_fingerprint

TEST_ID = "test_xi5x2_source_pocket_policy_valid"
TEST_TAGS = ["fast", "xi5x2", "policy"]


def run(repo_root: str):
    payload = committed_source_pocket_policy(repo_root)
    if payload.get("deterministic_fingerprint") != recompute_fingerprint(payload):
        return {"status": "fail", "message": "Xi-5x2 source-pocket policy fingerprint mismatch"}
    rows = list(payload.get("policy_rows") or [])
    if not rows:
        return {"status": "fail", "message": "Xi-5x2 source-pocket policy has no policy rows"}
    allowlisted = {_ for _ in (item.get("root_path") for item in list(payload.get("allowlisted_residual_roots") or [])) if _}
    if "packs/source" not in allowlisted or "legacy/source/tests" not in allowlisted:
        return {"status": "fail", "message": "Xi-5x2 source-pocket policy missing expected allowlisted residual roots"}
    return {"status": "pass", "message": "Xi-5x2 source-pocket policy artifact is present and deterministic"}
