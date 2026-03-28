"""FAST test: MW-0 star-system IDs remain stable across equivalent requests."""

from __future__ import annotations

import sys


TEST_ID = "test_system_ids_stable"
TEST_TAGS = ["fast", "mw", "worldgen", "identity"]


def _system_identity_rows(payload: dict) -> list[tuple[int, str, str]]:
    rows = []
    for row in list(payload.get("generated_system_seed_rows") or []):
        if not isinstance(row, dict):
            continue
        rows.append(
            (
                int(row.get("local_index", 0)),
                str(row.get("local_subkey", "")).strip(),
                str(row.get("object_id_hash", "")).strip(),
            )
        )
    return rows


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    identity = dict(state.get("universe_identity") or {})
    first = generate_worldgen_result(
        universe_identity=identity,
        worldgen_request=worldgen_request_row(
            request_id="mw0.fixture.ids.first",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="query",
        ),
        cache_enabled=False,
    )
    second = generate_worldgen_result(
        universe_identity=identity,
        worldgen_request=worldgen_request_row(
            request_id="mw0.fixture.ids.second",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="roi",
        ),
        cache_enabled=False,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "system identity fixture did not complete"}
    if _system_identity_rows(first) != _system_identity_rows(second):
        return {"status": "fail", "message": "MW-0 system seed identity rows drifted across equivalent requests"}
    if not _system_identity_rows(first):
        return {"status": "fail", "message": "MW-0 system identity rows were empty"}
    return {"status": "pass", "message": "MW-0 star-system IDs stable across equivalent requests"}
