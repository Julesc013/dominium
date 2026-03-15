"""FAST test: DIST-6 identical rebuilds keep the same negotiation hash."""

from __future__ import annotations


TEST_ID = "test_identical_rebuild_negotiation_hash_match"
TEST_TAGS = ["fast", "dist", "interop", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.dist6_testlib import load_case

    report = load_case(repo_root, "same_build_identical_rebuild")
    assertions = dict(report.get("assertions") or {})
    if not report:
        return {"status": "fail", "message": "DIST-6 identical rebuild report is missing"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "DIST-6 identical rebuild case did not complete"}
    if not bool(assertions.get("identical_rebuild_hash_match", False)):
        return {"status": "fail", "message": "identical rebuild negotiation hash drifted"}
    if not bool(assertions.get("same_build_id", False)):
        return {"status": "fail", "message": "identical rebuild build_id drifted"}
    return {"status": "pass", "message": "identical rebuilds keep the same build_id and negotiation hash"}
