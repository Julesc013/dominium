"""FAST test: META-REF0 energy ledger reference evaluator matches runtime output."""

from __future__ import annotations


TEST_ID = "test_energy_ledger_ref_matches_runtime"
TEST_TAGS = ["fast", "meta", "reference", "energy"]


def run(repo_root: str):
    from tools.xstack.testx.tests import meta_ref0_testlib

    report = meta_ref0_testlib.run_reference_evaluator_case(
        repo_root=repo_root,
        evaluator_id="ref.energy_ledger",
        seed=1732,
        tick_start=0,
        tick_end=3,
    )
    if str(report.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "energy reference evaluator reported mismatch: {}".format(
                str(report.get("discrepancy_summary", "")).strip()
            ),
        }
    runtime_hash = str(dict(report.get("runtime_output") or {}).get("output_hash", "")).strip()
    reference_hash = str(dict(report.get("reference_output") or {}).get("output_hash", "")).strip()
    if (not runtime_hash) or (runtime_hash != reference_hash):
        return {"status": "fail", "message": "energy runtime/reference output hashes diverged"}
    return {"status": "pass", "message": "energy reference evaluator matches runtime"}

