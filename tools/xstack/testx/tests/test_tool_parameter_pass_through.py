"""STRICT test: tool effect metadata is passed through interaction intent payloads."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_tool_parameter_pass_through"
TEST_TAGS = ["strict", "interaction", "tool", "intent"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.affordance_generator import build_affordance_list
    from src.client.interaction.interaction_dispatch import build_interaction_control_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, policy_context

    perceived_model = {
        "schema_version": "1.0.0",
        "viewpoint_id": "camera.main",
        "time_state": {"tick": 12},
        "channels": ["ch.core.entities"],
        "entities": {
            "entries": [
                {
                    "entity_id": "assembly.test.pass",
                    "semantic_id": "assembly.test.pass",
                    "entity_kind": "installed_structure",
                    "action_surfaces": [
                        {
                            "surface_type_id": "surface.handle",
                            "allowed_process_ids": ["process.tool_use_prepare"],
                            "compatible_tool_tags": ["tool_tag.fastening"],
                            "visibility_policy_id": "visibility.default",
                            "local_transform": {
                                "position_mm": {"x": 2, "y": 4, "z": 6},
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
            }
        ]
    }
    law_profile = {
        "law_profile_id": "law.test.tool.pass_through",
        "allowed_processes": ["process.tool_use_prepare"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {"process.tool_use_prepare": "entitlement.tool.use"},
        "process_privilege_requirements": {"process.tool_use_prepare": "operator"},
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }
    auth = authority_context(entitlements=["entitlement.tool.use"], privilege_level="operator")
    policy = policy_context()

    listed = build_affordance_list(
        perceived_model=copy.deepcopy(perceived_model),
        target_semantic_id="assembly.test.pass",
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
            "tool_tags": ["tool_tag.fastening", "tool_tag.operating"],
        },
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(listed.get("result", "")) != "complete":
        return {"status": "fail", "message": "affordance generation refused unexpectedly"}
    rows = list((dict(listed.get("affordance_list") or {})).get("affordances") or [])
    if len(rows) != 1:
        return {"status": "fail", "message": "expected one tool_use_prepare affordance"}
    affordance_row = dict(rows[0])
    if not bool((dict(affordance_row.get("extensions") or {})).get("enabled", False)):
        return {"status": "fail", "message": "tool_use_prepare affordance should be enabled"}

    intent_result = build_interaction_control_intent(
        affordance_row=copy.deepcopy(affordance_row),
        parameters={"target_id": "assembly.test.pass"},
        authority_context=copy.deepcopy(auth),
        policy_context=copy.deepcopy(policy),
        tick=12,
    )
    if str(intent_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "build_interaction_control_intent refused unexpectedly"}
    control_intent = dict(intent_result.get("control_intent") or {})
    inputs = dict(control_intent.get("parameters") or {})
    effect = dict(inputs.get("tool_effect") or {})
    if str(control_intent.get("requested_action_id", "")).strip() != "action.interaction.execute_process":
        return {"status": "fail", "message": "requested_action_id should route through control action adapter"}
    if str(inputs.get("tool_id", "")).strip() != "tool.instance.wrench.alpha":
        return {"status": "fail", "message": "tool_id missing from control intent parameters"}
    if str(inputs.get("tool_type_id", "")).strip() != "tool.wrench.basic":
        return {"status": "fail", "message": "tool_type_id missing from control intent parameters"}
    if str(inputs.get("tool_effect_model_id", "")).strip() != "effect.basic_fastening":
        return {"status": "fail", "message": "tool_effect_model_id missing from control intent parameters"}
    if int(effect.get("torque_limit", 0) or 0) != 5000:
        return {"status": "fail", "message": "tool_effect.torque_limit missing or incorrect"}
    if int(effect.get("efficiency_multiplier", 0) or 0) != 1000:
        return {"status": "fail", "message": "tool_effect.efficiency_multiplier missing or incorrect"}
    return {"status": "pass", "message": "tool parameter pass-through verified"}
