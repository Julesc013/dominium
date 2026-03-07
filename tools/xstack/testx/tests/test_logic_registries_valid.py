"""FAST test: LOGIC registries declare the constitutional baseline IDs."""

from __future__ import annotations

import json
import os


TEST_ID = "test_logic_registries_valid"
TEST_TAGS = ["fast", "logic", "registry"]


def _load(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid"


def _rows(payload: dict, key: str) -> list[dict]:
    rows = list((dict(payload.get("record") or {})).get(key) or payload.get(key) or [])
    return [dict(row) for row in rows if isinstance(row, dict)]


def run(repo_root: str):
    checks = (
        (
            "data/registries/signal_type_registry.json",
            "signal_types",
            "signal_type_id",
            {"signal.boolean", "signal.scalar", "signal.pulse", "signal.message", "signal.bus"},
        ),
        (
            "data/registries/carrier_type_registry.json",
            "carrier_types",
            "carrier_type_id",
            {
                "carrier.electrical",
                "carrier.pneumatic",
                "carrier.hydraulic",
                "carrier.mechanical",
                "carrier.optical",
                "carrier.sig",
            },
        ),
        (
            "data/registries/logic_policy_registry.json",
            "logic_policies",
            "policy_id",
            {"logic.default", "logic.rank_strict", "logic.lab_experimental"},
        ),
    )

    for rel_path, key, id_field, required_ids in checks:
        payload, err = _load(repo_root, rel_path)
        if err:
            return {"status": "fail", "message": "{} missing or invalid".format(rel_path)}
        if str(payload.get("schema_version", "")).strip() != "1.0.0":
            return {"status": "fail", "message": "{} must declare schema_version 1.0.0".format(rel_path)}
        rows = _rows(payload, key)
        if not rows:
            return {"status": "fail", "message": "{} has no {} rows".format(rel_path, key)}
        declared_ids = {str(row.get(id_field, "")).strip() for row in rows if str(row.get(id_field, "")).strip()}
        missing = sorted(required_ids - declared_ids)
        if missing:
            return {"status": "fail", "message": "{} missing required ids: {}".format(rel_path, ",".join(missing))}

    return {"status": "pass", "message": "LOGIC registries declare required baseline ids"}
