"""FAST test: PHYS-3 ledger helper enforces per-transform conservation when required."""

from __future__ import annotations

import sys


TEST_ID = "test_energy_conservation_enforced"
TEST_TAGS = ["fast", "physics", "energy", "conservation"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.physics import record_energy_transformation

    transformation_rows = [
        {
            "schema_version": "1.0.0",
            "transformation_id": "transform.test.conservation",
            "input_quantities": {"quantity.energy_kinetic": 1},
            "output_quantities": {"quantity.energy_thermal": 1},
            "boundary_allowed": False,
            "requires_profile_flag": None,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]

    violating = record_energy_transformation(
        transformation_rows=transformation_rows,
        transformation_id="transform.test.conservation",
        tick=7,
        source_id="source.test.energy",
        input_values={"quantity.energy_kinetic": 10},
        output_values={"quantity.energy_thermal": 9},
        enforce_conservation=True,
        tolerance=0,
        extensions={},
    )
    if str(violating.get("result", "")) != "violation":
        return {"status": "fail", "message": "non-conserving transform was not rejected under enforcement"}
    if str(violating.get("reason_code", "")) != "refusal.energy.conservation_violation":
        return {"status": "fail", "message": "unexpected conservation violation reason code"}

    permissive = record_energy_transformation(
        transformation_rows=transformation_rows,
        transformation_id="transform.test.conservation",
        tick=7,
        source_id="source.test.energy",
        input_values={"quantity.energy_kinetic": 10},
        output_values={"quantity.energy_thermal": 9},
        enforce_conservation=False,
        tolerance=0,
        extensions={},
    )
    if str(permissive.get("result", "")) != "complete":
        return {"status": "fail", "message": "conservation-disabled transform should complete deterministically"}
    return {"status": "pass", "message": "energy conservation enforcement behaves as expected"}
