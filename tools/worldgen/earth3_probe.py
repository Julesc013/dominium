"""Deterministic EARTH-3 tide probes for replay and TestX reuse."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Iterable, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.worldgen.earth0_probe import (  # noqa: E402
    EARTH_SAMPLE_BANDS,
    EARTH_SAMPLE_COLUMNS,
    build_earth_probe_context,
    generate_earth_probe_tile,
)
from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402
from tools.xstack.testx.tests.mobility_free_testlib import authority_context, law_profile, policy_context, seed_free_state  # noqa: E402
from src.worldgen.earth import (  # noqa: E402
    DEFAULT_TIDE_PARAMS_ID,
    lunar_phase_from_params,
    tide_params_rows,
    tide_window_hash,
)


TIDE_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "tide_params_registry.json")
TIDE_ALLOWED_PROCESSES = ["process.earth_tide_tick"]
TIDE_REPLAY_TICK = 72
TIDE_LAST_PROCESSED_TICK = 61
TIDE_MAX_TILES_PER_UPDATE = 24
TIDE_DAY_TICK_A = 10
TIDE_DAY_TICK_B = 15


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError("expected object json at {}".format(rel_path.replace("\\", "/")))
    return dict(payload)


def _earth_tide_params_row(repo_root: str, tide_params_id: str = DEFAULT_TIDE_PARAMS_ID) -> dict:
    payload = _load_json(repo_root, TIDE_PARAMS_REGISTRY_REL)
    rows = tide_params_rows(payload)
    row = _as_map(rows.get(str(tide_params_id).strip()))
    if not row:
        raise RuntimeError("earth tide params not found: {}".format(tide_params_id))
    return row


def _seed_tide_state(
    tile_rows: Sequence[Mapping[str, object]],
    *,
    universe_identity: Mapping[str, object],
    simulation_tick: int,
    last_processed_tick: int | None = None,
    tide_params_id: str = DEFAULT_TIDE_PARAMS_ID,
) -> dict:
    state = seed_free_state(initial_velocity_x=0)
    state["simulation_time"] = {"tick": int(max(0, int(simulation_tick)))}
    state["universe_identity"] = dict(universe_identity)
    state["worldgen_requests"] = []
    state["worldgen_results"] = []
    state["worldgen_spawned_objects"] = []
    state["worldgen_star_system_artifacts"] = []
    state["worldgen_star_artifacts"] = []
    state["worldgen_planet_orbit_artifacts"] = []
    state["worldgen_planet_basic_artifacts"] = []
    state["worldgen_system_l2_summaries"] = []
    state["worldgen_surface_tile_artifacts"] = []
    state["geometry_cell_states"] = []
    layer_by_id: Dict[str, dict] = {}
    field_cells: List[dict] = []
    for tile in list(tile_rows or []):
        payload = _as_map(tile)
        for row in _as_list(payload.get("generated_surface_tile_artifact_rows")):
            if isinstance(row, Mapping):
                state["worldgen_surface_tile_artifacts"].append(dict(row))
        for row in _as_list(payload.get("geometry_initializations")):
            if isinstance(row, Mapping):
                state["geometry_cell_states"].append(dict(row))
        for row in _as_list(payload.get("field_layers")):
            if not isinstance(row, Mapping):
                continue
            field_id = str(row.get("field_id", "")).strip()
            if field_id:
                layer_by_id[field_id] = dict(row)
        for row in _as_list(payload.get("field_initializations")):
            if isinstance(row, Mapping):
                field_cells.append(dict(row))
    state["field_layers"] = [dict(layer_by_id[key]) for key in sorted(layer_by_id.keys())]
    state["field_cells"] = list(field_cells)
    if last_processed_tick is not None:
        state["earth_tide_runtime_state"] = {
            "version": "EARTH3-4",
            "last_processed_tick": int(last_processed_tick),
            "last_tick_window_start": int(last_processed_tick),
            "last_tick_window_end": int(last_processed_tick),
            "last_tick_window_span": 1,
            "last_tide_params_id": str(tide_params_id).strip() or DEFAULT_TIDE_PARAMS_ID,
            "last_due_bucket_ids": [],
            "last_updated_tile_ids": [],
            "last_skipped_tile_ids": [],
            "last_window_hash": "",
            "last_degraded": False,
            "last_degrade_reason": None,
        }
    return state


def _tide_overlay_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        normalized.append(
            {
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "tide_height_value": int(row.get("tide_height_value", 0) or 0),
                "lunar_phase": int(row.get("lunar_phase", 0) or 0),
                "rotation_phase": int(row.get("rotation_phase", 0) or 0),
                "surface_class_id": str(row.get("surface_class_id", "")).strip(),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


def generate_tide_tile_fixture(
    repo_root: str,
    *,
    current_tick: int = 0,
    chart_ids: Iterable[str] = ("chart.atlas.north", "chart.atlas.south"),
    columns: Iterable[int] = EARTH_SAMPLE_COLUMNS,
    bands: Iterable[int] = EARTH_SAMPLE_BANDS,
) -> dict:
    context = build_earth_probe_context(repo_root)
    tiles: List[dict] = []
    for chart_id in list(chart_ids):
        for band in list(bands):
            for column in list(columns):
                tiles.append(
                    generate_earth_probe_tile(
                        context,
                        chart_id=str(chart_id),
                        index_tuple=[int(column), int(band)],
                        refinement_level=1,
                        current_tick=int(current_tick),
                    )
                )
    return {
        "context": context,
        "tiles": tiles,
        "deterministic_fingerprint": canonical_sha256(
            {
                "tile_count": len(tiles),
                "chart_ids": [str(item) for item in list(chart_ids or [])],
                "columns": [int(item) for item in list(columns or [])],
                "bands": [int(item) for item in list(bands or [])],
                "current_tick": int(current_tick),
            }
        ),
    }


def run_tide_tick_fixture(
    repo_root: str,
    *,
    current_tick: int = TIDE_REPLAY_TICK,
    last_processed_tick: int | None = TIDE_LAST_PROCESSED_TICK,
    max_tiles_per_update: int = TIDE_MAX_TILES_PER_UPDATE,
) -> dict:
    fixture = generate_tide_tile_fixture(repo_root, current_tick=0)
    context = _as_map(fixture.get("context"))
    tiles = [dict(row) for row in _as_list(fixture.get("tiles")) if isinstance(row, Mapping)]
    tide_row = _earth_tide_params_row(repo_root)
    tide_params_id = str(tide_row.get("tide_params_id", "")).strip() or DEFAULT_TIDE_PARAMS_ID
    state = _seed_tide_state(
        tiles,
        universe_identity=_as_map(context.get("universe_identity")),
        simulation_tick=int(current_tick),
        last_processed_tick=last_processed_tick,
        tide_params_id=tide_params_id,
    )
    policy = policy_context(max_compute_units_per_tick=4096)
    policy["earth_tide_max_tiles_per_update"] = int(max(0, int(max_tiles_per_update)))
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.earth3.tide.tick.{}".format(int(current_tick)),
            "process_id": "process.earth_tide_tick",
            "inputs": {
                "max_tiles_per_update": int(max_tiles_per_update),
            },
        },
        law_profile=law_profile(TIDE_ALLOWED_PROCESSES),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=policy,
    )
    overlays = [dict(row) for row in _as_list(state.get("earth_tide_tile_overlays")) if isinstance(row, Mapping)]
    runtime_state = _as_map(state.get("earth_tide_runtime_state"))
    return {
        "result": str(result.get("result", "")).strip() or "unknown",
        "process_result": dict(result),
        "tide_params_id": tide_params_id,
        "tide_params_registry_hash": canonical_sha256(_load_json(repo_root, TIDE_PARAMS_REGISTRY_REL)),
        "tick_window_start": int(runtime_state.get("last_tick_window_start", current_tick) or current_tick),
        "tick_window_end": int(runtime_state.get("last_tick_window_end", current_tick) or current_tick),
        "tick_window_span": int(runtime_state.get("last_tick_window_span", 1) or 1),
        "selected_tile_ids": [str(item).strip() for item in list(result.get("selected_tile_ids") or []) if str(item).strip()],
        "skipped_tile_ids": [str(item).strip() for item in list(result.get("skipped_tile_ids") or []) if str(item).strip()],
        "due_bucket_ids": [int(item) for item in list(result.get("due_bucket_ids") or [])],
        "tide_window_hash": str(result.get("tide_window_hash", "")).strip() or tide_window_hash(overlays),
        "overlay_hash": _tide_overlay_hash(overlays),
        "overlays": overlays,
        "state": state,
        "deterministic_fingerprint": "",
    }


def verify_tide_window_replay(repo_root: str) -> dict:
    first = run_tide_tick_fixture(repo_root)
    second = run_tide_tick_fixture(repo_root)
    stable = (
        str(first.get("overlay_hash", "")).strip() == str(second.get("overlay_hash", "")).strip()
        and str(first.get("tide_window_hash", "")).strip() == str(second.get("tide_window_hash", "")).strip()
        and list(first.get("selected_tile_ids") or []) == list(second.get("selected_tile_ids") or [])
        and list(first.get("skipped_tile_ids") or []) == list(second.get("skipped_tile_ids") or [])
    )
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "tide_params_registry_hash": str(first.get("tide_params_registry_hash", "")).strip(),
        "tide_window_hash": str(first.get("tide_window_hash", "")).strip(),
        "overlay_hash": str(first.get("overlay_hash", "")).strip(),
        "first_run": {
            "tick_window_start": int(first.get("tick_window_start", 0) or 0),
            "tick_window_end": int(first.get("tick_window_end", 0) or 0),
            "tick_window_span": int(first.get("tick_window_span", 0) or 0),
            "selected_tile_ids": list(first.get("selected_tile_ids") or []),
            "skipped_tile_ids": list(first.get("skipped_tile_ids") or []),
            "due_bucket_ids": list(first.get("due_bucket_ids") or []),
            "overlay_hash": str(first.get("overlay_hash", "")).strip(),
        },
        "second_run": {
            "tick_window_start": int(second.get("tick_window_start", 0) or 0),
            "tick_window_end": int(second.get("tick_window_end", 0) or 0),
            "tick_window_span": int(second.get("tick_window_span", 0) or 0),
            "selected_tile_ids": list(second.get("selected_tile_ids") or []),
            "skipped_tile_ids": list(second.get("skipped_tile_ids") or []),
            "due_bucket_ids": list(second.get("due_bucket_ids") or []),
            "overlay_hash": str(second.get("overlay_hash", "")).strip(),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def lunar_phase_report(repo_root: str) -> dict:
    tide_row = _earth_tide_params_row(repo_root)
    tick = 123
    first = lunar_phase_from_params(tick=tick, tide_params_row=tide_row)
    second = lunar_phase_from_params(tick=tick, tide_params_row=tide_row)
    report = {
        "result": "complete" if first == second else "violation",
        "tick": int(tick),
        "lunar_phase_a": int(first),
        "lunar_phase_b": int(second),
        "tide_params_id": str(tide_row.get("tide_params_id", "")).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def tide_day_delta_report(repo_root: str) -> dict:
    fixture_a = run_tide_tick_fixture(repo_root, current_tick=TIDE_DAY_TICK_A, last_processed_tick=None, max_tiles_per_update=128)
    fixture_b = run_tide_tick_fixture(repo_root, current_tick=TIDE_DAY_TICK_B, last_processed_tick=None, max_tiles_per_update=128)
    overlays_a = dict((str(row.get("tile_object_id", "")).strip(), dict(row)) for row in list(fixture_a.get("overlays") or []))
    overlays_b = dict((str(row.get("tile_object_id", "")).strip(), dict(row)) for row in list(fixture_b.get("overlays") or []))
    changed = 0
    for tile_id in sorted(set(overlays_a.keys()) & set(overlays_b.keys())):
        if int(_as_map(overlays_a.get(tile_id)).get("tide_height_value", 0) or 0) != int(_as_map(overlays_b.get(tile_id)).get("tide_height_value", 0) or 0):
            changed += 1
    report = {
        "result": "complete",
        "tick_a": TIDE_DAY_TICK_A,
        "tick_b": TIDE_DAY_TICK_B,
        "changed_tide_tile_count": int(changed),
        "overlay_hash_a": str(fixture_a.get("overlay_hash", "")).strip(),
        "overlay_hash_b": str(fixture_b.get("overlay_hash", "")).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def inland_damping_report(repo_root: str) -> dict:
    fixture = run_tide_tick_fixture(repo_root, current_tick=TIDE_REPLAY_TICK, last_processed_tick=None, max_tiles_per_update=128)
    ocean_rows = [
        dict(row)
        for row in list(fixture.get("overlays") or [])
        if isinstance(row, Mapping) and str(dict(row).get("surface_class_id", "")).strip() == "surface.class.ocean"
    ]
    land_rows = [
        dict(row)
        for row in list(fixture.get("overlays") or [])
        if isinstance(row, Mapping) and str(dict(row).get("surface_class_id", "")).strip() == "surface.class.land"
    ]
    max_ocean = max((abs(int(row.get("tide_height_value", 0) or 0)) for row in ocean_rows), default=0)
    max_land = max((abs(int(row.get("tide_height_value", 0) or 0)) for row in land_rows), default=0)
    report = {
        "result": "complete" if ocean_rows and land_rows else "violation",
        "ocean_tile_count": len(ocean_rows),
        "land_tile_count": len(land_rows),
        "max_ocean_abs_tide": int(max_ocean),
        "max_land_abs_tide": int(max_land),
        "inland_damping_applied": bool(max_ocean > max_land),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


__all__ = [
    "TIDE_ALLOWED_PROCESSES",
    "inland_damping_report",
    "lunar_phase_report",
    "run_tide_tick_fixture",
    "tide_day_delta_report",
    "verify_tide_window_replay",
]
