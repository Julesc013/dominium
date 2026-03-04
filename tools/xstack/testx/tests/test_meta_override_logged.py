"""STRICT test: process.meta_pose_override logs deterministic meta-law exception."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_meta_override_logged"
TEST_TAGS = ["strict", "pose", "meta_law", "ledger"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.pose.meta_override",
        "allowed_processes": ["process.meta_pose_override"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.meta_pose_override": "entitlement.control.admin",
        },
        "process_privilege_requirements": {
            "process.meta_pose_override": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": True},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context
    from tools.xstack.testx.tests.reality_rs2_ledger_testlib import build_policy_context

    state = base_state()
    state["agent_states"] = [
        {
            "agent_id": "agent.alpha",
            "body_id": "body.agent.alpha",
            "interior_volume_id": "volume.a",
            "extensions": {"interior_volume_id": "volume.a"},
        }
    ]
    state["pose_slots"] = [
        {
            "schema_version": "1.0.0",
            "pose_slot_id": "pose.slot.override.alpha",
            "parent_assembly_id": "assembly.vehicle.alpha",
            "interior_volume_id": "volume.b",
            "allowed_postures": ["posture.sit"],
            "allowed_body_tags": [],
            "requires_access_path": True,
            "control_binding_id": None,
            "exclusivity": "single",
            "current_occupant_id": None,
            "extensions": {"interior_graph_id": "interior.graph.override"},
        }
    ]
    state["interior_graphs"] = [
        {
            "schema_version": "1.0.0",
            "graph_id": "interior.graph.override",
            "volumes": ["volume.a", "volume.b"],
            "portals": ["portal.blocked"],
            "extensions": {},
        }
    ]
    state["interior_volumes"] = [{"volume_id": "volume.a"}, {"volume_id": "volume.b"}]
    state["interior_portals"] = [
        {
            "portal_id": "portal.blocked",
            "from_volume_id": "volume.a",
            "to_volume_id": "volume.b",
            "portal_type_id": "portal.door",
            "state_machine_id": "state.portal.blocked",
            "sealing_coefficient": 1000,
            "tags": [],
            "extensions": {},
        }
    ]
    state["interior_portal_state_machines"] = [{"machine_id": "state.portal.blocked", "state_id": "closed", "extensions": {}}]

    policy = policy_context()
    policy.update(build_policy_context("contracts.magic_relaxed", physics_profile_id="physics.test.pose.meta"))
    auth = authority_context(entitlements=["entitlement.control.admin"], privilege_level="operator")

    intent = {
        "intent_id": "intent.pose.meta.override.001",
        "process_id": "process.meta_pose_override",
        "inputs": {
            "action": "enter",
            "agent_id": "agent.alpha",
            "pose_slot_id": "pose.slot.override.alpha",
        },
    }
    out = execute_intent(
        state=state,
        intent=copy.deepcopy(intent),
        law_profile=_law_profile(),
        authority_context=auth,
        navigation_indices={},
        policy_context=policy,
    )
    if str(out.get("result", "")) != "complete":
        return {"status": "fail", "message": "meta pose override refused unexpectedly"}

    runtime_by_shard = dict(policy.get("conservation_runtime_by_shard") or {})
    shard_runtime = dict(runtime_by_shard.get("shard.0") or {})
    last_ledger = dict(shard_runtime.get("last_ledger") or {})
    entries = [dict(item) for item in list(last_ledger.get("entries") or []) if isinstance(item, dict)]
    exception_types = set(str(item.get("exception_type_id", "")).strip() for item in entries)
    if "exception.meta_law_override" not in exception_types:
        return {"status": "fail", "message": "meta override exception entry missing from conservation ledger"}
    return {"status": "pass", "message": "meta pose override logged deterministic exception entry"}

