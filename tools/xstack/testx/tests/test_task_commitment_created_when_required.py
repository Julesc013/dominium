"""STRICT test: task creation emits linked commitment under C1 strictness."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_task_commitment_created_when_required"
TEST_TAGS = ["strict", "interaction", "task", "commitment", "causality"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.task.commitment",
        "allowed_processes": ["process.task_create"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.task_create": "entitlement.tool.use",
        },
        "process_privilege_requirements": {
            "process.task_create": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def _strictness_registry() -> dict:
    return {
        "strictness_levels": [
            {
                "schema_version": "1.0.0",
                "causality_strictness_id": "causality.C0",
                "level": "C0",
                "description": "events required only",
                "major_change_requires_commitment": False,
                "event_required_for_macro_change": True,
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "causality_strictness_id": "causality.C1",
                "level": "C1",
                "description": "major changes require commitments",
                "major_change_requires_commitment": True,
                "event_required_for_macro_change": True,
                "extensions": {},
            },
        ]
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state = base_state()
    law = _law_profile()
    authority = authority_context(entitlements=["entitlement.tool.use"], privilege_level="operator")
    authority["subject_id"] = "agent.alpha"
    policy = policy_context()
    policy["causality_strictness_id"] = "causality.C1"
    policy["causality_strictness_registry"] = _strictness_registry()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.task.commitment.create",
            "process_id": "process.task_create",
            "inputs": {
                "task_type_id": "task.tighten_fastener",
                "process_id_to_execute": "process.fastener_turn",
                "actor_subject_id": "agent.alpha",
                "target_semantic_id": "assembly.commitment.target",
                "surface_id": "surface.commitment.target",
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
        return {"status": "fail", "message": "process.task_create refused unexpectedly under C1 strictness"}
    linked_commitment_id = str(created.get("linked_commitment_id", "")).strip()
    if not linked_commitment_id:
        return {"status": "fail", "message": "task creation did not emit linked commitment under C1 strictness"}
    commitment_rows = [
        dict(row)
        for row in list(state.get("material_commitments") or [])
        if isinstance(row, dict) and str(row.get("commitment_id", "")).strip() == linked_commitment_id
    ]
    if not commitment_rows:
        return {"status": "fail", "message": "linked task commitment id missing from material_commitments state"}
    return {"status": "pass", "message": "task commitment linkage under C1 strictness verified"}
