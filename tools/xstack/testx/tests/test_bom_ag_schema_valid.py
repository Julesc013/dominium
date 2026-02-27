"""FAST test: baseline blueprints provide schema-valid BOM and AG payloads."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.bom_ag_schema_valid"
TEST_TAGS = ["fast", "materials", "schema", "blueprint"]


def _read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.compatx.validator import validate_instance

    registry = _read_json(os.path.join(repo_root, "data", "registries", "blueprint_registry.json"))
    rows = list(((registry.get("record") or {}).get("blueprints") or []))
    if not rows:
        return {"status": "fail", "message": "blueprint registry has no entries"}

    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("blueprint_id", ""))):
        blueprint_path = str(row.get("blueprint_path", "")).strip()
        if not blueprint_path:
            return {"status": "fail", "message": "blueprint registry entry missing blueprint_path"}
        payload = _read_json(os.path.join(repo_root, blueprint_path.replace("/", os.sep)))
        blueprint_check = validate_instance(
            repo_root=repo_root,
            schema_name="blueprint",
            payload=payload,
            strict_top_level=True,
        )
        if not bool(blueprint_check.get("valid", False)):
            return {"status": "fail", "message": "blueprint schema invalid for '{}'".format(str(row.get("blueprint_id", "")))}
        bom = dict(payload.get("bom_ref") or {})
        ag = dict(payload.get("ag_ref") or {})
        bom_check = validate_instance(
            repo_root=repo_root,
            schema_name="bom",
            payload=bom,
            strict_top_level=True,
        )
        if not bool(bom_check.get("valid", False)):
            return {"status": "fail", "message": "bom schema invalid for '{}'".format(str(row.get("blueprint_id", "")))}
        ag_check = validate_instance(
            repo_root=repo_root,
            schema_name="assembly_graph",
            payload=ag,
            strict_top_level=True,
        )
        if not bool(ag_check.get("valid", False)):
            return {"status": "fail", "message": "assembly_graph schema invalid for '{}'".format(str(row.get("blueprint_id", "")))}

    return {"status": "pass", "message": "all baseline blueprint BOM/AG payloads are schema-valid"}
