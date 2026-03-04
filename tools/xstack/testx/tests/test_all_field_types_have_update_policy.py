"""FAST test: every registered field type must declare a valid update policy."""

from __future__ import annotations

import json
import os


TEST_ID = "test_all_field_types_have_update_policy"
TEST_TAGS = ["fast", "fields", "registry", "policy"]


def _read_json(path: str):
    try:
        return json.load(open(path, "r", encoding="utf-8")), ""
    except (OSError, ValueError) as exc:
        return {}, str(exc)


def run(repo_root: str):
    field_registry_path = os.path.join(repo_root, "data", "registries", "field_type_registry.json")
    policy_registry_path = os.path.join(repo_root, "data", "registries", "field_update_policy_registry.json")

    field_registry, field_error = _read_json(field_registry_path)
    if field_error:
        return {"status": "fail", "message": "invalid field type registry: {}".format(field_error)}
    policy_registry, policy_error = _read_json(policy_registry_path)
    if policy_error:
        return {"status": "fail", "message": "invalid field update policy registry: {}".format(policy_error)}

    field_rows = list((dict(field_registry.get("record") or {})).get("field_types") or [])
    policy_rows = list((dict(policy_registry.get("record") or {})).get("policies") or [])
    registered_policy_ids = set()
    for row in policy_rows:
        if not isinstance(row, dict):
            continue
        token = str(row.get("policy_id", "")).strip() or str(row.get("update_policy_id", "")).strip()
        if token:
            registered_policy_ids.add(token)

    missing = []
    unknown = []
    for row in field_rows:
        if not isinstance(row, dict):
            continue
        field_id = str(row.get("field_id", "")).strip() or str(row.get("field_type_id", "")).strip()
        policy_id = str(row.get("update_policy_id", "")).strip()
        if not field_id:
            continue
        if not policy_id:
            missing.append(field_id)
            continue
        if policy_id not in registered_policy_ids:
            unknown.append("{}->{}".format(field_id, policy_id))

    if missing or unknown:
        parts = []
        if missing:
            parts.append("missing update_policy_id: {}".format(",".join(sorted(missing)[:8])))
        if unknown:
            parts.append("unknown update_policy_id: {}".format(",".join(sorted(unknown)[:8])))
        return {"status": "fail", "message": "; ".join(parts)}

    return {"status": "pass", "message": "all field types declare valid update policies"}

