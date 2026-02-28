"""STRICT test: server-authoritative task execution enforces entitlement-gated validation."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_mp_task_authoritative_validation"
TEST_TAGS = ["strict", "interaction", "task", "multiplayer", "authoritative"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.task.mp_authoritative",
        "allowed_processes": ["process.task_create", "process.task_tick"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.task_create": "entitlement.tool.use",
            "process.task_tick": "session.boot",
        },
        "process_privilege_requirements": {
            "process.task_create": "operator",
            "process.task_tick": "observer",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state = base_state()
    law = _law_profile()
    operator_auth = authority_context(entitlements=["entitlement.tool.use"], privilege_level="operator")
    operator_auth["subject_id"] = "agent.alpha"
    policy = policy_context()
    policy["net_policy_id"] = "net.policy.server_authoritative.v1"

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.mp.create",
            "process_id": "process.task_create",
            "inputs": {
                "task_type_id": "task.tighten_fastener",
                "process_id_to_execute": "process.fastener_turn",
                "actor_subject_id": "agent.alpha",
                "target_semantic_id": "assembly.mp.target",
                "surface_id": "surface.mp.target",
                "surface_type_id": "surface.fastener",
                "active_tool_tags": ["tool_tag.fastening"],
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(operator_auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "authoritative task_create refused unexpectedly"}

    # Simulate unauthorized client trying to drive task progression directly.
    unauthorized_tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.mp.tick.unauthorized",
            "process_id": "process.task_tick",
            "inputs": {"dt_ticks": 1, "max_cost_units": 32},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(operator_auth),  # does not include session.boot
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(unauthorized_tick.get("result", "")) != "refused":
        return {"status": "fail", "message": "unauthorized authoritative task_tick should be refused"}
    reason_code = str((dict(unauthorized_tick.get("refusal") or {})).get("reason_code", "")).strip()
    if reason_code != "refusal.task.forbidden_by_law":
        return {"status": "fail", "message": "unexpected refusal code for unauthorized task_tick"}
    return {"status": "pass", "message": "authoritative task entitlement validation verified"}

