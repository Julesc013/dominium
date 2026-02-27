"""FAST test: event stream index rebuild is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.event_stream_index_deterministic"
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
        mass=2_000,
        batch_id="batch.seed",
    )
    law = law_profile(["process.manifest_create", "process.manifest_tick", "process.event_stream_index_rebuild"])
    authority = authority_context(
        ["entitlement.control.admin", "session.boot", "entitlement.inspect"],
        privilege_level="operator",
    )
    policy = policy_context(strictness_id="causality.C0")

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.stream.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.seed",
                "material_id": "material.steel_basic",
                "quantity_mass": 300,
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
            "intent_id": "intent.materials.stream.tick",
            "process_id": "process.manifest_tick",
            "inputs": {"graph_id": "graph.logistics.test", "max_manifests_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {}
    indexed = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.materials.stream.index",
            "process_id": "process.event_stream_index_rebuild",
            "inputs": {
                "target_id": manifest_id,
                "start_tick": 0,
                "end_tick": 16,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(indexed.get("result", "")) != "complete":
        return {}
    stream_rows = sorted(
        (dict(row) for row in list(state.get("event_stream_indices") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("stream_id", "")),
    )
    if not stream_rows:
        return {}
    stream_row = dict(stream_rows[-1])
    return {
        "state": state,
        "result": indexed,
        "stream_id": str(stream_row.get("stream_id", "")),
        "stream_hash": str(stream_row.get("stream_hash", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if not first or not second:
        return {"status": "fail", "message": "event stream deterministic fixture setup failed"}
    if str(first.get("stream_hash", "")) != str(second.get("stream_hash", "")):
        return {"status": "fail", "message": "event stream hash diverged across identical runs"}
    if str(first.get("stream_id", "")) != str(second.get("stream_id", "")):
        return {"status": "fail", "message": "event stream id diverged across identical runs"}
    if str((dict(first.get("result") or {})).get("state_hash_anchor", "")) != str((dict(second.get("result") or {})).get("state_hash_anchor", "")):
        return {"status": "fail", "message": "event stream index state hash anchor diverged"}
    if copy.deepcopy(dict(first.get("state") or {})) != copy.deepcopy(dict(second.get("state") or {})):
        return {"status": "fail", "message": "event stream indexing mutated state non-deterministically"}
    return {"status": "pass", "message": "event stream index determinism passed"}
