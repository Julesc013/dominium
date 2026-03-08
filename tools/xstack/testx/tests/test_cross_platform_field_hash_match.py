"""STRICT test: GEO-bound field hashes match across ordering variants."""

from __future__ import annotations

import copy
import re
import sys


TEST_ID = "test_cross_platform_field_hash_match"
TEST_TAGS = ["strict", "fields", "geo", "determinism", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_variant(repo_root: str, *, reverse_order: bool) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.fields import build_field_cell, build_field_layer
    from tools.geo.tool_replay_field_geo_window import verify_geo_field_replay_window
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.mobility_free_testlib import (
        authority_context,
        law_profile,
        policy_context,
        seed_free_state,
    )

    state = seed_free_state(initial_velocity_x=0)
    state["field_layers"] = [
        build_field_layer(
            field_id="field.irradiance.global",
            field_type_id="field.irradiance",
            spatial_scope_id="spatial.global",
            resolution_level="macro",
            update_policy_id="field.profile_defined",
            extensions={
                "topology_profile_id": "geo.topology.r3_infinite",
                "partition_profile_id": "geo.partition.grid_zd",
                "chart_id": "chart.global",
            },
        )
    ]
    state["field_cells"] = [
        build_field_cell(
            field_id="field.irradiance.global",
            value=0,
            value_kind="scalar",
            last_updated_tick=0,
            geo_cell_key={
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global",
                "index_tuple": [0, 0, 0],
                "refinement_level": 0,
                "extensions": {},
            },
        ),
        build_field_cell(
            field_id="field.irradiance.global",
            value=0,
            value_kind="scalar",
            last_updated_tick=0,
            geo_cell_key={
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global",
                "index_tuple": [1, 0, 0],
                "refinement_level": 0,
                "extensions": {},
            },
        ),
    ]
    updates = [
        {
            "field_id": "field.irradiance.global",
            "field_type_id": "field.irradiance",
            "spatial_node_id": "cell.0.0.0",
            "geo_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global",
                "index_tuple": [0, 0, 0],
                "refinement_level": 0,
                "extensions": {},
            },
            "sampled_value": 125,
            "spatial_scope_id": "spatial.global",
            "resolution_level": "macro",
        },
        {
            "field_id": "field.irradiance.global",
            "field_type_id": "field.irradiance",
            "spatial_node_id": "cell.1.0.0",
            "geo_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global",
                "index_tuple": [1, 0, 0],
                "refinement_level": 0,
                "extensions": {},
            },
            "sampled_value": 375,
            "spatial_scope_id": "spatial.global",
            "resolution_level": "macro",
        },
    ]
    if reverse_order:
        updates = list(reversed(updates))

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.field.geo.hash.{}".format("b" if reverse_order else "a"),
            "process_id": "process.field_update",
            "inputs": {
                "field_updates": list(updates),
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.field_update"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    replay = verify_geo_field_replay_window(state_payload=copy.deepcopy(state))
    state_hash = canonical_sha256(
        {
            "field_layers": [dict(row) for row in list(state.get("field_layers") or []) if isinstance(row, dict)],
            "field_cells": [dict(row) for row in list(state.get("field_cells") or []) if isinstance(row, dict)],
            "field_sample_rows": [dict(row) for row in list(state.get("field_sample_rows") or []) if isinstance(row, dict)],
            "field_binding_registry_hash": str(state.get("field_binding_registry_hash", "")).strip(),
        }
    )
    return {
        "result": dict(result),
        "replay": dict(replay),
        "state_hash": str(state_hash).strip().lower(),
    }


def run(repo_root: str):
    first = _run_variant(repo_root=repo_root, reverse_order=False)
    second = _run_variant(repo_root=repo_root, reverse_order=True)
    for payload in (first, second):
        result = dict(payload.get("result") or {})
        replay = dict(payload.get("replay") or {})
        if str(result.get("result", "")) != "complete":
            return {"status": "fail", "message": "GEO field update variant refused: {}".format(result)}
        if str(replay.get("result", "")) != "complete":
            return {"status": "fail", "message": "GEO field replay verification failed: {}".format(replay)}
    fp_a = str(dict(first.get("result") or {}).get("deterministic_fingerprint", "")).strip().lower()
    fp_b = str(dict(second.get("result") or {}).get("deterministic_fingerprint", "")).strip().lower()
    if (not _HASH64.fullmatch(fp_a)) or (not _HASH64.fullmatch(fp_b)):
        return {"status": "fail", "message": "missing deterministic_fingerprint on GEO process.field_update result"}
    if fp_a != fp_b:
        return {"status": "fail", "message": "GEO field update fingerprint diverged for equivalent ordering variants"}
    hash_a = str(first.get("state_hash", "")).strip().lower()
    hash_b = str(second.get("state_hash", "")).strip().lower()
    if (not _HASH64.fullmatch(hash_a)) or (not _HASH64.fullmatch(hash_b)):
        return {"status": "fail", "message": "invalid GEO state hash shape for field ordering variants"}
    if hash_a != hash_b:
        return {"status": "fail", "message": "GEO field state hash diverged across equivalent ordering variants"}
    return {"status": "pass", "message": "GEO-bound field hashes match across ordering variants"}
