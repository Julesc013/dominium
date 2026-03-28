"""Deterministic EARTH-10 material/surface/albedo proxy helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key

from ..climate_field_engine import is_earth_surface_tile


MATERIAL_PROXY_REGISTRY_REL = os.path.join("data", "registries", "material_proxy_registry.json")
SURFACE_FLAG_REGISTRY_REL = os.path.join("data", "registries", "surface_flag_registry.json")
EARTH_MATERIAL_PROXY_ENGINE_VERSION = "EARTH10-3"
EARTH_MATERIAL_PROXY_DEFAULT_MAX_TILES_PER_UPDATE = 64


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    markers = (
        os.path.join("docs", "canon", "constitution_v1.md"),
        os.path.join("data", "registries"),
        os.path.join("tools", "xstack"),
    )
    while True:
        if all(os.path.exists(os.path.join(current, marker)) for marker in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.normpath(os.path.join(here, "..", "..", "..", ".."))
        current = parent


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


def material_proxy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(MATERIAL_PROXY_REGISTRY_REL),
        row_key="material_proxies",
        id_key="material_proxy_id",
    )


def surface_flag_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(SURFACE_FLAG_REGISTRY_REL),
        row_key="surface_flags",
        id_key="surface_flag_id",
    )


def material_proxy_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(MATERIAL_PROXY_REGISTRY_REL))


def surface_flag_registry_hash(payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(payload) or _registry_payload(SURFACE_FLAG_REGISTRY_REL))


def _geo_hash(tile_cell_key: Mapping[str, object]) -> str:
    key_row = _coerce_cell_key(tile_cell_key) or {}
    return canonical_sha256(_semantic_cell_key(key_row)) if key_row else ""


def _geo_sort_tuple(tile_cell_key: Mapping[str, object]) -> tuple:
    key_row = _coerce_cell_key(tile_cell_key) or {}
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
    chart_token = "north"
    if "south" in base_chart_id or "south" in str(key_row.get("chart_id", "")).strip().lower():
        chart_token = "south"
    index_tuple = list(key_row.get("index_tuple") or [])
    u_idx = int(index_tuple[0]) if len(index_tuple) > 0 else 0
    v_idx = int(index_tuple[1]) if len(index_tuple) > 1 else 0
    return "atlas.{}.{}.{}".format(chart_token, u_idx, v_idx)


def _effective_height_proxy(artifact_row: Mapping[str, object], geometry_row: Mapping[str, object] | None = None) -> int:
    geometry = _as_map(geometry_row)
    if geometry:
        value = _as_int(geometry.get("height_proxy", 0), 0)
        if value > 0:
            return int(value)
    extensions = _as_map(_as_map(artifact_row).get("extensions"))
    elevation = _as_map(_as_map(artifact_row).get("elevation_params_ref"))
    return int(
        max(
            0,
            _as_int(
                extensions.get(
                    "hydrology_effective_height_proxy",
                    elevation.get("height_proxy", 0),
                ),
                0,
            ),
        )
    )


def _surface_class_id(artifact_row: Mapping[str, object]) -> str:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    surface_class_id = str(extensions.get("surface_class_id", "")).strip()
    if surface_class_id:
        return surface_class_id
    material_id = str(row.get("material_baseline_id", "")).strip().lower()
    if material_id == "material.water":
        return "surface.class.ocean"
    if "ice" in material_id:
        return "surface.class.ice"
    return "surface.class.land"


def _material_proxy_by_id() -> Dict[str, dict]:
    return material_proxy_rows()


def _surface_flag_by_id() -> Dict[str, dict]:
    return surface_flag_rows()


def material_proxy_value_from_id(material_proxy_id: str) -> int:
    row = _as_map(_material_proxy_by_id().get(str(material_proxy_id).strip()))
    return int(max(0, _as_int(row.get("field_scalar_code", 0), 0)))


def material_proxy_id_from_value(material_proxy_value: int) -> str:
    value = int(max(0, _as_int(material_proxy_value, 0)))
    for material_proxy_id, row in sorted(_material_proxy_by_id().items()):
        if int(max(0, _as_int(_as_map(row).get("field_scalar_code", 0), 0))) == value:
            return str(material_proxy_id)
    return ""


def material_proxy_albedo_permille(material_proxy_id: str) -> int:
    row = _as_map(_material_proxy_by_id().get(str(material_proxy_id).strip()))
    return int(_clamp(_as_int(_as_map(row.get("extensions")).get("albedo_proxy_permille", 0), 0), 0, 1000))


def material_proxy_friction_permille(material_proxy_id: str) -> int:
    row = _as_map(_material_proxy_by_id().get(str(material_proxy_id).strip()))
    return int(_clamp(_as_int(_as_map(row.get("extensions")).get("friction_proxy_permille", 1000), 1000), 100, 1200))


def surface_flag_mask_from_ids(flag_ids: Sequence[str]) -> int:
    rows = _surface_flag_by_id()
    mask = 0
    for flag_id in sorted(set(str(item).strip() for item in list(flag_ids or []) if str(item).strip())):
        mask |= int(max(0, _as_int(_as_map(rows.get(flag_id)).get("bit_mask", 0), 0)))
    return int(mask)


def surface_flag_ids_from_mask(mask: int) -> List[str]:
    value = int(max(0, _as_int(mask, 0)))
    selected: List[str] = []
    for flag_id, row in sorted(
        _surface_flag_by_id().items(),
        key=lambda item: (int(_as_int(_as_map(item[1]).get("bit_mask", 0), 0)), str(item[0])),
    ):
        bit_mask = int(max(0, _as_int(_as_map(row).get("bit_mask", 0), 0)))
        if bit_mask > 0 and (value & bit_mask) == bit_mask:
            selected.append(str(flag_id))
    return [str(item) for item in selected]


def surface_flag_map_from_mask(mask: int) -> dict:
    selected = set(surface_flag_ids_from_mask(mask))
    return dict((flag_id, flag_id in selected) for flag_id in sorted(_surface_flag_by_id().keys()))


def evaluate_earth_tile_material_proxy(
    *,
    artifact_row: Mapping[str, object],
    current_tick: int,
    geometry_row: Mapping[str, object] | None = None,
) -> dict:
    row = _as_map(artifact_row)
    extensions = _as_map(row.get("extensions"))
    elevation = _as_map(row.get("elevation_params_ref"))
    tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
    surface_class_id = _surface_class_id(row)
    material_baseline_id = str(row.get("material_baseline_id", "")).strip()
    material_token = material_baseline_id.lower()
    climate_band_id = str(extensions.get("climate_band_id", "")).strip() or "climate.band.temperate"
    river_flag = bool(row.get("river_flag", False))
    lake_flag = bool(extensions.get("lake_flag", False))
    height_proxy = _effective_height_proxy(row, geometry_row=geometry_row)
    macro_relief_permille = int(_clamp(_as_int(elevation.get("macro_relief_permille", 0), 0), 0, 1000))
    ridge_bias_permille = int(_clamp(_as_int(elevation.get("ridge_bias_permille", 0), 0), 0, 1000))
    coastal_proximity_permille = int(_clamp(_as_int(extensions.get("coastal_proximity_permille", 0), 0), 0, 1000))
    continent_score_permille = int(_clamp(_as_int(extensions.get("continent_score_permille", 0), 0), 0, 1000))

    material_proxy_id = "mat.soil"
    derivation_reason = "land_default"
    if surface_class_id == "surface.class.ice" or "ice" in material_token:
        material_proxy_id = "mat.ice"
        derivation_reason = "ice_surface"
    elif surface_class_id == "surface.class.ocean" or material_token == "material.water" or river_flag or lake_flag:
        material_proxy_id = "mat.water"
        derivation_reason = "water_surface"
    elif (
        climate_band_id == "climate.band.arid"
        and height_proxy <= 2200
        and coastal_proximity_permille <= 650
        and continent_score_permille >= 450
    ):
        material_proxy_id = "mat.sand"
        derivation_reason = "arid_surface"
    elif height_proxy >= 2800 or macro_relief_permille >= 650 or ridge_bias_permille >= 700:
        material_proxy_id = "mat.rock"
        derivation_reason = "high_relief_land"

    surface_flag_ids: List[str] = []
    if material_proxy_id == "mat.water":
        surface_flag_ids = ["flag.fluid"]
    elif material_proxy_id == "mat.ice":
        surface_flag_ids = ["flag.slippery"]
    else:
        surface_flag_ids = ["flag.buildable"]
    surface_flags_mask = surface_flag_mask_from_ids(surface_flag_ids)
    material_proxy_value = material_proxy_value_from_id(material_proxy_id)
    albedo_proxy_value = material_proxy_albedo_permille(material_proxy_id)
    friction_proxy_permille = material_proxy_friction_permille(material_proxy_id)
    payload = {
        "tile_object_id": str(row.get("tile_object_id", "")).strip(),
        "planet_object_id": str(row.get("planet_object_id", "")).strip(),
        "tile_cell_key": dict(tile_cell_key),
        "cell_id": _legacy_cell_alias_from_tile_key(tile_cell_key),
        "current_tick": int(max(0, _as_int(current_tick, 0))),
        "material_proxy_id": material_proxy_id,
        "material_proxy_value": int(material_proxy_value),
        "surface_flags_mask": int(surface_flags_mask),
        "surface_flag_ids": [str(item) for item in surface_flag_ids_from_mask(surface_flags_mask)],
        "albedo_proxy_value": int(albedo_proxy_value),
        "friction_proxy_permille": int(friction_proxy_permille),
        "surface_class_id": surface_class_id,
        "material_baseline_id": material_baseline_id,
        "climate_band_id": climate_band_id,
        "height_proxy": int(height_proxy),
        "derivation_reason": derivation_reason,
        "deterministic_fingerprint": "",
        "extensions": {
            "macro_relief_permille": int(macro_relief_permille),
            "ridge_bias_permille": int(ridge_bias_permille),
            "coastal_proximity_permille": int(coastal_proximity_permille),
            "continent_score_permille": int(continent_score_permille),
            "river_flag": bool(river_flag),
            "lake_flag": bool(lake_flag),
            "surface_flag_map": surface_flag_map_from_mask(surface_flags_mask),
            "registry_hashes": {
                "material_proxy_registry_hash": material_proxy_registry_hash(),
                "surface_flag_registry_hash": surface_flag_registry_hash(),
            },
            "source": EARTH_MATERIAL_PROXY_ENGINE_VERSION,
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_material_proxy_field_updates(
    *,
    material_evaluations: Sequence[Mapping[str, object]],
) -> List[dict]:
    evaluations = [dict(row) for row in list(material_evaluations or []) if isinstance(row, Mapping)]
    if not evaluations:
        return []
    planet_id = str(evaluations[0].get("planet_object_id", "")).strip()
    field_updates: List[dict] = []
    for row in evaluations:
        cell_id = str(row.get("cell_id", "")).strip()
        geo_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not cell_id:
            continue
        field_updates.extend(
            [
                {
                    "field_id": "field.material_proxy.surface.{}".format(planet_id),
                    "field_type_id": "field.material_proxy",
                    "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("material_proxy_value", 0), 0)),
                    "extensions": {
                        "material_proxy_id": str(row.get("material_proxy_id", "")).strip(),
                        "source": EARTH_MATERIAL_PROXY_ENGINE_VERSION,
                    },
                },
                {
                    "field_id": "field.surface_flags.surface.{}".format(planet_id),
                    "field_type_id": "field.surface_flags",
                    "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("surface_flags_mask", 0), 0)),
                    "extensions": {
                        "surface_flag_ids": [str(item) for item in list(row.get("surface_flag_ids") or []) if str(item).strip()],
                        "source": EARTH_MATERIAL_PROXY_ENGINE_VERSION,
                    },
                },
                {
                    "field_id": "field.albedo_proxy.surface.{}".format(planet_id),
                    "field_type_id": "field.albedo_proxy",
                    "spatial_scope_id": "spatial.surface.{}".format(planet_id),
                    "resolution_level": "macro",
                    "cell_id": cell_id,
                    "geo_cell_key": dict(geo_cell_key),
                    "value": int(_as_int(row.get("albedo_proxy_value", 0), 0)),
                    "extensions": {
                        "material_proxy_id": str(row.get("material_proxy_id", "")).strip(),
                        "source": EARTH_MATERIAL_PROXY_ENGINE_VERSION,
                    },
                },
            ]
        )
    return sorted(
        field_updates,
        key=lambda row: (
            str(row.get("field_id", "")),
            _geo_sort_tuple(row.get("geo_cell_key") or {}),
            str(row.get("cell_id", "")),
        ),
    )


def build_earth_material_proxy_update_plan(
    *,
    artifact_rows: object,
    current_tick: int,
    geometry_rows_by_key: Mapping[str, object] | None = None,
    max_tiles_per_update: int,
) -> dict:
    candidates: List[dict] = []
    geometry_index = dict((str(key), dict(value)) for key, value in dict(geometry_rows_by_key or {}).items())
    for raw in list(artifact_rows or []):
        row = _as_map(raw)
        if not row or not is_earth_surface_tile(row):
            continue
        tile_cell_key = _coerce_cell_key(row.get("tile_cell_key")) or {}
        if not tile_cell_key:
            continue
        candidates.append(
            {
                "artifact_row": dict(row),
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "tile_cell_key": dict(tile_cell_key),
                "geo_hash": _geo_hash(tile_cell_key),
            }
        )
    candidates = sorted(
        candidates,
        key=lambda row: (
            _geo_sort_tuple(row.get("tile_cell_key") or {}),
            str(row.get("tile_object_id", "")),
        ),
    )
    budget = max(0, _as_int(max_tiles_per_update, 0))
    selected = list(candidates[:budget]) if budget > 0 else []
    skipped = list(candidates[budget:]) if budget > 0 else list(candidates)
    evaluations = [
        evaluate_earth_tile_material_proxy(
            artifact_row=dict(row.get("artifact_row") or {}),
            current_tick=int(current_tick),
            geometry_row=dict(geometry_index.get(str(row.get("geo_hash", ""))) or {}),
        )
        for row in selected
    ]
    field_updates = build_material_proxy_field_updates(material_evaluations=evaluations)
    payload = {
        "selected_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in selected if str(row.get("tile_object_id", "")).strip()],
        "skipped_tile_ids": [str(row.get("tile_object_id", "")).strip() for row in skipped if str(row.get("tile_object_id", "")).strip()],
        "evaluations": [dict(row) for row in evaluations],
        "field_updates": [dict(row) for row in field_updates],
        "cost_units_used": int(len(selected)),
        "degraded": bool(skipped),
        "degrade_reason": "degrade.earth.material_proxy.max_tiles_per_update" if skipped else None,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def material_proxy_window_hash(rows: object) -> str:
    normalized = []
    for raw in list(rows or []):
        row = _as_map(raw)
        normalized.append(
            {
                "tile_object_id": str(row.get("tile_object_id", "")).strip(),
                "material_proxy_id": str(row.get("material_proxy_id", "")).strip(),
                "material_proxy_value": int(_as_int(row.get("material_proxy_value", 0), 0)),
                "surface_flags_mask": int(_as_int(row.get("surface_flags_mask", 0), 0)),
                "albedo_proxy_value": int(_as_int(row.get("albedo_proxy_value", 0), 0)),
                "friction_proxy_permille": int(_as_int(row.get("friction_proxy_permille", 0), 0)),
                "derivation_reason": str(row.get("derivation_reason", "")).strip(),
            }
        )
    normalized.sort(key=lambda item: item["tile_object_id"])
    return canonical_sha256(normalized)


__all__ = [
    "EARTH_MATERIAL_PROXY_DEFAULT_MAX_TILES_PER_UPDATE",
    "EARTH_MATERIAL_PROXY_ENGINE_VERSION",
    "MATERIAL_PROXY_REGISTRY_REL",
    "SURFACE_FLAG_REGISTRY_REL",
    "build_earth_material_proxy_update_plan",
    "build_material_proxy_field_updates",
    "evaluate_earth_tile_material_proxy",
    "material_proxy_albedo_permille",
    "material_proxy_friction_permille",
    "material_proxy_id_from_value",
    "material_proxy_registry_hash",
    "material_proxy_rows",
    "material_proxy_value_from_id",
    "material_proxy_window_hash",
    "surface_flag_ids_from_mask",
    "surface_flag_map_from_mask",
    "surface_flag_mask_from_ids",
    "surface_flag_registry_hash",
    "surface_flag_rows",
]
