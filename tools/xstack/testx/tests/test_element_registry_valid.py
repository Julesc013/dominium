"""FAST test: element registry baseline validates for MAT-2."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.element_registry_valid"
TEST_TAGS = ["fast", "materials", "taxonomy"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.composition_engine import validate_element_registry

    path = os.path.join(repo_root, "data", "registries", "element_registry.json")
    payload = json.load(open(path, "r", encoding="utf-8"))
    record = dict(payload.get("record") or {})
    rows = validate_element_registry(record)
    required = {"element.H", "element.O", "element.C", "element.Fe", "element.Si"}
    if not required.issubset(set(rows.keys())):
        return {"status": "fail", "message": "element registry is missing baseline entries"}
    return {"status": "pass", "message": "element registry baseline validated"}
