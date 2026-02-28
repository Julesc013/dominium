"""STRICT test: task progress tick is deterministic across equivalent runs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_task_progress_deterministic"
TEST_TAGS = ["strict", "interaction", "task", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.task.progress",
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


def _create_and_tick(*, execute_intent, state: dict, law: dict, authority: dict, policy: dict):
    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.progress.create",
            "process_id": "process.task_create",
            "inputs": {
                "task_type_id": "task.tighten_fastener",
                "process_id_to_execute": "process.fastener_turn",
                "actor_subject_id": "agent.alpha",
                "target_semantic_id": "assembly.target.alpha",
                "surface_id": "surface.alpha",
                "surface_type_id": "surface.fastener",
                "active_tool_tags": ["tool_tag.fastening"],
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return created, {}
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.progress.tick",
            "process_id": "process.task_tick",
            "inputs": {"dt_ticks": 1, "max_cost_units": 64},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return created, ticked


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
    created_one, ticked_one = _create_and_tick(
        execute_intent=execute_intent,
        state=state_one,
        law=law,
        authority=authority,
        policy=policy,
    )
    created_two, ticked_two = _create_and_tick(
        execute_intent=execute_intent,
        state=state_two,
        law=law,
        authority=authority,
        policy=policy,
    )
    if str(created_one.get("result", "")) != "complete" or str(created_two.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.task_create refused unexpectedly"}
    if str(ticked_one.get("result", "")) != "complete" or str(ticked_two.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.task_tick refused unexpectedly"}
    if list(state_one.get("tasks") or []) != list(state_two.get("tasks") or []):
        return {"status": "fail", "message": "task rows diverged across equivalent deterministic runs"}
    if str(ticked_one.get("state_hash_anchor", "")) != str(ticked_two.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "task tick state hash anchor diverged across equivalent runs"}
    task_rows = list(state_one.get("tasks") or [])
    if not task_rows:
        return {"status": "fail", "message": "task rows missing after deterministic task tick"}
    progress_done = int((dict(task_rows[0])).get("progress_units_done", 0) or 0)
    if progress_done <= 0:
        return {"status": "fail", "message": "task progress did not advance under deterministic tick"}
    return {"status": "pass", "message": "task progress determinism verified"}

