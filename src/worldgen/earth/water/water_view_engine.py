"""Deterministic EARTH-8 water-view artifact helpers."""

from __future__ import annotations

import copy
import json
import os
from functools import lru_cache
from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key, geo_cell_key_neighbors
from ..material import evaluate_earth_tile_material_proxy


DEFAULT_WATER_VISUAL_POLICY_ID = "water.mvp_default"
WATER_VISUAL_POLICY_REGISTRY_REL = os.path.join("data", "registries", "water_visual_policy_registry.json")
EARTH_WATER_VIEW_ENGINE_VERSION = "EARTH8-3"
_WATER_VIEW_CACHE: Dict[str, dict] = {}
_WATER_VIEW_CACHE_MAX = 128


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", "..", ".."))


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


def water_visual_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(WATER_VISUAL_POLICY_REGISTRY_REL),
        row_key="water_visual_policies",
        id_key="policy_id",
    )


def water_visual_policy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(WATER_VISUAL_POLICY_REGISTRY_REL))


def _geo_hash(cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(cell_key) or {}
    return canonical_sha256(_semantic_cell_key(key_row)) if key_row else ""


def _geo_sort_tuple(cell_key: Mapping[str, object]) -> tuple:
    key_row = _coerce_cell_key(cell_key) or {}
    chart_id = str(key_row.get("chart_id", "")).strip()
    index_tuple = [int(item) for item in list(key_row.get("index_tuple") or [])]
    while len(index_tuple) < 3:
        index_tuple.append(0)
    return (
        chart_id,
        int(_as_int(key_row.get("refinement_level", 0), 0)),
        int(index_tuple[1]),
        int(index_tuple[0]),
        int(index_tuple[2]),
    )


def _legacy_cell_alias_from_tile_key(tile_cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(tile_cell_key) or {}
    extensions = _as_map(key_row.get("extensions"))
    alias = str(extensions.get("legacy_cell_alias", "")).strip()
    if alias:
        return alias
    base_chart_id = str(extensions.get("base_chart_id", "")).strip().lower()
    chart_id = str(key_row.get("chart_id", "")).strip().lower()
    chart_token = "south" if ("south" in base_chart_id or "south" in chart_id) else "north"
    index_tuple = list(key_row.get("index_tuple") or [])
    u_idx = int(index_tuple[0]) if len(index_tuple) > 0 else 0
    v_idx = int(index_tuple[1]) if len(index_tuple) > 1 else 0
    return "atlas.{}.{}.{}".format(chart_token, u_idx, v_idx)


def _sorted_geo_cell_keys(values: object) -> List[dict]:
    rows = [_coerce_cell_key(item) for item in list(values or [])]
    return [dict(row) for row in sorted((row for row in rows if row), key=_geo_sort_tuple)]


def _observer_cell_key(
    *,
    observer_surface_artifact: Mapping[str, object] | None,
    observer_ref: Mapping[str, object] | None,
) -> dict:
    artifact = _as_map(observer_surface_artifact)
    tile_cell_key = _as_map(artifact.get("tile_cell_key"))
    if tile_cell_key:
        return tile_cell_key
    observer_ext = _as_map(_as_map(observer_ref).get("extensions"))
    return _as_map(observer_ext.get("geo_cell_key"))


def _default_region_cell_keys(
    *,
    observer_cell_key: Mapping[str, object] | None,
    water_visual_policy_row: Mapping[str, object],
) -> List[dict]:
    key_row = _coerce_cell_key(observer_cell_key) or {}
    if not key_row:
        return []
    policy_ext = _as_map(_as_map(water_visual_policy_row).get("extensions"))
    radius = _clamp(_as_int(policy_ext.get("default_neighbor_radius", 2), 2), 0, 3)
    max_region_tiles = max(1, _as_int(policy_ext.get("max_region_tiles", 81), 81))
    payload = geo_cell_key_neighbors(key_row, radius)
    neighbors = []
    if str(payload.get("result", "")).strip() == "complete":
        neighbors = [dict(row) for row in list(payload.get("neighbors") or []) if isinstance(row, Mapping)]
    rows = _sorted_geo_cell_keys([key_row] + neighbors)
    return [dict(row) for row in rows[:max_region_tiles]]


def _surface_class_id(artifact_row: Mapping[str, object]) -> str:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    material_id = str(row.get("material_baseline_id", "")).strip()
    surface_class_id = str(extensions.get("surface_class_id", "")).strip()
    if surface_class_id:
        return surface_class_id
    if material_id == "material.water":
        return "surface.class.ocean"
    if "ice" in material_id:
        return "surface.class.ice"
    return "surface.class.land"


def _is_ocean_tile(artifact_row: Mapping[str, object]) -> bool:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    if bool(extensions.get("lake_flag", False)):
        return False
    return _surface_class_id(row) == "surface.class.ocean"


def _river_flag(artifact_row: Mapping[str, object]) -> bool:
    row = _as_map(artifact_row)
    if bool(row.get("river_flag", False)):
        return True
    biome_overlay_tags = [str(item).strip() for item in _as_list(_as_map(row.get("extensions")).get("biome_overlay_tags")) if str(item).strip()]
    return "river" in set(biome_overlay_tags)


def _lake_flag(artifact_row: Mapping[str, object]) -> bool:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    if bool(extensions.get("lake_flag", False)):
        return True
    return str(extensions.get("hydrology_structure_kind", "")).strip() == "lake"


def _river_fan_in_count_by_hash(
    artifact_rows_by_hash: Mapping[str, object],
    artifact_rows_by_alias: Mapping[str, object],
) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for cell_hash, raw in sorted(artifact_rows_by_hash.items()):
        row = _as_map(raw)
        if _is_ocean_tile(row) or _lake_flag(row):
            continue
        target_key = _coerce_cell_key(row.get("flow_target_tile_key")) or {}
        target_row = _as_map(artifact_rows_by_alias.get(_legacy_cell_alias_from_tile_key(target_key)))
        target_hash = _geo_hash(_as_map(target_row.get("tile_cell_key")))
        if not target_hash or target_hash not in artifact_rows_by_hash:
            continue
        counts[target_hash] = int(counts.get(target_hash, 0)) + 1
    return dict((key, int(counts[key])) for key in sorted(counts.keys()))


def _tide_overlay_lookup(tide_overlay_rows: object) -> tuple[Dict[str, dict], Dict[str, dict]]:
    by_tile_id: Dict[str, dict] = {}
    by_cell_hash: Dict[str, dict] = {}
    for raw in list(tide_overlay_rows or []):
        row = _as_map(raw)
        tile_id = str(row.get("tile_object_id", "")).strip()
        cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if tile_id:
            by_tile_id[tile_id] = dict(row)
        if cell_key:
            by_cell_hash[_geo_hash(cell_key)] = dict(row)
    return by_tile_id, by_cell_hash


def _artifact_rows_by_cell_hash(surface_tile_artifact_rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(surface_tile_artifact_rows or []):
        row = _as_map(raw)
        cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        cell_hash = _geo_hash(cell_key)
        tile_id = str(row.get("tile_object_id", "")).strip()
        if cell_hash and tile_id:
            out[cell_hash] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _artifact_rows_by_legacy_alias(surface_tile_artifact_rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for raw in list(surface_tile_artifact_rows or []):
        row = _as_map(raw)
        cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        tile_id = str(row.get("tile_object_id", "")).strip()
        if cell_key and tile_id:
            out[_legacy_cell_alias_from_tile_key(cell_key)] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _material_proxy_preview(
    artifact_row: Mapping[str, object] | None,
    *,
    current_tick: int,
) -> dict:
    row = _as_map(artifact_row)
    if not row:
        return {}
    return evaluate_earth_tile_material_proxy(
        artifact_row=row,
        current_tick=int(current_tick),
        geometry_row=None,
    )


def water_view_artifact_hash(artifact_row: Mapping[str, object] | None) -> str:
    artifact = _as_map(artifact_row)
    if not artifact:
        return ""
    semantic = dict(artifact)
    semantic.pop("deterministic_fingerprint", None)
    return canonical_sha256(semantic)


def _cache_lookup(cache_key: str) -> dict | None:
    row = _WATER_VIEW_CACHE.get(str(cache_key))
    if not isinstance(row, dict):
        return None
    return copy.deepcopy(dict(row))


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _WATER_VIEW_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_WATER_VIEW_CACHE) > _WATER_VIEW_CACHE_MAX:
        for stale_key in sorted(_WATER_VIEW_CACHE.keys())[:-_WATER_VIEW_CACHE_MAX]:
            _WATER_VIEW_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


def build_water_layer_source_payloads(water_view_surface: Mapping[str, object] | None) -> dict:
    surface = _as_map(water_view_surface)
    artifact = _as_map(surface.get("water_view_artifact"))
    if not artifact and str(surface.get("view_id", "")).strip():
        artifact = dict(surface)
    artifact_hash = water_view_artifact_hash(artifact)
    return {
        "layer.water_ocean": {
            "source_kind": "water_view",
            "water_kind": "ocean",
            "rows": [dict(row) for row in _as_list(artifact.get("ocean_mask_ref")) if isinstance(row, Mapping)],
            "water_view_artifact_hash": artifact_hash,
        },
        "layer.water_river": {
            "source_kind": "water_view",
            "water_kind": "river",
            "rows": [dict(row) for row in _as_list(artifact.get("river_mask_ref")) if isinstance(row, Mapping)],
            "water_view_artifact_hash": artifact_hash,
        },
        "layer.water_lake": {
            "source_kind": "water_view",
            "water_kind": "lake",
            "rows": [dict(row) for row in _as_list(artifact.get("lake_mask_ref")) if isinstance(row, Mapping)],
            "water_view_artifact_hash": artifact_hash,
        },
        "layer.tide_offset": {
            "source_kind": "water_view",
            "water_kind": "tide_offset",
            "required_entitlements": ["entitlement.debug_view"],
            "rows": [dict(row) for row in _as_list(artifact.get("tide_offset_ref")) if isinstance(row, Mapping)],
            "water_view_artifact_hash": artifact_hash,
        },
    }


def build_water_view_surface(
    *,
    current_tick: int,
    observer_ref: Mapping[str, object] | None = None,
    observer_surface_artifact: Mapping[str, object] | None = None,
    region_cell_keys: object = None,
    surface_tile_artifact_rows: object = None,
    tide_overlay_rows: object = None,
    water_visual_policy_id: str = DEFAULT_WATER_VISUAL_POLICY_ID,
    ui_mode: str = "gui",
) -> dict:
    policy_row = dict(
        water_visual_policy_rows().get(str(water_visual_policy_id).strip() or DEFAULT_WATER_VISUAL_POLICY_ID)
        or water_visual_policy_rows().get(DEFAULT_WATER_VISUAL_POLICY_ID)
        or {}
    )
    if not policy_row:
        payload = {
            "result": "refused",
            "message": "water visual policy registry missing default row",
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload
    observer_cell_key = _observer_cell_key(
        observer_surface_artifact=observer_surface_artifact,
        observer_ref=observer_ref,
    )
    resolved_region_cell_keys = _sorted_geo_cell_keys(region_cell_keys)
    if not resolved_region_cell_keys:
        resolved_region_cell_keys = _default_region_cell_keys(
            observer_cell_key=observer_cell_key,
            water_visual_policy_row=policy_row,
        )
    artifact_rows_by_hash = _artifact_rows_by_cell_hash(surface_tile_artifact_rows)
    artifact_rows_by_alias = _artifact_rows_by_legacy_alias(surface_tile_artifact_rows)
    if not artifact_rows_by_hash and _as_map(observer_surface_artifact):
        artifact_rows_by_hash = _artifact_rows_by_cell_hash([observer_surface_artifact])
        artifact_rows_by_alias = _artifact_rows_by_legacy_alias([observer_surface_artifact])
    if not resolved_region_cell_keys:
        resolved_region_cell_keys = _sorted_geo_cell_keys(
            [_as_map(row).get("tile_cell_key") for row in artifact_rows_by_hash.values()]
        )
    by_tile_id, by_cell_hash = _tide_overlay_lookup(tide_overlay_rows)
    observer_material_proxy = _material_proxy_preview(observer_surface_artifact, current_tick=int(current_tick))
    cache_key = canonical_sha256(
        {
            "current_tick": int(max(0, _as_int(current_tick, 0))),
            "observer_cell_key_hash": _geo_hash(observer_cell_key),
            "region_hash": canonical_sha256([_semantic_cell_key(row) for row in resolved_region_cell_keys]),
            "artifact_hash": canonical_sha256(list(artifact_rows_by_hash.values())),
            "tide_hash": canonical_sha256(
                [
                    {
                        "tile_object_id": str(_as_map(row).get("tile_object_id", "")).strip(),
                        "tile_cell_key": _semantic_cell_key(_coerce_cell_key(_as_map(row).get("tile_cell_key")) or {}),
                        "tide_height_value": int(_as_int(_as_map(row).get("tide_height_value", 0), 0)),
                    }
                    for row in sorted(
                        list(by_tile_id.values()) + [row for key, row in by_cell_hash.items() if key not in set(by_tile_id.keys())],
                        key=lambda item: (str(_as_map(item).get("tile_object_id", "")), _geo_sort_tuple(_as_map(item).get("tile_cell_key"))),
                    )
                ]
            ),
            "water_visual_policy_id": str(policy_row.get("policy_id", "")).strip(),
        }
    )
    cached = _cache_lookup(cache_key)
    if cached is not None:
        out = dict(cached)
        out["cache_hit"] = True
        return out

    river_width_scale = max(1, _as_int(policy_row.get("river_width_scale", 220), 220))
    lake_fill_threshold = max(0, _as_int(policy_row.get("lake_fill_threshold", 180), 180))
    tide_visual_strength = max(0, _as_int(policy_row.get("tide_visual_strength", 80), 80))
    flow_fan_in_threshold = max(2, _as_int(_as_map(policy_row.get("extensions")).get("river_flow_fan_in_threshold", 3), 3))
    river_fan_in_counts = _river_fan_in_count_by_hash(artifact_rows_by_hash, artifact_rows_by_alias)

    ocean_rows: List[dict] = []
    river_rows: List[dict] = []
    lake_rows: List[dict] = []
    tide_rows: List[dict] = []
    seen_tide_hashes: set[str] = set()
    reflection_albedo_samples: List[int] = []
    for cell_key in resolved_region_cell_keys:
        cell_hash = _geo_hash(cell_key)
        artifact_row = dict(artifact_rows_by_hash.get(cell_hash) or {})
        if not artifact_row:
            continue
        tile_object_id = str(artifact_row.get("tile_object_id", "")).strip()
        tide_row = dict(by_tile_id.get(tile_object_id) or by_cell_hash.get(cell_hash) or {})
        tide_height_value = int(_as_int(tide_row.get("tide_height_value", 0), 0))
        tide_offset_value = int((tide_height_value * tide_visual_strength) // 1000)
        material_proxy_preview = _material_proxy_preview(artifact_row, current_tick=int(current_tick))
        shared = {
            "tile_object_id": tile_object_id,
            "planet_object_id": str(artifact_row.get("planet_object_id", "")).strip(),
            "geo_cell_key": dict(cell_key),
            "tile_cell_key": dict(cell_key),
            "material_baseline_id": str(artifact_row.get("material_baseline_id", "")).strip(),
            "biome_stub_id": str(artifact_row.get("biome_stub_id", "")).strip(),
            "tide_offset_value": int(tide_offset_value),
        }
        if _is_ocean_tile(artifact_row):
            reflection_albedo_samples.append(int(_as_int(material_proxy_preview.get("albedo_proxy_value", 0), 0)))
            ocean_rows.append(
                {
                    **shared,
                    "water_kind": "ocean",
                    "reflection_strength": int(_as_int(policy_row.get("reflection_strength", 520), 520)),
                }
            )
        target_alias = _legacy_cell_alias_from_tile_key(_as_map(artifact_row.get("flow_target_tile_key")))
        target_row = _as_map(artifact_rows_by_alias.get(target_alias))
        target_hash = _geo_hash(_as_map(target_row.get("tile_cell_key")))
        river_visual = bool(
            _river_flag(artifact_row)
            or (
                not _is_ocean_tile(artifact_row)
                and not _lake_flag(artifact_row)
                and _as_map(artifact_row.get("flow_target_tile_key"))
                and (
                    int(river_fan_in_counts.get(cell_hash, 0)) >= flow_fan_in_threshold
                    or int(river_fan_in_counts.get(target_hash, 0)) >= flow_fan_in_threshold
                )
            )
        )
        if river_visual:
            drainage = int(max(1, _as_int(artifact_row.get("drainage_accumulation_proxy", 1), 1)))
            river_rows.append(
                {
                    **shared,
                    "water_kind": "river",
                    "flow_target_tile_key": _as_map(artifact_row.get("flow_target_tile_key")),
                    "drainage_accumulation_proxy": drainage,
                    "flow_fan_in_count": int(river_fan_in_counts.get(cell_hash, 0)),
                    "river_source_kind": "hydrology_flag" if _river_flag(artifact_row) else "flow_convergence",
                    "river_width_permille": int(min(1000, river_width_scale + min(600, drainage * 24))),
                }
            )
        if _lake_flag(artifact_row):
            drainage = int(max(1, _as_int(artifact_row.get("drainage_accumulation_proxy", 1), 1)))
            reflection_albedo_samples.append(int(_as_int(material_proxy_preview.get("albedo_proxy_value", 0), 0)))
            lake_rows.append(
                {
                    **shared,
                    "water_kind": "lake",
                    "lake_fill_permille": int(min(1000, lake_fill_threshold + min(500, drainage * 12))),
                }
            )
        if (_is_ocean_tile(artifact_row) or _lake_flag(artifact_row)) and cell_hash not in seen_tide_hashes:
            tide_rows.append(
                {
                    "geo_cell_key": dict(cell_key),
                    "tile_object_id": tile_object_id,
                    "tide_height_value": int(tide_height_value),
                    "tide_offset_value": int(tide_offset_value),
                }
            )
            seen_tide_hashes.add(cell_hash)

    ocean_rows.sort(key=lambda row: _geo_sort_tuple(row.get("geo_cell_key") or {}))
    river_rows.sort(key=lambda row: _geo_sort_tuple(row.get("geo_cell_key") or {}))
    lake_rows.sort(key=lambda row: _geo_sort_tuple(row.get("geo_cell_key") or {}))
    tide_rows.sort(key=lambda row: _geo_sort_tuple(row.get("geo_cell_key") or {}))

    artifact = {
        "view_id": "water_view.{}".format(cache_key[:16]),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "region_cell_keys": [dict(row) for row in resolved_region_cell_keys],
        "ocean_mask_ref": ocean_rows,
        "river_mask_ref": river_rows,
        "lake_mask_ref": lake_rows,
        "tide_offset_ref": tide_rows,
        "deterministic_fingerprint": "",
        "extensions": {
            "source": EARTH_WATER_VIEW_ENGINE_VERSION,
            "source_kind": "derived.water_view_artifact",
            "derived_only": True,
            "artifact_class": "DERIVED_VIEW",
            "compactable": True,
            "cache_key": cache_key,
            "cache_policy_id": "cache.water.region_tick",
            "water_visual_policy_id": str(policy_row.get("policy_id", "")).strip() or DEFAULT_WATER_VISUAL_POLICY_ID,
            "observer_cell_key": dict(observer_cell_key),
            "observer_surface_artifact_hash": water_view_artifact_hash(observer_surface_artifact),
            "registry_hashes": {
                "water_visual_policy_registry_hash": water_visual_policy_registry_hash(),
            },
            "summary": {
                "ocean_tile_count": int(len(ocean_rows)),
                "river_tile_count": int(len(river_rows)),
                "lake_tile_count": int(len(lake_rows)),
                "tide_tile_count": int(len(tide_rows)),
            },
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    summary = {
        "ocean_tile_count": int(len(ocean_rows)),
        "river_tile_count": int(len(river_rows)),
        "lake_tile_count": int(len(lake_rows)),
        "tide_tile_count": int(len(tide_rows)),
    }
    reflection_tint_preview = {
        "observer_material_proxy_id": str(observer_material_proxy.get("material_proxy_id", "")).strip() or None,
        "observer_albedo_proxy_value": int(_as_int(observer_material_proxy.get("albedo_proxy_value", 0), 0)),
        "region_mean_albedo_proxy_value": (
            0
            if not reflection_albedo_samples
            else int(sum(reflection_albedo_samples) // max(1, len(reflection_albedo_samples)))
        ),
        "sample_count": int(len(reflection_albedo_samples)),
        "source_kind": "derived.water_reflection_tint_preview",
    }
    payload = {
        "result": "complete",
        "source_kind": "derived.water_view_artifact",
        "cache_hit": False,
        "cache_key": cache_key,
        "lens_layer_ids": [
            "layer.water_ocean",
            "layer.water_river",
            "layer.water_lake",
            "layer.tide_offset",
        ],
        "water_view_artifact": artifact,
        "layer_source_payloads": build_water_layer_source_payloads({"water_view_artifact": artifact}),
        "presentation": {
            "preferred_presentation": "summary" if str(ui_mode or "").strip().lower() in {"cli", "tui"} else "buffer",
            "summary": summary,
            "reflection_tint_preview": reflection_tint_preview,
            "summary_text": "water ocean={} river={} lake={} tide={}".format(
                summary["ocean_tile_count"],
                summary["river_tile_count"],
                summary["lake_tile_count"],
                summary["tide_tile_count"],
            ),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


__all__ = [
    "DEFAULT_WATER_VISUAL_POLICY_ID",
    "EARTH_WATER_VIEW_ENGINE_VERSION",
    "WATER_VISUAL_POLICY_REGISTRY_REL",
    "build_water_layer_source_payloads",
    "build_water_view_surface",
    "water_view_artifact_hash",
    "water_visual_policy_registry_hash",
    "water_visual_policy_rows",
]
