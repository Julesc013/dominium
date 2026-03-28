"""FAST test: MW-2 planet-count summaries are deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "test_planet_count_deterministic"
TEST_TAGS = ["fast", "mw", "worldgen", "determinism", "l2"]


def _summary_signature_rows(rows) -> list[tuple[str, int]]:
    out = []
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        out.append(
            (
                str(row.get("system_object_id", "")).strip(),
                int(row.get("planet_count", 0) or 0),
            )
        )
    return sorted(out)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from geo import generate_worldgen_result
    from tools.xstack.testx.tests.geo8_testlib import seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    request = worldgen_request_row(
        request_id="mw2.planet_count.deterministic",
        index_tuple=[800, 0, 0],
        refinement_level=2,
        reason="query",
    )
    first = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=request,
        cache_enabled=False,
    )
    second = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=request,
        cache_enabled=False,
    )
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-2 planet-count fixture did not complete"}
    first_rows = _summary_signature_rows(first.get("generated_system_l2_summary_rows"))
    second_rows = _summary_signature_rows(second.get("generated_system_l2_summary_rows"))
    if first_rows != second_rows:
        return {"status": "fail", "message": "MW-2 planet-count summaries drifted across repeated runs"}
    if not first_rows or max(count for _system_id, count in first_rows) <= 0:
        return {"status": "fail", "message": "MW-2 planet-count fixture generated no planets"}
    return {"status": "pass", "message": "MW-2 planet-count summaries deterministic for identical inputs"}
