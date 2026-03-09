"""Shared deterministic MW-3 surface-fixture helpers."""

from __future__ import annotations

import sys


FIXTURE_CELL_INDEX = [800, 0, 0]
FIXTURE_CHART_ID = "chart.atlas.north"
FIXTURE_SURFACE_INDEX = [1, 2]
FIXTURE_SURFACE_REFINEMENT = 1
FIXTURE_CURRENT_TICK = 4096


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _planet_tags(row: dict) -> list[str]:
    extensions = dict(dict(row).get("extensions") or {})
    tags = extensions.get("tags")
    if not isinstance(tags, list):
        return []
    return sorted(set(str(tag).strip() for tag in tags if str(tag).strip()))


def select_surface_fixture_planet(rows: object, *, require_atmosphere: bool = True) -> dict:
    candidates = []
    for raw in list(rows or []):
        if not isinstance(raw, dict):
            continue
        row = dict(raw)
        if not str(row.get("object_id", "")).strip():
            continue
        atmosphere_class_id = str(row.get("atmosphere_class_id", "")).strip()
        if require_atmosphere and atmosphere_class_id in {"", "atmo.none"}:
            continue
        candidates.append(row)
    if not candidates and require_atmosphere:
        return {}
    if not candidates:
        for raw in list(rows or []):
            if isinstance(raw, dict) and str(dict(raw).get("object_id", "")).strip():
                candidates.append(dict(raw))
    if not candidates:
        return {}
    return dict(sorted(candidates, key=lambda row: str(row.get("object_id", "")).strip())[0])


def build_surface_request_from_fixture(fixture: dict, *, request_id: str, reason: str = "query") -> dict:
    from src.geo import build_worldgen_request

    return build_worldgen_request(
        request_id=request_id,
        geo_cell_key=dict(fixture.get("surface_cell_key") or {}),
        refinement_level=3,
        reason=reason,
        extensions={"source": "mw3_testlib"},
    )


def build_surface_fixture(repo_root: str, *, current_tick: int = FIXTURE_CURRENT_TICK, require_atmosphere: bool = True) -> dict:
    _ensure_repo_root(repo_root)
    from src.geo import generate_worldgen_result
    from src.worldgen.mw import build_planet_surface_cell_key
    from tools.xstack.testx.tests.geo8_testlib import (
        reset_worldgen_cache,
        seed_worldgen_state,
        worldgen_cell_key,
        worldgen_request_row,
    )

    reset_worldgen_cache()
    state = seed_worldgen_state()
    state["current_tick"] = int(current_tick)
    ancestor_world_cell_key = worldgen_cell_key(FIXTURE_CELL_INDEX)
    l2_request = worldgen_request_row(
        request_id="mw3.fixture.l2",
        index_tuple=FIXTURE_CELL_INDEX,
        refinement_level=2,
        reason="query",
    )
    l2_result = generate_worldgen_result(
        universe_identity=state.get("universe_identity"),
        worldgen_request=l2_request,
        current_tick=int(current_tick),
        cache_enabled=False,
    )
    if str(l2_result.get("result", "")) != "complete":
        raise RuntimeError("MW-3 fixture L2 request did not complete")
    planet_row = select_surface_fixture_planet(
        l2_result.get("generated_planet_basic_artifact_rows"),
        require_atmosphere=require_atmosphere,
    )
    if not planet_row:
        raise RuntimeError("MW-3 fixture could not select a planet with the required atmosphere profile")
    planet_object_id = str(planet_row.get("object_id", "")).strip()
    if not planet_object_id:
        raise RuntimeError("MW-3 fixture selected an invalid planet row")
    surface_cell_key = build_planet_surface_cell_key(
        planet_object_id=planet_object_id,
        ancestor_world_cell_key=ancestor_world_cell_key,
        chart_id=FIXTURE_CHART_ID,
        index_tuple=FIXTURE_SURFACE_INDEX,
        refinement_level=FIXTURE_SURFACE_REFINEMENT,
        planet_tags=_planet_tags(planet_row),
    )
    fixture = {
        "state": state,
        "current_tick": int(current_tick),
        "ancestor_world_cell_key": ancestor_world_cell_key,
        "l2_request": l2_request,
        "l2_result": l2_result,
        "planet_row": planet_row,
        "planet_object_id": planet_object_id,
        "surface_cell_key": surface_cell_key,
    }
    fixture["surface_request"] = build_surface_request_from_fixture(
        fixture,
        request_id="mw3.fixture.surface",
        reason="query",
    )
    return fixture


def generate_surface_fixture_result(repo_root: str, *, current_tick: int = FIXTURE_CURRENT_TICK) -> tuple[dict, dict]:
    _ensure_repo_root(repo_root)
    from src.geo import generate_worldgen_result

    fixture = build_surface_fixture(repo_root, current_tick=current_tick, require_atmosphere=True)
    result = generate_worldgen_result(
        universe_identity=fixture["state"].get("universe_identity"),
        worldgen_request=fixture["surface_request"],
        current_tick=int(current_tick),
        cache_enabled=False,
    )
    return fixture, result


def surface_result_hash(result: dict) -> str:
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from src.worldgen.mw import surface_tile_artifact_hash_chain

    field_rows = sorted(
        (
            dict(row)
            for row in list(result.get("field_initializations") or [])
            if isinstance(row, dict)
        ),
        key=lambda row: (
            str(row.get("field_id", "")).strip(),
            canonical_sha256(dict(dict(row.get("extensions") or {}).get("geo_cell_key") or {})),
        ),
    )
    geometry_rows = sorted(
        (
            dict(row)
            for row in list(result.get("geometry_initializations") or [])
            if isinstance(row, dict)
        ),
        key=lambda row: canonical_sha256(dict(row.get("geo_cell_key") or {})),
    )
    return canonical_sha256(
        {
            "surface_tile_artifact_hash_chain": surface_tile_artifact_hash_chain(
                result.get("generated_surface_tile_artifact_rows")
            ),
            "field_initializations": field_rows,
            "geometry_initializations": geometry_rows,
            "surface_summary": dict(result.get("surface_summary") or {}),
        }
    )
