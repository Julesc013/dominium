"""STRICT test: META-CONTRACT schemas expose required canonical fields."""

from __future__ import annotations

import json
import os


TEST_ID = "test_contract_schema_valid"
TEST_TAGS = ["strict", "meta", "contracts", "schema"]


def _load_json(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root"
    return payload, ""


def _required_fields(schema_payload: dict):
    return set(str(token).strip() for token in list(schema_payload.get("required") or []) if str(token).strip())


def run(repo_root: str):
    checks = (
        (
            "schemas/tier_contract.schema.json",
            {"contract_id", "subsystem_id", "supported_tiers", "deterministic_degradation_order", "cost_model_id", "shard_safe"},
        ),
        (
            "schemas/coupling_contract.schema.json",
            {"contract_id", "coupling_class_id", "from_domain_id", "to_domain_id", "mechanism", "mechanism_id"},
        ),
        (
            "schemas/explain_contract.schema.json",
            {"contract_id", "event_kind_id", "explain_artifact_type_id", "required_inputs", "remediation_hint_keys"},
        ),
        (
            "schemas/explain_artifact.schema.json",
            {"explain_id", "cause_chain", "referenced_artifacts", "remediation_hints", "deterministic_fingerprint"},
        ),
    )

    for rel_path, required_fields in checks:
        payload, err = _load_json(repo_root, rel_path)
        if err:
            return {"status": "fail", "message": "{} {}".format(rel_path, err)}
        if str(payload.get("$schema", "")).strip() == "":
            return {"status": "fail", "message": "{} missing $schema".format(rel_path)}
        required = _required_fields(payload)
        missing = sorted(set(required_fields) - required)
        if missing:
            return {"status": "fail", "message": "{} missing required fields: {}".format(rel_path, ",".join(missing))}
        additional = payload.get("additionalProperties")
        if additional is not False:
            return {"status": "fail", "message": "{} must set additionalProperties=false".format(rel_path)}

    return {"status": "pass", "message": "contract schemas expose required canonical fields"}
