"""Deterministic EARTH-1 hydrology probe helpers for replay and TestX reuse."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


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
from geo.index.geo_index_engine import geo_cell_key_neighbors  # noqa: E402
from worldgen.earth import compute_hydrology_window, hydrology_params_rows  # noqa: E402
from worldgen.mw import build_planet_surface_cell_key  # noqa: E402


HYDROLOGY_FIXTURE_TICK = 4096
HYDROLOGY_HASH_TICK = 0
HYDROLOGY_WINDOW_CHART_ID = "chart.atlas.north"
HYDROLOGY_WINDOW_CENTER_INDEX = [16, 6]
HYDROLOGY_EDIT_VOLUME_AMOUNT = 200
HYDROLOGY_CANDIDATE_COLUMNS = tuple(range(0, 64, 4))
HYDROLOGY_CANDIDATE_BANDS = tuple(range(0, 16, 1))
HYDROLOGY_ALLOWED_PROCESSES = ["process.geometry_remove"]


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


def _hydrology_params_row(repo_root: str, params_id: str = "params.hydrology.default_stub") -> dict:
    payload = _load_json(repo_root, os.path.join("data", "registries", "hydrology_params_registry.json"))
    rows = hydrology_params_rows(payload)
    row = _as_map(rows.get(str(params_id).strip()))
    if not row:
        raise RuntimeError("hydrology params not found: {}".format(params_id))
    return row


def _surface_summary(row: Mapping[str, object]) -> dict:
    return _as_map(_as_map(row).get("surface_summary"))


def generate_earth_hydrology_tile(
    repo_root: str,
    *,
    chart_id: str,
    index_tuple: Sequence[int],
    refinement_level: int = 1,
    current_tick: int = HYDROLOGY_FIXTURE_TICK,
) -> dict:
    context = build_earth_probe_context(repo_root)
    return generate_earth_probe_tile(
        context,
        chart_id=str(chart_id),
        index_tuple=[int(item) for item in list(index_tuple or [])],
        refinement_level=int(refinement_level),
        current_tick=int(current_tick),
    )


def generate_hydrology_window_fixture(
    repo_root: str,
    *,
    chart_id: str = HYDROLOGY_WINDOW_CHART_ID,
    center_index_tuple: Sequence[int] = HYDROLOGY_WINDOW_CENTER_INDEX,
    current_tick: int = HYDROLOGY_FIXTURE_TICK,
) -> dict:
    context = build_earth_probe_context(repo_root)
    params_row = _hydrology_params_row(repo_root)
    analysis_radius = int(max(1, int(_as_map(_as_map(params_row).get("extensions")).get("analysis_radius", 2) or 2)))
    center_cell_key = build_planet_surface_cell_key(
        planet_object_id=str(context.get("earth_object_id", "")).strip(),
        ancestor_world_cell_key=_as_map(context.get("anchor_cell_key")),
        chart_id=str(chart_id),
        index_tuple=[int(item) for item in list(center_index_tuple or [])],
        refinement_level=1,
        planet_tags=list(context.get("planet_tags") or []),
    )
    neighbor_payload = geo_cell_key_neighbors(center_cell_key, analysis_radius)
    if str(neighbor_payload.get("result", "")).strip() != "complete":
        raise RuntimeError("hydrology window neighbor query failed")
    tile_payloads = []
    ordered_rows = [dict(center_cell_key)] + [dict(row) for row in _as_list(neighbor_payload.get("neighbors")) if isinstance(row, Mapping)]
    seen: set[str] = set()
    for cell_key in ordered_rows:
        cell_hash = canonical_sha256(cell_key)
        if cell_hash in seen:
            continue
        seen.add(cell_hash)
        extensions = _as_map(cell_key.get("extensions"))
        base_chart_id = str(extensions.get("base_chart_id", "")).strip() or HYDROLOGY_WINDOW_CHART_ID
        tile_payloads.append(
            generate_earth_probe_tile(
                context,
                chart_id=base_chart_id,
                index_tuple=[int(item) for item in list(cell_key.get("index_tuple") or [])],
                refinement_level=int(max(0, int(cell_key.get("refinement_level", 1) or 1))),
                current_tick=int(current_tick),
            )
        )
    tile_payloads = sorted(
        tile_payloads,
        key=lambda row: (
            str(row.get("chart_id", "")),
            list(row.get("index_tuple") or [0, 0])[1],
            list(row.get("index_tuple") or [0, 0])[0],
        ),
    )
    return {
        "analysis_radius": analysis_radius,
        "center_chart_id": str(chart_id),
        "center_index_tuple": [int(item) for item in list(center_index_tuple or [])],
        "current_tick": int(current_tick),
        "tiles": tile_payloads,
        "deterministic_fingerprint": canonical_sha256(
            {
                "analysis_radius": analysis_radius,
                "center_chart_id": str(chart_id),
                "center_index_tuple": [int(item) for item in list(center_index_tuple or [])],
                "tile_count": len(tile_payloads),
            }
        ),
    }


def earth_hydrology_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        summary = _surface_summary(row)
        normalized.append(
            {
                "chart_id": str(row.get("chart_id", "")).strip(),
                "index_tuple": [int(item) for item in list(row.get("index_tuple") or [])],
                "flow_target_tile_key": _as_map(summary.get("flow_target_tile_key")),
                "drainage_accumulation_proxy": int(summary.get("drainage_accumulation_proxy", 0) or 0),
                "river_flag": bool(summary.get("river_flag", False)),
                "lake_flag": bool(summary.get("lake_flag", False)),
                "hydrology_structure_kind": str(summary.get("hydrology_structure_kind", "")).strip(),
            }
        )
    normalized.sort(key=lambda item: (item["chart_id"], item["index_tuple"][1], item["index_tuple"][0]))
    return canonical_sha256(normalized)


def sample_earth_hydrology(
    repo_root: str,
    *,
    current_tick: int = HYDROLOGY_HASH_TICK,
    chart_ids: Iterable[str] = ("chart.atlas.north", "chart.atlas.south"),
    columns: Iterable[int] = EARTH_SAMPLE_COLUMNS,
    bands: Iterable[int] = EARTH_SAMPLE_BANDS,
) -> List[dict]:
    context = build_earth_probe_context(repo_root)
    rows: List[dict] = []
    for chart_id in list(chart_ids):
        for band in list(bands):
            for column in list(columns):
                rows.append(
                    generate_earth_probe_tile(
                        context,
                        chart_id=str(chart_id),
                        index_tuple=[int(column), int(band)],
                        refinement_level=1,
                        current_tick=int(current_tick),
                    )
                )
    return rows


def _window_tiles_by_cell_hash(window_fixture: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in _as_list(_as_map(window_fixture).get("tiles")):
        artifact_rows = [dict(item) for item in _as_list(_as_map(row).get("generated_surface_tile_artifact_rows")) if isinstance(item, Mapping)]
        if not artifact_rows:
            continue
        tile_cell_key = _as_map(artifact_rows[0].get("tile_cell_key"))
        if tile_cell_key:
            out[canonical_sha256(tile_cell_key)] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def verify_hydrology_window_replay(repo_root: str) -> dict:
    first = generate_hydrology_window_fixture(repo_root, current_tick=HYDROLOGY_FIXTURE_TICK)
    second = generate_hydrology_window_fixture(repo_root, current_tick=HYDROLOGY_FIXTURE_TICK)
    stable = first == second
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "window_hash": earth_hydrology_hash(_as_list(first.get("tiles"))),
        "first_run": first,
        "second_run": second,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def verify_window_monotonicity(repo_root: str) -> dict:
    fixture = generate_hydrology_window_fixture(repo_root, current_tick=HYDROLOGY_FIXTURE_TICK)
    rows_by_hash = _window_tiles_by_cell_hash(fixture)
    violations = []
    for cell_hash, row in sorted(rows_by_hash.items()):
        summary = _surface_summary(row)
        target_key = _as_map(summary.get("flow_target_tile_key"))
        target_hash = canonical_sha256(target_key) if target_key else ""
        if not target_hash or target_hash not in rows_by_hash:
            continue
        target_summary = _surface_summary(rows_by_hash[target_hash])
        current_acc = int(summary.get("drainage_accumulation_proxy", 0) or 0)
        target_acc = int(target_summary.get("drainage_accumulation_proxy", 0) or 0)
        if target_acc < current_acc:
            violations.append(
                {
                    "tile_hash": cell_hash,
                    "target_hash": target_hash,
                    "current_accumulation": current_acc,
                    "target_accumulation": target_acc,
                }
            )
    report = {
        "result": "complete" if not violations else "violation",
        "window_hash": earth_hydrology_hash(_as_list(fixture.get("tiles"))),
        "violation_count": len(violations),
        "violations": violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def find_river_candidate(repo_root: str) -> dict:
    context = build_earth_probe_context(repo_root)
    threshold = int(_hydrology_params_row(repo_root).get("accumulation_threshold", 0) or 0)
    for chart_id in ("chart.atlas.north", "chart.atlas.south"):
        for band in HYDROLOGY_CANDIDATE_BANDS:
            for column in HYDROLOGY_CANDIDATE_COLUMNS:
                tile = generate_earth_probe_tile(
                    context,
                    chart_id=chart_id,
                    index_tuple=[int(column), int(band)],
                    refinement_level=1,
                    current_tick=HYDROLOGY_FIXTURE_TICK,
                )
                summary = _surface_summary(tile)
                accumulation = int(summary.get("drainage_accumulation_proxy", 0) or 0)
                river_flag = bool(summary.get("river_flag", False))
                if accumulation >= threshold and river_flag:
                    return {
                        "result": "complete",
                        "source": "earth_sample",
                        "threshold": threshold,
                        "candidate": tile,
                        "deterministic_fingerprint": canonical_sha256(
                            {
                                "threshold": threshold,
                                "chart_id": chart_id,
                                "index_tuple": [int(column), int(band)],
                            }
                        ),
                    }
    synthetic = verify_river_threshold_fixture(repo_root)
    if str(synthetic.get("result", "")).strip() == "complete":
        return {
            "result": "complete",
            "source": "synthetic_fixture",
            "threshold": threshold,
            "candidate": dict(synthetic.get("candidate") or {}),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "threshold": threshold,
                    "source": "synthetic_fixture",
                    "candidate_fingerprint": str(synthetic.get("deterministic_fingerprint", "")).strip(),
                }
            ),
        }
    return {
        "result": "violation",
        "source": "none",
        "threshold": threshold,
        "candidate": {},
        "deterministic_fingerprint": canonical_sha256({"threshold": threshold, "result": "violation"}),
    }


def build_synthetic_river_fixture(repo_root: str) -> dict:
    params_row = _hydrology_params_row(repo_root)

    def _grid_cell(index_x: int, index_y: int) -> dict:
        return {
            "partition_profile_id": "geo.partition.grid_zd",
            "topology_profile_id": "geo.topology.r2_infinite",
            "chart_id": "chart.global.r2",
            "index_tuple": [int(index_x), int(index_y)],
            "refinement_level": 0,
            "extensions": {},
        }

    center_cell_key = _grid_cell(0, 0)
    heights: Dict[Tuple[int, int], int] = {}
    for y in range(-2, 3):
        for x in range(-2, 3):
            distance = abs(int(x)) + abs(int(y))
            if distance == 0:
                heights[(x, y)] = 0
            elif distance == 1:
                heights[(x, y)] = 10
            elif distance == 2:
                heights[(x, y)] = 20
            else:
                heights[(x, y)] = 30

    def _resolver(cell_key: Mapping[str, object]) -> dict:
        row = _as_map(cell_key)
        index_tuple = [int(item) for item in list(row.get("index_tuple") or [0, 0])]
        x_value = int(index_tuple[0] if index_tuple else 0)
        y_value = int(index_tuple[1] if len(index_tuple) > 1 else 0)
        height_proxy = int(heights.get((x_value, y_value), 40))
        return {
            "tile_cell_key": dict(_grid_cell(x_value, y_value)),
            "surface_class_id": "surface.class.land",
            "material_baseline_id": "material.stone_basic",
            "biome_stub_id": "biome.stub.temperate",
            "effective_height_proxy": height_proxy,
            "elevation_params_ref": {"height_proxy": height_proxy},
            "extensions": {"surface_class_id": "surface.class.land", "source": "EARTH1-9.synthetic"},
        }

    hydrology_payload = compute_hydrology_window(
        center_tile_cell_key=center_cell_key,
        hydrology_params_row=params_row,
        resolve_tile_snapshot=_resolver,
    )
    return {
        "center_cell_key": center_cell_key,
        "hydrology_payload": hydrology_payload,
        "deterministic_fingerprint": canonical_sha256(
            {
                "center_cell_key": center_cell_key,
                "window_fingerprint": str(_as_map(hydrology_payload).get("window_fingerprint", "")).strip(),
            }
        ),
    }


def verify_river_threshold_fixture(repo_root: str) -> dict:
    params_row = _hydrology_params_row(repo_root)
    threshold = int(params_row.get("accumulation_threshold", 0) or 0)
    fixture = build_synthetic_river_fixture(repo_root)
    candidate = _as_map(_as_map(fixture.get("hydrology_payload")).get("center_tile"))
    accumulation = int(candidate.get("drainage_accumulation_proxy", 0) or 0)
    river_flag = bool(candidate.get("river_flag", False))
    report = {
        "result": "complete" if accumulation >= threshold and river_flag else "violation",
        "threshold": threshold,
        "candidate": candidate,
        "window_fingerprint": str(_as_map(fixture.get("hydrology_payload")).get("window_fingerprint", "")).strip(),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _seed_edit_state(tile_rows: Sequence[Mapping[str, object]], *, universe_identity: Mapping[str, object]) -> dict:
    state = seed_free_state(initial_velocity_x=0)
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
    state["field_layers"] = []
    state["field_cells"] = []
    for tile in list(tile_rows or []):
        artifact_rows = [dict(row) for row in _as_list(_as_map(tile).get("generated_surface_tile_artifact_rows")) if isinstance(row, Mapping)]
        geometry_rows = [dict(row) for row in _as_list(_as_map(tile).get("geometry_initializations")) if isinstance(row, Mapping)]
        state["worldgen_surface_tile_artifacts"].extend(artifact_rows)
        state["geometry_cell_states"].extend(geometry_rows)
    return state


def _hydrology_fields_by_tile_id(rows: Sequence[Mapping[str, object]]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(rows or []):
        row = _as_map(raw)
        tile_id = str(row.get("tile_object_id", "")).strip()
        if not tile_id:
            continue
        extensions = _as_map(row.get("extensions"))
        out[tile_id] = {
            "flow_target_tile_key": _as_map(row.get("flow_target_tile_key")),
            "drainage_accumulation_proxy": int(row.get("drainage_accumulation_proxy", 0) or 0),
            "river_flag": bool(row.get("river_flag", False)),
            "hydrology_window_fingerprint": str(extensions.get("hydrology_window_fingerprint", "")).strip(),
            "hydrology_effective_height_proxy": int(extensions.get("hydrology_effective_height_proxy", 0) or 0),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def verify_local_edit_hydrology_update(repo_root: str) -> dict:
    context = build_earth_probe_context(repo_root)
    fixture = generate_hydrology_window_fixture(repo_root, current_tick=HYDROLOGY_FIXTURE_TICK)
    window_tiles = [dict(row) for row in _as_list(fixture.get("tiles")) if isinstance(row, Mapping)]
    if not window_tiles:
        raise RuntimeError("hydrology window fixture produced no tiles")

    candidate_rows = sorted(
        window_tiles,
        key=lambda row: (
            int(_surface_summary(row).get("drainage_accumulation_proxy", 0) or 0),
            str(row.get("chart_id", "")),
            list(row.get("index_tuple") or [0, 0])[1],
            list(row.get("index_tuple") or [0, 0])[0],
        ),
        reverse=True,
    )
    selected_report = {}
    for candidate in candidate_rows:
        summary = _surface_summary(candidate)
        if str(summary.get("surface_class_id", "")).strip() == "surface.class.ocean":
            continue
        state = _seed_edit_state(window_tiles, universe_identity=_as_map(context.get("universe_identity")))
        before_fields = _hydrology_fields_by_tile_id(_as_list(state.get("worldgen_surface_tile_artifacts")))
        artifact_rows = [dict(row) for row in _as_list(candidate.get("generated_surface_tile_artifact_rows")) if isinstance(row, Mapping)]
        if not artifact_rows:
            continue
        law = law_profile(HYDROLOGY_ALLOWED_PROCESSES)
        auth = authority_context()
        policy = policy_context()
        result = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.earth1.hydrology.local_edit.{}".format(
                    canonical_sha256({"chart_id": candidate.get("chart_id"), "index_tuple": candidate.get("index_tuple")})[:16]
                ),
                "process_id": "process.geometry_remove",
                "inputs": {
                    "target_cell_keys": [dict(artifact_rows[0].get("tile_cell_key") or {})],
                    "volume_amount": HYDROLOGY_EDIT_VOLUME_AMOUNT,
                },
            },
            law_profile=law,
            authority_context=auth,
            navigation_indices={},
            policy_context=policy,
        )
        after_fields = _hydrology_fields_by_tile_id(_as_list(state.get("worldgen_surface_tile_artifacts")))
        changed_tile_ids = [
            tile_id
            for tile_id in sorted(after_fields.keys())
            if dict(before_fields.get(tile_id) or {}) != dict(after_fields.get(tile_id) or {})
        ]
        recomputed_tile_count = int(result.get("hydrology_recomputed_tile_count", 0) or 0)
        if changed_tile_ids:
            selected_report = {
                "result": "complete",
                "candidate_chart_id": str(candidate.get("chart_id", "")).strip(),
                "candidate_index_tuple": [int(item) for item in list(candidate.get("index_tuple") or [])],
                "changed_tile_ids": changed_tile_ids,
                "recomputed_tile_count": recomputed_tile_count,
                "dirty_tile_count": int(result.get("hydrology_dirty_tile_count", 0) or 0),
                "window_tile_count": len(window_tiles),
                "local_update_ok": bool(recomputed_tile_count <= len(window_tiles)),
                "deterministic_fingerprint": "",
            }
            selected_report["deterministic_fingerprint"] = canonical_sha256(
                dict(selected_report, deterministic_fingerprint="")
            )
            return selected_report
    return {
        "result": "violation",
        "candidate_chart_id": "",
        "candidate_index_tuple": [],
        "changed_tile_ids": [],
        "recomputed_tile_count": 0,
        "dirty_tile_count": 0,
        "window_tile_count": len(window_tiles),
        "local_update_ok": False,
        "deterministic_fingerprint": canonical_sha256({"result": "violation", "window_tile_count": len(window_tiles)}),
    }


__all__ = [
    "HYDROLOGY_FIXTURE_TICK",
    "HYDROLOGY_HASH_TICK",
    "HYDROLOGY_WINDOW_CHART_ID",
    "HYDROLOGY_WINDOW_CENTER_INDEX",
    "earth_hydrology_hash",
    "find_river_candidate",
    "build_synthetic_river_fixture",
    "generate_earth_hydrology_tile",
    "generate_hydrology_window_fixture",
    "sample_earth_hydrology",
    "verify_hydrology_window_replay",
    "verify_local_edit_hydrology_update",
    "verify_river_threshold_fixture",
    "verify_window_monotonicity",
]
