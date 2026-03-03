"""STRICT test: produced artifacts must map to canonical META-INFO families."""

from __future__ import annotations

import json
import os


TEST_ID = "test_info_artifact_family_mapping"
TEST_TAGS = ["strict", "meta", "info_grammar"]


def _load_record(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return dict(payload.get("record") or payload)


def run(repo_root: str):
    templates = _load_record(repo_root, "data/registries/action_template_registry.json")
    mapping = _load_record(repo_root, "data/registries/info_artifact_family_registry.json")
    if not mapping:
        return {"status": "fail", "message": "info_artifact_family_registry missing or invalid"}

    families = set()
    for row in list(mapping.get("families") or []):
        if not isinstance(row, dict):
            continue
        family_id = str(row.get("info_family_id", "")).strip()
        if family_id:
            families.add(family_id)
    if not families:
        return {"status": "fail", "message": "no info families declared"}

    artifact_to_family = {}
    for row in list(mapping.get("artifact_type_mappings") or []):
        if not isinstance(row, dict):
            continue
        artifact_type_id = str(row.get("artifact_type_id", "")).strip()
        info_family_id = str(row.get("info_family_id", "")).strip()
        if artifact_type_id:
            artifact_to_family[artifact_type_id] = info_family_id

    missing = []
    unknown = []
    used_types = set()
    for row in list(templates.get("templates") or []):
        if not isinstance(row, dict):
            continue
        for token in list(row.get("produced_artifact_types") or []):
            artifact_type_id = str(token).strip()
            if not artifact_type_id:
                continue
            used_types.add(artifact_type_id)
            info_family_id = str(artifact_to_family.get(artifact_type_id, "")).strip()
            if not info_family_id:
                missing.append(artifact_type_id)
                continue
            if info_family_id not in families:
                unknown.append("{}->{}".format(artifact_type_id, info_family_id))

    if missing:
        return {
            "status": "fail",
            "message": "missing info family mapping for artifact types: {}".format(",".join(sorted(set(missing))[:10])),
        }
    if unknown:
        return {
            "status": "fail",
            "message": "artifact types mapped to unknown info family: {}".format(",".join(sorted(set(unknown))[:10])),
        }
    return {
        "status": "pass",
        "message": "all action-template artifacts map to canonical info families (types={})".format(len(used_types)),
    }

