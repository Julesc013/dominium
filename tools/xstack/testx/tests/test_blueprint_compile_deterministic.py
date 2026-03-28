"""FAST test: blueprint compilation is deterministic for identical inputs."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.blueprint_compile_deterministic"
TEST_TAGS = ["fast", "materials", "blueprint"]


def _read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from materials.blueprint_engine import compile_blueprint_artifacts

    blueprint_registry = _read_json(os.path.join(repo_root, "data", "registries", "blueprint_registry.json"))
    part_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "part_class_registry.json"))
    connection_type_registry = _read_json(os.path.join(repo_root, "data", "registries", "connection_type_registry.json"))
    material_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "material_class_registry.json"))

    first = compile_blueprint_artifacts(
        repo_root=repo_root,
        blueprint_id="blueprint.house.basic",
        parameter_values={},
        pack_lock_hash="a" * 64,
        blueprint_registry=blueprint_registry,
        part_class_registry=part_class_registry,
        connection_type_registry=connection_type_registry,
        material_class_registry=material_class_registry,
    )
    second = compile_blueprint_artifacts(
        repo_root=repo_root,
        blueprint_id="blueprint.house.basic",
        parameter_values={},
        pack_lock_hash="a" * 64,
        blueprint_registry=blueprint_registry,
        part_class_registry=part_class_registry,
        connection_type_registry=connection_type_registry,
        material_class_registry=material_class_registry,
    )

    if first != second:
        return {"status": "fail", "message": "blueprint compile artifacts diverged for identical inputs"}
    return {"status": "pass", "message": "blueprint compile deterministic"}
