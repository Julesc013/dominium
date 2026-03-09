"""Deterministic EARTH-7 wind probes for replay and TestX reuse."""

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
from src.fields import build_field_cell  # noqa: E402
from src.pollution import evaluate_pollution_dispersion  # noqa: E402
from src.worldgen.earth import (  # noqa: E402
    DEFAULT_WIND_PARAMS_ID,
    evaluate_earth_tile_wind,
    wind_params_rows,
    wind_window_hash,
)


WIND_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "wind_params_registry.json")
WIND_ALLOWED_PROCESSES = ["process.earth_wind_tick"]
WIND_REPLAY_TICK = 88
WIND_LAST_PROCESSED_TICK = 79
WIND_MAX_TILES_PER_UPDATE = 24


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError("expected object json at {}".format(rel_path.replace("\\", "/")))
    return dict(payload)


def _earth_wind_params_row(repo_root: str, wind_params_id: str = DEFAULT_WIND_PARAMS_ID) -> dict:
    payload = _load_json(repo_root, WIND_PARAMS_REGISTRY_REL)
    rows = wind_params_rows(payload)
    row = _as_map(rows.get(str(wind_params_id).strip()))
    if not row:
        raise RuntimeError("earth wind params not found: {}".format(wind_params_id))
    return row


def _seed_wind_state(
    tile_rows: Sequence[Mapping[str, object]],
    *,
    universe_identity: Mapping[str, object],
    simulation_tick: int,
    last_processed_tick: int | None = None,
    wind_params_id: str = DEFAULT_WIND_PARAMS_ID,
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
        state["earth_wind_runtime_state"] = {
            "version": "EARTH7-3",
            "last_processed_tick": int(last_processed_tick),
            "last_tick_window_start": int(last_processed_tick),
            "last_tick_window_end": int(last_processed_tick),
            "last_tick_window_span": 1,
            "last_wind_params_id": str(wind_params_id).strip() or DEFAULT_WIND_PARAMS_ID,
            "last_due_bucket_ids": [],
            "last_updated_tile_ids": [],
            "last_skipped_tile_ids": [],
            "last_window_hash": "",
            "last_degraded": False,
            "last_degrade_reason": None,
        }
    return state


def _flatten_artifact_rows(tile_rows: Sequence[Mapping[str, object]]) -> List[dict]:
    rows: List[dict] = []
    for tile in list(tile_rows or []):
        payload = _as_map(tile)
        for row in _as_list(payload.get("generated_surface_tile_artifact_rows")):
            if isinstance(row, Mapping):
                rows.append(dict(row))
    return rows


def _wind_overlay_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        vector = _as_map(row.get("wind_vector"))
        normalized.append(
            {
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "wind_band_id": str(row.get("wind_band_id", "")).strip(),
                "band_shift_mdeg": int(_as_int(row.get("band_shift_mdeg", 0), 0)),
                "wind_vector": {
                    "x": int(_as_int(vector.get("x", 0), 0)),
                    "y": int(_as_int(vector.get("y", 0), 0)),
                    "z": int(_as_int(vector.get("z", 0), 0)),
                },
                "tick_bucket": int(_as_int(row.get("tick_bucket", 0), 0)),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


def _vector_sign(value: int) -> int:
    if int(value) > 0:
        return 1
    if int(value) < 0:
        return -1
    return 0


def _closest_artifact_by_latitude(
    artifact_rows: Sequence[Mapping[str, object]],
    *,
    target_abs_latitude_mdeg: int,
) -> dict:
    candidates = []
    for raw in list(artifact_rows or []):
        row = _as_map(raw)
        extensions = _as_map(row.get("extensions"))
        latitude_mdeg = int(_as_int(extensions.get("latitude_mdeg", 0), 0))
        tile_id = str(row.get("tile_object_id", "")).strip()
        if not tile_id:
            continue
        candidates.append(
            (
                abs(abs(latitude_mdeg) - int(target_abs_latitude_mdeg)),
                abs(latitude_mdeg),
                tile_id,
                dict(row),
            )
        )
    if not candidates:
        raise RuntimeError("no surface tile artifacts available for EARTH-7 probe")
    candidates.sort(key=lambda item: (int(item[0]), int(item[1]), str(item[2])))
    return dict(candidates[0][3])


def generate_wind_tile_fixture(
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


def run_wind_tick_fixture(
    repo_root: str,
    *,
    current_tick: int = WIND_REPLAY_TICK,
    last_processed_tick: int | None = WIND_LAST_PROCESSED_TICK,
    max_tiles_per_update: int = WIND_MAX_TILES_PER_UPDATE,
) -> dict:
    fixture = generate_wind_tile_fixture(repo_root, current_tick=0)
    context = _as_map(fixture.get("context"))
    tiles = [dict(row) for row in _as_list(fixture.get("tiles")) if isinstance(row, Mapping)]
    wind_row = _earth_wind_params_row(repo_root)
    wind_params_id = str(wind_row.get("wind_params_id", "")).strip() or DEFAULT_WIND_PARAMS_ID
    state = _seed_wind_state(
        tiles,
        universe_identity=_as_map(context.get("universe_identity")),
        simulation_tick=int(current_tick),
        last_processed_tick=last_processed_tick,
        wind_params_id=wind_params_id,
    )
    policy = policy_context(max_compute_units_per_tick=4096)
    policy["earth_wind_max_tiles_per_update"] = int(max(0, int(max_tiles_per_update)))
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.earth7.wind.tick.{}".format(int(current_tick)),
            "process_id": "process.earth_wind_tick",
            "inputs": {
                "max_tiles_per_update": int(max_tiles_per_update),
            },
        },
        law_profile=law_profile(WIND_ALLOWED_PROCESSES),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=policy,
    )
    overlays = [dict(row) for row in _as_list(state.get("earth_wind_tile_overlays")) if isinstance(row, Mapping)]
    runtime_state = _as_map(state.get("earth_wind_runtime_state"))
    payload = {
        "result": str(result.get("result", "")).strip() or "unknown",
        "process_result": dict(result),
        "wind_params_id": wind_params_id,
        "wind_params_registry_hash": canonical_sha256(_load_json(repo_root, WIND_PARAMS_REGISTRY_REL)),
        "tick_window_start": int(runtime_state.get("last_tick_window_start", current_tick) or current_tick),
        "tick_window_end": int(runtime_state.get("last_tick_window_end", current_tick) or current_tick),
        "tick_window_span": int(runtime_state.get("last_tick_window_span", 1) or 1),
        "selected_tile_ids": [str(item).strip() for item in list(result.get("selected_tile_ids") or []) if str(item).strip()],
        "skipped_tile_ids": [str(item).strip() for item in list(result.get("skipped_tile_ids") or []) if str(item).strip()],
        "due_bucket_ids": [int(item) for item in list(result.get("due_bucket_ids") or [])],
        "wind_window_hash": str(result.get("wind_window_hash", "")).strip() or wind_window_hash(overlays),
        "overlay_hash": _wind_overlay_hash(overlays),
        "overlays": overlays,
        "state": state,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(
        dict(payload, state="<omitted>", overlays="<omitted>", process_result="<omitted>", deterministic_fingerprint="")
    )
    return payload


def verify_wind_window_replay(repo_root: str) -> dict:
    first = run_wind_tick_fixture(repo_root)
    second = run_wind_tick_fixture(repo_root)
    stable = (
        str(first.get("overlay_hash", "")).strip() == str(second.get("overlay_hash", "")).strip()
        and str(first.get("wind_window_hash", "")).strip() == str(second.get("wind_window_hash", "")).strip()
        and list(first.get("selected_tile_ids") or []) == list(second.get("selected_tile_ids") or [])
        and list(first.get("skipped_tile_ids") or []) == list(second.get("skipped_tile_ids") or [])
    )
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "wind_params_registry_hash": str(first.get("wind_params_registry_hash", "")).strip(),
        "wind_window_hash": str(first.get("wind_window_hash", "")).strip(),
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


def wind_latitude_band_report(repo_root: str) -> dict:
    fixture = generate_wind_tile_fixture(repo_root, current_tick=0)
    artifact_rows = _flatten_artifact_rows(_as_list(fixture.get("tiles")))
    wind_row = _earth_wind_params_row(repo_root)
    samples = {}
    for sample_id, target in (
        ("hadley", 5_000),
        ("ferrel", 45_000),
        ("polar", 75_000),
    ):
        artifact_row = _closest_artifact_by_latitude(artifact_rows, target_abs_latitude_mdeg=target)
        evaluation = evaluate_earth_tile_wind(
            artifact_row=artifact_row,
            wind_params_row=wind_row,
            current_tick=WIND_REPLAY_TICK,
        )
        vector = _as_map(evaluation.get("wind_vector"))
        samples[sample_id] = {
            "tile_object_id": str(evaluation.get("tile_object_id", "")).strip(),
            "latitude_mdeg": int(_as_int(evaluation.get("latitude_mdeg", 0), 0)),
            "wind_band_id": str(evaluation.get("wind_band_id", "")).strip(),
            "vector_x": int(_as_int(vector.get("x", 0), 0)),
            "vector_y": int(_as_int(vector.get("y", 0), 0)),
            "vector_sign_x": int(_vector_sign(_as_int(vector.get("x", 0), 0))),
            "vector_sign_y": int(_vector_sign(_as_int(vector.get("y", 0), 0))),
        }
    hadley = _as_map(samples.get("hadley"))
    ferrel = _as_map(samples.get("ferrel"))
    polar = _as_map(samples.get("polar"))
    valid = (
        str(hadley.get("wind_band_id", "")) == "wind.band.hadley"
        and str(ferrel.get("wind_band_id", "")) == "wind.band.ferrel"
        and str(polar.get("wind_band_id", "")) == "wind.band.polar"
        and int(_as_int(hadley.get("vector_sign_x", 0), 0)) == -1
        and int(_as_int(ferrel.get("vector_sign_x", 0), 0)) == 1
        and int(_as_int(polar.get("vector_sign_x", 0), 0)) == -1
    )
    report = {
        "result": "complete" if valid else "violation",
        "samples": dict(samples),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def wind_seasonal_shift_report(repo_root: str) -> dict:
    fixture = generate_wind_tile_fixture(repo_root, current_tick=0)
    artifact_rows = _flatten_artifact_rows(_as_list(fixture.get("tiles")))
    wind_row = _earth_wind_params_row(repo_root)
    extensions = _as_map(wind_row.get("extensions"))
    year_length_ticks = max(4, _as_int(extensions.get("year_length_ticks", 3650), 3650))
    candidate_ticks = sorted({0, year_length_ticks // 4, year_length_ticks // 2, (year_length_ticks * 3) // 4})
    by_tile: Dict[str, Dict[int, dict]] = {}
    for artifact_row in artifact_rows:
        tile_id = str(_as_map(artifact_row).get("tile_object_id", "")).strip()
        if not tile_id:
            continue
        evaluations = {}
        for tick in candidate_ticks:
            evaluation = evaluate_earth_tile_wind(
                artifact_row=artifact_row,
                wind_params_row=wind_row,
                current_tick=int(tick),
            )
            evaluations[int(tick)] = {
                "wind_band_id": str(evaluation.get("wind_band_id", "")).strip(),
                "band_shift_mdeg": int(_as_int(evaluation.get("band_shift_mdeg", 0), 0)),
                "effective_latitude_mdeg": int(_as_int(evaluation.get("effective_latitude_mdeg", 0), 0)),
            }
        by_tile[tile_id] = evaluations

    changed_tiles = []
    for tile_id in sorted(by_tile.keys()):
        evaluations = dict(by_tile.get(tile_id) or {})
        band_ids = sorted(set(str(_as_map(row).get("wind_band_id", "")).strip() for row in evaluations.values()))
        if len(band_ids) > 1:
            changed_tiles.append(tile_id)
    report = {
        "result": "complete" if changed_tiles else "violation",
        "candidate_ticks": [int(item) for item in candidate_ticks],
        "changed_band_tile_count": int(len(changed_tiles)),
        "changed_band_tile_ids": list(changed_tiles[:12]),
        "sample_tiles": {
            tile_id: dict(by_tile.get(tile_id) or {})
            for tile_id in list(changed_tiles[:3])
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def poll_advection_bias_report(repo_root: str) -> dict:
    fixture = run_wind_tick_fixture(repo_root, current_tick=WIND_REPLAY_TICK, last_processed_tick=None, max_tiles_per_update=128)
    overlays = [dict(row) for row in _as_list(fixture.get("overlays")) if isinstance(row, Mapping)]
    wind_overlay = {}
    for row in overlays:
        vector = _as_map(row.get("wind_vector"))
        magnitude = abs(_as_int(vector.get("x", 0), 0)) + abs(_as_int(vector.get("y", 0), 0))
        if magnitude > 0:
            wind_overlay = dict(row)
            break
    if not wind_overlay:
        wind_overlay = {"wind_vector": {"x": -288, "y": 70, "z": 0}}
    wind_vector = _as_map(wind_overlay.get("wind_vector"))
    field_rows = [
        build_field_cell(
            field_id="field.pollution.smoke_particulate_concentration",
            cell_id="cell.center",
            value=100,
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.pollution.smoke_particulate_concentration",
            cell_id="cell.west",
            value=0,
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.pollution.smoke_particulate_concentration",
            cell_id="cell.east",
            value=0,
            last_updated_tick=0,
        ),
        build_field_cell(
            field_id="field.wind_vector",
            cell_id="cell.center",
            value={
                "x": int(_as_int(wind_vector.get("x", 0), 0)),
                "y": int(_as_int(wind_vector.get("y", 0), 0)),
                "z": int(_as_int(wind_vector.get("z", 0), 0)),
            },
            value_kind="vector",
            last_updated_tick=0,
        ),
    ]
    pollutant_types_by_id = {
        "pollutant.smoke_particulate": {
            "pollutant_id": "pollutant.smoke_particulate",
            "default_dispersion_policy_id": "poll.policy.wind_enabled",
            "default_decay_model_id": "model.poll_decay_none",
            "extensions": {},
        }
    }
    policy_extensions = {
        "topology_profile_id": "geo.topology.r2_infinite",
        "metric_profile_id": "geo.metric.euclidean",
        "partition_profile_id": "geo.partition.grid_zd",
        "neighbor_radius": 1,
    }
    pollution_policies_enabled = {
        "poll.policy.wind_enabled": {
            "policy_id": "poll.policy.wind_enabled",
            "tier": "P1",
            "wind_modifier_enabled": True,
            "extensions": dict(policy_extensions),
        }
    }
    pollution_policies_disabled = {
        "poll.policy.wind_enabled": {
            "policy_id": "poll.policy.wind_enabled",
            "tier": "P1",
            "wind_modifier_enabled": False,
            "extensions": dict(policy_extensions),
        }
    }
    decay_models_by_id = {
        "model.poll_decay_none": {
            "model_id": "model.poll_decay_none",
            "kind": "none",
            "extensions": {},
        }
    }
    neighbor_map = {
        "cell.center": ["cell.east", "cell.west"],
        "cell.east": ["cell.center"],
        "cell.west": ["cell.center"],
    }
    enabled_a = evaluate_pollution_dispersion(
        current_tick=4,
        pollutant_types_by_id=pollutant_types_by_id,
        pollution_policies_by_id=pollution_policies_enabled,
        decay_models_by_id=decay_models_by_id,
        pollution_source_event_rows=[],
        processed_source_event_ids=[],
        field_cell_rows=field_rows,
        neighbor_map_by_cell=neighbor_map,
        wind_field_id="field.wind_vector",
        max_cell_updates_per_tick=16,
    )
    enabled_b = evaluate_pollution_dispersion(
        current_tick=4,
        pollutant_types_by_id=pollutant_types_by_id,
        pollution_policies_by_id=pollution_policies_enabled,
        decay_models_by_id=decay_models_by_id,
        pollution_source_event_rows=[],
        processed_source_event_ids=[],
        field_cell_rows=field_rows,
        neighbor_map_by_cell=neighbor_map,
        wind_field_id="field.wind_vector",
        max_cell_updates_per_tick=16,
    )
    calm = evaluate_pollution_dispersion(
        current_tick=4,
        pollutant_types_by_id=pollutant_types_by_id,
        pollution_policies_by_id=pollution_policies_disabled,
        decay_models_by_id=decay_models_by_id,
        pollution_source_event_rows=[],
        processed_source_event_ids=[],
        field_cell_rows=field_rows,
        neighbor_map_by_cell=neighbor_map,
        wind_field_id="field.wind_vector",
        max_cell_updates_per_tick=16,
    )
    enabled_hash = canonical_sha256(
        {
            "field_updates": list(enabled_a.get("field_updates") or []),
            "dispersion_step_rows": list(enabled_a.get("dispersion_step_rows") or []),
        }
    )
    stable = canonical_sha256(enabled_a) == canonical_sha256(enabled_b)
    enabled_step = _as_map((list(enabled_a.get("dispersion_step_rows") or []) or [{}])[0])
    calm_step = _as_map((list(calm.get("dispersion_step_rows") or []) or [{}])[0])
    changed = int(_as_int(enabled_step.get("diffusion_term", 0), 0)) != int(_as_int(calm_step.get("diffusion_term", 0), 0))
    report = {
        "result": "complete" if stable and changed else "violation",
        "stable_across_repeated_runs": bool(stable),
        "wind_effect_observed": bool(changed),
        "enabled_diffusion_term": int(_as_int(enabled_step.get("diffusion_term", 0), 0)),
        "calm_diffusion_term": int(_as_int(calm_step.get("diffusion_term", 0), 0)),
        "enabled_wind_field_id": str(_as_map(enabled_step.get("extensions")).get("wind_field_id", "")).strip(),
        "enabled_hash": enabled_hash,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    repo_root = os.path.normpath(os.path.abspath(REPO_ROOT_HINT))
    report = verify_wind_window_replay(repo_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
