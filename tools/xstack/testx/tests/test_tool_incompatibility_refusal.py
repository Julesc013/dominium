"""STRICT test: incompatible tool tags produce deterministic disabled affordance reason."""

from __future__ import annotations

import sys


TEST_ID = "test_tool_incompatibility_refusal"
TEST_TAGS = ["strict", "interaction", "action_surface"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.affordance_generator import build_affordance_list

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 9},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.gamma",
                    "semantic_id": "assembly.test.gamma",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.fastener",
                            "allowed_process_ids": ["process.agent_move"],
                            "compatible_tool_tags": ["tool_tag.fastening"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 1, "y": 2, "z": 3},
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
        "law_profile_id": "law.test.interaction",
        "allowed_processes": ["process.agent_move"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {},
        "process_privilege_requirements": {},
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 100, "allow_hidden_state_access": False},
    }
    authority_context = {
        "authority_origin": "client",
        "law_profile_id": "law.test.interaction",
        "entitlements": [],
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
                "surface_type_id": "surface.fastener",
                "description": "Fastener",
                "default_icon_tag": "glyph.surface.fastener",
                "extensions": {},
            }
        ]
    }
    tool_tag_registry = {
        "tool_tags": [
            {"schema_version": "1.0.0", "tool_tag_id": "tool_tag.fastening", "description": "Fastening", "extensions": {}},
            {"schema_version": "1.0.0", "tool_tag_id": "tool_tag.operating", "description": "Operating", "extensions": {}},
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
        target_semantic_id="assembly.test.gamma",
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
    rows = list((dict(out.get("affordance_list") or {})).get("affordances") or [])
    if len(rows) != 1:
        return {"status": "fail", "message": "expected one affordance row"}
    extensions = dict((dict(rows[0])).get("extensions") or {})
    if bool(extensions.get("enabled", True)):
        return {"status": "fail", "message": "incompatible tool should produce disabled affordance"}
    if str(extensions.get("disabled_reason_code", "")) != "refusal.tool.incompatible":
        return {"status": "fail", "message": "disabled affordance missing refusal.tool.incompatible reason"}
    return {"status": "pass", "message": "tool incompatibility refusal surfaced deterministically"}

