"""STRICT test: order queue ordering follows deterministic sort key."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.order_queue_ordering_deterministic"
TEST_TAGS = ["strict", "civilisation", "orders", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.order_testlib import authority_context, base_state, law_profile, policy_context, with_cohort

    state = with_cohort(base_state(), "cohort.queue.alpha", size=11, faction_id="faction.alpha", location_ref="region.alpha")
    law = law_profile(["process.order_create", "process.order_tick"])
    authority = authority_context(["entitlement.civ.order"])
    policy = policy_context()

    create_inputs = [
        {"order_id": "order.queue.c", "priority": 10, "destination": "region.one"},
        {"order_id": "order.queue.a", "priority": 80, "destination": "region.two"},
        {"order_id": "order.queue.b", "priority": 80, "destination": "region.three"},
        {"order_id": "order.queue.d", "priority": 30, "destination": "region.four"},
    ]
    for index, row in enumerate(create_inputs):
        created = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.civ.order.create.queue.{:03d}".format(index),
                "process_id": "process.order_create",
                "inputs": {
                    "order_id": str(row.get("order_id", "")),
                    "order_type_id": "order.move",
                    "target_kind": "cohort",
                    "target_id": "cohort.queue.alpha",
                    "priority": int(row.get("priority", 0)),
                    "payload": {
                        "destination": str(row.get("destination", "")),
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
            return {"result": dict(created), "state": state}

    queue_rows = sorted(
        (dict(item) for item in list(state.get("order_queue_assemblies") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("queue_id", "")),
    )
    order_rows = sorted(
        (dict(item) for item in list(state.get("order_assemblies") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("order_id", "")),
    )
    before_tick = list((queue_rows[0] if queue_rows else {}).get("order_ids") or [])

    tick_result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.order.tick.queue.001",
            "process_id": "process.order_tick",
            "inputs": {"max_orders_per_tick": 8},
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    return {
        "result": dict(tick_result),
        "state": state,
        "before_tick_order_ids": before_tick,
        "order_rows": order_rows,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()

    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")) != "complete" or str(second_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "order queue scenario should complete deterministically"}

    first_rows = list(first.get("order_rows") or [])
    expected_order = [
        str(row.get("order_id", ""))
        for row in sorted(
            first_rows,
            key=lambda row: (
                -max(0, int(row.get("priority", 0) or 0)),
                max(0, int(row.get("created_tick", 0) or 0)),
                str(row.get("order_id", "")),
            ),
        )
    ]
    first_before = list(first.get("before_tick_order_ids") or [])
    if first_before != expected_order:
        return {
            "status": "fail",
            "message": "queue ordering before tick does not match deterministic priority/tick key: expected={} actual={}".format(
                ",".join(expected_order),
                ",".join(first_before),
            ),
        }
    if list(second.get("before_tick_order_ids") or []) != expected_order:
        return {"status": "fail", "message": "repeated run queue ordering diverged before tick"}

    processed_first = list(first_result.get("processed_order_ids") or [])
    processed_second = list(second_result.get("processed_order_ids") or [])
    if processed_first != expected_order or processed_second != expected_order:
        return {"status": "fail", "message": "order_tick processing order does not respect deterministic queue key"}
    if processed_first != processed_second:
        return {"status": "fail", "message": "order_tick processed order_ids diverged across repeated runs"}

    completed_first = sorted(set(str(item).strip() for item in (first_result.get("completed_order_ids") or []) if str(item).strip()))
    if completed_first != sorted(expected_order):
        return {"status": "fail", "message": "all queued cohort move orders should complete in stub executor"}
    return {"status": "pass", "message": "order queue deterministic ordering passed"}
