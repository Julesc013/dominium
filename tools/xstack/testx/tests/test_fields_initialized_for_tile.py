"""FAST test: MW-3 tile refinement initializes the required macro field and geometry rows."""

from __future__ import annotations

import sys


TEST_ID = "test_fields_initialized_for_tile"
TEST_TAGS = ["fast", "mw", "worldgen", "surface", "fields"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.testx.tests.geo8_testlib import run_worldgen_process
    from tools.xstack.testx.tests.mw3_testlib import build_surface_fixture, build_surface_request_from_fixture

    fixture = build_surface_fixture(repo_root, require_atmosphere=True)
    state = fixture["state"]
    result = run_worldgen_process(
        state=state,
        request_row=build_surface_request_from_fixture(fixture, request_id="mw3.fields.init", reason="query"),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "MW-3 field-initialization fixture did not complete"}
    planet_object_id = str(fixture.get("planet_object_id", "")).strip()
    required_field_ids = {
        "field.temperature.surface.{}".format(planet_object_id),
        "field.daylight.surface.{}".format(planet_object_id),
        "field.pressure_stub.surface.{}".format(planet_object_id),
    }
    present_field_layers = {
        str(dict(row).get("field_id", "")).strip()
        for row in list(state.get("field_layers") or [])
        if isinstance(row, dict)
    }
    if not required_field_ids.issubset(present_field_layers):
        return {"status": "fail", "message": "MW-3 field layers omitted required tile field bindings"}
    present_field_cells = {
        str(dict(row).get("field_id", "")).strip()
        for row in list(state.get("field_cells") or [])
        if isinstance(row, dict)
        and dict(dict(row).get("extensions") or {}).get("geo_cell_key") == fixture["surface_cell_key"]
    }
    if not required_field_ids.issubset(present_field_cells):
        return {"status": "fail", "message": "MW-3 field cells omitted one or more required tile initializations"}
    geometry_rows = [
        dict(row)
        for row in list(state.get("geometry_cell_states") or [])
        if isinstance(row, dict) and dict(row.get("geo_cell_key") or {}) == fixture["surface_cell_key"]
    ]
    if len(geometry_rows) != 1:
        return {"status": "fail", "message": "MW-3 geometry initialization did not persist exactly one tile state"}
    return {"status": "pass", "message": "MW-3 tile refinement initializes required field and geometry rows"}
