"""FAST test: CHEM-4 stress entropy remains monotonic absent reset events."""

from __future__ import annotations

import sys


TEST_ID = "test_chem4_entropy_monotonicity"
TEST_TAGS = ["fast", "chem", "entropy", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.chem.tool_verify_entropy_monotonicity import verify_chem_entropy
    from tools.xstack.testx.tests.chem4_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(
        repo_root=repo_root,
        seed=9204,
        species_pools=48,
        reactions=24,
        process_runs=18,
        ticks=40,
    )
    report = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        tick_count=40,
        budget_envelope_id="chem.envelope.standard",
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "CHEM stress run failed for entropy-monotonicity fixture"}

    verification = verify_chem_entropy(report_payload=dict(report))
    if str(verification.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "CHEM entropy monotonicity verifier reported violations",
            "details": {"violation_count": int(verification.get("violation_count", 0) or 0)},
        }
    return {"status": "pass", "message": "CHEM entropy monotonicity verified"}

