"""STRICT test: stub executor refusals remain deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.order_executor_stub_refusals_deterministic"
TEST_TAGS = ["strict", "civilisation", "orders", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.order_testlib import authority_context, base_state, law_profile, policy_context, with_agent

    state = with_agent(base_state(), "agent.order.stub", location_ref="region.alpha")
    law = law_profile(["process.order_create", "process.order_tick"])
    authority = authority_context(["entitlement.civ.order"])
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.order.create.stub_refusal.001",
            "process_id": "process.order_create",
            "inputs": {
                "order_type_id": "order.move",
                "target_kind": "agent",
                "target_id": "agent.order.stub",
                "payload": {
                    "destination": "region.target",
                    "speed_policy_id": "speed.stub.default",
                },
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(created.get("result", "")) != "complete":
        return {"create": dict(created), "tick": {}, "order_row": {}}
    order_id = str(created.get("order_id", ""))

    tick = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.order.tick.stub_refusal.001",
            "process_id": "process.order_tick",
            "inputs": {"max_orders_per_tick": 1},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    order_row = {}
    for row in sorted((item for item in list(state.get("order_assemblies") or []) if isinstance(item, dict)), key=lambda item: str(item.get("order_id", ""))):
        if str(row.get("order_id", "")).strip() == order_id:
            order_row = dict(row)
            break
    return {
        "create": dict(created),
        "tick": dict(tick),
        "order_row": order_row,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_create = dict(first.get("create") or {})
    second_create = dict(second.get("create") or {})
    if str(first_create.get("result", "")) != "complete" or str(second_create.get("result", "")) != "complete":
        return {"status": "fail", "message": "order_create should complete before stub refusal checks"}

    first_tick = dict(first.get("tick") or {})
    second_tick = dict(second.get("tick") or {})
    if str(first_tick.get("result", "")) != "complete" or str(second_tick.get("result", "")) != "complete":
        return {"status": "fail", "message": "order_tick should complete even when one order fails"}

    expected_order_id = str(first_create.get("order_id", ""))
    if list(first_tick.get("failed_order_ids") or []) != [expected_order_id]:
        return {"status": "fail", "message": "order_tick failed_order_ids should contain created micro move order"}
    if list(first_tick.get("failed_order_ids") or []) != list(second_tick.get("failed_order_ids") or []):
        return {"status": "fail", "message": "failed order ids diverged across repeated runs"}

    first_order = dict(first.get("order_row") or {})
    second_order = dict(second.get("order_row") or {})
    if str(first_order.get("status", "")) != "failed":
        return {"status": "fail", "message": "micro move order should fail in CIV-3 stub executor"}
    first_refusal = dict(first_order.get("refusal") or {})
    second_refusal = dict(second_order.get("refusal") or {})
    if str(first_refusal.get("code", "")) != "refusal.civ.order_requires_pathing_not_supported":
        return {"status": "fail", "message": "unexpected refusal code for unsupported micro pathing executor"}
    if first_refusal != second_refusal:
        return {"status": "fail", "message": "stub executor refusal payload diverged across repeated runs"}
    return {"status": "pass", "message": "order stub refusal determinism passed"}

