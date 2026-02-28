"""STRICT test: process.tool_bind produces deterministic binding state and metadata."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_tool_bind_deterministic"
TEST_TAGS = ["strict", "interaction", "tool", "determinism"]


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.test.tool.bind",
        "allowed_processes": ["process.tool_bind"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.tool_bind": "entitlement.tool.equip",
        },
        "process_privilege_requirements": {
            "process.tool_bind": "operator",
        },
        "allowed_lenses": ["lens.diegetic.sensor"],
        "epistemic_limits": {"max_view_radius_km": 1000, "allow_hidden_state_access": False},
    }


def _tool_row() -> dict:
    return {
        "schema_version": "1.0.0",
        "tool_id": "tool.instance.wrench.alpha",
        "tool_type_id": "tool.wrench.basic",
        "tool_tags": ["tool_tag.fastening", "tool_tag.operating"],
        "effect_model_id": "effect.basic_fastening",
        "equipped_by_agent_id": None,
        "durability_state": {"health_permille": 1000},
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.interaction_testlib import authority_context, base_state, policy_context

    state_one = base_state()
    state_one["tool_assemblies"] = [_tool_row()]
    state_one["tool_bindings"] = []
    state_two = copy.deepcopy(state_one)

    intent = {
        "intent_id": "intent.tool.bind.001",
        "process_id": "process.tool_bind",
        "inputs": {
            "subject_id": "agent.alpha",
            "tool_id": "tool.instance.wrench.alpha",
        },
    }
    auth = authority_context(entitlements=["entitlement.tool.equip"], privilege_level="operator")
    law = _law_profile()
    policy = policy_context()

    first = execute_intent(
        state=state_one,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    second = execute_intent(
        state=state_two,
        intent=copy.deepcopy(intent),
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )

    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.tool_bind refused unexpectedly"}
    if str(first.get("bind_id", "")) != str(second.get("bind_id", "")):
        return {"status": "fail", "message": "tool bind_id differs across equivalent runs"}
    if str(first.get("state_hash_anchor", "")) != str(second.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "tool bind state hash anchor differs across equivalent runs"}
    if list(state_one.get("tool_bindings") or []) != list(state_two.get("tool_bindings") or []):
        return {"status": "fail", "message": "tool bindings differ after deterministic bind replay"}
    agent_rows = list(state_one.get("agent_states") or [])
    equipped = ""
    for row in agent_rows:
        if str((dict(row)).get("agent_id", "")).strip() == "agent.alpha":
            equipped = str((dict(row)).get("equipped_tool_id", "")).strip()
            break
    if equipped != "tool.instance.wrench.alpha":
        return {"status": "fail", "message": "agent equipped_tool_id not updated by deterministic bind"}
    return {"status": "pass", "message": "process.tool_bind determinism verified"}

