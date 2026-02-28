"""STRICT test: task completion emits deterministic completion process intents."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_task_completion_triggers_process_intent"
TEST_TAGS = ["strict", "interaction", "task", "intent"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.task.completion",
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
    authority = authority_context(entitlements=["entitlement.tool.use", "session.boot"], privilege_level="operator")
    authority["subject_id"] = "agent.alpha"
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.complete.create",
            "process_id": "process.task_create",
            "inputs": {
                "task_type_id": "task.tighten_fastener",
                "process_id_to_execute": "process.fastener_turn",
                "actor_subject_id": "agent.alpha",
                "target_semantic_id": "assembly.complete.target",
                "surface_id": "surface.complete.target",
                "surface_type_id": "surface.fastener",
                "active_tool_tags": ["tool_tag.fastening"],
                "progress_units_total": 1024,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.task_create refused unexpectedly"}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.complete.tick",
            "process_id": "process.task_tick",
            "inputs": {"dt_ticks": 1, "max_cost_units": 128},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.task_tick refused unexpectedly"}
    completion_ids = list(ticked.get("completion_intent_ids") or [])
    if not completion_ids:
        return {"status": "fail", "message": "no completion intent ids emitted for completed task"}
    pending_intents = list(state.get("pending_task_completion_intents") or [])
    if not pending_intents:
        return {"status": "fail", "message": "pending task completion intents state collection is empty"}
    completion_intent = dict(pending_intents[0] or {})
    if str(completion_intent.get("process_id", "")).strip() != "process.fastener_turn":
        return {"status": "fail", "message": "completion process intent id mismatch"}
    task_id = str(created.get("task_id", "")).strip()
    if str((dict(completion_intent.get("inputs") or {})).get("task_id", "")).strip() != task_id:
        return {"status": "fail", "message": "completion intent missing deterministic task_id payload"}
    return {"status": "pass", "message": "task completion process handoff verified"}

