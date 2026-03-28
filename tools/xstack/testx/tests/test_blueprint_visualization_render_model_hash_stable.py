"""FAST test: blueprint ghost visualization has stable RenderModel hash."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.materials.blueprint_visualization_render_model_hash_stable"
TEST_TAGS = ["fast", "materials", "blueprint", "render"]


def _read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.render import build_render_model
    from materials.blueprint_engine import build_blueprint_ghost_overlay, compile_blueprint_artifacts

    blueprint_registry = _read_json(os.path.join(repo_root, "data", "registries", "blueprint_registry.json"))
    part_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "part_class_registry.json"))
    connection_type_registry = _read_json(os.path.join(repo_root, "data", "registries", "connection_type_registry.json"))
    material_class_registry = _read_json(os.path.join(repo_root, "data", "registries", "material_class_registry.json"))

    compiled = compile_blueprint_artifacts(
        repo_root=repo_root,
        blueprint_id="blueprint.house.basic",
        parameter_values={},
        pack_lock_hash="d" * 64,
        blueprint_registry=blueprint_registry,
        part_class_registry=part_class_registry,
        connection_type_registry=connection_type_registry,
        material_class_registry=material_class_registry,
    )
    ghost = build_blueprint_ghost_overlay(
        compiled_ag_artifact=dict(compiled.get("compiled_ag_artifact") or {}),
        blueprint_id="blueprint.house.basic",
        include_labels=True,
    )
    perceived = {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.blueprint",
        "time_state": {"tick": 42},
        "camera_viewpoint": {"view_mode_id": "view.follow.spectator"},
        "interaction": {
            "inspection_overlays": {
                "renderables": list(ghost.get("renderables") or []),
                "materials": list(ghost.get("materials") or []),
            }
        },
        "entities": {"entries": []},
    }
    first = build_render_model(
        perceived_model=perceived,
        registry_payloads={},
        pack_lock_hash="d" * 64,
        physics_profile_id="physics.null",
    )
    second = build_render_model(
        perceived_model=perceived,
        registry_payloads={},
        pack_lock_hash="d" * 64,
        physics_profile_id="physics.null",
    )
    first_hash = str(first.get("render_model_hash", ""))
    second_hash = str(second.get("render_model_hash", ""))
    if not first_hash or first_hash != second_hash:
        return {"status": "fail", "message": "blueprint visualization render hash is unstable"}
    return {"status": "pass", "message": "blueprint visualization render hash stable"}
