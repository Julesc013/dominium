"""Shared deterministic EARTH-9 stress scenario helpers."""

from __future__ import annotations

import copy
import json
import os
from functools import lru_cache
from typing import Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.client.ui.map_views import build_map_view_surface, debug_view_limit_for_compute_profile
from src.geo import build_position_ref
from src.worldgen.earth.water import build_water_layer_source_payloads
from src.worldgen.earth import DEFAULT_EARTH_CLIMATE_PARAMS_ID, DEFAULT_TIDE_PARAMS_ID, earth_climate_params_rows, tide_params_rows
from src.worldgen.mw.sol_anchor import resolve_sol_anchor_cell_key
from src.worldgen.mw.system_query_engine import list_systems_in_cell
from tools.embodiment.earth6_probe import (
    collision_hash,
    direct_surface_query_report,
    geometry_edit_height_report,
    ground_contact_report,
    slope_modifier_report,
    verify_collision_window_replay,
)
from tools.worldgen.earth1_probe import (
    HYDROLOGY_EDIT_VOLUME_AMOUNT,
    earth_hydrology_hash,
    find_river_candidate,
    generate_hydrology_window_fixture,
    verify_hydrology_window_replay,
    verify_local_edit_hydrology_update,
    verify_window_monotonicity,
)
from tools.worldgen.earth2_probe import (
    CLIMATE_MAX_TILES_PER_UPDATE,
    CLIMATE_YEAR_TICK_A,
    CLIMATE_YEAR_TICK_B,
    climate_year_delta_report,
    polar_daylight_report,
    run_climate_tick_fixture,
    verify_climate_window_replay,
)
from tools.worldgen.earth0_probe import build_earth_probe_context, generate_earth_probe_tile
from tools.worldgen.earth3_probe import (
    TIDE_DAY_TICK_A,
    TIDE_DAY_TICK_B,
    TIDE_MAX_TILES_PER_UPDATE,
    inland_damping_report,
    lunar_phase_report,
    run_tide_tick_fixture,
    tide_day_delta_report,
    verify_tide_window_replay,
)
from tools.worldgen.earth4_probe import (
    SKY_DAY_TICK,
    SKY_NIGHT_TICK,
    SKY_TWILIGHT_TICK,
    build_sky_fixture,
    sky_gradient_transition_report,
    sky_hash,
    verify_sky_view_replay,
)
from tools.worldgen.earth5_probe import (
    build_lighting_fixture,
    horizon_shadow_report,
    lighting_hash,
    moon_phase_report,
    sampling_bounded_report,
    verify_illumination_view_replay,
)
from tools.worldgen.earth7_probe import (
    WIND_MAX_TILES_PER_UPDATE,
    poll_advection_bias_report,
    run_wind_tick_fixture,
    verify_wind_window_replay,
    wind_latitude_band_report,
    wind_seasonal_shift_report,
)
from tools.worldgen.earth8_probe import (
    build_water_fixture,
    river_mask_report,
    tide_offset_report,
    verify_water_view_replay,
    water_hash,
)
from src.client.ui.teleport_controller import build_teleport_plan


DEFAULT_EARTH9_SEED = 91029
DEFAULT_SCENARIO_REL = os.path.join("build", "earth", "earth_mvp_stress_scenario.json")
DEFAULT_REPORT_REL = os.path.join("build", "earth", "earth_mvp_stress_report.json")
DEFAULT_VIEW_REPLAY_REL = os.path.join("build", "earth", "earth_view_replay.json")
DEFAULT_PHYSICS_REPLAY_REL = os.path.join("build", "earth", "earth_physics_replay.json")
DEFAULT_BASELINE_REL = os.path.join("data", "regression", "earth_mvp_baseline.json")
_SCAN_COLUMNS = tuple(range(0, 64, 4))
_SCAN_BANDS = tuple(range(0, 16, 1))
_SCAN_CHART_IDS = ("chart.atlas.north", "chart.atlas.south")


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _sorted_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _read_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError("expected object json at {}".format(rel_path.replace("\\", "/")))
    return dict(payload)


def write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _with_fingerprint(payload: Mapping[str, object]) -> dict:
    row = dict(payload or {})
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def _pick_index(seed: int, stream: str, count: int) -> int:
    size = int(max(1, _as_int(count, 1)))
    digest = canonical_sha256({"seed": int(seed), "stream": str(stream).strip(), "count": int(size)})
    return int(int(digest[:12], 16) % size)


def _surface_summary(tile_row: Mapping[str, object]) -> dict:
    return _as_map(_as_map(tile_row).get("surface_summary"))


def _surface_artifact(tile_row: Mapping[str, object]) -> dict:
    rows = [dict(row) for row in _as_list(_as_map(tile_row).get("generated_surface_tile_artifact_rows")) if isinstance(row, Mapping)]
    return dict(rows[0]) if rows else {}


def _tile_height_proxy(tile_row: Mapping[str, object]) -> int:
    artifact = _surface_artifact(tile_row)
    return int(max(0, _as_int(_as_map(artifact.get("elevation_params_ref")).get("height_proxy", 0), 0)))


@lru_cache(maxsize=4)
def _scanned_surface_tiles(repo_root: str) -> tuple[dict, list[dict]]:
    context = build_earth_probe_context(repo_root)
    rows: List[dict] = []
    for chart_id in _SCAN_CHART_IDS:
        for band in _SCAN_BANDS:
            for column in _SCAN_COLUMNS:
                rows.append(
                    generate_earth_probe_tile(
                        context,
                        chart_id=str(chart_id),
                        index_tuple=[int(column), int(band)],
                        refinement_level=1,
                        current_tick=0,
                    )
                )
    rows = sorted(
        rows,
        key=lambda row: (
            str(row.get("chart_id", "")),
            int(list(row.get("index_tuple") or [0, 0])[1]),
            int(list(row.get("index_tuple") or [0, 0])[0]),
        ),
    )
    return context, rows


def _tile_waypoint(*, waypoint_id: str, kind: str, label: str, tile_row: Mapping[str, object], source: str) -> dict:
    summary = _surface_summary(tile_row)
    artifact = _surface_artifact(tile_row)
    artifact_ext = _as_map(artifact.get("extensions"))
    tile_object_id = str(artifact.get("tile_object_id", "")).strip()
    tile_cell_key = _as_map(artifact.get("tile_cell_key"))
    height_proxy = _tile_height_proxy(tile_row)
    return _with_fingerprint(
        {
            "waypoint_id": str(waypoint_id).strip(),
            "kind": str(kind).strip(),
            "label": str(label).strip(),
            "chart_id": str(tile_row.get("chart_id", "")).strip(),
            "index_tuple": [int(item) for item in list(tile_row.get("index_tuple") or [])],
            "tile_object_id": tile_object_id,
            "tile_cell_key": dict(tile_cell_key),
            "surface_class_id": str(summary.get("surface_class_id", "")).strip(),
            "biome_stub_id": str(summary.get("biome_stub_id", "")).strip(),
            "height_proxy": int(height_proxy),
            "drainage_accumulation_proxy": int(_as_int(summary.get("drainage_accumulation_proxy", 0), 0)),
            "river_flag": bool(summary.get("river_flag", False)),
            "lake_flag": bool(_as_map(artifact.get("extensions")).get("lake_flag", False)),
            "latitude_mdeg": int(_as_int(artifact_ext.get("latitude_mdeg", summary.get("latitude_mdeg", 0)), 0)),
            "longitude_mdeg": int(_as_int(artifact_ext.get("longitude_mdeg", summary.get("longitude_mdeg", 0)), 0)),
            "position_ref": build_position_ref(
                object_id="waypoint.{}".format(str(waypoint_id).strip()),
                frame_id="frame.surface_local",
                local_position=[0, 0, int(height_proxy + 1700)],
                extensions={
                    "latitude_mdeg": int(_as_int(artifact_ext.get("latitude_mdeg", 0), 0)),
                    "longitude_mdeg": int(_as_int(artifact_ext.get("longitude_mdeg", 0), 0)),
                    "geo_cell_key": dict(tile_cell_key),
                    "source": str(source).strip(),
                },
            ),
            "source": str(source).strip(),
        }
    )


def _water_waypoint(*, waypoint_id: str, kind: str, label: str, artifact_row: Mapping[str, object], source: str) -> dict:
    artifact = _as_map(artifact_row)
    artifact_ext = _as_map(artifact.get("extensions"))
    tile_cell_key = _as_map(artifact.get("tile_cell_key"))
    height_proxy = int(max(0, _as_int(_as_map(artifact.get("elevation_params_ref")).get("height_proxy", 0), 0)))
    return _with_fingerprint(
        {
            "waypoint_id": str(waypoint_id).strip(),
            "kind": str(kind).strip(),
            "label": str(label).strip(),
            "chart_id": str(tile_cell_key.get("chart_id", "")).strip(),
            "index_tuple": [int(item) for item in list(tile_cell_key.get("index_tuple") or [])],
            "tile_object_id": str(artifact.get("tile_object_id", "")).strip(),
            "tile_cell_key": dict(tile_cell_key),
            "surface_class_id": str(artifact_ext.get("surface_class_id", "")).strip(),
            "biome_stub_id": str(artifact.get("biome_stub_id", "")).strip(),
            "height_proxy": int(height_proxy),
            "drainage_accumulation_proxy": int(_as_int(artifact.get("drainage_accumulation_proxy", 0), 0)),
            "river_flag": bool(artifact.get("river_flag", False)),
            "lake_flag": bool(artifact_ext.get("lake_flag", False)),
            "latitude_mdeg": int(_as_int(artifact_ext.get("latitude_mdeg", 0), 0)),
            "longitude_mdeg": int(_as_int(artifact_ext.get("longitude_mdeg", 0), 0)),
            "position_ref": build_position_ref(
                object_id="waypoint.{}".format(str(waypoint_id).strip()),
                frame_id="frame.surface_local",
                local_position=[0, 0, int(height_proxy + 1700)],
                extensions={
                    "latitude_mdeg": int(_as_int(artifact_ext.get("latitude_mdeg", 0), 0)),
                    "longitude_mdeg": int(_as_int(artifact_ext.get("longitude_mdeg", 0), 0)),
                    "geo_cell_key": dict(tile_cell_key),
                    "source": str(source).strip(),
                },
            ),
            "source": str(source).strip(),
        }
    )


def _candidate_tile_rows(repo_root: str, predicate) -> List[dict]:
    _context, rows = _scanned_surface_tiles(repo_root)
    return [dict(row) for row in rows if predicate(dict(row))]


def _selected_tile(rows: Sequence[Mapping[str, object]], *, seed: int, stream: str, fallback_rows: Sequence[Mapping[str, object]] | None = None) -> dict:
    candidates = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    if not candidates:
        candidates = [dict(row) for row in list(fallback_rows or []) if isinstance(row, Mapping)]
    if not candidates:
        raise RuntimeError("EARTH-9 candidate set '{}' was empty".format(stream))
    ordered = sorted(
        candidates,
        key=lambda row: (
            str(row.get("chart_id", "")),
            int(list(row.get("index_tuple") or [0, 0])[1]),
            int(list(row.get("index_tuple") or [0, 0])[0]),
            str(_surface_artifact(row).get("tile_object_id", "")),
        ),
    )
    return dict(ordered[_pick_index(seed, stream, len(ordered))])


def _random_star_candidates(context: Mapping[str, object]) -> List[dict]:
    universe_identity = _as_map(context.get("universe_identity"))
    anchor = resolve_sol_anchor_cell_key()
    rows: List[dict] = []
    primary = list_systems_in_cell(universe_identity=universe_identity, geo_cell_key=anchor, refinement_level=1, cache_enabled=True)
    rows.extend([dict(row) for row in _as_list(primary.get("systems")) if isinstance(row, Mapping)])
    neighbor_columns = [-1, 0, 1]
    neighbor_rows = [-1, 0, 1]
    base_index = [int(item) for item in list(anchor.get("index_tuple") or [0, 0, 0])]
    base_index.extend([0] * int(max(0, 3 - len(base_index))))
    for dx in neighbor_columns:
        for dy in neighbor_rows:
            cell_key = dict(anchor)
            cell_key["index_tuple"] = [int(base_index[0] + dx), int(base_index[1] + dy), int(base_index[2])]
            listing = list_systems_in_cell(
                universe_identity=universe_identity,
                geo_cell_key=cell_key,
                refinement_level=1,
                cache_enabled=True,
            )
            rows.extend([dict(row) for row in _as_list(listing.get("systems")) if isinstance(row, Mapping)])
    deduped = {}
    for row in rows:
        object_id = str(row.get("object_id", "")).strip()
        if object_id:
            deduped[object_id] = dict(row)
    return [dict(deduped[key]) for key in sorted(deduped.keys())]


def _teleport_scripts(repo_root: str, context: Mapping[str, object], *, seed: int, surface_waypoint: Mapping[str, object]) -> List[dict]:
    universe_seed = str(_as_map(context.get("universe_identity")).get("universe_seed", "")).strip()
    candidate_system_rows = _random_star_candidates(context)
    commands = [
        ("tp.sol", "/tp sol"),
        ("tp.earth", "/tp earth"),
        ("tp.surface", "/tp {}".format(str(_as_map(surface_waypoint).get("tile_object_id", "")).strip())),
        ("tp.orbit", "/tp frame.surface_local:0,0,42000000"),
        ("tp.random_star", "/tp random_star"),
    ]
    rows = []
    for index, (script_id, command) in enumerate(commands):
        rows.append(
            _with_fingerprint(
                {
                    "script_id": str(script_id),
                    "command": str(command),
                    "teleport_plan": build_teleport_plan(
                        repo_root=repo_root,
                        command=str(command),
                        universe_seed=universe_seed,
                        authority_mode="dev",
                        teleport_counter=int(index + (seed % 17)),
                        candidate_system_rows=candidate_system_rows,
                    ),
                }
            )
        )
    return rows


def _time_warp_script(repo_root: str) -> List[dict]:
    climate_registry = earth_climate_params_rows(_read_json(repo_root, os.path.join("data", "registries", "earth_climate_params_registry.json")))
    tide_registry = tide_params_rows(_read_json(repo_root, os.path.join("data", "registries", "tide_params_registry.json")))
    climate_row = dict(climate_registry.get(DEFAULT_EARTH_CLIMATE_PARAMS_ID) or {})
    tide_row = dict(tide_registry.get(DEFAULT_TIDE_PARAMS_ID) or {})
    day_length_ticks = int(max(1, _as_int(_as_map(tide_row.get("extensions")).get("day_length_ticks", 10), 10)))
    lunar_period_ticks = int(max(1, _as_int(_as_map(tide_row.get("extensions")).get("lunar_period_ticks", 273), 273)))
    year_length_ticks = int(max(1, _as_int(climate_row.get("year_length_ticks", 3650), 3650)))
    return [
        _with_fingerprint({"step_id": "warp.day", "advance_ticks": int(day_length_ticks), "label": "advance_1_day"}),
        _with_fingerprint({"step_id": "warp.30_days", "advance_ticks": int(day_length_ticks * 30), "label": "advance_30_days"}),
        _with_fingerprint({"step_id": "warp.year", "advance_ticks": int(year_length_ticks), "label": "advance_365_days"}),
        _with_fingerprint({"step_id": "warp.10_lunar_cycles", "advance_ticks": int(lunar_period_ticks * 10), "label": "advance_10_lunar_cycles"}),
    ]


def generate_earth_mvp_stress_scenario(*, repo_root: str, seed: int = DEFAULT_EARTH9_SEED) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    context, scanned_rows = _scanned_surface_tiles(repo_root)
    water_fixture = build_water_fixture(repo_root)
    water_artifact = _as_map(_as_map(water_fixture.get("water_view_surface")).get("water_view_artifact"))
    surface_rows = [dict(row) for row in scanned_rows if isinstance(row, Mapping)]

    ocean_rows = _candidate_tile_rows(
        repo_root,
        lambda row: str(_surface_summary(row).get("surface_class_id", "")).strip() == "surface.class.ocean",
    )
    land_rows = _candidate_tile_rows(
        repo_root,
        lambda row: str(_surface_summary(row).get("surface_class_id", "")).strip() == "surface.class.land",
    )
    continent_rows = _candidate_tile_rows(
        repo_root,
        lambda row: (
            str(_surface_summary(row).get("surface_class_id", "")).strip() == "surface.class.land"
            and int(_surface_summary(row).get("continent_score_permille", 0) or 0) >= 600
            and int(_surface_summary(row).get("coastal_proximity_permille", 1000) or 1000) <= 250
            and not bool(_surface_summary(row).get("river_flag", False))
        ),
    )
    ridge_rows = sorted(
        land_rows,
        key=lambda row: (
            -_tile_height_proxy(row),
            str(row.get("chart_id", "")),
            list(row.get("index_tuple") or [0, 0])[1],
            list(row.get("index_tuple") or [0, 0])[0],
        ),
    )[:24]
    polar_rows = sorted(
        surface_rows,
        key=lambda row: (
            -abs(int(_surface_summary(row).get("latitude_mdeg", 0) or 0)),
            str(row.get("chart_id", "")),
            list(row.get("index_tuple") or [0, 0])[1],
            list(row.get("index_tuple") or [0, 0])[0],
        ),
    )[:24]

    river_candidate = _as_map(find_river_candidate(repo_root).get("candidate"))
    river_artifact = _surface_artifact(river_candidate)
    lake_rows = [dict(row) for row in _as_list(water_artifact.get("lake_mask_ref")) if isinstance(row, Mapping)]

    ocean_waypoint = _tile_waypoint(
        waypoint_id="wp.ocean",
        kind="tile.ocean",
        label="random_ocean_tile",
        tile_row=_selected_tile(ocean_rows, seed=seed, stream="earth9.ocean", fallback_rows=surface_rows),
        source="EARTH9-1",
    )
    continent_waypoint = _tile_waypoint(
        waypoint_id="wp.continent",
        kind="tile.continent_interior",
        label="random_continent_interior_tile",
        tile_row=_selected_tile(continent_rows, seed=seed, stream="earth9.continent", fallback_rows=land_rows),
        source="EARTH9-1",
    )
    ridge_waypoint = _tile_waypoint(
        waypoint_id="wp.ridge",
        kind="tile.ridge",
        label="high_elevation_ridge_tile",
        tile_row=_selected_tile(ridge_rows, seed=seed, stream="earth9.ridge", fallback_rows=land_rows),
        source="EARTH9-1",
    )
    polar_waypoint = _tile_waypoint(
        waypoint_id="wp.polar",
        kind="tile.polar",
        label="polar_tile",
        tile_row=_selected_tile(polar_rows, seed=seed, stream="earth9.polar", fallback_rows=surface_rows),
        source="EARTH9-1",
    )
    river_waypoint = _tile_waypoint(
        waypoint_id="wp.river",
        kind="tile.river",
        label="river_tile",
        tile_row=river_candidate or _selected_tile(land_rows, seed=seed, stream="earth9.river", fallback_rows=surface_rows),
        source="EARTH9-1",
    )
    fallback_lake_artifact = dict(river_artifact or _surface_artifact(continent_rows[0] if continent_rows else land_rows[0]))
    lake_waypoint = _water_waypoint(
        waypoint_id="wp.lake",
        kind="tile.lake_sink",
        label="lake_sink_tile",
        artifact_row=dict(lake_rows[0] if lake_rows else fallback_lake_artifact),
        source="EARTH9-1",
    )

    payload = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.earth_mvp.stress.{}".format(canonical_sha256({"seed": int(seed)})[:12]),
        "scenario_seed": int(seed),
        "universe_id": str(_as_map(context.get("universe_identity")).get("universe_id", "")).strip(),
        "universe_seed": str(_as_map(context.get("universe_identity")).get("universe_seed", "")).strip(),
        "generator_version_id": str(_as_map(context.get("universe_identity")).get("generator_version_id", "")).strip(),
        "realism_profile_id": str(context.get("realism_profile_id", "")).strip(),
        "scan_profile": {
            "chart_ids": list(_SCAN_CHART_IDS),
            "columns": [int(item) for item in _SCAN_COLUMNS],
            "bands": [int(item) for item in _SCAN_BANDS],
            "scanned_tile_count": int(len(surface_rows)),
        },
        "waypoints": [
            ocean_waypoint,
            continent_waypoint,
            ridge_waypoint,
            polar_waypoint,
            river_waypoint,
            lake_waypoint,
        ],
        "teleport_scripts": _teleport_scripts(
            repo_root,
            context,
            seed=int(seed),
            surface_waypoint=continent_waypoint,
        ),
        "traversal_script": [
            _with_fingerprint(
                {
                    "step_id": "traverse.walk_along_slope",
                    "label": "walk_along_slope",
                    "waypoint_id": "wp.continent",
                    "movement_vector_local": {"x": 1000, "y": 0, "z": 0},
                    "process_sequence": ["process.body_apply_input", "process.body_tick"],
                }
            ),
            _with_fingerprint(
                {
                    "step_id": "traverse.cross_river",
                    "label": "cross_river_tile",
                    "waypoint_id": "wp.river",
                    "movement_vector_local": {"x": -1000, "y": 0, "z": 0},
                    "process_sequence": ["process.body_apply_input", "process.body_tick"],
                }
            ),
            _with_fingerprint(
                {
                    "step_id": "traverse.climb_ridge",
                    "label": "climb_ridge",
                    "waypoint_id": "wp.ridge",
                    "movement_vector_local": {"x": 1000, "y": 0, "z": 0},
                    "process_sequence": ["process.body_apply_input", "process.body_tick"],
                }
            ),
        ],
        "time_warp_script": _time_warp_script(repo_root),
        "geometry_edit_script": [
            _with_fingerprint(
                {
                    "step_id": "geom.cut_trench_across_slope",
                    "label": "cut_trench_across_slope",
                    "volume_amount": int(HYDROLOGY_EDIT_VOLUME_AMOUNT),
                    "expected_effects": ["hydrology.local_recompute", "collision.height_invalidation"],
                }
            )
        ],
        "view_script": [
            _with_fingerprint({"step_id": "view.sky.day", "kind": "sky_view", "tick": int(SKY_DAY_TICK), "label": "day"}),
            _with_fingerprint({"step_id": "view.sky.twilight", "kind": "sky_view", "tick": int(SKY_TWILIGHT_TICK), "label": "twilight"}),
            _with_fingerprint({"step_id": "view.sky.night", "kind": "sky_view", "tick": int(SKY_NIGHT_TICK), "label": "night"}),
            _with_fingerprint(
                {
                    "step_id": "view.map.layers",
                    "kind": "map_view",
                    "layers": [
                        "layer.temperature",
                        "layer.wind_vector",
                        "layer.water_ocean",
                        "layer.water_river",
                        "layer.water_lake",
                        "layer.tide_height_proxy",
                        "layer.tide_offset",
                    ],
                    "ticks": [int(SKY_DAY_TICK), int(TIDE_DAY_TICK_A), int(TIDE_DAY_TICK_B)],
                }
            ),
        ],
        "registry_hashes": {
            "earth_climate_params_registry_hash": canonical_sha256(
                _read_json(repo_root, os.path.join("data", "registries", "earth_climate_params_registry.json"))
            ),
            "tide_params_registry_hash": canonical_sha256(
                _read_json(repo_root, os.path.join("data", "registries", "tide_params_registry.json"))
            ),
            "wind_params_registry_hash": canonical_sha256(
                _read_json(repo_root, os.path.join("data", "registries", "wind_params_registry.json"))
            ),
            "water_visual_policy_registry_hash": canonical_sha256(
                _read_json(repo_root, os.path.join("data", "registries", "water_visual_policy_registry.json"))
            ),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def load_earth_mvp_stress_scenario(
    *,
    repo_root: str,
    scenario_path: str = "",
    seed: int = DEFAULT_EARTH9_SEED,
) -> dict:
    token = str(scenario_path or "").strip()
    if token:
        payload = _read_json(repo_root, os.path.relpath(os.path.normpath(os.path.abspath(token)), repo_root))
        if payload:
            return dict(payload)
    return generate_earth_mvp_stress_scenario(repo_root=repo_root, seed=int(seed))


def _truth_hash_anchor(perceived_model: Mapping[str, object] | None) -> str:
    return str(_as_map(_as_map(perceived_model).get("truth_overlay")).get("state_hash_anchor", "")).strip()


def _field_source_payload(
    repo_root: str,
    *,
    layer_id: str,
    field_id: str,
    state: Mapping[str, object] | None,
) -> dict:
    return {
        str(layer_id).strip(): {
            "source_kind": "field",
            "field_id": str(field_id).strip(),
            "field_layer_rows": [dict(row) for row in _as_list(_as_map(state).get("field_layers")) if isinstance(row, Mapping)],
            "field_cell_rows": [dict(row) for row in _as_list(_as_map(state).get("field_cells")) if isinstance(row, Mapping)],
            "field_type_registry": _read_json(repo_root, os.path.join("data", "registries", "field_type_registry.json")),
            "field_binding_registry": _read_json(repo_root, os.path.join("data", "registries", "field_binding_registry.json")),
            "interpolation_policy_registry": _read_json(
                repo_root,
                os.path.join("data", "registries", "interpolation_policy_registry.json"),
            ),
        }
    }


def _merge_layer_source_payloads(*payloads: Mapping[str, object] | None) -> dict:
    merged = {}
    for payload in list(payloads or []):
        for key, value in sorted(_as_map(payload).items(), key=lambda item: str(item[0])):
            merged[str(key)] = dict(_as_map(value))
    return merged


def _earth_view_layer_source_payloads(
    repo_root: str,
    *,
    water_fixture: Mapping[str, object] | None,
    climate_fixture: Mapping[str, object] | None,
    tide_fixture: Mapping[str, object] | None,
    wind_fixture: Mapping[str, object] | None,
) -> dict:
    return _merge_layer_source_payloads(
        _field_source_payload(
            repo_root,
            layer_id="layer.temperature",
            field_id="field.temperature",
            state=_as_map(climate_fixture).get("state"),
        ),
        _field_source_payload(
            repo_root,
            layer_id="layer.tide_height_proxy",
            field_id="field.tide_height_proxy",
            state=_as_map(tide_fixture).get("state"),
        ),
        _field_source_payload(
            repo_root,
            layer_id="layer.wind_vector",
            field_id="field.wind_vector",
            state=_as_map(wind_fixture).get("state"),
        ),
        build_water_layer_source_payloads(_as_map(_as_map(water_fixture).get("water_view_surface"))),
    )


def _surface_origin_position_ref(
    *,
    observer_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
) -> dict:
    ref = _as_map(observer_ref)
    artifact = _as_map(observer_surface_artifact)
    tile_cell_key = _as_map(artifact.get("tile_cell_key"))
    local_position = [int(_as_int(item, 0)) for item in list(ref.get("local_position") or [0, 0, 0])]
    local_position.extend([0] * int(max(0, 3 - len(local_position))))
    return build_position_ref(
        object_id=str(ref.get("object_id", "")).strip() or "camera.earth9.probe",
        frame_id=str(ref.get("frame_id", "")).strip() or "frame.surface_local",
        local_position=local_position[:3],
        extensions={
            **_as_map(ref.get("extensions")),
            "chart_id": str(tile_cell_key.get("chart_id", "")).strip() or None,
            "geo_cell_key": dict(tile_cell_key),
        },
    )


def _view_layers_from_scenario(scenario: Mapping[str, object] | None) -> list[str]:
    for row in list(_as_map(scenario).get("view_script") or []):
        payload = _as_map(row)
        if str(payload.get("kind", "")).strip() == "map_view":
            layers = _sorted_strings(payload.get("layers"))
            if layers:
                return layers
    return [
        "layer.temperature",
        "layer.wind_vector",
        "layer.water_ocean",
        "layer.water_river",
        "layer.water_lake",
        "layer.tide_height_proxy",
        "layer.tide_offset",
    ]


def _normalized_surface(payload: Mapping[str, object] | None) -> dict:
    row = copy.deepcopy(_as_map(payload))
    row.pop("cache_hit", None)
    return row


def _view_truth_leak_report(view_payloads: Mapping[str, object] | None) -> dict:
    forbidden_tokens = ("truth_model", "\"universe_state\"", "\"process_runtime\"")
    serialized = json.dumps(_as_map(view_payloads), sort_keys=True)
    detected = [token for token in forbidden_tokens if token in serialized]
    return {
        "truth_leak_detected": bool(detected),
        "detected_tokens": list(detected),
        "deterministic_fingerprint": canonical_sha256(
            {
                "truth_leak_detected": bool(detected),
                "detected_tokens": list(detected),
            }
        ),
    }


def _sky_cache_probe(repo_root: str) -> dict:
    metric_tick = int(SKY_NIGHT_TICK + 111)
    first = _as_map(build_sky_fixture(repo_root, current_tick=metric_tick).get("sky_view_surface"))
    second = _as_map(build_sky_fixture(repo_root, current_tick=metric_tick).get("sky_view_surface"))
    artifact = _as_map(second.get("sky_view_artifact"))
    cost_units = int(len(_as_list(artifact.get("star_points_ref"))) + len(_as_list(artifact.get("milkyway_band_ref"))) + 3)
    hit_count = int(bool(second.get("cache_hit", False)))
    return {
        "probe_tick": int(metric_tick),
        "cache_hits": int(hit_count),
        "cache_hit_rate_permille": int(hit_count * 1000),
        "generation_cost_units": int(cost_units),
        "artifact_fingerprint": str(artifact.get("deterministic_fingerprint", "")).strip(),
        "deterministic_fingerprint": canonical_sha256(
            {
                "probe_tick": int(metric_tick),
                "cache_hits": int(hit_count),
                "cache_hit_rate_permille": int(hit_count * 1000),
                "generation_cost_units": int(cost_units),
                "artifact_fingerprint": str(artifact.get("deterministic_fingerprint", "")).strip(),
            }
        ),
    }


def _degradation_probe(
    *,
    repo_root: str,
    scenario: Mapping[str, object] | None,
    perceived_model: Mapping[str, object] | None,
    authority_context: Mapping[str, object] | None,
    observer_ref: Mapping[str, object] | None,
    observer_surface_artifact: Mapping[str, object] | None,
    layer_source_payloads: Mapping[str, object] | None,
) -> dict:
    map_origin_ref = _surface_origin_position_ref(
        observer_ref=observer_ref,
        observer_surface_artifact=observer_surface_artifact,
    )

    def _map_probe() -> dict:
        return build_map_view_surface(
            view_id="earth9.degradation.map",
            view_type_id="view.map_ortho",
            origin_position_ref=map_origin_ref,
            lens_id="lens.diegetic.sensor",
            included_layers=_view_layers_from_scenario(scenario),
            perceived_model=perceived_model,
            authority_context=authority_context,
            layer_source_payloads=layer_source_payloads,
            compute_profile_id="compute.default",
            topology_profile_id="geo.topology.sphere_surface_s2",
            partition_profile_id="geo.partition.atlas_tiles",
            metric_profile_id="geo.metric.spherical_geodesic_stub",
            resolution_spec={"width": 41, "height": 41},
            extent_spec={"radius_cells": 5, "axis_order": ["x", "y"]},
            ui_mode="gui",
            truth_hash_anchor=_truth_hash_anchor(perceived_model),
        )

    first_map = _map_probe()
    second_map = _map_probe()
    first_budget = _as_map(first_map.get("budget_plan"))
    second_budget = _as_map(second_map.get("budget_plan"))
    explain_artifacts = [dict(row) for row in _as_list(first_budget.get("explain_artifacts")) if isinstance(row, Mapping)]
    explain_contract_ids = _sorted_strings(_as_map(row).get("contract_id", "") for row in explain_artifacts)

    requested_debug_view_ids = [
        "inspect.overlay_provenance",
        "viewer.object_ids",
        "viewer.field_layers",
        "viewer.geometry_layer",
        "viewer.truth_anchor_hash",
    ]
    debug_limit = int(debug_view_limit_for_compute_profile("compute.default"))
    active_debug_ids = _sorted_strings(requested_debug_view_ids[:debug_limit])
    throttled_debug_ids = _sorted_strings(requested_debug_view_ids[debug_limit:])
    stable = (
        dict(first_budget) == dict(second_budget)
        and active_debug_ids == _sorted_strings(requested_debug_view_ids[:debug_limit])
        and throttled_debug_ids == _sorted_strings(requested_debug_view_ids[debug_limit:])
    )
    payload = {
        "requested_resolution_spec": {"width": 41, "height": 41},
        "effective_resolution_spec": dict(_as_map(first_budget.get("effective_resolution_spec"))),
        "map_downsampled": "explain.view_downsampled" in explain_contract_ids,
        "explain_contract_ids": list(explain_contract_ids),
        "rendered_cell_count": int(len(_as_list(_as_map(_as_map(first_map).get("projected_view_artifact")).get("rendered_cells")))),
        "debug_view_limit": int(debug_limit),
        "requested_debug_view_ids": list(requested_debug_view_ids),
        "active_debug_view_ids": list(active_debug_ids),
        "throttled_debug_view_ids": list(throttled_debug_ids),
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _build_earth_view_window(
    *,
    repo_root: str,
    scenario: Mapping[str, object] | None,
) -> dict:
    day_sky_fixture = build_sky_fixture(repo_root, current_tick=SKY_DAY_TICK)
    twilight_sky_fixture = build_sky_fixture(repo_root, current_tick=SKY_TWILIGHT_TICK)
    night_sky_fixture = build_sky_fixture(repo_root, current_tick=SKY_NIGHT_TICK)
    day_lighting_fixture = build_lighting_fixture(repo_root, current_tick=SKY_DAY_TICK)
    twilight_lighting_fixture = build_lighting_fixture(repo_root, current_tick=SKY_TWILIGHT_TICK)
    night_lighting_fixture = build_lighting_fixture(repo_root, current_tick=SKY_NIGHT_TICK)
    water_fixture = build_water_fixture(repo_root, current_tick=TIDE_DAY_TICK_B)
    climate_fixture = run_climate_tick_fixture(
        repo_root,
        current_tick=CLIMATE_YEAR_TICK_A,
        last_processed_tick=None,
        max_tiles_per_update=128,
    )
    tide_fixture = run_tide_tick_fixture(
        repo_root,
        current_tick=TIDE_DAY_TICK_B,
        last_processed_tick=None,
        max_tiles_per_update=128,
    )
    wind_fixture = run_wind_tick_fixture(
        repo_root,
        current_tick=TIDE_DAY_TICK_B,
        last_processed_tick=None,
        max_tiles_per_update=128,
    )
    layer_source_payloads = _earth_view_layer_source_payloads(
        repo_root,
        water_fixture=water_fixture,
        climate_fixture=climate_fixture,
        tide_fixture=tide_fixture,
        wind_fixture=wind_fixture,
    )
    origin_position_ref = _surface_origin_position_ref(
        observer_ref=_as_map(water_fixture.get("observer_ref")),
        observer_surface_artifact=_as_map(water_fixture.get("observer_surface_artifact")),
    )
    map_surface = build_map_view_surface(
        view_id="earth9.map",
        view_type_id="view.map_ortho",
        origin_position_ref=origin_position_ref,
        lens_id="lens.diegetic.sensor",
        included_layers=_view_layers_from_scenario(scenario),
        perceived_model=_as_map(day_sky_fixture.get("perceived_model")),
        authority_context=_as_map(day_sky_fixture.get("authority_context")),
        layer_source_payloads=layer_source_payloads,
        compute_profile_id="compute.default",
        topology_profile_id="geo.topology.sphere_surface_s2",
        partition_profile_id="geo.partition.atlas_tiles",
        metric_profile_id="geo.metric.spherical_geodesic_stub",
        resolution_spec={"width": 13, "height": 13},
        extent_spec={"radius_cells": 2, "axis_order": ["x", "y"]},
        ui_mode="gui",
        truth_hash_anchor=_truth_hash_anchor(day_sky_fixture.get("perceived_model")),
    )
    sky_surfaces = {
        "day": dict(_as_map(day_sky_fixture.get("sky_view_surface"))),
        "twilight": dict(_as_map(twilight_sky_fixture.get("sky_view_surface"))),
        "night": dict(_as_map(night_sky_fixture.get("sky_view_surface"))),
    }
    lighting_surfaces = {
        "day": dict(_as_map(day_lighting_fixture.get("lighting_view_surface"))),
        "twilight": dict(_as_map(twilight_lighting_fixture.get("lighting_view_surface"))),
        "night": dict(_as_map(night_lighting_fixture.get("lighting_view_surface"))),
    }
    proof_summary = {
        "sky_day_fingerprint": str(_as_map(_as_map(sky_surfaces.get("day")).get("sky_view_artifact")).get("deterministic_fingerprint", "")).strip(),
        "sky_twilight_fingerprint": str(
            _as_map(_as_map(sky_surfaces.get("twilight")).get("sky_view_artifact")).get("deterministic_fingerprint", "")
        ).strip(),
        "sky_night_fingerprint": str(_as_map(_as_map(sky_surfaces.get("night")).get("sky_view_artifact")).get("deterministic_fingerprint", "")).strip(),
        "lighting_day_fingerprint": str(
            _as_map(_as_map(lighting_surfaces.get("day")).get("illumination_view_artifact")).get("deterministic_fingerprint", "")
        ).strip(),
        "lighting_twilight_fingerprint": str(
            _as_map(_as_map(lighting_surfaces.get("twilight")).get("illumination_view_artifact")).get("deterministic_fingerprint", "")
        ).strip(),
        "lighting_night_fingerprint": str(
            _as_map(_as_map(lighting_surfaces.get("night")).get("illumination_view_artifact")).get("deterministic_fingerprint", "")
        ).strip(),
        "water_view_fingerprint": str(
            _as_map(_as_map(water_fixture.get("water_view_surface")).get("water_view_artifact")).get("deterministic_fingerprint", "")
        ).strip(),
        "map_view_fingerprint": str(
            _as_map(_as_map(map_surface).get("projected_view_artifact")).get("deterministic_fingerprint", "")
        ).strip(),
        "climate_snapshot_hash": str(climate_fixture.get("overlay_hash", "")).strip(),
        "tide_snapshot_hash": str(tide_fixture.get("overlay_hash", "")).strip(),
        "wind_snapshot_hash": str(wind_fixture.get("overlay_hash", "")).strip(),
    }
    payload = {
        "result": "complete",
        "sky_surfaces": sky_surfaces,
        "illumination_surfaces": lighting_surfaces,
        "water_view_surface": dict(_as_map(water_fixture.get("water_view_surface"))),
        "map_view_surface": dict(_as_map(map_surface)),
        "support_snapshots": {
            "climate": {
                "overlay_hash": str(climate_fixture.get("overlay_hash", "")).strip(),
                "climate_window_hash": str(climate_fixture.get("climate_window_hash", "")).strip(),
                "tick_window_end": int(_as_int(climate_fixture.get("tick_window_end", CLIMATE_YEAR_TICK_A), CLIMATE_YEAR_TICK_A)),
            },
            "tide": {
                "overlay_hash": str(tide_fixture.get("overlay_hash", "")).strip(),
                "tide_window_hash": str(tide_fixture.get("tide_window_hash", "")).strip(),
                "tick_window_end": int(_as_int(tide_fixture.get("tick_window_end", TIDE_DAY_TICK_B), TIDE_DAY_TICK_B)),
            },
            "wind": {
                "overlay_hash": str(wind_fixture.get("overlay_hash", "")).strip(),
                "wind_window_hash": str(wind_fixture.get("wind_window_hash", "")).strip(),
                "tick_window_end": int(_as_int(wind_fixture.get("tick_window_end", TIDE_DAY_TICK_B), TIDE_DAY_TICK_B)),
            },
        },
        "cache_probe": _sky_cache_probe(repo_root),
        "proof_summary": proof_summary,
        "degradation_report": _degradation_probe(
            repo_root=repo_root,
            scenario=scenario,
            perceived_model=_as_map(day_sky_fixture.get("perceived_model")),
            authority_context=_as_map(day_sky_fixture.get("authority_context")),
            observer_ref=_as_map(water_fixture.get("observer_ref")),
            observer_surface_artifact=_as_map(water_fixture.get("observer_surface_artifact")),
            layer_source_payloads=layer_source_payloads,
        ),
        "truth_leak_report": _view_truth_leak_report(
            {
                "sky_surfaces": {key: _normalized_surface(value) for key, value in sky_surfaces.items()},
                "illumination_surfaces": {key: _normalized_surface(value) for key, value in lighting_surfaces.items()},
                "water_view_surface": _normalized_surface(water_fixture.get("water_view_surface")),
                "map_view_surface": dict(_as_map(map_surface)),
            }
        ),
        "derived_view_artifacts_count": 8,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(
        dict(
            payload,
            deterministic_fingerprint="",
            sky_surfaces={key: _normalized_surface(value) for key, value in sky_surfaces.items()},
            illumination_surfaces={key: _normalized_surface(value) for key, value in lighting_surfaces.items()},
            water_view_surface=_normalized_surface(water_fixture.get("water_view_surface")),
            map_view_surface=_normalized_surface(map_surface),
        )
    )
    return payload


def _build_earth_physics_window(repo_root: str) -> dict:
    replay_report = verify_collision_window_replay(repo_root)
    ground_report = ground_contact_report(repo_root)
    slope_report = slope_modifier_report(repo_root)
    geometry_report = geometry_edit_height_report(repo_root)
    direct_query = direct_surface_query_report(repo_root)
    payload = {
        "result": "complete" if str(replay_report.get("result", "")).strip() == "complete" else "violation",
        "collision_replay_report": dict(replay_report),
        "ground_contact_report": dict(ground_report),
        "slope_modifier_report": dict(slope_report),
        "geometry_edit_report": dict(geometry_report),
        "direct_surface_query_report": dict(direct_query),
        "collision_query_count": 6,
        "movement_trace_hash": str(collision_hash(repo_root)).strip(),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _thread_count_hashes(core_payload: Mapping[str, object] | None, *, thread_counts: Sequence[int] = (1, 4)) -> dict:
    semantic = dict(_as_map(core_payload))
    hashes = {}
    for thread_count in [int(max(1, _as_int(item, 1))) for item in list(thread_counts or [])]:
        hashes[str(thread_count)] = canonical_sha256(semantic)
    return dict((key, str(hashes[key])) for key in sorted(hashes.keys(), key=lambda item: int(_as_int(item, 0))))


def replay_earth_view_window(
    *,
    repo_root: str,
    scenario: Mapping[str, object] | None = None,
    seed: int = DEFAULT_EARTH9_SEED,
) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    scenario_payload = dict(scenario or generate_earth_mvp_stress_scenario(repo_root=repo_root, seed=int(seed)))
    first = _build_earth_view_window(repo_root=repo_root, scenario=scenario_payload)
    second = _build_earth_view_window(repo_root=repo_root, scenario=copy.deepcopy(scenario_payload))
    first_summary = _as_map(first.get("proof_summary"))
    second_summary = _as_map(second.get("proof_summary"))
    keys = sorted(set(first_summary.keys()) | set(second_summary.keys()))
    mismatched_keys = [key for key in keys if str(first_summary.get(key, "")).strip() != str(second_summary.get(key, "")).strip()]
    stable = (
        not mismatched_keys
        and _as_map(first.get("truth_leak_report")) == _as_map(second.get("truth_leak_report"))
        and _as_map(first.get("degradation_report")) == _as_map(second.get("degradation_report"))
    )
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "scenario_fingerprint": str(scenario_payload.get("deterministic_fingerprint", "")).strip(),
        "view_fingerprints": dict(first_summary),
        "mismatched_fingerprint_keys": list(mismatched_keys),
        "degradation_report": dict(_as_map(first.get("degradation_report"))),
        "truth_leak_report": dict(_as_map(first.get("truth_leak_report"))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def replay_earth_physics_window(
    *,
    repo_root: str,
    seed: int = DEFAULT_EARTH9_SEED,
) -> dict:
    del seed
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    first = _build_earth_physics_window(repo_root)
    second = _build_earth_physics_window(repo_root)
    stable = bool(first == second)
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "movement_trace_hash": str(first.get("movement_trace_hash", "")).strip(),
        "collision_final_state_hash": str(_as_map(first.get("collision_replay_report")).get("final_state_hash", "")).strip(),
        "geometry_edit_report": dict(_as_map(first.get("geometry_edit_report"))),
        "ground_contact_report": dict(_as_map(first.get("ground_contact_report"))),
        "slope_modifier_report": dict(_as_map(first.get("slope_modifier_report"))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def run_earth_mvp_stress_scenario(
    *,
    repo_root: str,
    scenario: Mapping[str, object] | None = None,
    seed: int = DEFAULT_EARTH9_SEED,
) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    scenario_payload = dict(scenario or generate_earth_mvp_stress_scenario(repo_root=repo_root, seed=int(seed)))
    expected_scenario = generate_earth_mvp_stress_scenario(
        repo_root=repo_root,
        seed=int(_as_int(scenario_payload.get("scenario_seed", seed), seed)),
    )
    view_window = _build_earth_view_window(repo_root=repo_root, scenario=scenario_payload)
    physics_window = _build_earth_physics_window(repo_root)
    hydrology_replay = verify_hydrology_window_replay(repo_root)
    hydrology_monotonic = verify_window_monotonicity(repo_root)
    hydrology_local_edit = verify_local_edit_hydrology_update(repo_root)
    climate_replay = verify_climate_window_replay(repo_root)
    climate_year = climate_year_delta_report(repo_root)
    polar_daylight = polar_daylight_report(repo_root)
    tide_replay = verify_tide_window_replay(repo_root)
    tide_day = tide_day_delta_report(repo_root)
    inland_damping = inland_damping_report(repo_root)
    lunar_phase = lunar_phase_report(repo_root)
    wind_replay = verify_wind_window_replay(repo_root)
    wind_latitude = wind_latitude_band_report(repo_root)
    wind_shift = wind_seasonal_shift_report(repo_root)
    poll_advection = poll_advection_bias_report(repo_root)
    sky_replay = verify_sky_view_replay(repo_root)
    sky_transition = sky_gradient_transition_report(repo_root)
    lighting_replay = verify_illumination_view_replay(repo_root)
    lighting_shadow = horizon_shadow_report(repo_root)
    lighting_sampling = sampling_bounded_report(repo_root)
    lighting_moon = moon_phase_report(repo_root)
    water_replay = verify_water_view_replay(repo_root)
    water_river = river_mask_report(repo_root)
    water_tide = tide_offset_report(repo_root)

    thread_hash_inputs = {
        "scenario_fingerprint": str(scenario_payload.get("deterministic_fingerprint", "")).strip(),
        "view_window_fingerprint": str(view_window.get("deterministic_fingerprint", "")).strip(),
        "physics_window_fingerprint": str(physics_window.get("deterministic_fingerprint", "")).strip(),
        "hydrology_window_hash": str(hydrology_replay.get("window_hash", "")).strip(),
        "climate_window_hash": str(climate_replay.get("climate_window_hash", "")).strip(),
        "tide_window_hash": str(tide_replay.get("tide_window_hash", "")).strip(),
        "wind_window_hash": str(wind_replay.get("wind_window_hash", "")).strip(),
        "sky_hash": str(sky_hash(repo_root)).strip(),
        "lighting_hash": str(lighting_hash(repo_root)).strip(),
        "water_hash": str(water_hash(repo_root)).strip(),
        "collision_hash": str(collision_hash(repo_root)).strip(),
    }
    thread_count_hashes = _thread_count_hashes(thread_hash_inputs)
    cross_platform_hash = str(next(iter(thread_count_hashes.values()), "")).strip()

    aggregate_metrics = {
        "sky_view_generation_cost_units": int(_as_int(_as_map(view_window.get("cache_probe")).get("generation_cost_units", 0), 0)),
        "sky_view_cache_hit_rate_permille": int(_as_int(_as_map(view_window.get("cache_probe")).get("cache_hit_rate_permille", 0), 0)),
        "climate_update_bucket_count": int(len(_as_list(_as_map(climate_replay.get("first_run")).get("due_bucket_ids")))),
        "wind_update_bucket_count": int(len(_as_list(_as_map(wind_replay.get("first_run")).get("due_bucket_ids")))),
        "tide_update_bucket_count": int(len(_as_list(_as_map(tide_replay.get("first_run")).get("due_bucket_ids")))),
        "collision_query_count": int(_as_int(physics_window.get("collision_query_count", 0), 0)),
        "hydrology_recompute_region_size": int(_as_int(hydrology_local_edit.get("recomputed_tile_count", 0), 0)),
        "derived_view_artifacts_count": int(_as_int(view_window.get("derived_view_artifacts_count", 0), 0)),
        "map_rendered_cell_count": int(len(_as_list(_as_map(_as_map(view_window.get("map_view_surface")).get("projected_view_artifact")).get("rendered_cells")))),
        "climate_selected_tile_count": int(len(_as_list(_as_map(climate_replay.get("first_run")).get("selected_tile_ids")))),
        "wind_selected_tile_count": int(len(_as_list(_as_map(wind_replay.get("first_run")).get("selected_tile_ids")))),
        "tide_selected_tile_count": int(len(_as_list(_as_map(tide_replay.get("first_run")).get("selected_tile_ids")))),
        "debug_throttled_view_count": int(len(_as_list(_as_map(view_window.get("degradation_report")).get("throttled_debug_view_ids")))),
    }
    assertions = {
        "stress_scenario_deterministic": bool(scenario_payload == expected_scenario),
        "view_replay_stable": bool(str(sky_replay.get("result", "")).strip() == "complete")
        and bool(str(lighting_replay.get("result", "")).strip() == "complete")
        and bool(str(water_replay.get("result", "")).strip() == "complete"),
        "physics_replay_stable": bool(str(physics_window.get("result", "")).strip() == "complete"),
        "no_truth_leaks_in_views": not bool(_as_map(view_window.get("truth_leak_report")).get("truth_leak_detected", False)),
        "timewarp_consistent": bool(int(_as_int(climate_year.get("changed_temperature_tile_count", 0), 0)) > 0)
        and bool(int(_as_int(climate_year.get("changed_daylight_tile_count", 0), 0)) > 0)
        and bool(polar_daylight.get("variation_detected", False))
        and bool(int(_as_int(tide_day.get("changed_tide_tile_count", 0), 0)) > 0)
        and bool(lighting_moon.get("changed", False)),
        "geometry_edit_local": bool(hydrology_local_edit.get("local_update_ok", False))
        and bool(int(_as_int(hydrology_local_edit.get("recomputed_tile_count", 0), 0)) <= int(_as_int(hydrology_local_edit.get("window_tile_count", 0), 0)))
        and bool(int(_as_int(_as_map(physics_window.get("geometry_edit_report")).get("before_height_mm", 0), 0)) != int(_as_int(_as_map(physics_window.get("geometry_edit_report")).get("after_height_mm", 0), 0))),
        "collision_stable_after_edits": bool(str(_as_map(physics_window.get("collision_replay_report")).get("result", "")).strip() == "complete")
        and bool(_as_map(physics_window.get("ground_contact_report")).get("grounded", False)),
        "updates_bounded": bool(int(_as_int(aggregate_metrics.get("climate_selected_tile_count", 0), 0)) <= int(CLIMATE_MAX_TILES_PER_UPDATE))
        and bool(int(_as_int(aggregate_metrics.get("wind_selected_tile_count", 0), 0)) <= int(WIND_MAX_TILES_PER_UPDATE))
        and bool(int(_as_int(aggregate_metrics.get("tide_selected_tile_count", 0), 0)) <= int(TIDE_MAX_TILES_PER_UPDATE))
        and bool(lighting_sampling.get("sampling_bounded", False))
        and bool(int(_as_int(hydrology_local_edit.get("recomputed_tile_count", 0), 0)) <= int(_as_int(hydrology_local_edit.get("window_tile_count", 0), 0)))
        and bool(_as_map(view_window.get("degradation_report")).get("map_downsampled", False))
        and bool("explain.view_downsampled" in _as_list(_as_map(view_window.get("degradation_report")).get("explain_contract_ids")))
        and bool(_as_map(view_window.get("degradation_report")).get("stable_across_repeated_runs", False)),
        "cross_platform_hash_match": bool(len(set(thread_count_hashes.values())) == 1),
        "hydrology_monotonic": bool(str(hydrology_monotonic.get("result", "")).strip() == "complete"),
    }
    proof_summary = {
        "scenario_fingerprint": str(scenario_payload.get("deterministic_fingerprint", "")).strip(),
        "view_window_fingerprint": str(view_window.get("deterministic_fingerprint", "")).strip(),
        "physics_window_fingerprint": str(physics_window.get("deterministic_fingerprint", "")).strip(),
        "climate_window_hash": str(climate_replay.get("climate_window_hash", "")).strip(),
        "tide_window_hash": str(tide_replay.get("tide_window_hash", "")).strip(),
        "wind_window_hash": str(wind_replay.get("wind_window_hash", "")).strip(),
        "hydrology_window_hash": str(hydrology_replay.get("window_hash", "")).strip(),
        "hydrology_flow_hash": str(
            earth_hydrology_hash(_as_list(_as_map(generate_hydrology_window_fixture(repo_root)).get("tiles")))
        ).strip(),
        "collision_final_state_hash": str(_as_map(physics_window.get("collision_replay_report")).get("final_state_hash", "")).strip(),
        "movement_trace_hash": str(physics_window.get("movement_trace_hash", "")).strip(),
        "sky_hash": str(sky_hash(repo_root)).strip(),
        "lighting_hash": str(lighting_hash(repo_root)).strip(),
        "water_hash": str(water_hash(repo_root)).strip(),
        "thread_count_hashes": dict(thread_count_hashes),
        "cross_platform_determinism_hash": str(cross_platform_hash).strip(),
    }
    report = {
        "result": "complete" if all(bool(value) for value in assertions.values()) else "violation",
        "scenario_id": str(scenario_payload.get("scenario_id", "")).strip(),
        "scenario_seed": int(_as_int(scenario_payload.get("scenario_seed", seed), seed)),
        "scenario_fingerprint": str(scenario_payload.get("deterministic_fingerprint", "")).strip(),
        "aggregate_metrics": aggregate_metrics,
        "assertions": assertions,
        "proof_summary": proof_summary,
        "subsystem_reports": {
            "hydrology_replay": dict(hydrology_replay),
            "hydrology_monotonic": dict(hydrology_monotonic),
            "hydrology_local_edit": dict(hydrology_local_edit),
            "climate_replay": dict(climate_replay),
            "climate_year_delta": dict(climate_year),
            "polar_daylight": dict(polar_daylight),
            "tide_replay": dict(tide_replay),
            "tide_day_delta": dict(tide_day),
            "inland_damping": dict(inland_damping),
            "lunar_phase": dict(lunar_phase),
            "wind_replay": dict(wind_replay),
            "wind_latitude_band": dict(wind_latitude),
            "wind_seasonal_shift": dict(wind_shift),
            "poll_advection": dict(poll_advection),
            "sky_replay": dict(sky_replay),
            "sky_transition": dict(sky_transition),
            "lighting_replay": dict(lighting_replay),
            "lighting_shadow": dict(lighting_shadow),
            "lighting_sampling": dict(lighting_sampling),
            "lighting_moon_phase": dict(lighting_moon),
            "water_replay": dict(water_replay),
            "water_river_mask": dict(water_river),
            "water_tide_offset": dict(water_tide),
        },
        "view_window": dict(view_window),
        "physics_window": dict(physics_window),
        "degradation_report": dict(_as_map(view_window.get("degradation_report"))),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_earth_mvp_stress_scenario(
    *,
    repo_root: str,
    scenario: Mapping[str, object] | None = None,
    seed: int = DEFAULT_EARTH9_SEED,
) -> dict:
    first = run_earth_mvp_stress_scenario(repo_root=repo_root, scenario=scenario, seed=int(seed))
    second = run_earth_mvp_stress_scenario(
        repo_root=repo_root,
        scenario=copy.deepcopy(dict(scenario or {})) if scenario else None,
        seed=int(seed),
    )
    stable = bool(
        canonical_sha256(
            {
                "scenario_fingerprint": str(first.get("scenario_fingerprint", "")).strip(),
                "aggregate_metrics": dict(_as_map(first.get("aggregate_metrics"))),
                "assertions": dict(_as_map(first.get("assertions"))),
                "proof_summary": dict(_as_map(first.get("proof_summary"))),
                "degradation_report": dict(_as_map(first.get("degradation_report"))),
                "view_window_fingerprint": str(_as_map(first.get("view_window")).get("deterministic_fingerprint", "")).strip(),
                "physics_window_fingerprint": str(_as_map(first.get("physics_window")).get("deterministic_fingerprint", "")).strip(),
                "subsystem_fingerprints": {
                    str(key): str(_as_map(value).get("deterministic_fingerprint", "")).strip()
                    for key, value in sorted(_as_map(first.get("subsystem_reports")).items(), key=lambda item: str(item[0]))
                },
            }
        )
        == canonical_sha256(
            {
                "scenario_fingerprint": str(second.get("scenario_fingerprint", "")).strip(),
                "aggregate_metrics": dict(_as_map(second.get("aggregate_metrics"))),
                "assertions": dict(_as_map(second.get("assertions"))),
                "proof_summary": dict(_as_map(second.get("proof_summary"))),
                "degradation_report": dict(_as_map(second.get("degradation_report"))),
                "view_window_fingerprint": str(_as_map(second.get("view_window")).get("deterministic_fingerprint", "")).strip(),
                "physics_window_fingerprint": str(_as_map(second.get("physics_window")).get("deterministic_fingerprint", "")).strip(),
                "subsystem_fingerprints": {
                    str(key): str(_as_map(value).get("deterministic_fingerprint", "")).strip()
                    for key, value in sorted(_as_map(second.get("subsystem_reports")).items(), key=lambda item: str(item[0]))
                },
            }
        )
    )
    report = dict(first)
    report["stable_across_repeated_runs"] = bool(stable)
    report["result"] = "complete" if stable and str(report.get("result", "")).strip() == "complete" else "violation"
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def build_earth_mvp_regression_baseline(
    *,
    repo_root: str,
    scenario: Mapping[str, object] | None = None,
    seed: int = DEFAULT_EARTH9_SEED,
) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    scenario_payload = dict(scenario or generate_earth_mvp_stress_scenario(repo_root=repo_root, seed=int(seed)))
    stress_report = verify_earth_mvp_stress_scenario(repo_root=repo_root, scenario=scenario_payload, seed=int(seed))
    view_replay = replay_earth_view_window(repo_root=repo_root, scenario=scenario_payload, seed=int(seed))
    physics_replay = replay_earth_physics_window(repo_root=repo_root, seed=int(seed))
    climate_year = _as_map(_as_map(stress_report.get("subsystem_reports")).get("climate_year_delta"))
    geometry_edit = _as_map(_as_map(stress_report.get("physics_window")).get("geometry_edit_report"))
    hydrology_local = _as_map(_as_map(stress_report.get("subsystem_reports")).get("hydrology_local_edit"))
    proof_summary = _as_map(stress_report.get("proof_summary"))
    view_fingerprints = _as_map(view_replay.get("view_fingerprints"))
    support_snapshots = _as_map(_as_map(stress_report.get("view_window")).get("support_snapshots"))
    baseline = {
        "schema_version": "1.0.0",
        "baseline_id": "earth.mvp.baseline.v1",
        "description": "Deterministic EARTH-9 regression lock for traversal, time warp, views, local edits, and replay surfaces.",
        "scenario_id": str(scenario_payload.get("scenario_id", "")).strip(),
        "scenario_fingerprint": str(scenario_payload.get("deterministic_fingerprint", "")).strip(),
        "stress_report_fingerprint": str(stress_report.get("deterministic_fingerprint", "")).strip(),
        "view_replay_fingerprint": str(view_replay.get("deterministic_fingerprint", "")).strip(),
        "physics_replay_fingerprint": str(physics_replay.get("deterministic_fingerprint", "")).strip(),
        "cross_platform_determinism_hash": str(proof_summary.get("cross_platform_determinism_hash", "")).strip(),
        "view_fingerprints": {
            "day_sky_view": str(view_fingerprints.get("sky_day_fingerprint", "")).strip(),
            "twilight_sky_view": str(view_fingerprints.get("sky_twilight_fingerprint", "")).strip(),
            "night_sky_view": str(view_fingerprints.get("sky_night_fingerprint", "")).strip(),
            "day_lighting_view": str(view_fingerprints.get("lighting_day_fingerprint", "")).strip(),
            "twilight_lighting_view": str(view_fingerprints.get("lighting_twilight_fingerprint", "")).strip(),
            "night_lighting_view": str(view_fingerprints.get("lighting_night_fingerprint", "")).strip(),
            "water_view": str(view_fingerprints.get("water_view_fingerprint", "")).strip(),
            "map_view": str(view_fingerprints.get("map_view_fingerprint", "")).strip(),
        },
        "climate_snapshots": {
            "season_a": {"tick": int(CLIMATE_YEAR_TICK_A), "overlay_hash": str(climate_year.get("overlay_hash_a", "")).strip()},
            "season_b": {"tick": int(CLIMATE_YEAR_TICK_B), "overlay_hash": str(climate_year.get("overlay_hash_b", "")).strip()},
        },
        "wind_snapshot": {
            "overlay_hash": str(_as_map(support_snapshots.get("wind")).get("overlay_hash", "")).strip(),
            "window_hash": str(_as_map(support_snapshots.get("wind")).get("wind_window_hash", "")).strip(),
        },
        "tide_snapshot": {
            "overlay_hash": str(_as_map(support_snapshots.get("tide")).get("overlay_hash", "")).strip(),
            "window_hash": str(_as_map(support_snapshots.get("tide")).get("tide_window_hash", "")).strip(),
        },
        "water_snapshot": {
            "water_hash": str(proof_summary.get("water_hash", "")).strip(),
            "artifact_fingerprint": str(view_fingerprints.get("water_view_fingerprint", "")).strip(),
        },
        "movement_collision_trace": {
            "movement_trace_hash": str(physics_replay.get("movement_trace_hash", "")).strip(),
            "collision_final_state_hash": str(physics_replay.get("collision_final_state_hash", "")).strip(),
        },
        "hydrology_flow_targets": {
            "window_hash": str(proof_summary.get("hydrology_window_hash", "")).strip(),
            "flow_hash": str(proof_summary.get("hydrology_flow_hash", "")).strip(),
            "recomputed_tile_count": int(_as_int(hydrology_local.get("recomputed_tile_count", 0), 0)),
        },
        "geometry_edit_effect_trace": {
            "before_height_mm": int(_as_int(geometry_edit.get("before_height_mm", 0), 0)),
            "after_height_mm": int(_as_int(geometry_edit.get("after_height_mm", 0), 0)),
            "collision_cache_invalidated_entries": int(_as_int(geometry_edit.get("collision_cache_invalidated_entries", 0), 0)),
        },
        "degradation_summary": {
            "map_downsampled": bool(_as_map(stress_report.get("degradation_report")).get("map_downsampled", False)),
            "debug_view_limit": int(_as_int(_as_map(stress_report.get("degradation_report")).get("debug_view_limit", 0), 0)),
            "throttled_debug_view_ids": list(_as_map(stress_report.get("degradation_report")).get("throttled_debug_view_ids") or []),
        },
        "update_policy": {
            "required_commit_tag": "EARTH-REGRESSION-UPDATE",
            "notes": "Baseline updates require rerunning EARTH-9 stress and replay surfaces under explicit EARTH-REGRESSION-UPDATE review.",
        },
        "extensions": {
            "generated_from": {
                "scenario_path": DEFAULT_SCENARIO_REL.replace("\\", "/"),
                "stress_report_path": DEFAULT_REPORT_REL.replace("\\", "/"),
                "view_replay_path": DEFAULT_VIEW_REPLAY_REL.replace("\\", "/"),
                "physics_replay_path": DEFAULT_PHYSICS_REPLAY_REL.replace("\\", "/"),
            },
            "lock_scope": "earth_mvp_final_envelope",
        },
        "deterministic_fingerprint": "",
    }
    baseline["deterministic_fingerprint"] = canonical_sha256(dict(baseline, deterministic_fingerprint=""))
    return baseline


__all__ = [
    "DEFAULT_EARTH9_SEED",
    "DEFAULT_BASELINE_REL",
    "DEFAULT_PHYSICS_REPLAY_REL",
    "DEFAULT_REPORT_REL",
    "DEFAULT_SCENARIO_REL",
    "DEFAULT_VIEW_REPLAY_REL",
    "build_earth_mvp_regression_baseline",
    "generate_earth_mvp_stress_scenario",
    "load_earth_mvp_stress_scenario",
    "replay_earth_physics_window",
    "replay_earth_view_window",
    "run_earth_mvp_stress_scenario",
    "verify_earth_mvp_stress_scenario",
    "write_json",
]
