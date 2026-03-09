"""Shared deterministic EARTH-9 stress scenario helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Iterable, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo import build_position_ref
from src.worldgen.earth import DEFAULT_EARTH_CLIMATE_PARAMS_ID, DEFAULT_TIDE_PARAMS_ID, earth_climate_params_rows, tide_params_rows
from src.worldgen.mw.sol_anchor import resolve_sol_anchor_cell_key
from src.worldgen.mw.system_query_engine import list_systems_in_cell
from tools.worldgen.earth0_probe import build_earth_probe_context, generate_earth_probe_tile
from tools.worldgen.earth1_probe import HYDROLOGY_EDIT_VOLUME_AMOUNT, find_river_candidate
from tools.worldgen.earth3_probe import TIDE_DAY_TICK_A, TIDE_DAY_TICK_B
from tools.worldgen.earth4_probe import SKY_DAY_TICK, SKY_NIGHT_TICK, SKY_TWILIGHT_TICK
from tools.worldgen.earth8_probe import build_water_fixture
from src.client.ui.teleport_controller import build_teleport_plan


DEFAULT_EARTH9_SEED = 91029
DEFAULT_SCENARIO_REL = os.path.join("build", "earth", "earth_mvp_stress_scenario.json")
DEFAULT_REPORT_REL = os.path.join("build", "earth", "earth_mvp_stress_report.json")
DEFAULT_VIEW_REPLAY_REL = os.path.join("build", "earth", "earth_view_replay.json")
DEFAULT_PHYSICS_REPLAY_REL = os.path.join("build", "earth", "earth_physics_replay.json")
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
    while len(base_index) < 3:
        base_index.append(0)
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
        "scenario_id": "scenario.earth_mvp.stress.{}".format(canonical_sha256({"seed": int(seed), "repo_root": repo_root})[:12]),
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


__all__ = [
    "DEFAULT_EARTH9_SEED",
    "DEFAULT_PHYSICS_REPLAY_REL",
    "DEFAULT_REPORT_REL",
    "DEFAULT_SCENARIO_REL",
    "DEFAULT_VIEW_REPLAY_REL",
    "generate_earth_mvp_stress_scenario",
    "write_json",
]
