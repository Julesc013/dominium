"""FAST test: META-INSTR0 instrumentation surfaces expose required schema fields."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_instrumentation_surface_schema_valid"
TEST_TAGS = ["fast", "meta", "instrumentation", "schema"]


def _read(path: str) -> str:
    return open(path, "r", encoding="utf-8").read()


def _load_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.meta.instrumentation import normalize_instrumentation_surface_rows

    schema_checks = (
        (
            "schema/meta/instrumentation_surface.schema",
            ("owner_kind", "owner_id", "control_points", "measurement_points", "forensics_points", "deterministic_fingerprint"),
        ),
        (
            "schema/meta/control_point.schema",
            ("control_point_id", "action_template_id", "required_access_policy_id", "safety_interlock_refs"),
        ),
        (
            "schema/meta/measurement_point.schema",
            ("measurement_point_id", "quantity_id", "instrument_type_id", "measurement_model_id", "redaction_policy_id"),
        ),
        (
            "schema/meta/forensics_point.schema",
            ("forensics_point_id", "explain_contract_id", "redaction_policy_id"),
        ),
    )
    for rel_path, required_tokens in schema_checks:
        abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
        if not os.path.isfile(abs_path):
            return {"status": "fail", "message": "missing schema file {}".format(rel_path)}
        text = _read(abs_path)
        if "schema_version: 1.0.0" not in text:
            return {"status": "fail", "message": "{} missing schema_version: 1.0.0".format(rel_path)}
        for token in required_tokens:
            if str(token) not in text:
                return {"status": "fail", "message": "{} missing required token '{}'".format(rel_path, token)}

    registry_path = os.path.join(repo_root, "data/registries/instrumentation_surface_registry.json".replace("/", os.sep))
    payload = _load_json(registry_path)
    rows = list((dict(payload.get("record") or {})).get("instrumentation_surfaces") or [])
    if not rows:
        return {"status": "fail", "message": "instrumentation_surface_registry missing instrumentation_surfaces rows"}
    normalized = normalize_instrumentation_surface_rows(rows)
    if len(normalized) < 6:
        return {"status": "fail", "message": "expected >=6 normalized instrumentation surfaces, found {}".format(len(normalized))}
    for row in normalized:
        owner_kind = str(row.get("owner_kind", "")).strip()
        owner_id = str(row.get("owner_id", "")).strip()
        if not owner_kind or not owner_id:
            return {"status": "fail", "message": "normalized row missing owner key"}
        for field_key in ("control_points", "measurement_points", "forensics_points"):
            values = row.get(field_key)
            if not isinstance(values, list) or not values:
                return {"status": "fail", "message": "owner {}::{} missing non-empty {}".format(owner_kind, owner_id, field_key)}
        if not str(row.get("deterministic_fingerprint", "")).strip():
            return {"status": "fail", "message": "owner {}::{} missing deterministic_fingerprint".format(owner_kind, owner_id)}
    return {"status": "pass", "message": "instrumentation surfaces satisfy schema baseline fields"}

