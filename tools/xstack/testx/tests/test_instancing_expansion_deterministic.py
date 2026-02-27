"""FAST test: instancing expansion is deterministic under fixed parameters."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.instancing_expansion_deterministic"
TEST_TAGS = ["fast", "materials", "blueprint", "instancing"]


def _read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.materials.blueprint_engine import compile_blueprint_artifacts

    blueprint_registry = _read_json(os.path.join(repo_root, "data", "registries", "blueprint_registry.json"))
    part_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "part_class_registry.json"))
    connection_type_registry = _read_json(os.path.join(repo_root, "data", "registries", "connection_type_registry.json"))
    material_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "material_class_registry.json"))

    left = compile_blueprint_artifacts(
        repo_root=repo_root,
        blueprint_id="blueprint.space_elevator.template",
        parameter_values={"segment_count": 5},
        pack_lock_hash="b" * 64,
        blueprint_registry=blueprint_registry,
        part_class_registry=part_class_registry,
        connection_type_registry=connection_type_registry,
        material_class_registry=material_class_registry,
    )
    right = compile_blueprint_artifacts(
        repo_root=repo_root,
        blueprint_id="blueprint.space_elevator.template",
        parameter_values={"segment_count": 5},
        pack_lock_hash="b" * 64,
        blueprint_registry=blueprint_registry,
        part_class_registry=part_class_registry,
        connection_type_registry=connection_type_registry,
        material_class_registry=material_class_registry,
    )
    if left != right:
        return {"status": "fail", "message": "instancing expansion diverged for identical inputs"}

    nodes = dict((dict(left.get("compiled_ag_artifact") or {}).get("ag") or {}).get("nodes") or {})
    expected = {"node.se.cable.segment", "node.se.cable.segment.0001", "node.se.cable.segment.0002", "node.se.cable.segment.0003", "node.se.cable.segment.0004"}
    if not expected.issubset(set(nodes.keys())):
        return {"status": "fail", "message": "instancing expansion missing expected node ids"}
    return {"status": "pass", "message": "instancing expansion deterministic"}
