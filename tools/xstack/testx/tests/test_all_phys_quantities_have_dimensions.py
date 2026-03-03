"""FAST test: canonical PHYS quantities exist and have quantity-type dimensions."""

from __future__ import annotations

import json
import os


TEST_ID = "testx.physics.quantities_have_dimensions"
TEST_TAGS = ["fast", "physics", "registry", "dimensions"]


_REQUIRED_PHYS_QUANTITIES = {
    "quantity.mass",
    "quantity.momentum_linear",
    "quantity.momentum_angular",
    "quantity.force",
    "quantity.torque",
    "quantity.energy_kinetic",
    "quantity.energy_potential",
    "quantity.energy_thermal",
    "quantity.energy_electrical",
    "quantity.energy_chemical",
    "quantity.energy_total",
    "quantity.heat_loss",
    "quantity.entropy_index",
    "quantity.radiation_dose",
}


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(abs_path, "r", encoding="utf-8"))


def run(repo_root: str):
    try:
        quantity_payload = _load_json(repo_root, "data/registries/quantity_registry.json")
        quantity_type_payload = _load_json(repo_root, "data/registries/quantity_type_registry.json")
    except (OSError, ValueError):
        return {"status": "fail", "message": "quantity registries missing or invalid"}

    quantity_ids = {
        str(row.get("quantity_id", "")).strip()
        for row in list(((quantity_payload.get("record") or {}).get("quantities") or []))
        if isinstance(row, dict)
    }
    missing_quantities = sorted(token for token in _REQUIRED_PHYS_QUANTITIES if token not in quantity_ids)
    if missing_quantities:
        return {
            "status": "fail",
            "message": "missing canonical physics quantities: {}".format(",".join(missing_quantities)),
        }

    quantity_types = {
        str(row.get("quantity_id", "")).strip(): str(row.get("dimension_id", "")).strip()
        for row in list(((quantity_type_payload.get("record") or {}).get("quantity_types") or []))
        if isinstance(row, dict)
    }

    missing_dimensions = sorted(
        token
        for token in _REQUIRED_PHYS_QUANTITIES
        if token not in quantity_types or not str(quantity_types.get(token, "")).strip()
    )
    if missing_dimensions:
        return {
            "status": "fail",
            "message": "canonical physics quantities missing dimension declarations: {}".format(",".join(missing_dimensions)),
        }
    return {"status": "pass", "message": "canonical physics quantity dimension coverage valid"}
