"""Deterministic EARTH-0 probe helpers for aggregate verification and TestX reuse."""

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
from tools.xstack.testx.tests.sol0_testlib import load_sol_pack_fixture_payloads  # noqa: E402
from tools.xstack.testx.tests.geo8_testlib import worldgen_request_row  # noqa: E402
from geo import (  # noqa: E402
    RNG_WORLDGEN_SURFACE,
    generate_worldgen_result,
    worldgen_cache_clear,
    worldgen_rng_stream_policy,
)
from worldgen.mw import build_planet_surface_cell_key, generate_mw_surface_l3_payload  # noqa: E402
from worldgen.mw.sol_anchor import SOL_ANCHOR_CELL_INDEX_TUPLE  # noqa: E402


REALISM_PROFILE_REGISTRY_REL = os.path.join("data", "registries", "realism_profile_registry.json")
EARTH_SAMPLE_COLUMNS = tuple(range(0, 64, 8))
EARTH_SAMPLE_BANDS = tuple(range(0, 16, 2))
EARTH_SEASON_TICK_A = 0
EARTH_SEASON_TICK_B = 500_000


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    with open(abs_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise RuntimeError("expected object json at {}".format(rel_path.replace("\\", "/")))
    return dict(payload)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _realism_profile_row(repo_root: str, realism_profile_id: str) -> dict:
    payload = _load_json(repo_root, REALISM_PROFILE_REGISTRY_REL)
    record = _as_map(payload.get("record"))
    for raw in _as_list(record.get("realism_profiles")):
        row = _as_map(raw)
        if str(row.get("realism_profile_id", "")).strip() == str(realism_profile_id).strip():
            return row
    raise RuntimeError("realism profile not found: {}".format(realism_profile_id))


def build_earth_probe_context(repo_root: str) -> dict:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    worldgen_cache_clear()
    payloads = load_sol_pack_fixture_payloads(repo_root)
    universe_identity = _as_map(payloads.get("universe_identity"))
    patch_document = _as_map(payloads.get("patch_document"))
    slot_ids = dict(patch_document.get("slot_object_ids") or {})
    earth_object_id = str(slot_ids.get("sol.planet.earth", "")).strip()
    if not earth_object_id:
        raise RuntimeError("Sol pin patch document omitted sol.planet.earth")

    realism_profile_id = str(universe_identity.get("realism_profile_id", "")).strip() or "realism.realistic_default_milkyway_stub"
    realism_row = _realism_profile_row(repo_root, realism_profile_id)
    anchor_cell_key = _as_map(patch_document.get("sol_anchor_cell_key"))
    if not anchor_cell_key:
        raise RuntimeError("Sol pin patch document omitted sol_anchor_cell_key")

    l2_result = generate_worldgen_result(
        universe_identity=universe_identity,
        worldgen_request=worldgen_request_row(
            request_id="earth0.probe.l2",
            index_tuple=SOL_ANCHOR_CELL_INDEX_TUPLE,
            refinement_level=2,
            reason="query",
        ),
        current_tick=0,
        cache_enabled=False,
    )
    if str(l2_result.get("result", "")).strip() != "complete":
        raise RuntimeError("EARTH-0 probe L2 context generation did not complete")

    return {
        "repo_root": repo_root,
        "payloads": payloads,
        "universe_identity": universe_identity,
        "universe_identity_hash": str(universe_identity.get("identity_hash", "")).strip(),
        "realism_profile_id": realism_profile_id,
        "realism_row": realism_row,
        "anchor_cell_key": anchor_cell_key,
        "earth_object_id": earth_object_id,
        "planet_tags": ["planet.earth", "sol.planet.earth"],
        "star_artifact_rows": [dict(row) for row in _as_list(l2_result.get("generated_star_artifact_rows")) if isinstance(row, Mapping)],
        "planet_orbit_artifact_rows": [dict(row) for row in _as_list(l2_result.get("generated_planet_orbit_artifact_rows")) if isinstance(row, Mapping)],
        "planet_basic_artifact_rows": [dict(row) for row in _as_list(l2_result.get("generated_planet_basic_artifact_rows")) if isinstance(row, Mapping)],
    }


def generate_earth_probe_tile(
    context: Mapping[str, object],
    *,
    chart_id: str,
    index_tuple: Sequence[int],
    refinement_level: int = 1,
    current_tick: int = 0,
) -> dict:
    universe_identity = _as_map(context.get("universe_identity"))
    surface_cell_key = build_planet_surface_cell_key(
        planet_object_id=str(context.get("earth_object_id", "")).strip(),
        ancestor_world_cell_key=_as_map(context.get("anchor_cell_key")),
        chart_id=str(chart_id),
        index_tuple=[int(item) for item in list(index_tuple or [])],
        refinement_level=int(refinement_level),
        planet_tags=list(context.get("planet_tags") or []),
    )
    rng_policy = worldgen_rng_stream_policy(
        universe_identity=universe_identity,
        geo_cell_key=surface_cell_key,
        generator_version_id=str(universe_identity.get("generator_version_id", "")).strip(),
        realism_profile_id=str(context.get("realism_profile_id", "")).strip(),
    )
    if str(rng_policy.get("result", "")).strip() != "complete":
        raise RuntimeError("EARTH-0 probe surface RNG policy did not complete")
    surface_stream_seed = ""
    for raw in _as_list(rng_policy.get("streams")):
        row = _as_map(raw)
        if str(row.get("stream_name", "")).strip() == RNG_WORLDGEN_SURFACE:
            surface_stream_seed = str(row.get("stream_seed", "")).strip()
            break
    if not surface_stream_seed:
        raise RuntimeError("EARTH-0 probe surface RNG stream missing {}".format(RNG_WORLDGEN_SURFACE))

    payload = generate_mw_surface_l3_payload(
        universe_identity_hash=str(context.get("universe_identity_hash", "")).strip(),
        surface_geo_cell_key=surface_cell_key,
        ancestor_world_cell_key=_as_map(context.get("anchor_cell_key")),
        realism_profile_row=_as_map(context.get("realism_row")),
        planet_object_id=str(context.get("earth_object_id", "")).strip(),
        planet_basic_artifact_rows=context.get("planet_basic_artifact_rows"),
        planet_orbit_artifact_rows=context.get("planet_orbit_artifact_rows"),
        star_artifact_rows=context.get("star_artifact_rows"),
        surface_stream_seed=surface_stream_seed,
        current_tick=int(current_tick),
    )
    if str(payload.get("result", "")).strip() != "complete":
        raise RuntimeError("EARTH-0 probe tile generation did not complete")
    return {
        "chart_id": str(chart_id),
        "index_tuple": [int(item) for item in list(index_tuple or [])],
        "refinement_level": int(refinement_level),
        "current_tick": int(current_tick),
        "surface_summary": dict(payload.get("surface_summary") or {}),
        "generated_surface_tile_artifact_rows": [dict(row) for row in _as_list(payload.get("generated_surface_tile_artifact_rows")) if isinstance(row, Mapping)],
        "field_initializations": [dict(row) for row in _as_list(payload.get("field_initializations")) if isinstance(row, Mapping)],
        "geometry_initializations": [dict(row) for row in _as_list(payload.get("geometry_initializations")) if isinstance(row, Mapping)],
        "surface_handler_id": str(payload.get("handler_id", "")).strip(),
        "surface_generator_id": str(payload.get("selected_generator_id", "")).strip(),
        "surface_routing_id": str(payload.get("routing_id", "")).strip(),
    }


def sample_earth_surface(
    repo_root: str,
    *,
    current_tick: int = 0,
    chart_ids: Iterable[str] = ("chart.atlas.north", "chart.atlas.south"),
    columns: Iterable[int] = EARTH_SAMPLE_COLUMNS,
    bands: Iterable[int] = EARTH_SAMPLE_BANDS,
) -> List[dict]:
    context = build_earth_probe_context(repo_root)
    samples: List[dict] = []
    for chart_id in list(chart_ids):
        for band in list(bands):
            for column in list(columns):
                samples.append(
                    generate_earth_probe_tile(
                        context,
                        chart_id=str(chart_id),
                        index_tuple=[int(column), int(band)],
                        refinement_level=1,
                        current_tick=int(current_tick),
                    )
                )
    return samples


def earth_surface_sample_hash(samples: Sequence[Mapping[str, object]]) -> str:
    rows = []
    for raw in list(samples or []):
        row = _as_map(raw)
        summary = _as_map(row.get("surface_summary"))
        rows.append(
            {
                "chart_id": str(row.get("chart_id", "")).strip(),
                "index_tuple": [int(item) for item in list(row.get("index_tuple") or [])],
                "surface_class_id": str(summary.get("surface_class_id", "")).strip(),
                "biome_stub_id": str(summary.get("biome_stub_id", "")).strip(),
                "material_baseline_id": str(summary.get("material_baseline_id", "")).strip(),
                "temperature_value": int(summary.get("temperature_value", 0) or 0),
                "daylight_value": int(summary.get("daylight_value", 0) or 0),
                "far_lod_visual_class": str(summary.get("far_lod_visual_class", "")).strip(),
            }
        )
    rows.sort(key=lambda item: (item["chart_id"], item["index_tuple"][1], item["index_tuple"][0]))
    return canonical_sha256(rows)


def _latitude_weight(summary: Mapping[str, object]) -> int:
    latitude_mdeg = abs(int(_as_map(summary).get("latitude_mdeg", 0) or 0))
    return max(1, 90_000 - latitude_mdeg)


def verify_earth_surface_consistency(repo_root: str) -> dict:
    samples = sample_earth_surface(repo_root, current_tick=0)
    summary_rows = [_as_map(row.get("surface_summary")) for row in samples]
    total_weight = max(1, sum(_latitude_weight(row) for row in summary_rows))
    ocean_weight = sum(
        _latitude_weight(row)
        for row in summary_rows
        if str(row.get("surface_class_id", "")).strip() == "surface.class.ocean"
    )
    land_weight = sum(
        _latitude_weight(row)
        for row in summary_rows
        if str(row.get("surface_class_id", "")).strip() == "surface.class.land"
    )
    ice_weight = sum(
        _latitude_weight(row)
        for row in summary_rows
        if str(row.get("surface_class_id", "")).strip() == "surface.class.ice"
    )
    ocean_ratio_permille = (ocean_weight * 1000) // total_weight
    polar_ratio_permille = (ice_weight * 1000) // total_weight

    north_tile_a = generate_earth_probe_tile(
        build_earth_probe_context(repo_root),
        chart_id="chart.atlas.north",
        index_tuple=[16, 2],
        refinement_level=1,
        current_tick=EARTH_SEASON_TICK_A,
    )
    north_tile_b = generate_earth_probe_tile(
        build_earth_probe_context(repo_root),
        chart_id="chart.atlas.north",
        index_tuple=[16, 2],
        refinement_level=1,
        current_tick=EARTH_SEASON_TICK_B,
    )
    daylight_a = int(_as_map(north_tile_a.get("surface_summary")).get("daylight_value", 0) or 0)
    daylight_b = int(_as_map(north_tile_b.get("surface_summary")).get("daylight_value", 0) or 0)
    tilt_affects_daylight = daylight_a != daylight_b

    report = {
        "result": "complete",
        "sample_count": int(len(samples)),
        "ocean_ratio_permille": int(ocean_ratio_permille),
        "land_ratio_permille": int((land_weight * 1000) // total_weight),
        "polar_ice_ratio_permille": int(polar_ratio_permille),
        "ocean_ratio_within_bounds": 600 <= ocean_ratio_permille <= 780,
        "polar_ice_present": 15 <= polar_ratio_permille <= 180,
        "axial_tilt_affects_daylight": bool(tilt_affects_daylight),
        "season_daylight_values": {
            "tick_{}".format(EARTH_SEASON_TICK_A): int(daylight_a),
            "tick_{}".format(EARTH_SEASON_TICK_B): int(daylight_b),
        },
        "surface_sample_hash": earth_surface_sample_hash(samples),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


__all__ = [
    "EARTH_SAMPLE_BANDS",
    "EARTH_SAMPLE_COLUMNS",
    "EARTH_SEASON_TICK_A",
    "EARTH_SEASON_TICK_B",
    "build_earth_probe_context",
    "earth_surface_sample_hash",
    "generate_earth_probe_tile",
    "sample_earth_surface",
    "verify_earth_surface_consistency",
]
