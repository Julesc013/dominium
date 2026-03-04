"""FAST test: CHEM-4 stress mass conservation stays within declared tolerance."""

from __future__ import annotations

import sys


TEST_ID = "test_chem4_mass_conservation_within_tolerance"
TEST_TAGS = ["fast", "chem", "conservation", "mass", "tolerance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.chem.tool_verify_mass_conservation import _mass_tolerance_abs, verify_mass_conservation
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
        return {"status": "fail", "message": "CHEM stress run failed for mass-conservation fixture"}

    tolerance_abs = int(_mass_tolerance_abs(repo_root=repo_root, override=0))
    verification = verify_mass_conservation(
        report_payload=dict(report),
        tolerance_abs=int(tolerance_abs),
    )
    if str(verification.get("result", "")).strip() != "complete":
        return {
            "status": "fail",
            "message": "CHEM mass conservation verifier reported violations",
            "details": {"violation_count": int(verification.get("violation_count", 0) or 0)},
        }
    return {"status": "pass", "message": "CHEM mass conservation remains within tolerance"}

