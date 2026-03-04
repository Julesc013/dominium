"""FAST test: META-CONTRACT contract registries expose required schema shape."""

from __future__ import annotations

import json
import os


TEST_ID = "test_registry_schema_valid"
TEST_TAGS = ["fast", "meta", "contracts", "schema", "registry"]


def _read_registry(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root"
    return payload, ""


def run(repo_root: str):
    checks = (
        (
            "data/registries/tier_contract_registry.json",
            "tier_contracts",
            ("contract_id", "subsystem_id", "supported_tiers", "deterministic_degradation_order", "cost_model_id"),
        ),
        (
            "data/registries/coupling_contract_registry.json",
            "coupling_contracts",
            ("contract_id", "coupling_class_id", "from_domain_id", "to_domain_id", "mechanism", "mechanism_id"),
        ),
        (
            "data/registries/explain_contract_registry.json",
            "explain_contracts",
            ("contract_id", "event_kind_id", "explain_artifact_type_id", "required_inputs", "remediation_hint_keys"),
        ),
    )

    for rel_path, collection_key, required_fields in checks:
        payload, err = _read_registry(repo_root, rel_path)
        if err:
            return {"status": "fail", "message": "{} {}".format(rel_path, err)}
        schema_version = str(payload.get("schema_version", "")).strip()
        if schema_version != "1.0.0":
            return {"status": "fail", "message": "{} unexpected schema_version '{}'".format(rel_path, schema_version)}
        record = dict(payload.get("record") or {})
        rows = list(record.get(collection_key) or payload.get(collection_key) or [])
        if not rows:
            return {"status": "fail", "message": "{} missing '{}' rows".format(rel_path, collection_key)}
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                return {"status": "fail", "message": "{} row {} is not an object".format(rel_path, index)}
            if str(row.get("schema_version", "")).strip() != "1.0.0":
                return {"status": "fail", "message": "{} row {} missing schema_version=1.0.0".format(rel_path, index)}
            for field in required_fields:
                value = row.get(field)
                if isinstance(value, list):
                    if not value:
                        return {"status": "fail", "message": "{} row {} missing non-empty field '{}'".format(rel_path, index, field)}
                    continue
                if not str(value or "").strip():
                    return {"status": "fail", "message": "{} row {} missing field '{}'".format(rel_path, index, field)}
    return {"status": "pass", "message": "contract registries expose required schema shape"}

