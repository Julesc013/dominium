"""STRICT test: LOGIC-10 bounded reference evaluator matches runtime fixture output."""

from __future__ import annotations


TEST_ID = "test_reference_logic_fixture_match"
TEST_TAGS = ["strict", "logic", "envelope", "reference"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_ref0_testlib

    report = meta_ref0_testlib.run_reference_evaluator_case(
        repo_root=repo_root,
        evaluator_id="ref.logic_eval_small",
        seed=1739,
        tick_start=1,
        tick_end=3,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "logic small reference evaluator mismatch: {}".format(
                str(report.get("discrepancy_summary", "")).strip()
            ),
        }
    runtime_hash = str(dict(report.get("runtime_output") or {}).get("output_hash", "")).strip()
    reference_hash = str(dict(report.get("reference_output") or {}).get("output_hash", "")).strip()
    if (not runtime_hash) or (runtime_hash != reference_hash):
        return {"status": "fail", "message": "logic small reference runtime/reference output hashes diverged"}
    return {"status": "pass", "message": "logic small reference evaluator matches runtime"}
