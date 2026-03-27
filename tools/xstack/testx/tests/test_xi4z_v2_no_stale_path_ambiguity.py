"""FAST test: XI-4z-fix1 removes stale target-path ambiguity for Xi-5a."""

from __future__ import annotations


TEST_ID = "test_xi4z_v2_no_stale_path_ambiguity"
TEST_TAGS = ["fast", "xi", "restructure", "ambiguity"]


def run(repo_root: str):
    from tools.xstack.testx.tests.xi4z_fix1_testlib import (
        committed_fix1_report,
        committed_readiness_contract_v2,
        committed_target_paths,
    )

    report = committed_fix1_report(repo_root)
    if list(report.get("remaining_ambiguous_rows") or []):
        return {"status": "fail", "message": "XI-4z-fix1 report still records ambiguous approved rows"}
    if not bool(report.get("mechanical_ready_for_xi5a_with_v2")):
        return {"status": "fail", "message": "XI-4z-fix1 report must confirm mechanical Xi-5a readiness with v2 inputs"}

    target_paths = committed_target_paths(repo_root)
    summary = dict(target_paths.get("summary") or {})
    if int(summary.get("rows_with_exact_target_paths", 0) or 0) <= 0:
        return {"status": "fail", "message": "XI-4z-fix1 target-path index must expose exact approved targets"}

    readiness = committed_readiness_contract_v2(repo_root)
    if str(readiness.get("approved_lock_path", "")).strip() != "data/restructure/src_domain_mapping_lock_approved_v2.json":
        return {"status": "fail", "message": "XI-4z-fix1 readiness contract must point at the v2 lock"}
    if str(readiness.get("path_derivation_policy", "")).strip() != "forbidden":
        return {"status": "fail", "message": "XI-4z-fix1 readiness contract must forbid target-path derivation"}
    return {"status": "pass", "message": "XI-4z-fix1 removes stale target-path ambiguity for Xi-5a"}
