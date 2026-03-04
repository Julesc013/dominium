"""FAST test: PHYS-3 energy transformation registry includes required baseline transforms."""

from __future__ import annotations

import json
import os


TEST_ID = "test_energy_transformation_registered"
TEST_TAGS = ["fast", "physics", "energy", "registry"]


def run(repo_root: str):
    rel_path = "data/registries/energy_transformation_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "energy transformation registry missing or invalid JSON"}
    rows = list(payload.get("energy_transformations") or [])
    if not rows:
        rows = list((dict(payload.get("record") or {})).get("energy_transformations") or [])
    if not rows:
        return {"status": "fail", "message": "energy transformation registry is empty"}

    ids = sorted(
        set(
            str(row.get("transformation_id", "")).strip()
            for row in list(rows or [])
            if isinstance(row, dict) and str(row.get("transformation_id", "")).strip()
        )
    )
    required = {
        "transform.kinetic_to_thermal",
        "transform.electrical_to_thermal",
        "transform.chemical_to_thermal",
        "transform.potential_to_kinetic",
        "transform.external_irradiance",
    }
    missing = sorted(required - set(ids))
    if missing:
        return {"status": "fail", "message": "missing required transformations: {}".format(",".join(missing))}
    return {"status": "pass", "message": "energy transformation registry contains PHYS-3 baseline rows"}
