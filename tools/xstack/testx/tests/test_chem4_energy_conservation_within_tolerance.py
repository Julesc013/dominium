"""FAST test: CHEM-4 stress energy conservation stays within declared tolerance."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_chem4_energy_conservation_within_tolerance"
TEST_TAGS = ["fast", "chem", "conservation", "energy", "tolerance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.chem.tool_verify_energy_conservation import _energy_tolerance_abs
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
        return {"status": "fail", "message": "CHEM stress run failed for energy-conservation fixture"}

    registry_abs = os.path.join(repo_root, "data", "registries", "energy_transformation_registry.json")
    try:
        registry_payload = json.load(open(registry_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "energy transformation registry unreadable for CHEM energy verification"}
    if not isinstance(registry_payload, dict):
        return {"status": "fail", "message": "energy transformation registry payload invalid"}

    tolerance_abs = int(_energy_tolerance_abs(repo_root=repo_root, override=0))
    metrics = dict(report.get("metrics") or {})
    residual_stats = dict(metrics.get("energy_residual_stats") or {})
    max_abs = int(residual_stats.get("max_abs", 0) or 0)
    if max_abs > tolerance_abs:
        return {
            "status": "fail",
            "message": "CHEM energy residual exceeded tolerance",
            "details": {"max_abs": int(max_abs), "tolerance_abs": int(tolerance_abs)},
        }

    per_tick = [int(value or 0) for value in list(metrics.get("per_tick_energy_residual") or [])]
    for tick, residual in enumerate(per_tick):
        if abs(int(residual)) <= tolerance_abs:
            continue
        return {
            "status": "fail",
            "message": "CHEM per-tick energy residual exceeded tolerance",
            "details": {"tick": int(tick), "residual": int(residual), "tolerance_abs": int(tolerance_abs)},
        }
    return {"status": "pass", "message": "CHEM energy conservation remains within tolerance"}
