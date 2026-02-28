"""STRICT test: task pause/resume transitions are deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_task_pause_resume_deterministic"
TEST_TAGS = ["strict", "interaction", "task", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.task.pause_resume",
        "allowed_processes": [
            "process.task_create",
            "process.task_pause",
            "process.task_resume",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.task_create": "entitlement.tool.use",
            "process.task_pause": "entitlement.tool.use",
            "process.task_resume": "entitlement.tool.use",
        },
        "process_privilege_requirements": {
            "process.task_create": "operator",
            "process.task_pause": "operator",
            "process.task_resume": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def _run_sequence(*, execute_intent, state: dict, law: dict, authority: dict, policy: dict):
    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.pause_resume.create",
            "process_id": "process.task_create",
            "inputs": {
                "task_type_id": "task.tighten_fastener",
                "process_id_to_execute": "process.fastener_turn",
                "actor_subject_id": "agent.alpha",
                "target_semantic_id": "assembly.pause_resume",
                "surface_id": "surface.pause_resume",
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
        return created
    task_id = str(created.get("task_id", ""))
    paused = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.pause_resume.pause",
            "process_id": "process.task_pause",
            "inputs": {"task_id": task_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(paused.get("result", "")) != "complete":
        return paused
    resumed = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.pause_resume.resume",
            "process_id": "process.task_resume",
            "inputs": {"task_id": task_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return resumed


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    law = _law_profile()
    authority = authority_context(entitlements=["entitlement.tool.use"], privilege_level="operator")
    authority["subject_id"] = "agent.alpha"
    policy = policy_context()

    state_one = base_state()
    state_two = copy.deepcopy(state_one)
    out_one = _run_sequence(
        execute_intent=execute_intent,
        state=state_one,
        law=law,
        authority=authority,
        policy=policy,
    )
    out_two = _run_sequence(
        execute_intent=execute_intent,
        state=state_two,
        law=law,
        authority=authority,
        policy=policy,
    )
    if str(out_one.get("result", "")) != "complete" or str(out_two.get("result", "")) != "complete":
        return {"status": "fail", "message": "pause/resume sequence refused unexpectedly"}
    if list(state_one.get("tasks") or []) != list(state_two.get("tasks") or []):
        return {"status": "fail", "message": "task rows diverged across deterministic pause/resume sequence"}
    task_rows = list(state_one.get("tasks") or [])
    if not task_rows:
        return {"status": "fail", "message": "task missing after pause/resume sequence"}
    status = str((dict(task_rows[0])).get("status", ""))
    if status != "running":
        return {"status": "fail", "message": "task status expected running after resume transition"}
    return {"status": "pass", "message": "task pause/resume determinism verified"}

