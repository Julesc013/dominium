"""FAST test: compound composition normalizes to canonical mass-fraction scale."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.compound_mass_fraction_sum"
TEST_TAGS = ["fast", "materials", "taxonomy"]


def _row_by_id(rows: object, key: str, target: str) -> dict:
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and str(row.get(key, "")).strip() == str(target):
            return dict(row)
    return {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.composition_engine import DEFAULT_FRACTION_SCALE, validate_compound_composition

    element_payload = json.load(open(os.path.join(repo_root, "data", "registries", "element_registry.json"), "r", encoding="utf-8"))
    compound_payload = json.load(open(os.path.join(repo_root, "data", "registries", "compound_registry.json"), "r", encoding="utf-8"))
    element_registry = dict(element_payload.get("record") or {})
    compound_row = _row_by_id((compound_payload.get("record") or {}).get("compounds"), "compound_id", "compound.H2O")
    if not compound_row:
        return {"status": "fail", "message": "compound.H2O missing from registry"}
    validated = validate_compound_composition(compound_row, element_registry=element_registry)
    if int(validated.get("mass_fraction_sum_raw", 0) or 0) != int(DEFAULT_FRACTION_SCALE):
        return {"status": "fail", "message": "compound mass fractions did not normalize to canonical scale"}
    return {"status": "pass", "message": "compound mass fraction normalization passed"}
