"""STRICT test: interaction execute path must route through control intent/resolution."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_interaction_flow_uses_control_plane"
TEST_TAGS = ["strict", "interaction", "control"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.interaction_dispatch import execute_affordance
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, law_profile, policy_context

    affordance_list = {
        "affordances": [
            {
                "affordance_id": "affordance.pose.enter",
                "action_id": "interaction.pose.enter",
                "process_id": "process.pose_enter",
                "target_semantic_id": "pose.slot.alpha",
                "extensions": {
                    "enabled": True,
                    "surface_id": "surface.pose.alpha",
                    "surface_type_id": "surface.handle",
                },
            }
        ]
    }
    state = base_state()
    law = law_profile()
    law["allowed_processes"] = sorted(set(list(law.get("allowed_processes") or []) + ["process.pose_enter"]))
    auth = authority_context(entitlements=["entitlement.agent.move"], privilege_level="operator")
    policy = policy_context()
    policy["control_action_registry"] = {
        "actions": [
            {
                "schema_version": "1.0.0",
                "action_id": "action.interaction.execute_process",
                "display_name": "Execute Process",
                "produces": {"process_id": "", "task_type_id": "", "plan_intent_type": ""},
                "required_entitlements": [],
                "required_capabilities": [],
                "target_kinds": ["none", "surface", "pose_slot", "mount_point", "machine", "structure", "graph"],
                "extensions": {"adapter": "legacy.process_id"},
            }
        ]
    }
    policy["control_policy_registry"] = {
        "policies": [
            {
                "schema_version": "1.0.0",
                "control_policy_id": "ctrl.policy.player.diegetic",
                "description": "Diegetic baseline policy.",
                "allowed_actions": ["action.interaction.*", "action.pose.*", "action.mount.*"],
                "allowed_abstraction_levels": ["AL0"],
                "allowed_view_policies": ["view.mode.first_person", "view.mode.third_person"],
                "allowed_fidelity_ranges": ["macro", "meso", "micro"],
                "downgrade_rules": {},
                "strictness": "C0",
                "extensions": {},
            }
        ]
    }
    policy["control_policy_id"] = "ctrl.policy.player.diegetic"

    result = execute_affordance(
        state=copy.deepcopy(state),
        affordance_list=copy.deepcopy(affordance_list),
        affordance_id="affordance.pose.enter",
        parameters={"pose_slot_id": "pose.slot.alpha"},
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
        peer_id="peer.test.interaction",
        deterministic_sequence_number=1,
        submission_tick=7,
        source_shard_id="shard.0",
        target_shard_id="shard.0",
        repo_root=repo_root,
    )
    if str(result.get("result", "")) not in {"complete", "refused"}:
        return {"status": "fail", "message": "interaction execute returned unexpected result state"}

    control_intent = dict(result.get("control_intent") or {})
    resolution = dict(result.get("resolution") or {})
    if not control_intent or not resolution:
        return {"status": "fail", "message": "interaction execute did not return control_intent/resolution"}
    if str(control_intent.get("requested_action_id", "")).strip() != "action.interaction.execute_process":
        return {"status": "fail", "message": "interaction did not use control action adapter"}
    if str((dict(resolution.get("extensions") or {})).get("control_action_id", "")).strip() != "action.interaction.execute_process":
        return {"status": "fail", "message": "resolution missing expected control action id"}
    return {"status": "pass", "message": "interaction flow routes through control plane"}
