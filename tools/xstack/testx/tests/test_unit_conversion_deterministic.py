"""FAST test: unit conversion remains deterministic for fixed-point quantities."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.unit_conversion_deterministic"
TEST_TAGS = ["fast", "materials", "units", "determinism"]


def _read_registry(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = json.load(open(abs_path, "r", encoding="utf-8"))
    return dict((payload.get("record") or {}))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.dimension_engine import quantity_convert

    unit_registry = _read_registry(repo_root, "data/registries/unit_registry.json")
    dimension_registry = _read_registry(repo_root, "data/registries/dimension_registry.json")

    quantity = {
        "quantity_id": "quantity.energy",
        "dimension_id": "dim.energy",
        "unit_id": "unit.J",
        "value_raw": 123456789,
    }

    first = quantity_convert(
        quantity=quantity,
        target_unit_id="unit.J",
        unit_registry=unit_registry,
        dimension_registry=dimension_registry,
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64, "overflow_behavior": "refuse", "error_budget_max": 0}},
    )
    second = quantity_convert(
        quantity=quantity,
        target_unit_id="unit.J",
        unit_registry=unit_registry,
        dimension_registry=dimension_registry,
        numeric_policy={"fixed_point": {"fractional_bits": 24, "storage_bits": 64, "overflow_behavior": "refuse", "error_budget_max": 0}},
    )
    if first != second:
        return {"status": "fail", "message": "quantity_convert produced non-deterministic output"}
    if int(first.get("value_raw", -1)) != int(quantity["value_raw"]):
        return {"status": "fail", "message": "identity conversion changed value_raw"}
    return {"status": "pass", "message": "unit conversion determinism passed"}
