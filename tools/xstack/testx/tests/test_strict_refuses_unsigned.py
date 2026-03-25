"""FAST test: strict trust refuses unsigned governed artifacts."""

from __future__ import annotations


TEST_ID = "test_strict_refuses_unsigned"
TEST_TAGS = ["fast", "omega", "trust", "strict"]


def run(repo_root: str):
    from tools.xstack.testx.tests.trust_strict_testlib import build_report, case_by_id

    report = build_report(repo_root)
    release_case = case_by_id(report, "strict_ranked_refuses_unsigned_release_index")
    pack_case = case_by_id(report, "strict_ranked_refuses_unsigned_official_pack")
    if str(release_case.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "strict trust must refuse unsigned release_index fixtures"}
    if str(pack_case.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "strict trust must refuse unsigned official pack fixtures"}
    if str(release_case.get("refusal_code", "")).strip() != "refusal.trust.signature_missing":
        return {"status": "fail", "message": "strict unsigned release_index refusal_code drifted"}
    if str(pack_case.get("refusal_code", "")).strip() != "refusal.trust.signature_missing":
        return {"status": "fail", "message": "strict unsigned official pack refusal_code drifted"}
    return {"status": "pass", "message": "strict trust refuses unsigned governed artifacts"}
