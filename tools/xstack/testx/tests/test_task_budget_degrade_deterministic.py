"""STRICT test: task budget degradation order is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_task_budget_degrade_deterministic"
TEST_TAGS = ["strict", "interaction", "task", "budget", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.task.budget",
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


def _create_task(*, execute_intent, state: dict, law: dict, authority: dict, policy: dict, task_id: str):
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.budget.create.{}".format(task_id),
            "process_id": "process.task_create",
            "inputs": {
                "task_id": task_id,
                "task_type_id": "task.tighten_fastener",
                "process_id_to_execute": "process.fastener_turn",
                "actor_subject_id": "agent.alpha",
                "target_semantic_id": "assembly.task.{}".format(task_id),
                "surface_id": "surface.{}".format(task_id),
                "surface_type_id": "surface.fastener",
                "active_tool_tags": ["tool_tag.fastening"],
                "cost_units_per_tick": 10,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    law = _law_profile()
    authority = authority_context(entitlements=["entitlement.tool.use", "session.boot"], privilege_level="operator")
    authority["subject_id"] = "agent.alpha"
    policy = policy_context()

    state_one = base_state()
    state_two = copy.deepcopy(state_one)
    for state in (state_one, state_two):
        created_alpha = _create_task(
            execute_intent=execute_intent,
            state=state,
            law=law,
            authority=authority,
            policy=policy,
            task_id="task.alpha",
        )
        created_beta = _create_task(
            execute_intent=execute_intent,
            state=state,
            law=law,
            authority=authority,
            policy=policy,
            task_id="task.beta",
        )
        if str(created_alpha.get("result", "")) != "complete" or str(created_beta.get("result", "")) != "complete":
            return {"status": "fail", "message": "task setup refused unexpectedly for budget degrade test"}

    tick_one = execute_intent(
        state=state_one,
        intent={
            "intent_id": "intent.task.budget.tick.1",
            "process_id": "process.task_tick",
            "inputs": {"dt_ticks": 1, "max_cost_units": 10},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    tick_two = execute_intent(
        state=state_two,
        intent={
            "intent_id": "intent.task.budget.tick.1",
            "process_id": "process.task_tick",
            "inputs": {"dt_ticks": 1, "max_cost_units": 10},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(tick_one.get("result", "")) != "complete" or str(tick_two.get("result", "")) != "complete":
        return {"status": "fail", "message": "task_tick refused unexpectedly during budget degrade test"}
    degraded_one = list(tick_one.get("degraded_task_ids") or [])
    degraded_two = list(tick_two.get("degraded_task_ids") or [])
    if degraded_one != degraded_two:
        return {"status": "fail", "message": "degraded task id ordering diverged across equivalent runs"}
    if degraded_one != ["task.beta"]:
        return {"status": "fail", "message": "expected deterministic budget degrade to pause task.beta"}
    if list(state_one.get("tasks") or []) != list(state_two.get("tasks") or []):
        return {"status": "fail", "message": "task state diverged across deterministic budget degrade runs"}
    return {"status": "pass", "message": "task budget degradation determinism verified"}

