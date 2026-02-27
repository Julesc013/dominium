"""FAST test: manifest_tick budget degradation order is deterministic by manifest_id."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.budget_degrade_order_deterministic"
TEST_TAGS = ["fast", "materials", "logistics", "budget", "determinism"]


def _run_once() -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.logistics_testlib import (
        authority_context,
        base_state,
        law_profile,
        logistics_graph,
        policy_context,
        with_inventory,
    )

    material_id = "material.steel_basic"
    state = with_inventory(
        base_state(),
        node_id="node.alpha",
        material_id=material_id,
        mass=5_000,
        batch_id="batch.seed",
    )
    law = law_profile(["process.manifest_create", "process.manifest_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context(
        graph_rows=[logistics_graph(delay_ticks=0, loss_fraction=0)],
        max_compute_units_per_tick=1,
        logistics_manifest_tick_budget=3,
    )

    for index in range(1, 4):
        created = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.logistics.budget.create.{}".format(index),
                "process_id": "process.manifest_create",
                "inputs": {
                    "graph_id": "graph.logistics.test",
                    "from_node_id": "node.alpha",
                    "to_node_id": "node.beta",
                    "batch_id": "batch.{}".format(index),
                    "material_id": material_id,
                    "quantity_mass": 500,
                    "earliest_depart_tick": 0,
                },
            },
            law_profile=copy.deepcopy(law),
            authority_context=copy.deepcopy(authority),
            navigation_indices={},
            policy_context=copy.deepcopy(policy),
        )
        if str(created.get("result", "")) != "complete":
            return {"created_error": created, "ticked": {}, "state": state}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.budget.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 3},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    return {"ticked": ticked, "state": state}


def _delivered_manifest_ids(state: dict) -> list[str]:
    out = []
    for row in sorted(
        (dict(item) for item in list(state.get("logistics_manifests") or []) if isinstance(item, dict)),
        key=lambda item: str(item.get("manifest_id", "")),
    ):
        if str(row.get("status", "")) == "delivered":
            out.append(str(row.get("manifest_id", "")))
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    first_tick = dict(first.get("ticked") or {})
    second_tick = dict(second.get("ticked") or {})
    if str(first_tick.get("result", "")) != "complete" or str(second_tick.get("result", "")) != "complete":
        return {"status": "fail", "message": "budget degradation tick should complete deterministically"}
    if str(first_tick.get("state_hash_anchor", "")) != str(second_tick.get("state_hash_anchor", "")):
        return {"status": "fail", "message": "budget-degraded tick state hash anchor diverged"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    if first_state != second_state:
        return {"status": "fail", "message": "budget-degraded logistics state diverged across runs"}

    delivered = _delivered_manifest_ids(first_state)
    if len(delivered) != 1:
        return {"status": "fail", "message": "budget-degraded tick should deliver exactly one manifest"}
    all_manifest_ids = sorted(
        str((dict(row).get("manifest_id", "")))
        for row in list(first_state.get("logistics_manifests") or [])
        if isinstance(row, dict)
    )
    if not all_manifest_ids:
        return {"status": "fail", "message": "expected manifests in budget degradation test state"}
    if delivered[0] != all_manifest_ids[0]:
        return {"status": "fail", "message": "degraded manifest processing order must be deterministic by manifest_id"}

    if str(first_tick.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "budget outcome should be degraded when compute budget limits updates"}
    if int(first_tick.get("processed_count", 0) or 0) != 1:
        return {"status": "fail", "message": "processed_count should respect budget-limited deterministic chunk size"}
    return {"status": "pass", "message": "budget degradation deterministic order passed"}
