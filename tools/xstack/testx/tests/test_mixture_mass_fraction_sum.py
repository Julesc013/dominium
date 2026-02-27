"""FAST test: mixture mass fractions must sum to canonical scale."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.mixture_mass_fraction_sum"
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

    from src.materials.composition_engine import DEFAULT_FRACTION_SCALE, validate_mixture_composition

    payload = json.load(open(os.path.join(repo_root, "data", "registries", "mixture_registry.json"), "r", encoding="utf-8"))
    mixture_row = _row_by_id((payload.get("record") or {}).get("mixtures"), "mixture_id", "mixture.air")
    if not mixture_row:
        return {"status": "fail", "message": "mixture.air missing from registry"}
    validated = validate_mixture_composition(mixture_row)
    if int(validated.get("mass_fraction_sum_raw", 0) or 0) != int(DEFAULT_FRACTION_SCALE):
        return {"status": "fail", "message": "mixture mass fractions did not match canonical scale"}
    return {"status": "pass", "message": "mixture mass fraction normalization passed"}
