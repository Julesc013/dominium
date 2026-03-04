"""FAST test: every registered quantity has a declared tolerance policy row."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_quantities_have_tolerance"
TEST_TAGS = ["fast", "meta", "numeric", "registry"]


def _read_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    return json.load(open(abs_path, "r", encoding="utf-8"))


def run(repo_root: str):
    try:
        quantity_payload = _read_json(repo_root, "data/registries/quantity_registry.json")
        tolerance_payload = _read_json(repo_root, "data/registries/quantity_tolerance_registry.json")
    except (OSError, ValueError):
        return {"status": "fail", "message": "quantity/tolerance registry payloads missing or invalid"}

    quantity_ids = sorted(
        str(row.get("quantity_id", "")).strip()
        for row in list((dict(quantity_payload.get("record") or {})).get("quantities") or [])
        if isinstance(row, dict) and str(row.get("quantity_id", "")).strip()
    )
    tolerance_rows = list((dict(tolerance_payload.get("record") or {})).get("quantity_tolerances") or [])
    if not tolerance_rows:
        tolerance_rows = list(tolerance_payload.get("quantity_tolerances") or [])
    tolerance_ids = set(
        str(row.get("quantity_id", "")).strip()
        for row in tolerance_rows
        if isinstance(row, dict) and str(row.get("quantity_id", "")).strip()
    )

    missing = sorted(quantity_id for quantity_id in quantity_ids if quantity_id not in tolerance_ids)
    if missing:
        return {
            "status": "fail",
            "message": "missing quantity tolerance declarations (count={}): {}".format(len(missing), ",".join(missing[:8])),
        }
    return {"status": "pass", "message": "all registered quantities have tolerance policy rows"}
