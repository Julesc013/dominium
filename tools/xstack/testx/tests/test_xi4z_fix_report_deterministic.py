"""FAST test: XI-4z fix report remains deterministic.""" 

from __future__ import annotations


TEST_ID = "test_xi4z_fix_report_deterministic"
TEST_TAGS = ["fast", "xi", "restructure", "determinism"]


def run(repo_root: str):
    from tools.review.xi4z_fix_common import XI4Z_FIX_REPORT_JSON_REL, artifact_hashes, build_xi4z_fix_snapshot
    from tools.xstack.testx.tests.xi4z_fix_testlib import committed_fix_report

    committed = committed_fix_report(repo_root)
    first = build_xi4z_fix_snapshot(repo_root)
    second = build_xi4z_fix_snapshot(repo_root)
    if artifact_hashes(first) != artifact_hashes(second):
        return {"status": "fail", "message": "Fresh XI-4z fix scans are nondeterministic"}
    fresh = dict(first.get("json_payloads", {}).get(XI4Z_FIX_REPORT_JSON_REL) or {})
    if list(committed.get("remaining_mismatches") or []):
        return {"status": "fail", "message": "XI-4z fix report still records remaining mismatches"}
    if committed.get("mapping_decisions_changed"):
        return {"status": "fail", "message": "XI-4z fix report must confirm mapping decisions unchanged"}
    if list(fresh.get("remaining_mismatches") or []):
        return {"status": "fail", "message": "Fresh XI-4z fix scan still records remaining mismatches"}
    if fresh.get("mapping_decisions_changed"):
        return {"status": "fail", "message": "Fresh XI-4z fix scan must confirm mapping decisions unchanged"}
    return {"status": "pass", "message": "XI-4z fix report remains deterministic"}
