"""STRICT test: affordances are generated from ActionSurfaces."""

from __future__ import annotations

import sys


TEST_ID = "test_affordance_generation_from_surfaces"
TEST_TAGS = ["strict", "interaction", "action_surface"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.interaction.affordance_generator import build_affordance_list

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 5},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.beta",
                    "semantic_id": "assembly.test.beta",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.handle",
                            "allowed_process_ids": ["process.agent_move"],
                            "compatible_tool_tags": ["tool_tag.operating"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 0, "y": 0, "z": 0},
                                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                                "scale_permille": 300,
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
        "law_profile_id": "law.test.interaction",
        "allowed_processes": ["process.agent_move"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.agent_move": "entitlement.move",
        },
        "process_privilege_requirements": {},
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 100, "allow_hidden_state_access": False},
    }
    authority_context = {
        "authority_origin": "client",
        "law_profile_id": "law.test.interaction",
        "entitlements": ["entitlement.move"],
        "privilege_level": "operator",
    }
    interaction_action_registry = {
        "actions": [
            {
                "action_id": "interaction.move_agent",
                "process_id": "process.agent_move",
                "display_name": "Move",
                "target_kinds": ["agent"],
                "parameter_schema_id": "dominium.intent.agent_move",
                "preview_mode": "cheap",
                "required_lens_channels": ["ch.core.entities"],
                "default_ui_hints": {},
                "extensions": {},
            }
        ]
    }
    surface_type_registry = {
        "surface_types": [
            {
                "schema_version": "1.0.0",
                "surface_type_id": "surface.handle",
                "description": "Handle",
                "default_icon_tag": "glyph.surface.handle",
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
            }
        ]
    }
    out = build_affordance_list(
        perceived_model=perceived_model,
        target_semantic_id="assembly.test.beta",
        law_profile=law_profile,
        authority_context=authority_context,
        interaction_action_registry=interaction_action_registry,
        surface_type_registry=surface_type_registry,
        tool_tag_registry=tool_tag_registry,
        surface_visibility_policy_registry=visibility_registry,
        held_tool_tags=["tool_tag.operating"],
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(out.get("result", "")) != "complete":
        return {"status": "fail", "message": "affordance generation refused unexpectedly"}
    affordance_list = dict(out.get("affordance_list") or {})
    if not bool(dict(affordance_list.get("extensions") or {}).get("surface_driven", False)):
        return {"status": "fail", "message": "affordance list did not report surface_driven generation"}
    rows = list(affordance_list.get("affordances") or [])
    if len(rows) != 1:
        return {"status": "fail", "message": "expected one surface-derived affordance"}
    row = dict(rows[0])
    surface_id = str((dict(row.get("extensions") or {})).get("surface_id", "")).strip()
    if not surface_id:
        return {"status": "fail", "message": "surface-derived affordance missing surface_id extension"}
    if str(row.get("process_id", "")) != "process.agent_move":
        return {"status": "fail", "message": "surface-derived affordance process id mismatch"}
    return {"status": "pass", "message": "surface-driven affordance generation passed"}

