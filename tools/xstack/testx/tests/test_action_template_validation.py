"""STRICT test: action family/template rows validate against CompatX schemas."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_action_template_validation"
TEST_TAGS = ["strict", "meta", "schema"]


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
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_instance

    families = _load_record(repo_root, "data/registries/action_family_registry.json")
    templates = _load_record(repo_root, "data/registries/action_template_registry.json")

    for index, row in enumerate(list(families.get("families") or [])):
        if not isinstance(row, dict):
            continue
        valid = validate_instance(
            repo_root=repo_root,
            schema_name="action_family",
            payload=dict(row),
            strict_top_level=True,
        )
        if not bool(valid.get("valid", False)):
            return {
                "status": "fail",
                "message": "action_family row {} failed schema validation".format(index),
            }

    for index, row in enumerate(list(templates.get("templates") or [])):
        if not isinstance(row, dict):
            continue
        valid = validate_instance(
            repo_root=repo_root,
            schema_name="action_template",
            payload=dict(row),
            strict_top_level=True,
        )
        if not bool(valid.get("valid", False)):
            return {
                "status": "fail",
                "message": "action_template row {} failed schema validation".format(index),
            }

    return {"status": "pass", "message": "action family/template rows are schema-valid"}

