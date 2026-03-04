"""FAST test: registered dissipative transforms map loss to heat outputs."""

from __future__ import annotations

import json
import os


TEST_ID = "test_loss_to_heat_transform_present"
TEST_TAGS = ["fast", "physics", "energy", "registry"]


def _rows(payload: dict):
    rows = list(payload.get("energy_transformations") or [])
    if rows:
        return rows
    return list((dict(payload.get("record") or {})).get("energy_transformations") or [])


def run(repo_root: str):
    rel_path = "data/registries/energy_transformation_registry.json"
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "energy transformation registry missing or invalid"}

    rows = [dict(row) for row in _rows(payload) if isinstance(row, dict)]
    by_id = dict((str(row.get("transformation_id", "")).strip(), row) for row in rows if str(row.get("transformation_id", "")).strip())
    for transform_id in ("transform.kinetic_to_thermal", "transform.electrical_to_thermal", "transform.chemical_to_thermal"):
        row = dict(by_id.get(transform_id) or {})
        if not row:
            return {"status": "fail", "message": "missing transformation {}".format(transform_id)}
        outputs = dict(row.get("output_quantities") or {})
        if "quantity.heat_loss" not in outputs:
            return {"status": "fail", "message": "{} must output quantity.heat_loss".format(transform_id)}
    return {"status": "pass", "message": "dissipative transforms map to quantity.heat_loss"}
