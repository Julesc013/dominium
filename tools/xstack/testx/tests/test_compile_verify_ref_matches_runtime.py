"""FAST test: META-REF0 compiled-model verify reference evaluator matches runtime output."""

from __future__ import annotations


TEST_ID = "test_compile_verify_ref_matches_runtime"
TEST_TAGS = ["fast", "meta", "reference", "compile"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_ref0_testlib

    report = meta_ref0_testlib.run_reference_evaluator_case(
        repo_root=repo_root,
        evaluator_id="ref.compiled_model_verify",
        seed=1735,
        tick_start=0,
        tick_end=3,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "compiled-model verify reference mismatch: {}".format(
                str(report.get("discrepancy_summary", "")).strip()
            ),
        }
    runtime_hash = str(dict(report.get("runtime_output") or {}).get("output_hash", "")).strip()
    reference_hash = str(dict(report.get("reference_output") or {}).get("output_hash", "")).strip()
    if (not runtime_hash) or (runtime_hash != reference_hash):
        return {"status": "fail", "message": "compiled-model verify runtime/reference output hashes diverged"}
    return {"status": "pass", "message": "compiled-model verify reference evaluator matches runtime"}

