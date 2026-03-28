"""STRICT test: ActionSurface visibility policy filters hidden surfaces."""

from __future__ import annotations

import sys


TEST_ID = "test_surface_visibility_policy"
TEST_TAGS = ["strict", "interaction", "action_surface", "epistemic"]


def _resolve(repo_root: str, *, entitlements: list[str]):
    from interaction import resolve_action_surfaces

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 3},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.delta",
                    "semantic_id": "assembly.test.delta",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.panel",
                            "allowed_process_ids": ["process.inspect_generate_snapshot"],
                            "compatible_tool_tags": ["tool_tag.operating"],
                            "visibility_policy_id": "visibility.lab_only",
                            "local_transform": {
                                "position_mm": {"x": 0, "y": 0, "z": 0},
                                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                                "scale_permille": 250,
                            },
                        }
                    ],
                }
            ]
        },
        "populations": {"entries": []},
        "control": {"orders": [], "institutions": []},
    }
    law_profile = {
        "allowed_processes": ["process.inspect_generate_snapshot"],
        "process_entitlement_requirements": {},
    }
    authority_context = {
        "entitlements": sorted(set(str(item).strip() for item in entitlements if str(item).strip())),
    }
    surface_type_registry = {
        "surface_types": [
            {
                "schema_version": "1.0.0",
                "surface_type_id": "surface.panel",
                "description": "Panel",
                "default_icon_tag": "glyph.surface.panel",
                "extensions": {},
            }
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
            },
            {
                "schema_version": "1.0.0",
                "policy_id": "visibility.lab_only",
                "requires_entitlement": "entitlement.debug_view",
                "requires_lens_channel": None,
                "extensions": {},
            },
        ]
    }
    return resolve_action_surfaces(
        perceived_model=perceived_model,
        target_semantic_id="assembly.test.delta",
        law_profile=law_profile,
        authority_context=authority_context,
        surface_type_registry=surface_type_registry,
        tool_tag_registry=tool_tag_registry,
        surface_visibility_policy_registry=visibility_registry,
        held_tool_tags=["tool_tag.operating"],
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    hidden = _resolve(repo_root, entitlements=[])
    if str(hidden.get("result", "")) != "complete":
        return {"status": "fail", "message": "surface resolution refused unexpectedly"}
    if int(hidden.get("surface_count", 0)) != 0:
        return {"status": "fail", "message": "lab-only policy should hide surface without entitlement"}

    visible = _resolve(repo_root, entitlements=["entitlement.debug_view"])
    if int(visible.get("surface_count", 0)) != 1:
        return {"status": "fail", "message": "surface should be visible with required entitlement"}
    return {"status": "pass", "message": "visibility policy gating passed"}

