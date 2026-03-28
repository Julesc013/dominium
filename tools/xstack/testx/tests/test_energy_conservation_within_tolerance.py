"""FAST test: PHYS-3 conservation checks honor quantity tolerance policy bounds."""

from __future__ import annotations

import sys


TEST_ID = "test_energy_conservation_within_tolerance"
TEST_TAGS = ["fast", "physics", "energy", "numeric"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from physics.energy.energy_ledger_engine import record_energy_transformation

    transformation_rows = [
        {
            "schema_version": "1.0.0",
            "transformation_id": "transform.test.tolerance",
            "input_quantities": {"quantity.energy_total": 1},
            "output_quantities": {"quantity.energy_total": 1},
            "boundary_allowed": False,
            "deterministic_fingerprint": "0" * 64,
            "extensions": {},
        }
    ]
    tolerance_registry = {
        "record": {
            "quantity_tolerances": [
                {
                    "schema_version": "1.0.0",
                    "quantity_id": "quantity.energy_total",
                    "base_resolution": 1,
                    "tolerance_abs": 1,
                    "tolerance_rel": 0,
                    "rounding_mode": "round_half_to_even",
                    "overflow_policy": "fail",
                    "deterministic_fingerprint": "0" * 64,
                    "extensions": {},
                }
            ]
        }
    }

    within = record_energy_transformation(
        transformation_rows=transformation_rows,
        transformation_id="transform.test.tolerance",
        tick=1,
        source_id="source.alpha",
        input_values={"quantity.energy_total": 100},
        output_values={"quantity.energy_total": 101},
        enforce_conservation=True,
        tolerance=0,
        quantity_tolerance_registry=tolerance_registry,
        extensions={},
    )
    if str(within.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "expected complete result for conservation delta within tolerance"}

    outside = record_energy_transformation(
        transformation_rows=transformation_rows,
        transformation_id="transform.test.tolerance",
        tick=2,
        source_id="source.alpha",
        input_values={"quantity.energy_total": 100},
        output_values={"quantity.energy_total": 103},
        enforce_conservation=True,
        tolerance=0,
        quantity_tolerance_registry=tolerance_registry,
        extensions={},
    )
    if str(outside.get("result", "")).strip() != "violation":
        return {"status": "fail", "message": "expected violation result for delta beyond tolerance"}
    if str(outside.get("reason_code", "")).strip() != "refusal.energy.conservation_violation":
        return {"status": "fail", "message": "expected refusal.energy.conservation_violation reason code"}
    return {"status": "pass", "message": "energy conservation checks respect declared tolerance bounds"}
