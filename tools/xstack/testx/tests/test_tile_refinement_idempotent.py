"""FAST test: MW-3 tile refinement stays idempotent across repeated worldgen process execution."""

from __future__ import annotations

import sys


TEST_ID = "test_tile_refinement_idempotent"
TEST_TAGS = ["fast", "mw", "worldgen", "surface", "idempotent"]


def _tile_rows(state: dict) -> list[tuple[str, str]]:
    rows = []
    for row in list(state.get("worldgen_surface_tile_artifacts") or []):
        if not isinstance(row, dict):
            continue
        rows.append(
            (
                str(row.get("tile_object_id", "")).strip(),
                str(row.get("deterministic_fingerprint", "")).strip(),
            )
        )
    return sorted(rows)


def _tile_field_rows(state: dict, tile_field_ids: list[str]) -> list[tuple[str, str]]:
    rows = []
    for row in list(state.get("field_cells") or []):
        if not isinstance(row, dict):
            continue
        field_id = str(row.get("field_id", "")).strip()
        if field_id not in tile_field_ids:
            continue
        geo_cell_key = dict(dict(row.get("extensions") or {}).get("geo_cell_key") or {})
        rows.append((field_id, str(geo_cell_key)))
    return sorted(rows)


def _tile_geometry_rows(state: dict, surface_cell_key: dict) -> list[str]:
    rows = []
    for row in list(state.get("geometry_cell_states") or []):
        if not isinstance(row, dict):
            continue
        if dict(row.get("geo_cell_key") or {}) == dict(surface_cell_key or {}):
            rows.append(str(row.get("material_id", "")).strip())
    return sorted(rows)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process
    from tools.xstack.testx.tests.mw3_testlib import build_surface_fixture, build_surface_request_from_fixture

    fixture = build_surface_fixture(repo_root)
    state = fixture["state"]
    planet_object_id = str(fixture.get("planet_object_id", "")).strip()
    tile_field_ids = [
        "field.temperature.surface.{}".format(planet_object_id),
        "field.daylight.surface.{}".format(planet_object_id),
        "field.pressure_stub.surface.{}".format(planet_object_id),
    ]
    first = run_worldgen_process(
        state=state,
        request_row=build_surface_request_from_fixture(fixture, request_id="mw3.tile.first", reason="query"),
    )
    first_tiles = _tile_rows(state)
    first_fields = _tile_field_rows(state, tile_field_ids)
    first_geometry = _tile_geometry_rows(state, fixture["surface_cell_key"])
    second = run_worldgen_process(
        state=state,
        request_row=build_surface_request_from_fixture(fixture, request_id="mw3.tile.second", reason="roi"),
    )
    second_tiles = _tile_rows(state)
    second_fields = _tile_field_rows(state, tile_field_ids)
    second_geometry = _tile_geometry_rows(state, fixture["surface_cell_key"])
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-3 idempotence fixture did not complete"}
    if not first_tiles:
        return {"status": "fail", "message": "MW-3 idempotence fixture created no surface tile artifact"}
    if first_tiles != second_tiles:
        return {"status": "fail", "message": "MW-3 surface tile artifacts drifted across repeated process execution"}
    if first_fields != second_fields:
        return {"status": "fail", "message": "MW-3 tile field initializations were duplicated or drifted on replay"}
    if first_geometry != second_geometry:
        return {"status": "fail", "message": "MW-3 geometry initialization duplicated or drifted on replay"}
    return {"status": "pass", "message": "MW-3 tile refinement is idempotent across repeated worldgen execution"}
