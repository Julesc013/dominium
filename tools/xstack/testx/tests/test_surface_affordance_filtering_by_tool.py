"""STRICT test: ActionSurface affordances are filtered by active tool capabilities."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_surface_affordance_filtering_by_tool"
TEST_TAGS = ["strict", "interaction", "tool", "action_surface"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.interaction.affordance_generator import build_affordance_list
    from tools.xstack.testx.tests.interaction_testlib import authority_context, policy_context

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 11},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.toolfilter",
                    "semantic_id": "assembly.test.toolfilter",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.handle",
                            "allowed_process_ids": [
                                "process.tool_use_prepare",
                                "process.maintenance_perform",
                            ],
                            "compatible_tool_tags": ["tool_tag.fastening"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 0, "y": 0, "z": 0},
                                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                                "scale_permille": 1000,
                            },
                        }
                    ],
                }
            ]
        },
        "populations": {"entries": []},
        "control": {"orders": [], "institutions": []},
    }
    interaction_action_registry = {
        "actions": [
            {
                "action_id": "interaction.tool_use_prepare",
                "process_id": "process.tool_use_prepare",
                "display_name": "Prepare Tool",
                "target_kinds": ["installed_structure"],
                "parameter_schema_id": "dominium.intent.tool_prepare",
                "preview_mode": "cheap",
                "required_lens_channels": ["ch.core.entities"],
                "default_ui_hints": {},
                "extensions": {},
            },
            {
                "action_id": "interaction.maintenance",
                "process_id": "process.maintenance_perform",
                "display_name": "Maintenance",
                "target_kinds": ["installed_structure"],
                "parameter_schema_id": "dominium.intent.maintenance_perform",
                "preview_mode": "cheap",
                "required_lens_channels": ["ch.core.entities"],
                "default_ui_hints": {},
                "extensions": {},
            },
        ]
    }
    law_profile = {
        "law_profile_id": "law.test.tool.filter",
        "allowed_processes": [
            "process.tool_use_prepare",
            "process.maintenance_perform",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.tool_use_prepare": "entitlement.tool.use",
            "process.maintenance_perform": "entitlement.maintenance",
        },
        "process_privilege_requirements": {
            "process.tool_use_prepare": "operator",
            "process.maintenance_perform": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    auth = authority_context(
        entitlements=["entitlement.tool.use", "entitlement.maintenance"],
        privilege_level="operator",
    )
    policy = policy_context()

    result = build_affordance_list(
        perceived_model=copy.deepcopy(perceived_model),
        target_semantic_id="assembly.test.toolfilter",
        law_profile=copy.deepcopy(law_profile),
        authority_context=copy.deepcopy(auth),
        interaction_action_registry=copy.deepcopy(interaction_action_registry),
        surface_type_registry=copy.deepcopy(policy.get("surface_type_registry") or {}),
        tool_tag_registry=copy.deepcopy(policy.get("tool_tag_registry") or {}),
        tool_type_registry=copy.deepcopy(policy.get("tool_type_registry") or {}),
        tool_effect_model_registry=copy.deepcopy(policy.get("tool_effect_model_registry") or {}),
        surface_visibility_policy_registry=copy.deepcopy(policy.get("surface_visibility_policy_registry") or {}),
        active_tool={
            "tool_id": "tool.instance.wrench.alpha",
            "tool_type_id": "tool.wrench.basic",
            "effect_model_id": "effect.basic_fastening",
            "tool_tags": ["tool_tag.fastening"],
        },
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "build_affordance_list refused unexpectedly"}
    rows = list((dict(result.get("affordance_list") or {})).get("affordances") or [])
    if len(rows) != 2:
        return {"status": "fail", "message": "expected 2 affordances from one surface and two processes"}
    rows_by_process = dict((str((dict(row)).get("process_id", "")).strip(), dict(row)) for row in rows if isinstance(row, dict))
    prepare_row = dict(rows_by_process.get("process.tool_use_prepare") or {})
    maintenance_row = dict(rows_by_process.get("process.maintenance_perform") or {})
    if not prepare_row or not maintenance_row:
        return {"status": "fail", "message": "expected tool_use_prepare and maintenance affordances"}
    if not bool((dict(prepare_row.get("extensions") or {})).get("enabled", False)):
        return {"status": "fail", "message": "tool-compatible process should remain enabled"}
    maintenance_ext = dict(maintenance_row.get("extensions") or {})
    if bool(maintenance_ext.get("enabled", True)):
        return {"status": "fail", "message": "tool-disallowed process should be disabled deterministically"}
    if str(maintenance_ext.get("disabled_reason_code", "")).strip() != "refusal.tool.incompatible":
        return {"status": "fail", "message": "tool-disallowed process missing refusal.tool.incompatible reason"}
    return {"status": "pass", "message": "ActionSurface affordance tool filtering verified"}
