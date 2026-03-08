"""FAST test: GEO-8 cache hits preserve canonical result hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_worldgen_cache_hit_same_hash"
TEST_TAGS = ["fast", "geo", "worldgen", "cache"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo8_testlib import reset_worldgen_cache, run_worldgen_process, seed_worldgen_state, worldgen_request_row

    reset_worldgen_cache()
    state = seed_worldgen_state()
    first = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="worldgen.fixture.cache.first",
            index_tuple=[2, 5, -8],
            refinement_level=2,
            reason="query",
        ),
    )
    first_result_hash_chain = str(state.get("worldgen_result_hash_chain", "")).strip()
    second = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="worldgen.fixture.cache.second",
            index_tuple=[2, 5, -8],
            refinement_level=2,
            reason="roi",
        ),
    )
    second_result_hash_chain = str(state.get("worldgen_result_hash_chain", "")).strip()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "worldgen cache fixture did not complete"}
    if not bool(second.get("cache_hit", False)):
        return {"status": "fail", "message": "second worldgen request did not report a cache hit"}
    if str(first.get("result_id", "")).strip() != str(second.get("result_id", "")).strip():
        return {"status": "fail", "message": "cache hit did not preserve canonical worldgen result id"}
    if first_result_hash_chain != second_result_hash_chain:
        return {"status": "fail", "message": "cache hit changed canonical worldgen result hash chain"}
    return {"status": "pass", "message": "GEO-8 cache hits preserve canonical result hashes"}
