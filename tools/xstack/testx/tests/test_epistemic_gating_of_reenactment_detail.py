"""FAST test: micro reenactment playback is gated by epistemic authority."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.epistemic_gating_of_reenactment_detail"
TEST_TAGS = ["fast", "materials", "reenactment", "epistemic"]


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
        mass=7_000,
        batch_id="batch.seed",
    )
    law = law_profile(
        [
            "process.manifest_create",
            "process.manifest_tick",
            "process.reenactment_generate",
            "process.reenactment_play",
        ]
    )
    generate_authority = authority_context(
        ["entitlement.control.admin", "session.boot", "entitlement.inspect"],
        privilege_level="operator",
        visibility_level="nondiegetic",
    )
    policy = policy_context(strictness_id="causality.C0")

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.gating.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
                "quantity_mass": 700,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(generate_authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_create fixture failed for reenactment gating test"}
    manifest_rows = sorted(
        (dict(row) for row in list(state.get("logistics_manifests") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("manifest_id", "")),
    )
    if not manifest_rows:
        return {"status": "fail", "message": "manifest fixture missing for reenactment gating test"}
    manifest_id = str(manifest_rows[0].get("manifest_id", "")).strip()
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.gating.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 16},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(generate_authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {"status": "fail", "message": "manifest_tick fixture failed for reenactment gating test"}
    generated = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.gating.generate",
            "process_id": "process.reenactment_generate",
            "inputs": {
                "target_id": manifest_id,
                "start_tick": 0,
                "end_tick": 24,
                "desired_fidelity": "micro",
                "max_cost_units": 50_000,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(generate_authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(generated.get("result", "")) != "complete":
        return {"status": "fail", "message": "reenactment_generate fixture failed for gating test"}
    reenactment_id = str(generated.get("reenactment_id", "")).strip()
    if not reenactment_id:
        return {"status": "fail", "message": "reenactment_generate did not return reenactment_id"}
    if str(generated.get("fidelity_achieved", "")) != "micro":
        return {"status": "fail", "message": "fixture expected micro fidelity before applying diegetic playback gate"}

    diegetic_authority = authority_context(
        ["entitlement.inspect"],
        privilege_level="observer",
        visibility_level="diegetic",
    )
    played = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.gating.play",
            "process_id": "process.reenactment_play",
            "inputs": {"reenactment_id": reenactment_id},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(diegetic_authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(played.get("result", "")) != "refused":
        return {"status": "fail", "message": "diegetic playback should refuse micro reenactment detail"}
    refusal_row = dict(played.get("refusal") or {})
    if str(refusal_row.get("reason_code", "")) != "refusal.reenactment.forbidden_by_law":
        return {"status": "fail", "message": "expected refusal.reenactment.forbidden_by_law for diegetic micro playback"}
    return {"status": "pass", "message": "reenactment epistemic gating passed"}
