"""FAST test: action_template schemas allow constitutive model declarations."""

from __future__ import annotations

import json
import os


TEST_ID = "test_action_template_schema_allows_constitutive_models"
TEST_TAGS = ["fast", "schema", "meta", "model"]


def _read_text(path: str) -> str:
    try:
        return open(path, "r", encoding="utf-8").read()
    except OSError:
        return ""


def run(repo_root: str):
    textual_rel = "schema/meta/action_template.schema"
    textual_abs = os.path.join(repo_root, textual_rel.replace("/", os.sep))
    textual = _read_text(textual_abs)
    if "uses_constitutive_model_ids" not in textual:
        return {"status": "fail", "message": "text schema missing uses_constitutive_model_ids"}

    json_rel = "schemas/action_template.schema.json"
    json_abs = os.path.join(repo_root, json_rel.replace("/", os.sep))
    try:
        payload = json.load(open(json_abs, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid action_template json schema"}

    props = dict((payload if isinstance(payload, dict) else {}).get("properties") or {})
    model_prop = dict(props.get("uses_constitutive_model_ids") or {})
    if model_prop.get("type") != "array":
        return {"status": "fail", "message": "json schema property uses_constitutive_model_ids missing array type"}

    return {"status": "pass", "message": "action_template schema supports constitutive model declarations"}
