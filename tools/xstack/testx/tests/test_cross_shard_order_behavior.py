"""STRICT test: cross-shard order handling is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.cross_shard_order_behavior"
TEST_TAGS = ["strict", "civilisation", "orders", "srz", "determinism"]


def _scenario(active_shard_id: str) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.order_testlib import authority_context, base_state, law_profile, policy_context, with_cohort

    state = with_cohort(base_state(), "cohort.shard.alpha", size=9, faction_id="faction.alpha", location_ref="region.earth")
    policy = policy_context(
        active_shard_id=active_shard_id,
        shard_map={
            "object_owner": {
                "region.earth": "shard.0",
            },
            "shards": [
                {"shard_id": "shard.0", "region_scope": {"object_ids": ["region.earth"]}},
                {"shard_id": "shard.1", "region_scope": {"object_ids": ["region.mars"]}},
            ],
        },
    )
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.civ.order.create.cross_shard.001",
            "process_id": "process.order_create",
            "inputs": {
                "order_type_id": "order.move",
                "target_kind": "cohort",
                "target_id": "cohort.shard.alpha",
                "payload": {
                    "destination": "region.earth",
                    "speed_policy_id": "speed.stub.default",
                },
            },
        },
        law_profile=law_profile(["process.order_create"]),
        authority_context=authority_context(["entitlement.civ.order"]),
        navigation_indices={},
        policy_context=policy,
    )
    return {"result": dict(result), "state": state}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    refuse_a = _scenario("shard.1")
    refuse_b = _scenario("shard.1")
    refuse_a_result = dict(refuse_a.get("result") or {})
    refuse_b_result = dict(refuse_b.get("result") or {})
    if str(refuse_a_result.get("result", "")) != "refused" or str(refuse_b_result.get("result", "")) != "refused":
        return {"status": "fail", "message": "order_create should refuse when active shard does not own target"}
    refusal_a = dict(refuse_a_result.get("refusal") or {})
    refusal_b = dict(refuse_b_result.get("refusal") or {})
    if str(refusal_a.get("reason_code", "")) != "refusal.civ.order_cross_shard_not_supported":
        return {"status": "fail", "message": "cross-shard order refusal code mismatch"}
    if refusal_a != refusal_b:
        return {"status": "fail", "message": "cross-shard order refusal payload diverged across repeated runs"}

    accept = _scenario("shard.0")
    accept_result = dict(accept.get("result") or {})
    if str(accept_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "order_create should complete on owning shard"}
    order_rows = sorted(
        (dict(row) for row in list((accept.get("state") or {}).get("order_assemblies") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("order_id", "")),
    )
    if len(order_rows) != 1:
        return {"status": "fail", "message": "owning-shard create should persist exactly one order row"}
    return {"status": "pass", "message": "cross-shard order behavior deterministic passed"}

