"""FAST test: reenactment generation deterministically degrades fidelity under budget pressure."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.reenactment_budget_degrades"
TEST_TAGS = ["fast", "materials", "reenactment", "budget"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.commitment_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
    )
    from tools.xstack.testx.tests.construction_testlib import with_inventory

    state = with_inventory(
        base_state(),
        node_id="node.alpha",
        material_id="material.steel_basic",
        mass=5_000,
        batch_id="batch.seed",
    )
    law = law_profile(["process.manifest_create", "process.manifest_tick", "process.reenactment_generate"])
    authority = authority_context(
        ["entitlement.control.admin", "session.boot", "entitlement.inspect"],
        privilege_level="operator",
    )
    policy = policy_context(strictness_id="causality.C0")

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.budget.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
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
        return {"status": "fail", "message": "manifest_create fixture failed for budget degrade test"}
    manifest_rows = sorted(
        (dict(row) for row in list(state.get("logistics_manifests") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("manifest_id", "")),
    )
    if not manifest_rows:
        return {"status": "fail", "message": "manifest fixture missing for budget degrade test"}
    manifest_id = str(manifest_rows[0].get("manifest_id", "")).strip()
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.budget.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 16},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_tick fixture failed for budget degrade test"}
    generated = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.budget.generate",
            "process_id": "process.reenactment_generate",
            "inputs": {
                "target_id": manifest_id,
                "start_tick": 0,
                "end_tick": 24,
                "desired_fidelity": "micro",
                "max_cost_units": 6,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(generated.get("result", "")) != "complete":
        return {"status": "fail", "message": "reenactment_generate should degrade (not refuse) for moderate budget"}
    if str(generated.get("fidelity_achieved", "")) == "micro":
        return {"status": "fail", "message": "reenactment fidelity should degrade below micro for constrained budget"}
    if bool(generated.get("degraded", False)) is not True:
        return {"status": "fail", "message": "reenactment_generate should report degraded=true when fidelity drops"}
    return {"status": "pass", "message": "reenactment budget degradation passed"}
