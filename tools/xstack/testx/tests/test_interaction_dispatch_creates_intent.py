"""STRICT test: interaction dispatch creates deterministic intent/envelope and executes via process runtime."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.interaction.dispatch_creates_intent"
TEST_TAGS = ["strict", "interaction", "dispatch", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.interaction_dispatch import run_interaction_command
    from tools.xstack.testx.tests.interaction_testlib import (
        authority_context,
        base_state,
        interaction_action_registry,
        law_profile,
        perceived_model,
        policy_context,
    )

    perceived = perceived_model(include_truth_overlay=True)
    listed = run_interaction_command(
        command="interact.list_affordances",
        perceived_model=perceived,
        law_profile=law_profile(),
        authority_context=authority_context(entitlements=["entitlement.inspect", "entitlement.move"]),
        interaction_action_registry=interaction_action_registry(),
        target_semantic_id="agent.alpha",
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(listed.get("result", "")) != "complete":
        return {"status": "fail", "message": "interact.list_affordances refused unexpectedly"}

    affordance_rows = list((dict(listed.get("affordance_list") or {})).get("affordances") or [])
    inspect_affordance_id = ""
    for row in affordance_rows:
        if str((dict(row)).get("process_id", "")).strip() == "process.inspect_generate_snapshot":
            inspect_affordance_id = str((dict(row)).get("affordance_id", "")).strip()
            break
    if not inspect_affordance_id:
        return {"status": "fail", "message": "inspect affordance id missing from deterministic list"}

    state = copy.deepcopy(base_state())
    execute = run_interaction_command(
        command="interact.execute",
        perceived_model=perceived,
        law_profile=law_profile(),
        authority_context=authority_context(entitlements=["entitlement.inspect", "entitlement.move"]),
        interaction_action_registry=interaction_action_registry(),
        target_semantic_id="agent.alpha",
        affordance_id=inspect_affordance_id,
        parameters={"target_id": "agent.alpha", "cost_units": 1},
        state=state,
        policy_context=policy_context(max_inspection_budget_per_tick=8),
        peer_id="peer.test.interaction",
        deterministic_sequence_number=7,
        submission_tick=3,
        include_disabled=True,
        repo_root=repo_root,
    )
    if str(execute.get("result", "")) != "complete":
        return {"status": "fail", "message": "interact.execute refused unexpectedly"}

    intent = dict(execute.get("intent") or {})
    envelope = dict(execute.get("envelope") or {})
    execution = dict(execute.get("execution") or {})
    if str(intent.get("process_id", "")) != "process.inspect_generate_snapshot":
        return {"status": "fail", "message": "dispatch intent process_id mismatch"}
    if str(envelope.get("intent_id", "")) != str(intent.get("intent_id", "")):
        return {"status": "fail", "message": "envelope intent_id does not match dispatched intent"}
    if str(execution.get("result", "complete")) == "refused":
        return {"status": "fail", "message": "interaction dispatch execution unexpectedly refused"}
    if str(execution.get("target_id", "")) != "agent.alpha":
        return {"status": "fail", "message": "execution payload missing deterministic target_id"}
    return {"status": "pass", "message": "interaction dispatch deterministic intent creation passed"}
