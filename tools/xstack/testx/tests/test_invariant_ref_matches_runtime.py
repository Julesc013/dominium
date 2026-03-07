"""FAST test: META-REF0 system invariant reference evaluator matches runtime output."""

from __future__ import annotations


TEST_ID = "test_invariant_ref_matches_runtime"
TEST_TAGS = ["fast", "meta", "reference", "system", "invariant"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_ref0_testlib

    report = meta_ref0_testlib.run_reference_evaluator_case(
        repo_root=repo_root,
        evaluator_id="ref.system_invariant_check",
        seed=1734,
        tick_start=0,
        tick_end=3,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "system invariant reference mismatch: {}".format(
                str(report.get("discrepancy_summary", "")).strip()
            ),
        }
    runtime_hash = str(dict(report.get("runtime_output") or {}).get("output_hash", "")).strip()
    reference_hash = str(dict(report.get("reference_output") or {}).get("output_hash", "")).strip()
    if (not runtime_hash) or (runtime_hash != reference_hash):
        return {"status": "fail", "message": "system invariant runtime/reference output hashes diverged"}
    return {"status": "pass", "message": "system invariant reference evaluator matches runtime"}

