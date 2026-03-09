"""Deterministic EARTH-8 water-visual probes for replay and TestX reuse."""

from __future__ import annotations

import os
import sys
from typing import List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.geo import build_position_ref  # noqa: E402
from src.worldgen.earth import (  # noqa: E402
    DEFAULT_TIDE_PARAMS_ID,
    build_water_view_surface,
    evaluate_earth_tile_tide,
    tide_params_rows,
)
from tools.worldgen.earth0_probe import (  # noqa: E402
    build_earth_probe_context,
    generate_earth_probe_tile,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


WATER_SAMPLE_TICK = 15
WATER_RENDER_CENTER = ("chart.atlas.north", [0, 0])
WATER_REGION_SPECS = (
    ("chart.atlas.north", tuple(range(0, 10)), tuple(range(0, 3))),
    ("chart.atlas.south", tuple(range(18, 21)), tuple(range(1, 4))),
)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _flatten_surface_artifact_rows(tile_rows: Sequence[Mapping[str, object]]) -> List[dict]:
    rows: List[dict] = []
    for tile in list(tile_rows or []):
        payload = _as_map(tile)
        for row in _as_list(payload.get("generated_surface_tile_artifact_rows")):
            if isinstance(row, Mapping):
                rows.append(dict(row))
    return rows


def _observer_fixture(context: Mapping[str, object], tile_rows: Sequence[Mapping[str, object]]) -> tuple[dict, dict]:
    chart_id, index_tuple = WATER_RENDER_CENTER
    fallback = {}
    for tile in list(tile_rows or []):
        payload = _as_map(tile)
        if str(payload.get("chart_id", "")).strip() == str(chart_id) and list(payload.get("index_tuple") or []) == list(index_tuple):
            fallback = dict(list(payload.get("generated_surface_tile_artifact_rows") or [])[0] or {})
            break
    if not fallback:
        first_tile = _as_map(tile_rows[0] if tile_rows else {})
        first_artifact_rows = _as_list(first_tile.get("generated_surface_tile_artifact_rows"))
        fallback = dict(first_artifact_rows[0] or {}) if first_artifact_rows else {}
    artifact_ext = _as_map(fallback.get("extensions"))
    observer_ref = build_position_ref(
        object_id="camera.earth8.probe",
        frame_id="frame.surface_local",
        local_position=[0, 0, 1600],
        extensions={
            "latitude_mdeg": int(artifact_ext.get("latitude_mdeg", 0) or 0),
            "longitude_mdeg": int(artifact_ext.get("longitude_mdeg", 0) or 0),
            "geo_cell_key": dict(fallback.get("tile_cell_key") or {}),
            "source": "EARTH8-6",
        },
    )
    return observer_ref, fallback


def _tide_overlay_rows(repo_root: str, artifact_rows: Sequence[Mapping[str, object]], *, current_tick: int) -> List[dict]:
    registry_path = os.path.join(repo_root, "data", "registries", "tide_params_registry.json")
    with open(registry_path, "r", encoding="utf-8") as handle:
        registry_payload = tide_params_rows(__import__("json").load(handle))
    tide_row = dict(registry_payload.get(DEFAULT_TIDE_PARAMS_ID) or {})
    if not tide_row:
        raise RuntimeError("EARTH-8 tide params missing {}".format(DEFAULT_TIDE_PARAMS_ID))
    rows = []
    for artifact in list(artifact_rows or []):
        rows.append(
            evaluate_earth_tile_tide(
                artifact_row=dict(artifact),
                tide_params_row=tide_row,
                current_tick=int(current_tick),
            )
        )
    return [dict(row) for row in rows]


def build_water_fixture(
    repo_root: str,
    *,
    current_tick: int = WATER_SAMPLE_TICK,
    ui_mode: str = "gui",
) -> dict:
    context = build_earth_probe_context(repo_root)
    tile_rows: List[dict] = []
    for chart_id, columns, bands in list(WATER_REGION_SPECS):
        for band in list(bands):
            for column in list(columns):
                tile_rows.append(
                    generate_earth_probe_tile(
                        context,
                        chart_id=str(chart_id),
                        index_tuple=[int(column), int(band)],
                        refinement_level=1,
                        current_tick=int(current_tick),
                    )
                )
    artifact_rows = _flatten_surface_artifact_rows(tile_rows)
    observer_ref, observer_surface_artifact = _observer_fixture(context, tile_rows)
    water_view_surface = build_water_view_surface(
        current_tick=int(current_tick),
        observer_ref=observer_ref,
        observer_surface_artifact=observer_surface_artifact,
        region_cell_keys=[dict(row.get("tile_cell_key") or {}) for row in artifact_rows],
        surface_tile_artifact_rows=artifact_rows,
        tide_overlay_rows=_tide_overlay_rows(repo_root, artifact_rows, current_tick=int(current_tick)),
        ui_mode=str(ui_mode),
    )
    return {
        "context": context,
        "tile_rows": tile_rows,
        "surface_tile_artifact_rows": artifact_rows,
        "observer_ref": observer_ref,
        "observer_surface_artifact": observer_surface_artifact,
        "water_view_surface": water_view_surface,
    }


def verify_water_view_replay(repo_root: str) -> dict:
    first = build_water_fixture(repo_root, current_tick=WATER_SAMPLE_TICK)
    second = build_water_fixture(repo_root, current_tick=WATER_SAMPLE_TICK)
    first_surface = _as_map(first.get("water_view_surface"))
    second_surface = _as_map(second.get("water_view_surface"))
    first_artifact = _as_map(first_surface.get("water_view_artifact"))
    second_artifact = _as_map(second_surface.get("water_view_artifact"))
    normalized_first_surface = dict(first_surface)
    normalized_second_surface = dict(second_surface)
    normalized_first_surface.pop("cache_hit", None)
    normalized_second_surface.pop("cache_hit", None)
    stable = normalized_first_surface == normalized_second_surface and first_artifact == second_artifact
    report = {
        "result": "complete" if stable else "violation",
        "stable_across_repeated_runs": bool(stable),
        "artifact_fingerprint": str(first_artifact.get("deterministic_fingerprint", "")).strip(),
        "cache_key": str(_as_map(first_artifact.get("extensions")).get("cache_key", "")).strip(),
        "ocean_tile_count": int(len(list(first_artifact.get("ocean_mask_ref") or []))),
        "river_tile_count": int(len(list(first_artifact.get("river_mask_ref") or []))),
        "lake_tile_count": int(len(list(first_artifact.get("lake_mask_ref") or []))),
        "surface_fingerprint": canonical_sha256(normalized_first_surface),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def river_mask_report(repo_root: str) -> dict:
    fixture = build_water_fixture(repo_root, current_tick=WATER_SAMPLE_TICK)
    surface_rows = [dict(row) for row in list(fixture.get("surface_tile_artifact_rows") or []) if isinstance(row, Mapping)]
    water_artifact = _as_map(_as_map(fixture.get("water_view_surface")).get("water_view_artifact"))
    expected = sorted(
        str(row.get("tile_object_id", "")).strip()
        for row in surface_rows
        if bool(row.get("river_flag", False))
    )
    actual_rows = [dict(_as_map(row)) for row in list(water_artifact.get("river_mask_ref") or []) if isinstance(row, Mapping)]
    actual = sorted(
        str(row.get("tile_object_id", "")).strip()
        for row in actual_rows
        if str(row.get("tile_object_id", "")).strip()
    )
    flow_convergence_rows = [
        dict(row)
        for row in actual_rows
        if str(row.get("river_source_kind", "")).strip() == "flow_convergence"
    ]
    expected_subset_present = set(expected).issubset(set(actual))
    hydrology_flags_preserved = bool(expected_subset_present)
    visual_river_present = bool(actual_rows)
    flow_convergence_present = bool(flow_convergence_rows)
    return {
        "result": (
            "complete"
            if hydrology_flags_preserved and visual_river_present and (bool(expected) or flow_convergence_present)
            else "violation"
        ),
        "expected_tile_ids": expected,
        "actual_tile_ids": actual,
        "counts_match": len(actual) == len(expected),
        "expected_subset_present": bool(expected_subset_present),
        "hydrology_flags_preserved": bool(hydrology_flags_preserved),
        "visual_river_present": bool(visual_river_present),
        "flow_convergence_present": bool(flow_convergence_present),
        "flow_convergence_tile_ids": sorted(
            str(row.get("tile_object_id", "")).strip()
            for row in flow_convergence_rows
            if str(row.get("tile_object_id", "")).strip()
        ),
    }


def tide_offset_report(repo_root: str) -> dict:
    water_artifact = _as_map(_as_map(build_water_fixture(repo_root, current_tick=WATER_SAMPLE_TICK).get("water_view_surface")).get("water_view_artifact"))
    tide_rows = [dict(row) for row in list(water_artifact.get("tide_offset_ref") or []) if isinstance(row, Mapping)]
    nonzero = [row for row in tide_rows if int(_as_map(row).get("tide_offset_value", 0) or 0) != 0]
    return {
        "result": "complete" if tide_rows and nonzero else "violation",
        "tide_tile_count": int(len(tide_rows)),
        "nonzero_tile_count": int(len(nonzero)),
        "max_abs_tide_offset": max(abs(int(_as_map(row).get("tide_offset_value", 0) or 0)) for row in tide_rows) if tide_rows else 0,
    }


def water_hash(repo_root: str) -> str:
    surface = _as_map(build_water_fixture(repo_root, current_tick=WATER_SAMPLE_TICK).get("water_view_surface"))
    artifact = _as_map(surface.get("water_view_artifact"))
    return canonical_sha256(
        {
            "artifact_fingerprint": str(artifact.get("deterministic_fingerprint", "")).strip(),
            "summary": dict(_as_map(surface.get("presentation")).get("summary") or {}),
            "ocean_count": int(len(list(artifact.get("ocean_mask_ref") or []))),
            "river_count": int(len(list(artifact.get("river_mask_ref") or []))),
            "lake_count": int(len(list(artifact.get("lake_mask_ref") or []))),
            "tide_count": int(len(list(artifact.get("tide_offset_ref") or []))),
        }
    )


__all__ = [
    "build_water_fixture",
    "river_mask_report",
    "tide_offset_report",
    "verify_water_view_replay",
    "water_hash",
]
