"""Deterministic EARTH-2 seasonal climate probes for replay and TestX reuse."""

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
from worldgen.earth import (  # noqa: E402
    DEFAULT_EARTH_CLIMATE_PARAMS_ID,
    climate_window_hash,
    earth_climate_params_rows,
    earth_orbit_phase_from_params,
)


EARTH_CLIMATE_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "earth_climate_params_registry.json")
CLIMATE_ALLOWED_PROCESSES = ["process.earth_climate_tick"]
CLIMATE_REPLAY_TICK = 144
CLIMATE_LAST_PROCESSED_TICK = 131
CLIMATE_MAX_TILES_PER_UPDATE = 24
CLIMATE_YEAR_TICK_A = 912
CLIMATE_YEAR_TICK_B = 2737
CLIMATE_POLAR_CHART_ID = "chart.atlas.north"
CLIMATE_POLAR_INDEX_TUPLE = [16, 1]
CLIMATE_TEMPERATE_CHART_ID = "chart.atlas.north"
CLIMATE_TEMPERATE_INDEX_TUPLE = [16, 4]


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


def _earth_climate_params_row(repo_root: str, climate_params_id: str = DEFAULT_EARTH_CLIMATE_PARAMS_ID) -> dict:
    payload = _load_json(repo_root, EARTH_CLIMATE_PARAMS_REGISTRY_REL)
    rows = earth_climate_params_rows(payload)
    row = _as_map(rows.get(str(climate_params_id).strip()))
    if not row:
        raise RuntimeError("earth climate params not found: {}".format(climate_params_id))
    return row


def _seed_climate_state(
    tile_rows: Sequence[Mapping[str, object]],
    *,
    universe_identity: Mapping[str, object],
    simulation_tick: int,
    last_processed_tick: int | None = None,
    climate_params_id: str = DEFAULT_EARTH_CLIMATE_PARAMS_ID,
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
        state["earth_climate_runtime_state"] = {
            "version": "EARTH2-4",
            "last_processed_tick": int(last_processed_tick),
            "last_tick_window_start": int(last_processed_tick),
            "last_tick_window_end": int(last_processed_tick),
            "last_tick_window_span": 1,
            "last_climate_params_id": str(climate_params_id).strip() or DEFAULT_EARTH_CLIMATE_PARAMS_ID,
            "last_due_bucket_ids": [],
            "last_updated_tile_ids": [],
            "last_skipped_tile_ids": [],
            "last_window_hash": "",
            "last_degraded": False,
            "last_degrade_reason": None,
        }
    return state


def _climate_overlay_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        normalized.append(
            {
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "temperature_value": int(row.get("temperature_value", 0) or 0),
                "daylight_value": int(row.get("daylight_value", 0) or 0),
                "climate_band_id": str(row.get("climate_band_id", "")).strip(),
                "biome_overlay_tags": [str(item).strip() for item in list(row.get("biome_overlay_tags") or []) if str(item).strip()],
                "orbit_phase": int(row.get("orbit_phase", 0) or 0),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


def generate_climate_tile_fixture(
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


def run_climate_tick_fixture(
    repo_root: str,
    *,
    current_tick: int = CLIMATE_REPLAY_TICK,
    last_processed_tick: int | None = CLIMATE_LAST_PROCESSED_TICK,
    max_tiles_per_update: int = CLIMATE_MAX_TILES_PER_UPDATE,
) -> dict:
    fixture = generate_climate_tile_fixture(repo_root, current_tick=0)
    context = _as_map(fixture.get("context"))
    tiles = [dict(row) for row in _as_list(fixture.get("tiles")) if isinstance(row, Mapping)]
    climate_row = _earth_climate_params_row(repo_root)
    climate_params_id = str(climate_row.get("climate_params_id", "")).strip() or DEFAULT_EARTH_CLIMATE_PARAMS_ID
    state = _seed_climate_state(
        tiles,
        universe_identity=_as_map(context.get("universe_identity")),
        simulation_tick=int(current_tick),
        last_processed_tick=last_processed_tick,
        climate_params_id=climate_params_id,
    )
    policy = policy_context(max_compute_units_per_tick=4096)
    policy["earth_climate_max_tiles_per_update"] = int(max(0, int(max_tiles_per_update)))
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.earth2.climate.tick.{}".format(int(current_tick)),
            "process_id": "process.earth_climate_tick",
            "inputs": {
                "max_tiles_per_update": int(max_tiles_per_update),
            },
        },
        law_profile=law_profile(CLIMATE_ALLOWED_PROCESSES),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=policy,
    )
    overlays = [dict(row) for row in _as_list(state.get("earth_climate_tile_overlays")) if isinstance(row, Mapping)]
    runtime_state = _as_map(state.get("earth_climate_runtime_state"))
    return {
        "result": str(result.get("result", "")).strip() or "unknown",
        "process_result": dict(result),
        "climate_params_id": climate_params_id,
        "climate_params_registry_hash": canonical_sha256(_load_json(repo_root, EARTH_CLIMATE_PARAMS_REGISTRY_REL)),
        "tick_window_start": int(runtime_state.get("last_tick_window_start", current_tick) or current_tick),
        "tick_window_end": int(runtime_state.get("last_tick_window_end", current_tick) or current_tick),
        "tick_window_span": int(runtime_state.get("last_tick_window_span", 1) or 1),
        "selected_tile_ids": [str(item).strip() for item in list(result.get("selected_tile_ids") or []) if str(item).strip()],
        "skipped_tile_ids": [str(item).strip() for item in list(result.get("skipped_tile_ids") or []) if str(item).strip()],
        "due_bucket_ids": [int(item) for item in list(result.get("due_bucket_ids") or [])],
        "climate_window_hash": str(result.get("climate_window_hash", "")).strip() or climate_window_hash(overlays),
        "overlay_hash": _climate_overlay_hash(overlays),
        "overlays": overlays,
        "state": state,
        "deterministic_fingerprint": "",
    }


def verify_climate_window_replay(repo_root: str) -> dict:
    first = run_climate_tick_fixture(repo_root)
    second = run_climate_tick_fixture(repo_root)
    stable = (
        str(first.get("overlay_hash", "")).strip() == str(second.get("overlay_hash", "")).strip()
        and str(first.get("climate_window_hash", "")).strip() == str(second.get("climate_window_hash", "")).strip()
        and list(first.get("selected_tile_ids") or []) == list(second.get("selected_tile_ids") or [])
        and list(first.get("skipped_tile_ids") or []) == list(second.get("skipped_tile_ids") or [])
    )
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "climate_params_registry_hash": str(first.get("climate_params_registry_hash", "")).strip(),
        "climate_window_hash": str(first.get("climate_window_hash", "")).strip(),
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


def climate_year_delta_report(repo_root: str) -> dict:
    fixture_a = run_climate_tick_fixture(repo_root, current_tick=CLIMATE_YEAR_TICK_A, last_processed_tick=None, max_tiles_per_update=128)
    fixture_b = run_climate_tick_fixture(repo_root, current_tick=CLIMATE_YEAR_TICK_B, last_processed_tick=None, max_tiles_per_update=128)
    overlays_a = dict((str(row.get("tile_object_id", "")).strip(), dict(row)) for row in list(fixture_a.get("overlays") or []))
    overlays_b = dict((str(row.get("tile_object_id", "")).strip(), dict(row)) for row in list(fixture_b.get("overlays") or []))
    changed_temperatures = 0
    changed_daylight = 0
    for tile_id in sorted(set(overlays_a.keys()) & set(overlays_b.keys())):
        row_a = _as_map(overlays_a.get(tile_id))
        row_b = _as_map(overlays_b.get(tile_id))
        if int(row_a.get("temperature_value", 0) or 0) != int(row_b.get("temperature_value", 0) or 0):
            changed_temperatures += 1
        if int(row_a.get("daylight_value", 0) or 0) != int(row_b.get("daylight_value", 0) or 0):
            changed_daylight += 1
    report = {
        "result": "complete",
        "tick_a": CLIMATE_YEAR_TICK_A,
        "tick_b": CLIMATE_YEAR_TICK_B,
        "changed_temperature_tile_count": int(changed_temperatures),
        "changed_daylight_tile_count": int(changed_daylight),
        "overlay_hash_a": str(fixture_a.get("overlay_hash", "")).strip(),
        "overlay_hash_b": str(fixture_b.get("overlay_hash", "")).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def polar_daylight_report(repo_root: str) -> dict:
    context = build_earth_probe_context(repo_root)
    tile_a = generate_earth_probe_tile(
        context,
        chart_id=CLIMATE_POLAR_CHART_ID,
        index_tuple=CLIMATE_POLAR_INDEX_TUPLE,
        refinement_level=1,
        current_tick=0,
    )
    tile_b = generate_earth_probe_tile(
        context,
        chart_id=CLIMATE_POLAR_CHART_ID,
        index_tuple=CLIMATE_POLAR_INDEX_TUPLE,
        refinement_level=1,
        current_tick=0,
    )
    climate_row = _earth_climate_params_row(repo_root)
    artifact_a = _as_map(_as_list(tile_a.get("generated_surface_tile_artifact_rows"))[0])
    artifact_b = _as_map(_as_list(tile_b.get("generated_surface_tile_artifact_rows"))[0])
    from worldgen.earth import evaluate_earth_tile_climate  # noqa: E402

    eval_a = evaluate_earth_tile_climate(
        artifact_row=artifact_a,
        climate_params_row=climate_row,
        current_tick=CLIMATE_YEAR_TICK_A,
        geometry_row=_as_map(_as_list(tile_a.get("geometry_initializations"))[0]),
    )
    eval_b = evaluate_earth_tile_climate(
        artifact_row=artifact_b,
        climate_params_row=climate_row,
        current_tick=CLIMATE_YEAR_TICK_B,
        geometry_row=_as_map(_as_list(tile_b.get("geometry_initializations"))[0]),
    )
    report = {
        "result": "complete",
        "tick_a": CLIMATE_YEAR_TICK_A,
        "tick_b": CLIMATE_YEAR_TICK_B,
        "daylight_a": int(eval_a.get("daylight_value", 0) or 0),
        "daylight_b": int(eval_b.get("daylight_value", 0) or 0),
        "variation_detected": int(eval_a.get("daylight_value", 0) or 0) != int(eval_b.get("daylight_value", 0) or 0),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def orbit_phase_report(repo_root: str) -> dict:
    climate_row = _earth_climate_params_row(repo_root)
    phase_a = earth_orbit_phase_from_params(tick=CLIMATE_YEAR_TICK_A, climate_params_row=climate_row)
    phase_b = earth_orbit_phase_from_params(tick=CLIMATE_YEAR_TICK_B, climate_params_row=climate_row)
    return {
        "result": "complete",
        "phase_a": int(phase_a),
        "phase_b": int(phase_b),
        "deterministic_fingerprint": canonical_sha256({"phase_a": int(phase_a), "phase_b": int(phase_b)}),
    }


__all__ = [
    "CLIMATE_LAST_PROCESSED_TICK",
    "CLIMATE_MAX_TILES_PER_UPDATE",
    "CLIMATE_REPLAY_TICK",
    "CLIMATE_YEAR_TICK_A",
    "CLIMATE_YEAR_TICK_B",
    "climate_year_delta_report",
    "generate_climate_tile_fixture",
    "orbit_phase_report",
    "polar_daylight_report",
    "run_climate_tick_fixture",
    "verify_climate_window_replay",
]
