"""FAST test: deprecation registry shape is deterministic and internally consistent."""

from __future__ import annotations

import json
import os


TEST_ID = "test_deprecation_registry_consistency"
TEST_TAGS = ["fast", "schema", "architecture", "deprecation"]


def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def run(repo_root: str):
    registry_rel = "data/registries/deprecation_registry.json"
    schema_rel = "schemas/deprecation_registry.schema.json"
    registry_path = os.path.join(repo_root, registry_rel.replace("/", os.sep))
    schema_path = os.path.join(repo_root, schema_rel.replace("/", os.sep))
    if not os.path.isfile(registry_path):
        return {"status": "fail", "message": "{} missing".format(registry_rel)}
    if not os.path.isfile(schema_path):
        return {"status": "fail", "message": "{} missing".format(schema_rel)}

    try:
        registry = _read_json(registry_path)
        schema = _read_json(schema_path)
    except Exception as exc:
        return {"status": "fail", "message": "failed to parse deprecation artifacts: {}".format(exc)}

    if str(registry.get("schema_id", "")).strip() != "dominium.registry.deprecation":
        return {"status": "fail", "message": "deprecation registry schema_id mismatch"}
    if str(registry.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "deprecation registry schema_version mismatch"}
    if str(schema.get("version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "deprecation registry schema version mismatch"}

    record = dict(registry.get("record") or {})
    rows = record.get("deprecations")
    if not isinstance(rows, list):
        return {"status": "fail", "message": "record.deprecations must be a list"}
    valid_status = {"active", "removed"}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            return {"status": "fail", "message": "deprecations[{}] must be object".format(index)}
        for key in (
            "schema_version",
            "deprecated_id",
            "replacement_id",
            "reason",
            "removal_target_version",
            "status",
            "extensions",
        ):
            if key not in row:
                return {"status": "fail", "message": "deprecations[{}] missing {}".format(index, key)}
        if str(row.get("schema_version", "")).strip() != "1.0.0":
            return {"status": "fail", "message": "deprecations[{}] schema_version mismatch".format(index)}
        if str(row.get("status", "")).strip() not in valid_status:
            return {"status": "fail", "message": "deprecations[{}] invalid status".format(index)}
        if not isinstance(row.get("extensions"), dict):
            return {"status": "fail", "message": "deprecations[{}] extensions must be object".format(index)}

    return {"status": "pass", "message": "Deprecation registry consistency verified"}
