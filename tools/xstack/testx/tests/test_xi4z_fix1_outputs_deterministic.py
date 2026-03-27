"""FAST test: XI-4z-fix1 outputs remain deterministic."""

from __future__ import annotations


TEST_ID = "test_xi4z_fix1_outputs_deterministic"
TEST_TAGS = ["fast", "xi", "restructure", "determinism"]


def run(repo_root: str):
    from tools.review.xi4z_fix1_common import XI4Z_FIX1_REPORT_JSON_REL, artifact_hashes, build_xi4z_fix1_snapshot
    from tools.xstack.testx.tests.xi4z_fix1_testlib import committed_fix1_report

    committed = committed_fix1_report(repo_root)
    first = build_xi4z_fix1_snapshot(repo_root)
    second = build_xi4z_fix1_snapshot(repo_root)
    if artifact_hashes(first) != artifact_hashes(second):
        return {"status": "fail", "message": "Fresh XI-4z-fix1 snapshots are nondeterministic"}
    fresh = dict(first.get("json_payloads", {}).get(XI4Z_FIX1_REPORT_JSON_REL) or {})
    if list(committed.get("remaining_ambiguous_rows") or []):
        return {"status": "fail", "message": "Committed XI-4z-fix1 report still records remaining ambiguities"}
    if list(fresh.get("remaining_ambiguous_rows") or []):
        return {"status": "fail", "message": "Fresh XI-4z-fix1 snapshot still records remaining ambiguities"}
    return {"status": "pass", "message": "XI-4z-fix1 outputs remain deterministic"}
