"""Deterministic EARTH-1 macro hydrology helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Callable, Dict, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key, geo_cell_key_neighbors


DEFAULT_HYDROLOGY_PARAMS_ID = "params.hydrology.default_stub"
HYDROLOGY_PARAMS_REGISTRY_REL = os.path.join("data", "registries", "hydrology_params_registry.json")
HYDROLOGY_ENGINE_VERSION = "EARTH1-3"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(json.load(handle) or {})
    except (OSError, TypeError, ValueError):
        return {}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_bool(value: object) -> bool:
    return bool(value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value or []) if isinstance(value, list) else []


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(int(minimum), min(int(maximum), int(value)))


def _rows_by_id(payload: Mapping[str, object] | None, *, row_key: str, id_key: str) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get(row_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get(id_key, ""))):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def hydrology_params_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(HYDROLOGY_PARAMS_REGISTRY_REL),
        row_key="hydrology_params",
        id_key="params_id",
    )


def _geo_cell_key_sort_tuple(value: object) -> Tuple[str, Tuple[int, ...], int, str, str]:
    row = _coerce_cell_key(value)
    if not row:
        return ("", tuple(), 0, "", "")
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(item) for item in list(row.get("index_tuple") or [])),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
        str(row.get("partition_profile_id", "")).strip(),
        str(row.get("topology_profile_id", "")).strip(),
    )


def _cell_hash(value: object) -> str:
    row = _coerce_cell_key(value)
    return canonical_sha256(_semantic_cell_key(row)) if row else ""


def _sorted_geo_cell_keys(values: Sequence[object]) -> List[dict]:
    rows = [_coerce_cell_key(item) for item in list(values or [])]
    return [dict(row) for row in sorted((row for row in rows if row), key=_geo_cell_key_sort_tuple)]


def _normalize_tile_snapshot(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    cell_key = _coerce_cell_key(payload.get("tile_cell_key") or payload.get("geo_cell_key"))
    if not cell_key:
        raise ValueError("tile_cell_key is required")
    extensions = _as_map(payload.get("extensions"))
    normalized = {
        "tile_cell_key": dict(cell_key),
        "surface_class_id": str(payload.get("surface_class_id", "")).strip()
        or str(extensions.get("surface_class_id", "")).strip(),
        "material_baseline_id": str(payload.get("material_baseline_id", "")).strip(),
        "biome_stub_id": str(payload.get("biome_stub_id", "")).strip(),
        "effective_height_proxy": int(
            max(
                0,
                _as_int(
                    payload.get(
                        "effective_height_proxy",
                        extensions.get(
                            "hydrology_effective_height_proxy",
                            _as_map(payload.get("elevation_params_ref")).get("height_proxy", payload.get("height_proxy", 0)),
                        ),
                    ),
                    0,
                ),
            )
        ),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(extensions.items(), key=lambda item: str(item[0]))
        },
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def _window_cell_keys(*, center_tile_cell_key: Mapping[str, object], radius: int, max_window_tiles: int) -> List[dict]:
    center = _coerce_cell_key(center_tile_cell_key)
    if not center:
        return []
    payload = geo_cell_key_neighbors(center, int(max(0, radius)))
    neighbors = []
    if str(payload.get("result", "")) == "complete":
        neighbors = [dict(row) for row in list(payload.get("neighbors") or []) if isinstance(row, Mapping)]
    rows = _sorted_geo_cell_keys([center] + neighbors)
    return [dict(row) for row in rows[: max(1, int(max_window_tiles))]]


def _neighbor_rows(cell_key: Mapping[str, object]) -> List[dict]:
    payload = geo_cell_key_neighbors(_coerce_cell_key(cell_key), 1)
    if str(payload.get("result", "")) != "complete":
        return []
    return _sorted_geo_cell_keys(list(payload.get("neighbors") or []))


def _resolve_snapshot_cached(
    *,
    cell_key: Mapping[str, object],
    resolver: Callable[[Mapping[str, object]], Mapping[str, object]],
    cache: Dict[str, dict],
) -> dict:
    key_row = _coerce_cell_key(cell_key)
    if not key_row:
        return {}
    key_hash = _cell_hash(key_row)
    cached = cache.get(key_hash)
    if cached:
        return dict(cached)
    resolved = _normalize_tile_snapshot(resolver(dict(key_row)))
    cache[key_hash] = dict(resolved)
    return dict(resolved)


def hydrology_window_hash(rows: object) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        cell_key = _coerce_cell_key(row.get("tile_cell_key"))
        if not cell_key:
            continue
        normalized.append(
            {
                "tile_cell_key": dict(cell_key),
                "effective_height_proxy": int(max(0, _as_int(row.get("effective_height_proxy", 0), 0))),
                "surface_class_id": str(row.get("surface_class_id", "")).strip(),
                "flow_target_tile_key": _as_map(row.get("flow_target_tile_key")),
                "drainage_accumulation_proxy": int(max(1, _as_int(row.get("drainage_accumulation_proxy", 1), 1))),
                "river_flag": bool(row.get("river_flag", False)),
                "lake_flag": bool(row.get("lake_flag", False)),
            }
        )
    normalized.sort(key=lambda item: _geo_cell_key_sort_tuple(item.get("tile_cell_key")))
    return canonical_sha256(normalized)


def compute_hydrology_window(
    *,
    center_tile_cell_key: Mapping[str, object],
    hydrology_params_row: Mapping[str, object],
    resolve_tile_snapshot: Callable[[Mapping[str, object]], Mapping[str, object]],
) -> dict:
    center = _coerce_cell_key(center_tile_cell_key)
    params_row = _as_map(hydrology_params_row)
    if not center:
        raise ValueError("center_tile_cell_key is required")
    if not params_row:
        raise ValueError("hydrology_params_row is required")
    extensions = _as_map(params_row.get("extensions"))
    analysis_radius = _clamp(_as_int(extensions.get("analysis_radius", 2), 2), 1, 4)
    max_window_tiles = max(1, _as_int(extensions.get("max_window_tiles", 32), 32))
    accumulation_threshold = max(1, _as_int(params_row.get("accumulation_threshold", 7), 7))
    lake_delta_threshold = max(0, _as_int(params_row.get("lake_elevation_delta_threshold", 220), 220))
    window_rows = _window_cell_keys(center_tile_cell_key=center, radius=analysis_radius, max_window_tiles=max_window_tiles)
    snapshot_cache: Dict[str, dict] = {}
    window_snapshots: Dict[str, dict] = {}
    for cell_key in window_rows:
        snapshot = _resolve_snapshot_cached(cell_key=cell_key, resolver=resolve_tile_snapshot, cache=snapshot_cache)
        if snapshot:
            window_snapshots[_cell_hash(cell_key)] = snapshot

    flow_target_by_hash: Dict[str, dict] = {}
    lake_flag_by_hash: Dict[str, bool] = {}
    exit_window_by_hash: Dict[str, bool] = {}
    effective_height_by_hash = dict(
        (cell_hash, int(max(0, _as_int(row.get("effective_height_proxy", 0), 0))))
        for cell_hash, row in sorted(window_snapshots.items())
    )

    for cell_hash, snapshot in sorted(window_snapshots.items(), key=lambda item: _geo_cell_key_sort_tuple(item[1].get("tile_cell_key"))):
        current_height = int(max(0, _as_int(snapshot.get("effective_height_proxy", 0), 0)))
        neighbor_snapshots = []
        for neighbor_key in _neighbor_rows(snapshot.get("tile_cell_key")):
            neighbor_snapshot = _resolve_snapshot_cached(cell_key=neighbor_key, resolver=resolve_tile_snapshot, cache=snapshot_cache)
            if not neighbor_snapshot:
                continue
            neighbor_snapshots.append(neighbor_snapshot)
        lower_neighbors = [
            row
            for row in neighbor_snapshots
            if int(max(0, _as_int(row.get("effective_height_proxy", 0), 0))) < current_height
        ]
        lower_neighbors.sort(
            key=lambda row: (
                int(max(0, _as_int(row.get("effective_height_proxy", 0), 0))),
                _geo_cell_key_sort_tuple(row.get("tile_cell_key")),
            )
        )
        selected_target = dict(lower_neighbors[0].get("tile_cell_key")) if lower_neighbors else {}
        if selected_target:
            flow_target_by_hash[cell_hash] = selected_target
            exit_window_by_hash[cell_hash] = _cell_hash(selected_target) not in window_snapshots
        else:
            spill_candidates = sorted(
                (
                    row
                    for row in neighbor_snapshots
                    if int(max(0, _as_int(row.get("effective_height_proxy", current_height), current_height))) >= current_height
                ),
                key=lambda row: (
                    int(max(0, _as_int(row.get("effective_height_proxy", current_height), current_height))),
                    _geo_cell_key_sort_tuple(row.get("tile_cell_key")),
                ),
            )
            spill_height = (
                int(max(0, _as_int(spill_candidates[0].get("effective_height_proxy", current_height), current_height)))
                if spill_candidates
                else current_height + lake_delta_threshold + 1
            )
            surface_class_id = str(snapshot.get("surface_class_id", "")).strip()
            lake_flag_by_hash[cell_hash] = bool(
                surface_class_id not in {"surface.class.ocean", "surface.class.ice"}
                and int(max(0, spill_height - current_height)) <= lake_delta_threshold
            )
            exit_window_by_hash[cell_hash] = False

    accumulation_by_hash = dict((cell_hash, 1) for cell_hash in window_snapshots.keys())
    sorted_for_accumulation = sorted(
        window_snapshots.items(),
        key=lambda item: (
            -int(max(0, _as_int(item[1].get("effective_height_proxy", 0), 0))),
            _geo_cell_key_sort_tuple(item[1].get("tile_cell_key")),
        ),
    )
    for cell_hash, snapshot in sorted_for_accumulation:
        target_key = _as_map(flow_target_by_hash.get(cell_hash))
        target_hash = _cell_hash(target_key)
        if target_key and target_hash in accumulation_by_hash:
            accumulation_by_hash[target_hash] = int(accumulation_by_hash[target_hash] + accumulation_by_hash[cell_hash])

    rows = []
    for cell_hash, snapshot in sorted(window_snapshots.items(), key=lambda item: _geo_cell_key_sort_tuple(item[1].get("tile_cell_key"))):
        surface_class_id = str(snapshot.get("surface_class_id", "")).strip()
        river_flag = bool(
            surface_class_id != "surface.class.ocean"
            and int(accumulation_by_hash.get(cell_hash, 1)) >= accumulation_threshold
        )
        rows.append(
            {
                "tile_cell_key": dict(snapshot.get("tile_cell_key") or {}),
                "surface_class_id": surface_class_id,
                "material_baseline_id": str(snapshot.get("material_baseline_id", "")).strip(),
                "biome_stub_id": str(snapshot.get("biome_stub_id", "")).strip(),
                "effective_height_proxy": int(effective_height_by_hash.get(cell_hash, 0)),
                "flow_target_tile_key": _as_map(flow_target_by_hash.get(cell_hash)),
                "drainage_accumulation_proxy": int(max(1, accumulation_by_hash.get(cell_hash, 1))),
                "river_flag": bool(river_flag),
                "lake_flag": bool(lake_flag_by_hash.get(cell_hash, False)),
                "exit_window": bool(exit_window_by_hash.get(cell_hash, False)),
            }
        )
    window_fingerprint = hydrology_window_hash(rows)
    center_hash = _cell_hash(center)
    center_row = next((dict(row) for row in rows if _cell_hash(row.get("tile_cell_key")) == center_hash), {})
    return {
        "hydrology_params_id": str(params_row.get("params_id", "")).strip() or DEFAULT_HYDROLOGY_PARAMS_ID,
        "analysis_radius": int(analysis_radius),
        "accumulation_threshold": int(accumulation_threshold),
        "lake_elevation_delta_threshold": int(lake_delta_threshold),
        "window_rows": rows,
        "window_fingerprint": window_fingerprint,
        "center_tile": {
            **center_row,
            "analysis_radius": int(analysis_radius),
            "window_fingerprint": window_fingerprint,
            "deterministic_fingerprint": canonical_sha256(
                {
                    **center_row,
                    "analysis_radius": int(analysis_radius),
                    "window_fingerprint": window_fingerprint,
                }
            ),
        },
        "deterministic_fingerprint": canonical_sha256(
            {
                "hydrology_params_id": str(params_row.get("params_id", "")).strip() or DEFAULT_HYDROLOGY_PARAMS_ID,
                "analysis_radius": int(analysis_radius),
                "window_fingerprint": window_fingerprint,
                "rows": rows,
            }
        ),
    }


def apply_hydrology_to_surface_tile_artifact(
    *,
    artifact_row: Mapping[str, object],
    hydrology_center_row: Mapping[str, object],
    hydrology_params_id: str,
) -> dict:
    row = _as_map(artifact_row)
    center = _as_map(hydrology_center_row)
    tile_object_id = str(row.get("tile_object_id", "")).strip()
    if not tile_object_id:
        raise ValueError("artifact_row.tile_object_id is required")
    extensions = {
        str(key): value
        for key, value in sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))
    }
    biome_overlay_tags = sorted(
        set(
            str(tag).strip()
            for tag in list(extensions.get("biome_overlay_tags") or [])
            if str(tag).strip()
        )
    )
    if bool(center.get("river_flag", False)):
        biome_overlay_tags = sorted(set(biome_overlay_tags + ["river"]))
    if bool(center.get("lake_flag", False)):
        biome_overlay_tags = sorted(set(biome_overlay_tags + ["lake"]))
    merged = {
        "tile_object_id": tile_object_id,
        "planet_object_id": str(row.get("planet_object_id", "")).strip(),
        "tile_cell_key": _as_map(row.get("tile_cell_key")),
        "elevation_params_ref": _as_map(row.get("elevation_params_ref")),
        "material_baseline_id": str(row.get("material_baseline_id", "")).strip(),
        "biome_stub_id": str(row.get("biome_stub_id", "")).strip(),
        "drainage_accumulation_proxy": int(max(1, _as_int(center.get("drainage_accumulation_proxy", 1), 1))),
        "river_flag": bool(center.get("river_flag", False)),
        "deterministic_fingerprint": "",
        "extensions": {
            **extensions,
            "hydrology_params_id": str(hydrology_params_id or "").strip() or DEFAULT_HYDROLOGY_PARAMS_ID,
            "hydrology_window_fingerprint": str(center.get("window_fingerprint", "")).strip(),
            "hydrology_effective_height_proxy": int(max(0, _as_int(center.get("effective_height_proxy", 0), 0))),
            "lake_flag": bool(center.get("lake_flag", False)),
            "hydrology_exit_window": bool(center.get("exit_window", False)),
            "hydrology_structure_kind": (
                "river" if bool(center.get("river_flag", False)) else ("lake" if bool(center.get("lake_flag", False)) else "none")
            ),
            "biome_overlay_tags": biome_overlay_tags,
            "source": HYDROLOGY_ENGINE_VERSION,
        },
    }
    flow_target = _as_map(center.get("flow_target_tile_key"))
    if flow_target:
        merged["flow_target_tile_key"] = flow_target
    merged["deterministic_fingerprint"] = canonical_sha256(dict(merged, deterministic_fingerprint=""))
    return merged


def build_poll_transport_stub(
    *,
    artifact_row: Mapping[str, object],
    tile_rows_by_cell_hash: Mapping[str, object] | None = None,
    max_steps: int = 16,
) -> dict:
    current = _as_map(artifact_row)
    rows_by_hash = dict(tile_rows_by_cell_hash or {})
    chain: List[dict] = []
    visited: set[str] = set()
    for _ in range(max(1, _as_int(max_steps, 16))):
        cell_key = _as_map(current.get("tile_cell_key"))
        cell_hash = _cell_hash(cell_key)
        if (not cell_key) or (cell_hash in visited):
            break
        visited.add(cell_hash)
        chain.append(dict(cell_key))
        target_key = _as_map(current.get("flow_target_tile_key"))
        if not target_key:
            break
        next_row = _as_map(rows_by_hash.get(_cell_hash(target_key)))
        current = (
            next_row
            if next_row
            else {
                "tile_cell_key": dict(target_key),
                "flow_target_tile_key": {},
            }
        )
    payload = {
        "channel_kind": "poll.transport.surface_flow_stub",
        "tile_chain": chain,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_fluid_channel_guidance(*, artifact_row: Mapping[str, object]) -> dict:
    row = _as_map(artifact_row)
    payload = {
        "guidance_kind": "fluid.surface_flow_graph_stub",
        "entry_tile_key": _as_map(row.get("tile_cell_key")),
        "flow_target_tile_key": _as_map(row.get("flow_target_tile_key")),
        "river_flag": bool(row.get("river_flag", False)),
        "drainage_accumulation_proxy": int(max(1, _as_int(row.get("drainage_accumulation_proxy", 1), 1))),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "DEFAULT_HYDROLOGY_PARAMS_ID",
    "HYDROLOGY_ENGINE_VERSION",
    "HYDROLOGY_PARAMS_REGISTRY_REL",
    "apply_hydrology_to_surface_tile_artifact",
    "build_fluid_channel_guidance",
    "build_poll_transport_stub",
    "compute_hydrology_window",
    "hydrology_params_rows",
    "hydrology_window_hash",
]
