"""FAST test: MW-2 authoritative refinement is idempotent for repeated cell instantiation."""

from __future__ import annotations

import sys


TEST_ID = "test_idempotent_refinement_l2"
TEST_TAGS = ["fast", "mw", "worldgen", "idempotent", "l2"]


def _signature_rows(state: dict) -> dict:
    return {
        "stars": sorted(
            (
                str(row.get("object_id", "")).strip(),
                str(row.get("deterministic_fingerprint", "")).strip(),
            )
            for row in list(state.get("worldgen_star_artifacts") or [])
            if isinstance(row, dict)
        ),
        "planet_orbits": sorted(
            (
                str(row.get("planet_object_id", "")).strip(),
                str(row.get("deterministic_fingerprint", "")).strip(),
            )
            for row in list(state.get("worldgen_planet_orbit_artifacts") or [])
            if isinstance(row, dict)
        ),
        "planet_basics": sorted(
            (
                str(row.get("object_id", "")).strip(),
                str(row.get("deterministic_fingerprint", "")).strip(),
            )
            for row in list(state.get("worldgen_planet_basic_artifacts") or [])
            if isinstance(row, dict)
        ),
        "summaries": sorted(
            (
                str(row.get("system_object_id", "")).strip(),
                str(row.get("deterministic_fingerprint", "")).strip(),
            )
            for row in list(state.get("worldgen_system_l2_summaries") or [])
            if isinstance(row, dict)
        ),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process, seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    first = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="mw2.instantiation.first",
            index_tuple=[800, 0, 0],
            refinement_level=2,
            reason="query",
        ),
    )
    first_rows = _signature_rows(state)
    second = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="mw2.instantiation.second",
            index_tuple=[800, 0, 0],
            refinement_level=2,
            reason="roi",
        ),
    )
    second_rows = _signature_rows(state)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-2 authoritative refinement fixture did not complete"}
    if not first_rows["stars"] or not first_rows["planet_basics"]:
        return {"status": "fail", "message": "MW-2 authoritative refinement created no star or planet artifacts"}
    if first_rows != second_rows:
        return {"status": "fail", "message": "MW-2 refinement artifacts drifted across repeated refinement"}
    for key, rows in sorted(second_rows.items()):
        if len(rows) != len(set(rows)):
            return {"status": "fail", "message": "MW-2 {} rows were duplicated".format(key)}
    return {"status": "pass", "message": "MW-2 authoritative refinement is idempotent"}
