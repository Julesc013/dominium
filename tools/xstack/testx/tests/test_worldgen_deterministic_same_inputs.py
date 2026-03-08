"""FAST test: GEO-8 worldgen process is deterministic for identical inputs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_worldgen_deterministic_same_inputs"
TEST_TAGS = ["fast", "geo", "worldgen", "determinism"]


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo8_testlib import reset_worldgen_cache, run_worldgen_process, seed_worldgen_state, worldgen_request_row

    reset_worldgen_cache()
    state = seed_worldgen_state()
    result = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="worldgen.fixture.same_inputs",
            index_tuple=[9, -3, 14],
            refinement_level=3,
            reason="query",
        ),
    )
    return {
        "result": dict(result),
        "worldgen_results": copy.deepcopy(state.get("worldgen_results")),
        "worldgen_spawned_objects": copy.deepcopy(state.get("worldgen_spawned_objects")),
        "field_cells": copy.deepcopy(state.get("field_cells")),
        "geometry_cell_states": copy.deepcopy(state.get("geometry_cell_states")),
        "worldgen_result_hash_chain": str(state.get("worldgen_result_hash_chain", "")).strip(),
    }


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    if first != second:
        return {"status": "fail", "message": "worldgen process drifted across repeated runs"}
    result = dict(first.get("result") or {})
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "worldgen process did not complete"}
    if int(result.get("spawned_object_count", 0)) <= 0:
        return {"status": "fail", "message": "worldgen process did not spawn any deterministic objects"}
    if not str(first.get("worldgen_result_hash_chain", "")).strip():
        return {"status": "fail", "message": "worldgen result hash chain was not populated"}
    return {"status": "pass", "message": "GEO-8 worldgen process deterministic for identical inputs"}
