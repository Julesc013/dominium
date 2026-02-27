"""FAST test: reenactment generation yields deterministic hashes."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.reenactment_deterministic_hash"
TEST_TAGS = ["fast", "materials", "reenactment", "determinism"]


def _run_once() -> dict:
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
    law = law_profile(
        [
            "process.manifest_create",
            "process.manifest_tick",
            "process.reenactment_generate",
        ]
    )
    authority = authority_context(
        ["entitlement.control.admin", "session.boot", "entitlement.inspect"],
        privilege_level="operator",
    )
    policy = policy_context(strictness_id="causality.C0")

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.reenact.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
                "quantity_mass": 600,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {}
    manifest_rows = sorted(
        (dict(row) for row in list(state.get("logistics_manifests") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("manifest_id", "")),
    )
    if not manifest_rows:
        return {}
    manifest_id = str(manifest_rows[0].get("manifest_id", "")).strip()
    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.reenact.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 16},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {}
    generated = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.reenact.generate",
            "process_id": "process.reenactment_generate",
            "inputs": {
                "target_id": manifest_id,
                "start_tick": 0,
                "end_tick": 24,
                "desired_fidelity": "meso",
                "max_cost_units": 2_000,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(generated.get("result", "")) != "complete":
        return {}
    artifacts = sorted(
        (dict(row) for row in list(state.get("reenactment_artifacts") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("reenactment_id", "")),
    )
    if not artifacts:
        return {}
    artifact = dict(artifacts[-1])
    return {
        "state": state,
        "result": generated,
        "reenactment_id": str(artifact.get("reenactment_id", "")),
        "inputs_hash": str(artifact.get("inputs_hash", "")),
        "fingerprint": str(artifact.get("deterministic_fingerprint", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if not first or not second:
        return {"status": "fail", "message": "reenactment deterministic fixture setup failed"}
    if str(first.get("reenactment_id", "")) != str(second.get("reenactment_id", "")):
        return {"status": "fail", "message": "reenactment_id diverged across identical runs"}
    if str(first.get("inputs_hash", "")) != str(second.get("inputs_hash", "")):
        return {"status": "fail", "message": "reenactment inputs_hash diverged across identical runs"}
    if str(first.get("fingerprint", "")) != str(second.get("fingerprint", "")):
        return {"status": "fail", "message": "reenactment fingerprint diverged across identical runs"}
    if str((dict(first.get("result") or {})).get("state_hash_anchor", "")) != str((dict(second.get("result") or {})).get("state_hash_anchor", "")):
        return {"status": "fail", "message": "reenactment generation state hash anchor diverged"}
    if copy.deepcopy(dict(first.get("state") or {})) != copy.deepcopy(dict(second.get("state") or {})):
        return {"status": "fail", "message": "reenactment generation mutated state non-deterministically"}
    return {"status": "pass", "message": "reenactment deterministic hash passed"}
