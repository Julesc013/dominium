"""FAST test: MW-1 authoritative refinement is idempotent for repeated cell instantiation."""

from __future__ import annotations

import sys


TEST_ID = "test_instantiation_idempotent"
TEST_TAGS = ["fast", "mw", "worldgen", "idempotent"]


def _artifact_signature_rows(state: dict) -> list[tuple[str, str]]:
    rows = []
    for row in list(state.get("worldgen_star_system_artifacts") or []):
        if not isinstance(row, dict):
            continue
        rows.append(
            (
                str(row.get("object_id", "")).strip(),
                str(row.get("system_seed_value", "")).strip(),
            )
        )
    return sorted(rows)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process, seed_worldgen_state, worldgen_request_row

    state = seed_worldgen_state()
    first = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="mw1.instantiation.first",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="query",
        ),
    )
    first_rows = _artifact_signature_rows(state)
    second = run_worldgen_process(
        state=state,
        request_row=worldgen_request_row(
            request_id="mw1.instantiation.second",
            index_tuple=[800, 0, 0],
            refinement_level=1,
            reason="roi",
        ),
    )
    second_rows = _artifact_signature_rows(state)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-1 authoritative instantiation fixture did not complete"}
    if not first_rows:
        return {"status": "fail", "message": "MW-1 authoritative instantiation created no star-system artifacts"}
    if first_rows != second_rows:
        return {"status": "fail", "message": "MW-1 star-system artifact rows drifted across repeated refinement"}
    if len(first_rows) != len(set(first_rows)):
        return {"status": "fail", "message": "MW-1 star-system artifact rows were duplicated"}
    return {"status": "pass", "message": "MW-1 authoritative star-system instantiation is idempotent"}
