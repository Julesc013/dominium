"""STRICT test: ActionSurface resolution is deterministic and stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_surface_resolution_deterministic"
TEST_TAGS = ["strict", "interaction", "action_surface", "determinism"]


def _perceived_model() -> dict:
    return {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 11},
        "channels": ["ch.core.entities", "ch.diegetic.radio_text"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.alpha",
                    "semantic_id": "assembly.test.alpha",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.port",
                            "allowed_process_ids": [
                                "process.inspect_generate_snapshot",
                            ],
                            "compatible_tool_tags": ["tool_tag.operating"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 200, "y": 10, "z": 0},
                                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                                "scale_permille": 600,
                            },
                        },
                        {
                            "surface_type_id": "surface.handle",
                            "allowed_process_ids": [
                                "process.agent_move",
                            ],
                            "compatible_tool_tags": ["tool_tag.operating"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 50, "y": 5, "z": 0},
                                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                                "scale_permille": 400,
                            },
                        },
                    ],
                }
            ]
        },
        "populations": {"entries": []},
        "control": {"orders": [], "institutions": []},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.interaction import resolve_action_surfaces

    perceived = _perceived_model()
    law_profile = {
        "allowed_processes": ["process.inspect_generate_snapshot", "process.agent_move"],
        "process_entitlement_requirements": {},
    }
    authority = {"entitlements": []}
    surface_type_registry = {
        "surface_types": [
            {
                "schema_version": "1.0.0",
                "surface_type_id": "surface.handle",
                "description": "Handle",
                "default_icon_tag": "glyph.surface.handle",
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "surface_type_id": "surface.port",
                "description": "Port",
                "default_icon_tag": "glyph.surface.port",
                "extensions": {},
            },
        ]
    }
    tool_tag_registry = {
        "tool_tags": [
            {"schema_version": "1.0.0", "tool_tag_id": "tool_tag.operating", "description": "Operating", "extensions": {}}
        ]
    }
    visibility_registry = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "policy_id": "visibility.default",
                "requires_entitlement": None,
                "requires_lens_channel": None,
                "extensions": {},
            }
        ]
    }

    first = resolve_action_surfaces(
        perceived_model=copy.deepcopy(perceived),
        target_semantic_id="assembly.test.alpha",
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(authority),
        surface_type_registry=copy.deepcopy(surface_type_registry),
        tool_tag_registry=copy.deepcopy(tool_tag_registry),
        surface_visibility_policy_registry=copy.deepcopy(visibility_registry),
        held_tool_tags=["tool_tag.operating"],
    )
    second = resolve_action_surfaces(
        perceived_model=copy.deepcopy(perceived),
        target_semantic_id="assembly.test.alpha",
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(authority),
        surface_type_registry=copy.deepcopy(surface_type_registry),
        tool_tag_registry=copy.deepcopy(tool_tag_registry),
        surface_visibility_policy_registry=copy.deepcopy(visibility_registry),
        held_tool_tags=["tool_tag.operating"],
    )
    if first != second:
        return {"status": "fail", "message": "surface resolution is not deterministic across equivalent runs"}
    rows = list((dict(first)).get("surfaces") or [])
    if not rows:
        return {"status": "fail", "message": "surface resolution returned no rows for valid metadata"}
    ids = [str((dict(row)).get("surface_id", "")) for row in rows]
    if ids != sorted(ids):
        return {"status": "fail", "message": "resolved surface rows are not sorted by surface_id"}
    if len(set(ids)) != len(ids):
        return {"status": "fail", "message": "resolved surface ids are not unique"}
    return {"status": "pass", "message": "ActionSurface resolution deterministic"}

