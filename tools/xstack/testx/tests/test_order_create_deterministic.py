"""STRICT test: order_create emits deterministic order + queue artifacts."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.order_create_deterministic"
TEST_TAGS = ["strict", "civilisation", "orders", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.order_testlib import authority_context, base_state, law_profile, policy_context, with_cohort

    state = with_cohort(base_state(), "cohort.order.alpha", size=7, faction_id="faction.alpha", location_ref="region.alpha")
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.order.create.001",
            "process_id": "process.order_create",
            "inputs": {
                "order_type_id": "order.move",
                "target_kind": "cohort",
                "target_id": "cohort.order.alpha",
                "payload": {
                    "destination": "region.beta",
                    "speed_policy_id": "speed.stub.default",
                },
            },
        },
        law_profile=law_profile(["process.order_create"]),
        authority_context=authority_context(["entitlement.civ.order"]),
        navigation_indices={},
        policy_context=policy_context(),
    )
    return {
        "result": dict(result),
        "state": state,
    }


def _single_order_snapshot(state: dict) -> dict:
    order_rows = sorted(
        (dict(row) for row in list(state.get("order_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("order_id", "")),
    )
    queue_rows = sorted(
        (dict(row) for row in list(state.get("order_queue_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("queue_id", "")),
    )
    return {
        "order_rows": order_rows,
        "queue_rows": queue_rows,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})

    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "order_create should complete for lawful cohort target"}
    if str(first_result.get("order_id", "")) != str(second_result.get("order_id", "")):
        return {"status": "fail", "message": "deterministic order_id generation diverged"}
    if str(first_result.get("state_hash_anchor", "")) != str(second_result.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "order_create state hash anchor diverged across repeated runs"}

    first_state = _single_order_snapshot(dict(first.get("state") or {}))
    second_state = _single_order_snapshot(dict(second.get("state") or {}))
    if first_state != second_state:
        return {"status": "fail", "message": "order/queue assemblies diverged across repeated runs"}

    order_rows = list(first_state.get("order_rows") or [])
    if len(order_rows) != 1:
        return {"status": "fail", "message": "expected exactly one order assembly"}
    order_row = dict(order_rows[0])
    if str(order_row.get("status", "")) != "queued":
        return {"status": "fail", "message": "new order should be queued immediately"}

    queue_rows = list(first_state.get("queue_rows") or [])
    if len(queue_rows) != 1:
        return {"status": "fail", "message": "expected deterministic single queue owner for cohort order"}
    queue_order_ids = list(queue_rows[0].get("order_ids") or [])
    if queue_order_ids != [str(order_row.get("order_id", ""))]:
        return {"status": "fail", "message": "queue order_ids should contain deterministic created order id"}
    return {"status": "pass", "message": "order_create deterministic assembly + queue behavior passed"}

