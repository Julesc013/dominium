"""Deterministic EARTH-10 material-proxy probes for replay and TestX reuse."""

from __future__ import annotations

import json
import os
import sys
from typing import Dict, Iterable, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.worldgen.earth0_probe import (  # noqa: E402
    EARTH_SAMPLE_BANDS,
    EARTH_SAMPLE_COLUMNS,
    build_earth_probe_context,
    generate_earth_probe_tile,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402
from tools.xstack.testx.tests.mobility_free_testlib import authority_context, law_profile, policy_context, seed_free_state  # noqa: E402
from worldgen.earth import material_proxy_window_hash  # noqa: E402


EARTH10_ALLOWED_PROCESSES = ["process.earth_material_proxy_tick"]
MATERIAL_PROXY_REPLAY_TICK = 144
MATERIAL_PROXY_LAST_PROCESSED_TICK = 143
MATERIAL_PROXY_MAX_TILES_PER_UPDATE = 256
MATERIAL_PROXY_REGISTRY_REL = os.path.join("data", "registries", "material_proxy_registry.json")
SURFACE_FLAG_REGISTRY_REL = os.path.join("data", "registries", "surface_flag_registry.json")


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


def _flatten_artifact_rows(tile_rows: Sequence[Mapping[str, object]]) -> List[dict]:
    rows: List[dict] = []
    for tile in list(tile_rows or []):
        payload = _as_map(tile)
        for row in _as_list(payload.get("generated_surface_tile_artifact_rows")):
            if isinstance(row, Mapping):
                rows.append(dict(row))
    return rows


def _seed_material_proxy_state(
    tile_rows: Sequence[Mapping[str, object]],
    *,
    universe_identity: Mapping[str, object],
    simulation_tick: int,
    last_processed_tick: int | None = None,
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
        state["earth_material_proxy_runtime_state"] = {
            "version": "EARTH10-3",
            "last_processed_tick": int(last_processed_tick),
            "last_tick_window_start": int(last_processed_tick),
            "last_tick_window_end": int(last_processed_tick),
            "last_tick_window_span": 1,
            "last_due_bucket_ids": [0],
            "last_updated_tile_ids": [],
            "last_skipped_tile_ids": [],
            "last_window_hash": "",
            "last_degraded": False,
            "last_degrade_reason": None,
        }
    return state


def _overlay_hash(rows: Sequence[Mapping[str, object]]) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        normalized.append(
            {
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "material_proxy_id": str(row.get("material_proxy_id", "")).strip(),
                "material_proxy_value": int(_as_int(row.get("material_proxy_value", 0), 0)),
                "surface_flags_mask": int(_as_int(row.get("surface_flags_mask", 0), 0)),
                "surface_flag_ids": [str(item).strip() for item in list(row.get("surface_flag_ids") or []) if str(item).strip()],
                "albedo_proxy_value": int(_as_int(row.get("albedo_proxy_value", 0), 0)),
                "friction_proxy_permille": int(_as_int(row.get("friction_proxy_permille", 0), 0)),
                "derivation_reason": str(row.get("derivation_reason", "")).strip(),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


def _field_projection_hash(state: Mapping[str, object]) -> str:
    rows = []
    for raw in _as_list(_as_map(state).get("field_cells")):
        row = _as_map(raw)
        field_id = str(row.get("field_id", "")).strip()
        if not (
            field_id.startswith("field.material_proxy.surface.")
            or field_id.startswith("field.surface_flags.surface.")
            or field_id.startswith("field.albedo_proxy.surface.")
        ):
            continue
        rows.append(
            {
                "field_id": field_id,
                "cell_id": str(row.get("cell_id", "")).strip(),
                "value": row.get("value"),
                "geo_cell_key": _as_map(_as_map(row.get("extensions")).get("geo_cell_key")),
            }
        )
    rows.sort(key=lambda item: (item["field_id"], item["cell_id"]))
    return canonical_sha256(rows)


def _counts_by_material(rows: Sequence[Mapping[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for raw in list(rows or []):
        material_proxy_id = str(_as_map(raw).get("material_proxy_id", "")).strip()
        if material_proxy_id:
            counts[material_proxy_id] = int(counts.get(material_proxy_id, 0)) + 1
    return dict((key, int(counts[key])) for key in sorted(counts.keys()))


def _counts_by_surface_flag(rows: Sequence[Mapping[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for raw in list(rows or []):
        for flag_id in sorted(str(item).strip() for item in list(_as_map(raw).get("surface_flag_ids") or []) if str(item).strip()):
            counts[flag_id] = int(counts.get(flag_id, 0)) + 1
    return dict((key, int(counts[key])) for key in sorted(counts.keys()))


def generate_material_proxy_tile_fixture(
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


def run_material_proxy_tick_fixture(
    repo_root: str,
    *,
    current_tick: int = MATERIAL_PROXY_REPLAY_TICK,
    last_processed_tick: int | None = MATERIAL_PROXY_LAST_PROCESSED_TICK,
    max_tiles_per_update: int = MATERIAL_PROXY_MAX_TILES_PER_UPDATE,
) -> dict:
    fixture = generate_material_proxy_tile_fixture(repo_root, current_tick=0)
    context = _as_map(fixture.get("context"))
    tiles = [dict(row) for row in _as_list(fixture.get("tiles")) if isinstance(row, Mapping)]
    state = _seed_material_proxy_state(
        tiles,
        universe_identity=_as_map(context.get("universe_identity")),
        simulation_tick=int(current_tick),
        last_processed_tick=last_processed_tick,
    )
    policy = policy_context(max_compute_units_per_tick=4096)
    policy["earth_material_proxy_max_tiles_per_update"] = int(max(0, int(max_tiles_per_update)))
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.earth10.material.tick.{}".format(int(current_tick)),
            "process_id": "process.earth_material_proxy_tick",
            "inputs": {
                "max_tiles_per_update": int(max_tiles_per_update),
            },
        },
        law_profile=law_profile(EARTH10_ALLOWED_PROCESSES),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=policy,
    )
    overlays = [dict(row) for row in _as_list(state.get("earth_material_proxy_tile_overlays")) if isinstance(row, Mapping)]
    runtime_state = _as_map(state.get("earth_material_proxy_runtime_state"))
    payload = {
        "result": str(result.get("result", "")).strip() or "unknown",
        "process_result": dict(result),
        "material_proxy_registry_hash": canonical_sha256(_load_json(repo_root, MATERIAL_PROXY_REGISTRY_REL)),
        "surface_flag_registry_hash": canonical_sha256(_load_json(repo_root, SURFACE_FLAG_REGISTRY_REL)),
        "tick_window_start": int(runtime_state.get("last_tick_window_start", current_tick) or current_tick),
        "tick_window_end": int(runtime_state.get("last_tick_window_end", current_tick) or current_tick),
        "tick_window_span": int(runtime_state.get("last_tick_window_span", 1) or 1),
        "selected_tile_ids": [str(item).strip() for item in list(result.get("selected_tile_ids") or []) if str(item).strip()],
        "skipped_tile_ids": [str(item).strip() for item in list(result.get("skipped_tile_ids") or []) if str(item).strip()],
        "material_proxy_window_hash": str(result.get("material_proxy_window_hash", "")).strip() or material_proxy_window_hash(overlays),
        "overlay_hash": _overlay_hash(overlays),
        "field_projection_hash": _field_projection_hash(state),
        "counts_by_material": _counts_by_material(overlays),
        "counts_by_surface_flag": _counts_by_surface_flag(overlays),
        "overlays": overlays,
        "state": state,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(
        dict(payload, state="<omitted>", overlays="<omitted>", process_result="<omitted>", deterministic_fingerprint="")
    )
    return payload


def verify_material_proxy_window_replay(repo_root: str) -> dict:
    first = run_material_proxy_tick_fixture(repo_root)
    second = run_material_proxy_tick_fixture(repo_root)
    stable = (
        str(first.get("overlay_hash", "")).strip() == str(second.get("overlay_hash", "")).strip()
        and str(first.get("material_proxy_window_hash", "")).strip() == str(second.get("material_proxy_window_hash", "")).strip()
        and str(first.get("field_projection_hash", "")).strip() == str(second.get("field_projection_hash", "")).strip()
        and list(first.get("selected_tile_ids") or []) == list(second.get("selected_tile_ids") or [])
        and list(first.get("skipped_tile_ids") or []) == list(second.get("skipped_tile_ids") or [])
        and dict(first.get("counts_by_material") or {}) == dict(second.get("counts_by_material") or {})
    )
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "material_proxy_registry_hash": str(first.get("material_proxy_registry_hash", "")).strip(),
        "surface_flag_registry_hash": str(first.get("surface_flag_registry_hash", "")).strip(),
        "material_proxy_window_hash": str(first.get("material_proxy_window_hash", "")).strip(),
        "overlay_hash": str(first.get("overlay_hash", "")).strip(),
        "field_projection_hash": str(first.get("field_projection_hash", "")).strip(),
        "counts_by_material": dict(first.get("counts_by_material") or {}),
        "counts_by_surface_flag": dict(first.get("counts_by_surface_flag") or {}),
        "first_run": {
            "tick_window_start": int(first.get("tick_window_start", 0) or 0),
            "tick_window_end": int(first.get("tick_window_end", 0) or 0),
            "tick_window_span": int(first.get("tick_window_span", 0) or 0),
            "selected_tile_ids": list(first.get("selected_tile_ids") or []),
            "skipped_tile_ids": list(first.get("skipped_tile_ids") or []),
            "overlay_hash": str(first.get("overlay_hash", "")).strip(),
        },
        "second_run": {
            "tick_window_start": int(second.get("tick_window_start", 0) or 0),
            "tick_window_end": int(second.get("tick_window_end", 0) or 0),
            "tick_window_span": int(second.get("tick_window_span", 0) or 0),
            "selected_tile_ids": list(second.get("selected_tile_ids") or []),
            "skipped_tile_ids": list(second.get("skipped_tile_ids") or []),
            "overlay_hash": str(second.get("overlay_hash", "")).strip(),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def surface_flag_consistency_report(repo_root: str) -> dict:
    fixture = run_material_proxy_tick_fixture(repo_root)
    violations = []
    for raw in list(fixture.get("overlays") or []):
        row = _as_map(raw)
        material_proxy_id = str(row.get("material_proxy_id", "")).strip()
        surface_flag_ids = set(str(item).strip() for item in list(row.get("surface_flag_ids") or []) if str(item).strip())
        valid = (
            (material_proxy_id == "mat.water" and surface_flag_ids == {"flag.fluid"})
            or (material_proxy_id == "mat.ice" and surface_flag_ids == {"flag.slippery"})
            or (material_proxy_id not in {"mat.water", "mat.ice"} and surface_flag_ids == {"flag.buildable"})
        )
        if not valid:
            violations.append(
                {
                    "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                    "material_proxy_id": material_proxy_id,
                    "surface_flag_ids": sorted(surface_flag_ids),
                }
            )
    report = {
        "result": "complete" if not violations else "violation",
        "violation_count": int(len(violations)),
        "violations": list(violations[:12]),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def albedo_proxy_range_report(repo_root: str) -> dict:
    fixture = run_material_proxy_tick_fixture(repo_root)
    violations = []
    observed_values = []
    for raw in list(fixture.get("overlays") or []):
        row = _as_map(raw)
        albedo_proxy_value = int(_as_int(row.get("albedo_proxy_value", 0), 0))
        observed_values.append(albedo_proxy_value)
        if not (0 <= albedo_proxy_value <= 1000):
            violations.append(
                {
                    "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                    "material_proxy_id": str(row.get("material_proxy_id", "")).strip(),
                    "albedo_proxy_value": albedo_proxy_value,
                }
            )
    report = {
        "result": "complete" if not violations else "violation",
        "minimum_albedo_proxy_value": min(observed_values) if observed_values else 0,
        "maximum_albedo_proxy_value": max(observed_values) if observed_values else 0,
        "violation_count": int(len(violations)),
        "violations": list(violations[:12]),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def material_proxy_hash(repo_root: str) -> str:
    fixture = run_material_proxy_tick_fixture(repo_root)
    return canonical_sha256(
        {
            "material_proxy_window_hash": str(fixture.get("material_proxy_window_hash", "")).strip(),
            "overlay_hash": str(fixture.get("overlay_hash", "")).strip(),
            "field_projection_hash": str(fixture.get("field_projection_hash", "")).strip(),
            "counts_by_material": dict(fixture.get("counts_by_material") or {}),
            "counts_by_surface_flag": dict(fixture.get("counts_by_surface_flag") or {}),
        }
    )


__all__ = [
    "albedo_proxy_range_report",
    "generate_material_proxy_tile_fixture",
    "material_proxy_hash",
    "run_material_proxy_tick_fixture",
    "surface_flag_consistency_report",
    "verify_material_proxy_window_replay",
]
