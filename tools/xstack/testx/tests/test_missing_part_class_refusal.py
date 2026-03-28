"""FAST test: missing part_class references refuse deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.missing_part_class_refusal"
TEST_TAGS = ["fast", "materials", "blueprint", "refusal"]


def _read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from materials.blueprint_engine import (
        REFUSAL_BLUEPRINT_MISSING_PART_CLASS,
        BlueprintCompileError,
        compile_blueprint_artifacts,
    )

    blueprint_registry = _read_json(os.path.join(repo_root, "data", "registries", "blueprint_registry.json"))
    part_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "part_class_registry.json"))
    connection_type_registry = _read_json(os.path.join(repo_root, "data", "registries", "connection_type_registry.json"))
    material_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "material_class_registry.json"))

    rows = list(((part_class_registry.get("record") or {}).get("part_classes") or []))
    filtered = [dict(row) for row in rows if isinstance(row, dict) and str(row.get("part_class_id", "")) != "partclass.pipe.generic"]
    broken = dict(part_class_registry)
    broken_record = dict(broken.get("record") or {})
    broken_record["part_classes"] = filtered
    broken["record"] = broken_record

    try:
        compile_blueprint_artifacts(
            repo_root=repo_root,
            blueprint_id="blueprint.space_elevator.template",
            parameter_values={"segment_count": 3},
            pack_lock_hash="c" * 64,
            blueprint_registry=blueprint_registry,
            part_class_registry=broken,
            connection_type_registry=connection_type_registry,
            material_class_registry=material_class_registry,
        )
    except BlueprintCompileError as exc:
        if str(exc.reason_code) != REFUSAL_BLUEPRINT_MISSING_PART_CLASS:
            return {"status": "fail", "message": "unexpected refusal code '{}'".format(str(exc.reason_code))}
        return {"status": "pass", "message": "missing part class refusal emitted deterministically"}

    return {"status": "fail", "message": "compile unexpectedly succeeded without required part class"}
