"""Deterministic GEO-7 geometry state and edit helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256

from geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key


REFUSAL_GEO_GEOMETRY_INVALID = "refusal.geo.geometry_invalid"

_GEOMETRY_EDIT_POLICY_REGISTRY_REL = os.path.join("data", "registries", "geometry_edit_policy_registry.json")
_MATERIAL_CLASS_REGISTRY_REL = os.path.join("data", "registries", "material_class_registry.json")

_OCCUPANCY_SCALE = 1000
_DEFAULT_MATERIAL_ID = "material.air"
_DEFAULT_SOLID_MATERIAL_ID = "material.stone_basic"
_DEFAULT_POLICY_ID = "geo.edit.default"


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
            return os.path.normpath(os.path.join(here, "..", "..", ".."))
        current = parent


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(json.load(handle) or {})
    except (OSError, ValueError, TypeError):
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


def _sorted_unique_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _geo_cell_key_sort_tuple(value: object) -> Tuple[str, Tuple[int, ...], int, str, str]:
    row = _coerce_cell_key(_as_map(value))
    if not row:
        return ("", tuple(), 0, "", "")
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(item) for item in list(row.get("index_tuple") or [])),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
        str(row.get("partition_profile_id", "")).strip(),
        str(row.get("topology_profile_id", "")).strip(),
    )


def _geo_cell_key_hash(value: object) -> str:
    row = _coerce_cell_key(_as_map(value))
    return canonical_sha256(_semantic_cell_key(row)) if row else ""


def _sorted_geo_cell_keys(values: object) -> List[dict]:
    rows = [_coerce_cell_key(item) for item in _as_list(values)]
    return [dict(row) for row in sorted((row for row in rows if row), key=_geo_cell_key_sort_tuple)]


def _rows_from_registry(payload: Mapping[str, object] | None, row_key: str) -> List[dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    record = _as_map(body.get("record"))
    rows = record.get(row_key)
    if isinstance(rows, list):
        return [dict(item) for item in rows if isinstance(item, Mapping)]
    return []


def _material_rows_by_id(registry_payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    payload = _as_map(registry_payload) or _registry_payload(_MATERIAL_CLASS_REGISTRY_REL)
    rows = _rows_from_registry(payload, "materials")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("material_id", ""))):
        material_id = str(row.get("material_id", "")).strip()
        if material_id:
            out[material_id] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def geometry_edit_policy_rows_by_id(registry_payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    payload = _as_map(registry_payload) or _registry_payload(_GEOMETRY_EDIT_POLICY_REGISTRY_REL)
    rows = _rows_from_registry(payload, "geometry_edit_policies")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("geometry_edit_policy_id", ""))):
        policy_id = str(row.get("geometry_edit_policy_id", "")).strip()
        if not policy_id:
            continue
        payload_row = {
            "schema_version": "1.0.0",
            "geometry_edit_policy_id": policy_id,
            "description": str(row.get("description", "")).strip(),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": {
                str(key): value
                for key, value in sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))
            },
        }
        if not payload_row["deterministic_fingerprint"]:
            payload_row["deterministic_fingerprint"] = canonical_sha256(dict(payload_row, deterministic_fingerprint=""))
        out[policy_id] = payload_row
    if _DEFAULT_POLICY_ID not in out:
        out[_DEFAULT_POLICY_ID] = {
            "schema_version": "1.0.0",
            "geometry_edit_policy_id": _DEFAULT_POLICY_ID,
            "description": "default fallback geometry edit policy",
            "deterministic_fingerprint": "",
            "extensions": {
                "max_target_cells": 64,
                "max_volume_per_cell": _OCCUPANCY_SCALE,
                "allow_micro_chunks": True,
                "micro_chunk_budget": 64,
            },
        }
        out[_DEFAULT_POLICY_ID]["deterministic_fingerprint"] = canonical_sha256(
            dict(out[_DEFAULT_POLICY_ID], deterministic_fingerprint="")
        )
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def geometry_edit_policy_registry_hash(registry_payload: Mapping[str, object] | None = None) -> str:
    payload = _as_map(registry_payload) or _registry_payload(_GEOMETRY_EDIT_POLICY_REGISTRY_REL)
    return canonical_sha256(payload)


def _clamp_fraction(value: object) -> int:
    return int(max(0, min(_OCCUPANCY_SCALE, _as_int(value, 0))))


def _material_permeability_base(material_row: Mapping[str, object]) -> int:
    tags = set(_sorted_unique_strings(list(_as_map(material_row).get("tags") or []) + list(_as_map(material_row).get("phase_tags") or [])))
    if "gas" in tags or "atmosphere" in tags:
        return 1000
    if "liquid" in tags:
        return 900
    if "metal" in tags or "alloy" in tags:
        return 20
    if "aggregate" in tags or "stone" in tags:
        return 35
    if "wood" in tags or "composite" in tags or "organic" in tags:
        return 140
    return 60 if material_row else 900


def _material_conductance_base(material_row: Mapping[str, object]) -> int:
    tags = set(_sorted_unique_strings(list(_as_map(material_row).get("tags") or []) + list(_as_map(material_row).get("phase_tags") or [])))
    if "gas" in tags or "atmosphere" in tags:
        return 40
    if "liquid" in tags:
        return 450
    if "metal" in tags or "alloy" in tags:
        return 920
    if "aggregate" in tags or "stone" in tags:
        return 560
    if "wood" in tags or "composite" in tags or "organic" in tags:
        return 220
    return 180 if material_row else 40


def _derive_proxies(
    *,
    material_id: str,
    occupancy_fraction: int,
    material_registry: Mapping[str, object] | None = None,
) -> Tuple[int, int]:
    occupancy_value = _clamp_fraction(occupancy_fraction)
    rows = _material_rows_by_id(material_registry)
    material_row = dict(rows.get(str(material_id).strip()) or {})
    if occupancy_value <= 0:
        return (1000, 40)
    permeability_base = _material_permeability_base(material_row)
    conductance_base = _material_conductance_base(material_row)
    void_fraction = int(_OCCUPANCY_SCALE - occupancy_value)
    permeability = int(min(_OCCUPANCY_SCALE, max(0, permeability_base + ((void_fraction * 3) // 4))))
    conductance = int(max(0, min(_OCCUPANCY_SCALE, (conductance_base * occupancy_value) // _OCCUPANCY_SCALE)))
    return permeability, conductance


def build_geometry_cell_state(
    *,
    geo_cell_key: Mapping[str, object],
    material_id: str,
    occupancy_fraction: int,
    height_proxy: int | None = None,
    permeability_proxy: int | None = None,
    conductance_proxy: int | None = None,
    extensions: Mapping[str, object] | None = None,
    material_registry: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        raise ValueError("geo_cell_key is required")
    occupancy_value = _clamp_fraction(occupancy_fraction)
    material_token = str(material_id or "").strip() or (_DEFAULT_MATERIAL_ID if occupancy_value <= 0 else _DEFAULT_SOLID_MATERIAL_ID)
    if occupancy_value <= 0:
        material_token = _DEFAULT_MATERIAL_ID
    derived_permeability, derived_conductance = _derive_proxies(
        material_id=material_token,
        occupancy_fraction=occupancy_value,
        material_registry=material_registry,
    )
    payload = {
        "schema_version": "1.0.0",
        "geo_cell_key": dict(cell_key),
        "material_id": material_token,
        "occupancy_fraction": occupancy_value,
        "permeability_proxy": int(max(0, min(_OCCUPANCY_SCALE, _as_int(permeability_proxy, derived_permeability)))),
        "conductance_proxy": int(max(0, min(_OCCUPANCY_SCALE, _as_int(conductance_proxy, derived_conductance)))),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    if height_proxy is not None:
        payload["height_proxy"] = int(_as_int(height_proxy, 0))
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_geometry_cell_state(
    row: Mapping[str, object] | None,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> dict:
    payload = _as_map(row)
    geo_cell_key = _coerce_cell_key(payload.get("geo_cell_key"))
    if not geo_cell_key:
        raise ValueError("geometry_cell_state.geo_cell_key is required")
    return build_geometry_cell_state(
        geo_cell_key=geo_cell_key,
        material_id=str(payload.get("material_id", "")).strip() or _DEFAULT_MATERIAL_ID,
        occupancy_fraction=_as_int(payload.get("occupancy_fraction", 0), 0),
        height_proxy=(None if payload.get("height_proxy") is None else _as_int(payload.get("height_proxy", 0), 0)),
        permeability_proxy=(None if payload.get("permeability_proxy") is None else _as_int(payload.get("permeability_proxy", 0), 0)),
        conductance_proxy=(None if payload.get("conductance_proxy") is None else _as_int(payload.get("conductance_proxy", 0), 0)),
        extensions=_as_map(payload.get("extensions")),
        material_registry=material_registry,
    )


def normalize_geometry_cell_state_rows(
    rows: object,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _geo_cell_key_sort_tuple(item.get("geo_cell_key"))):
        try:
            normalized = normalize_geometry_cell_state(row, material_registry=material_registry)
        except ValueError:
            continue
        out[_geo_cell_key_hash(normalized.get("geo_cell_key"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def geometry_cell_state_rows_by_key(
    rows: object,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> Dict[str, dict]:
    normalized = normalize_geometry_cell_state_rows(rows, material_registry=material_registry)
    return dict((_geo_cell_key_hash(row.get("geo_cell_key")), dict(row)) for row in normalized)


def build_geometry_chunk_state(
    *,
    parent_cell_key: Mapping[str, object],
    chunk_payload_ref: Mapping[str, object],
    chunk_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    parent = _coerce_cell_key(parent_cell_key)
    if not parent:
        raise ValueError("parent_cell_key is required")
    payload_ref = {
        str(key): value
        for key, value in sorted(_as_map(chunk_payload_ref).items(), key=lambda item: str(item[0]))
    }
    resolved_chunk_id = str(chunk_id or "").strip()
    if not resolved_chunk_id:
        resolved_chunk_id = "chunk.geo.{}".format(
            canonical_sha256({"parent_cell_key": _semantic_cell_key(parent), "chunk_payload_ref": payload_ref})[:16]
        )
    payload = {
        "schema_version": "1.0.0",
        "chunk_id": resolved_chunk_id,
        "parent_cell_key": dict(parent),
        "chunk_payload_ref": payload_ref,
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_geometry_chunk_state(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_geometry_chunk_state(
        parent_cell_key=_as_map(payload.get("parent_cell_key")),
        chunk_payload_ref=_as_map(payload.get("chunk_payload_ref")),
        chunk_id=str(payload.get("chunk_id", "")).strip(),
        extensions=_as_map(payload.get("extensions")),
    )


def normalize_geometry_chunk_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("chunk_id", ""))):
        try:
            normalized = normalize_geometry_chunk_state(row)
        except ValueError:
            continue
        out[str(normalized.get("chunk_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def geometry_chunk_state_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_geometry_chunk_state_rows(rows)
    return dict((str(row.get("chunk_id", "")).strip(), dict(row)) for row in normalized if str(row.get("chunk_id", "")).strip())


def _normalize_material_transfer(value: object) -> dict | None:
    payload = _as_map(value)
    if not payload:
        return None
    material_id = str(payload.get("material_id", "")).strip()
    batch_id = str(payload.get("batch_id", "")).strip() or None
    quantity_mass_raw = int(max(0, _as_int(payload.get("quantity_mass_raw", 0), 0)))
    if (not material_id) and (not batch_id) and quantity_mass_raw <= 0:
        return None
    out = {
        "material_id": material_id or None,
        "batch_id": batch_id,
        "quantity_mass_raw": quantity_mass_raw,
        "batch_ids": _sorted_unique_strings(payload.get("batch_ids")),
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(payload.get("extensions")).items(), key=lambda item: str(item[0]))
        },
    }
    return out


def build_geometry_edit_event(
    *,
    edit_id: str,
    tick: int,
    operator_subject_id: str,
    edit_kind: str,
    target_cell_keys: Sequence[Mapping[str, object]],
    volume_amount: int,
    material_in: Mapping[str, object] | None = None,
    material_out: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind = str(edit_kind or "").strip().lower()
    if kind not in {"remove", "add", "replace", "cut"}:
        raise ValueError("edit_kind is required")
    target_rows = _sorted_geo_cell_keys(target_cell_keys)
    if not target_rows:
        raise ValueError("target_cell_keys is required")
    payload = {
        "schema_version": "1.0.0",
        "edit_id": str(edit_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "operator_subject_id": str(operator_subject_id or "").strip() or "subject.unknown",
        "edit_kind": kind,
        "target_cell_keys": target_rows,
        "volume_amount": int(max(0, _as_int(volume_amount, 0))),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): value
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    normalized_in = _normalize_material_transfer(material_in)
    normalized_out = _normalize_material_transfer(material_out)
    if normalized_in:
        payload["material_in"] = normalized_in
    if normalized_out:
        payload["material_out"] = normalized_out
    if not payload["edit_id"]:
        payload["edit_id"] = "edit.geometry.{}".format(
            canonical_sha256(
                {
                    "tick": payload["tick"],
                    "operator_subject_id": payload["operator_subject_id"],
                    "edit_kind": payload["edit_kind"],
                    "target_cell_keys": [dict(item) for item in target_rows],
                    "volume_amount": payload["volume_amount"],
                    "material_in": payload.get("material_in"),
                    "material_out": payload.get("material_out"),
                    "extensions": dict(payload["extensions"]),
                }
            )[:16]
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_geometry_edit_event(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_geometry_edit_event(
        edit_id=str(payload.get("edit_id", "")).strip(),
        tick=_as_int(payload.get("tick", 0), 0),
        operator_subject_id=str(payload.get("operator_subject_id", "")).strip(),
        edit_kind=str(payload.get("edit_kind", "")).strip(),
        target_cell_keys=_as_list(payload.get("target_cell_keys")),
        volume_amount=_as_int(payload.get("volume_amount", 0), 0),
        material_in=_as_map(payload.get("material_in")),
        material_out=_as_map(payload.get("material_out")),
        extensions=_as_map(payload.get("extensions")),
    )


def normalize_geometry_edit_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("edit_kind", "")),
            str(item.get("edit_id", "")),
        ),
    ):
        try:
            normalized = normalize_geometry_edit_event(row)
        except ValueError:
            continue
        out[str(normalized.get("edit_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def geometry_edit_event_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_geometry_edit_event_rows(rows))


def geometry_state_hash_surface(
    *,
    geometry_cell_states: object,
    geometry_chunk_states: object,
    geometry_edit_events: object | None = None,
    material_registry: Mapping[str, object] | None = None,
) -> dict:
    cell_rows = normalize_geometry_cell_state_rows(geometry_cell_states, material_registry=material_registry)
    chunk_rows = normalize_geometry_chunk_state_rows(geometry_chunk_states)
    event_rows = normalize_geometry_edit_event_rows(geometry_edit_events or [])
    payload = {
        "geometry_cell_state_hash": canonical_sha256(cell_rows),
        "geometry_chunk_state_hash": canonical_sha256(chunk_rows),
        "geometry_edit_event_hash_chain": canonical_sha256(event_rows),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def geometry_get_cell_state(
    geo_cell_key: Mapping[str, object] | None,
    geometry_cell_states: object,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> dict:
    cell_key = _coerce_cell_key(geo_cell_key)
    if not cell_key:
        raise ValueError("geo_cell_key is required")
    rows_by_key = geometry_cell_state_rows_by_key(geometry_cell_states, material_registry=material_registry)
    existing = dict(rows_by_key.get(_geo_cell_key_hash(cell_key)) or {})
    if existing:
        return existing
    return build_geometry_cell_state(
        geo_cell_key=cell_key,
        material_id=_DEFAULT_MATERIAL_ID,
        occupancy_fraction=0,
        material_registry=material_registry,
    )


def geometry_get_occupancy(
    geo_cell_key: Mapping[str, object] | None,
    geometry_cell_states: object,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> int:
    row = geometry_get_cell_state(geo_cell_key, geometry_cell_states, material_registry=material_registry)
    return int(max(0, _as_int(row.get("occupancy_fraction", 0), 0)))


def geometry_get_permeability_proxy(
    geo_cell_key: Mapping[str, object] | None,
    geometry_cell_states: object,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> int:
    row = geometry_get_cell_state(geo_cell_key, geometry_cell_states, material_registry=material_registry)
    return int(max(0, _as_int(row.get("permeability_proxy", 0), 0)))


def geometry_get_conductance_proxy(
    geo_cell_key: Mapping[str, object] | None,
    geometry_cell_states: object,
    *,
    material_registry: Mapping[str, object] | None = None,
) -> int:
    row = geometry_get_cell_state(geo_cell_key, geometry_cell_states, material_registry=material_registry)
    return int(max(0, _as_int(row.get("conductance_proxy", 0), 0)))


def _policy_row(policy_id: str, registry_payload: Mapping[str, object] | None = None) -> dict:
    rows = geometry_edit_policy_rows_by_id(registry_payload)
    return dict(rows.get(str(policy_id or "").strip()) or rows.get(_DEFAULT_POLICY_ID) or {})


def _policy_limits(policy_row: Mapping[str, object]) -> Tuple[int, int, bool, int, str]:
    ext = _as_map(_as_map(policy_row).get("extensions"))
    max_cells = int(max(1, _as_int(ext.get("max_target_cells", 64), 64)))
    max_per_cell = int(max(1, _as_int(ext.get("max_volume_per_cell", _OCCUPANCY_SCALE), _OCCUPANCY_SCALE)))
    allow_micro_chunks = bool(ext.get("allow_micro_chunks", False))
    micro_chunk_budget = int(max(0, _as_int(ext.get("micro_chunk_budget", 0), 0)))
    partial_chunk_policy = str(ext.get("partial_chunk_policy", "aggregate_macro")).strip() or "aggregate_macro"
    return max_cells, max_per_cell, allow_micro_chunks, micro_chunk_budget, partial_chunk_policy


def _refusal(message: str, *, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_GEOMETRY_INVALID,
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _material_breakdown_rows(material_breakdown: Mapping[str, int]) -> List[dict]:
    return [
        {"material_id": material_id, "quantity_mass_raw": int(max(0, int(quantity_mass_raw)))}
        for material_id, quantity_mass_raw in sorted(material_breakdown.items(), key=lambda item: str(item[0]))
        if str(material_id).strip() and int(quantity_mass_raw) > 0
    ]


def _dominant_material(material_breakdown: Mapping[str, int], *, fallback: str) -> str:
    rows = _material_breakdown_rows(material_breakdown)
    if not rows:
        return str(fallback or _DEFAULT_MATERIAL_ID)
    top = sorted(rows, key=lambda item: (-int(item.get("quantity_mass_raw", 0)), str(item.get("material_id", ""))))[0]
    return str(top.get("material_id", "")).strip() or str(fallback or _DEFAULT_MATERIAL_ID)


def _update_height_proxy(existing_row: Mapping[str, object], updated_occupancy: int) -> int | None:
    if "height_proxy" not in _as_map(existing_row):
        return None
    baseline = int(_as_int(_as_map(existing_row).get("height_proxy", 0), 0))
    return int((baseline * updated_occupancy) // max(1, _OCCUPANCY_SCALE))


def geometry_remove_volume(
    *,
    geometry_cell_states: object,
    target_cell_keys: Sequence[Mapping[str, object]],
    volume_amount: int,
    tick: int,
    operator_subject_id: str,
    edit_id: str = "",
    geometry_edit_policy_id: str = _DEFAULT_POLICY_ID,
    geometry_edit_policy_registry: Mapping[str, object] | None = None,
    material_registry: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    policy_row = _policy_row(geometry_edit_policy_id, geometry_edit_policy_registry)
    max_cells, max_per_cell, _allow_micro_chunks, _micro_chunk_budget, _partial_chunk_policy = _policy_limits(policy_row)
    sorted_targets = _sorted_geo_cell_keys(target_cell_keys)
    if not sorted_targets:
        return _refusal("geometry_remove requires target_cell_keys", details={"geometry_edit_policy_id": geometry_edit_policy_id})
    if len(sorted_targets) > max_cells:
        return _refusal(
            "geometry_remove exceeded target cell budget",
            details={"geometry_edit_policy_id": geometry_edit_policy_id, "max_target_cells": max_cells, "requested_target_cells": len(sorted_targets)},
        )
    remaining = int(max(0, _as_int(volume_amount, 0)))
    if remaining <= 0:
        return _refusal("geometry_remove requires positive volume_amount", details={"volume_amount": volume_amount})
    rows_by_key = geometry_cell_state_rows_by_key(geometry_cell_states, material_registry=material_registry)
    updated_keys: List[str] = []
    removed_total = 0
    material_breakdown: Dict[str, int] = {}
    for cell_key in sorted_targets:
        if remaining <= 0:
            break
        existing = dict(rows_by_key.get(_geo_cell_key_hash(cell_key)) or build_geometry_cell_state(
            geo_cell_key=cell_key,
            material_id=_DEFAULT_MATERIAL_ID,
            occupancy_fraction=0,
            material_registry=material_registry,
        ))
        available = int(max(0, _as_int(existing.get("occupancy_fraction", 0), 0)))
        delta = int(min(remaining, max_per_cell, available))
        if delta <= 0:
            continue
        updated_occupancy = int(max(0, available - delta))
        material_token = str(existing.get("material_id", _DEFAULT_MATERIAL_ID)).strip() or _DEFAULT_MATERIAL_ID
        material_breakdown[material_token] = int(material_breakdown.get(material_token, 0) + delta)
        updated_material = material_token if updated_occupancy > 0 else _DEFAULT_MATERIAL_ID
        updated_row = build_geometry_cell_state(
            geo_cell_key=_as_map(existing.get("geo_cell_key")),
            material_id=updated_material,
            occupancy_fraction=updated_occupancy,
            height_proxy=_update_height_proxy(existing, updated_occupancy),
            extensions={
                **_as_map(existing.get("extensions")),
                "last_edit_kind": "remove",
                "last_edit_tick": int(max(0, _as_int(tick, 0))),
            },
            material_registry=material_registry,
        )
        rows_by_key[_geo_cell_key_hash(updated_row.get("geo_cell_key"))] = updated_row
        updated_keys.append(_geo_cell_key_hash(updated_row.get("geo_cell_key")))
        removed_total += delta
        remaining -= delta
    material_out_rows = _material_breakdown_rows(material_breakdown)
    material_out = None
    if material_out_rows:
        material_out = {
            "material_id": _dominant_material(material_breakdown, fallback=_DEFAULT_SOLID_MATERIAL_ID),
            "quantity_mass_raw": int(removed_total),
            "extensions": {"material_breakdown": material_out_rows},
        }
    edit_event = build_geometry_edit_event(
        edit_id=edit_id,
        tick=tick,
        operator_subject_id=operator_subject_id,
        edit_kind="remove",
        target_cell_keys=sorted_targets,
        volume_amount=removed_total,
        material_out=material_out,
        extensions={
            "geometry_edit_policy_id": str(geometry_edit_policy_id or _DEFAULT_POLICY_ID),
            "requested_volume_amount": int(max(0, _as_int(volume_amount, 0))),
            "unapplied_volume_amount": int(max(0, remaining)),
            **_as_map(extensions),
        },
    )
    updated_rows = [dict(rows_by_key[key]) for key in sorted(rows_by_key.keys())]
    result = {
        "result": "complete",
        "geometry_cell_states": updated_rows,
        "updated_geometry_cell_states": [dict(rows_by_key[key]) for key in sorted(updated_keys)],
        "removed_volume_amount": int(removed_total),
        "unapplied_volume_amount": int(max(0, remaining)),
        "material_out": material_out,
        "geometry_edit_event": edit_event,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def geometry_add_volume(
    *,
    geometry_cell_states: object,
    target_cell_keys: Sequence[Mapping[str, object]],
    volume_amount: int,
    material_id: str,
    tick: int,
    operator_subject_id: str,
    edit_id: str = "",
    geometry_edit_policy_id: str = _DEFAULT_POLICY_ID,
    geometry_edit_policy_registry: Mapping[str, object] | None = None,
    material_registry: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
    material_in: Mapping[str, object] | None = None,
) -> dict:
    policy_row = _policy_row(geometry_edit_policy_id, geometry_edit_policy_registry)
    max_cells, max_per_cell, _allow_micro_chunks, _micro_chunk_budget, _partial_chunk_policy = _policy_limits(policy_row)
    sorted_targets = _sorted_geo_cell_keys(target_cell_keys)
    if not sorted_targets:
        return _refusal("geometry_add requires target_cell_keys", details={"geometry_edit_policy_id": geometry_edit_policy_id})
    if len(sorted_targets) > max_cells:
        return _refusal(
            "geometry_add exceeded target cell budget",
            details={"geometry_edit_policy_id": geometry_edit_policy_id, "max_target_cells": max_cells, "requested_target_cells": len(sorted_targets)},
        )
    material_token = str(material_id or "").strip()
    if not material_token:
        return _refusal("geometry_add requires material_id")
    remaining = int(max(0, _as_int(volume_amount, 0)))
    if remaining <= 0:
        return _refusal("geometry_add requires positive volume_amount", details={"volume_amount": volume_amount})
    rows_by_key = geometry_cell_state_rows_by_key(geometry_cell_states, material_registry=material_registry)
    updated_keys: List[str] = []
    added_total = 0
    for cell_key in sorted_targets:
        if remaining <= 0:
            break
        existing = dict(rows_by_key.get(_geo_cell_key_hash(cell_key)) or build_geometry_cell_state(
            geo_cell_key=cell_key,
            material_id=_DEFAULT_MATERIAL_ID,
            occupancy_fraction=0,
            material_registry=material_registry,
        ))
        available_void = int(max(0, _OCCUPANCY_SCALE - _as_int(existing.get("occupancy_fraction", 0), 0)))
        delta = int(min(remaining, max_per_cell, available_void))
        if delta <= 0:
            continue
        updated_occupancy = int(min(_OCCUPANCY_SCALE, _as_int(existing.get("occupancy_fraction", 0), 0) + delta))
        existing_material = str(existing.get("material_id", _DEFAULT_MATERIAL_ID)).strip() or _DEFAULT_MATERIAL_ID
        updated_material = material_token if existing_material == _DEFAULT_MATERIAL_ID or _as_int(existing.get("occupancy_fraction", 0), 0) <= 0 else existing_material
        updated_row = build_geometry_cell_state(
            geo_cell_key=_as_map(existing.get("geo_cell_key")),
            material_id=updated_material,
            occupancy_fraction=updated_occupancy,
            height_proxy=_update_height_proxy(existing, updated_occupancy),
            extensions={
                **_as_map(existing.get("extensions")),
                "last_edit_kind": "add",
                "last_edit_tick": int(max(0, _as_int(tick, 0))),
                "material_fill_id": material_token,
            },
            material_registry=material_registry,
        )
        rows_by_key[_geo_cell_key_hash(updated_row.get("geo_cell_key"))] = updated_row
        updated_keys.append(_geo_cell_key_hash(updated_row.get("geo_cell_key")))
        remaining -= delta
        added_total += delta
    normalized_material_in = _normalize_material_transfer(material_in) or {
        "material_id": material_token,
        "quantity_mass_raw": int(added_total),
        "batch_ids": [],
        "extensions": {},
    }
    normalized_material_in["quantity_mass_raw"] = int(max(_as_int(normalized_material_in.get("quantity_mass_raw", 0), 0), added_total))
    edit_event = build_geometry_edit_event(
        edit_id=edit_id,
        tick=tick,
        operator_subject_id=operator_subject_id,
        edit_kind="add",
        target_cell_keys=sorted_targets,
        volume_amount=added_total,
        material_in=normalized_material_in,
        extensions={
            "geometry_edit_policy_id": str(geometry_edit_policy_id or _DEFAULT_POLICY_ID),
            "requested_volume_amount": int(max(0, _as_int(volume_amount, 0))),
            "unapplied_volume_amount": int(max(0, remaining)),
            **_as_map(extensions),
        },
    )
    updated_rows = [dict(rows_by_key[key]) for key in sorted(rows_by_key.keys())]
    result = {
        "result": "complete",
        "geometry_cell_states": updated_rows,
        "updated_geometry_cell_states": [dict(rows_by_key[key]) for key in sorted(updated_keys)],
        "added_volume_amount": int(added_total),
        "unapplied_volume_amount": int(max(0, remaining)),
        "material_in": normalized_material_in,
        "geometry_edit_event": edit_event,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def geometry_replace_material(
    *,
    geometry_cell_states: object,
    target_cell_keys: Sequence[Mapping[str, object]],
    material_id: str,
    tick: int,
    operator_subject_id: str,
    volume_amount: int = _OCCUPANCY_SCALE,
    edit_id: str = "",
    geometry_edit_policy_id: str = _DEFAULT_POLICY_ID,
    geometry_edit_policy_registry: Mapping[str, object] | None = None,
    material_registry: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
    material_in: Mapping[str, object] | None = None,
) -> dict:
    material_token = str(material_id or "").strip()
    if not material_token:
        return _refusal("geometry_replace requires material_id")
    policy_row = _policy_row(geometry_edit_policy_id, geometry_edit_policy_registry)
    max_cells, max_per_cell, _allow_micro_chunks, _micro_chunk_budget, _partial_chunk_policy = _policy_limits(policy_row)
    sorted_targets = _sorted_geo_cell_keys(target_cell_keys)
    if not sorted_targets:
        return _refusal("geometry_replace requires target_cell_keys", details={"geometry_edit_policy_id": geometry_edit_policy_id})
    if len(sorted_targets) > max_cells:
        return _refusal(
            "geometry_replace exceeded target cell budget",
            details={"geometry_edit_policy_id": geometry_edit_policy_id, "max_target_cells": max_cells, "requested_target_cells": len(sorted_targets)},
        )
    remaining = int(max(0, _as_int(volume_amount, _OCCUPANCY_SCALE)))
    rows_by_key = geometry_cell_state_rows_by_key(geometry_cell_states, material_registry=material_registry)
    updated_keys: List[str] = []
    replaced_total = 0
    removed_breakdown: Dict[str, int] = {}
    for cell_key in sorted_targets:
        if remaining <= 0:
            break
        existing = dict(rows_by_key.get(_geo_cell_key_hash(cell_key)) or build_geometry_cell_state(
            geo_cell_key=cell_key,
            material_id=_DEFAULT_MATERIAL_ID,
            occupancy_fraction=0,
            material_registry=material_registry,
        ))
        occupied = int(max(0, _as_int(existing.get("occupancy_fraction", 0), 0)))
        if occupied <= 0:
            continue
        delta = int(min(remaining, max_per_cell, occupied))
        if delta <= 0:
            continue
        existing_material = str(existing.get("material_id", _DEFAULT_MATERIAL_ID)).strip() or _DEFAULT_MATERIAL_ID
        removed_breakdown[existing_material] = int(removed_breakdown.get(existing_material, 0) + delta)
        updated_row = build_geometry_cell_state(
            geo_cell_key=_as_map(existing.get("geo_cell_key")),
            material_id=material_token,
            occupancy_fraction=occupied,
            height_proxy=_update_height_proxy(existing, occupied),
            extensions={
                **_as_map(existing.get("extensions")),
                "last_edit_kind": "replace",
                "last_edit_tick": int(max(0, _as_int(tick, 0))),
                "replaced_material_id": existing_material,
            },
            material_registry=material_registry,
        )
        rows_by_key[_geo_cell_key_hash(updated_row.get("geo_cell_key"))] = updated_row
        updated_keys.append(_geo_cell_key_hash(updated_row.get("geo_cell_key")))
        remaining -= delta
        replaced_total += delta
    material_out = None
    removed_rows = _material_breakdown_rows(removed_breakdown)
    if removed_rows:
        material_out = {
            "material_id": _dominant_material(removed_breakdown, fallback=_DEFAULT_SOLID_MATERIAL_ID),
            "quantity_mass_raw": int(replaced_total),
            "extensions": {"material_breakdown": removed_rows},
        }
    normalized_material_in = _normalize_material_transfer(material_in) or {
        "material_id": material_token,
        "quantity_mass_raw": int(replaced_total),
        "batch_ids": [],
        "extensions": {},
    }
    edit_event = build_geometry_edit_event(
        edit_id=edit_id,
        tick=tick,
        operator_subject_id=operator_subject_id,
        edit_kind="replace",
        target_cell_keys=sorted_targets,
        volume_amount=replaced_total,
        material_in=normalized_material_in,
        material_out=material_out,
        extensions={
            "geometry_edit_policy_id": str(geometry_edit_policy_id or _DEFAULT_POLICY_ID),
            "requested_volume_amount": int(max(0, _as_int(volume_amount, 0))),
            "unapplied_volume_amount": int(max(0, remaining)),
            **_as_map(extensions),
        },
    )
    updated_rows = [dict(rows_by_key[key]) for key in sorted(rows_by_key.keys())]
    result = {
        "result": "complete",
        "geometry_cell_states": updated_rows,
        "updated_geometry_cell_states": [dict(rows_by_key[key]) for key in sorted(updated_keys)],
        "replaced_volume_amount": int(replaced_total),
        "unapplied_volume_amount": int(max(0, remaining)),
        "material_in": normalized_material_in,
        "material_out": material_out,
        "geometry_edit_event": edit_event,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def geometry_cut_volume(
    *,
    geometry_cell_states: object,
    target_cell_keys: Sequence[Mapping[str, object]],
    volume_amount: int,
    tick: int,
    operator_subject_id: str,
    edit_id: str = "",
    geometry_edit_policy_id: str = _DEFAULT_POLICY_ID,
    geometry_edit_policy_registry: Mapping[str, object] | None = None,
    material_registry: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    remove_result = geometry_remove_volume(
        geometry_cell_states=geometry_cell_states,
        target_cell_keys=target_cell_keys,
        volume_amount=volume_amount,
        tick=tick,
        operator_subject_id=operator_subject_id,
        edit_id=edit_id,
        geometry_edit_policy_id=geometry_edit_policy_id,
        geometry_edit_policy_registry=geometry_edit_policy_registry,
        material_registry=material_registry,
        extensions={"cut_path": True, **_as_map(extensions)},
    )
    if str(remove_result.get("result", "")) != "complete":
        return remove_result
    edit_event = normalize_geometry_edit_event(
        {
            **_as_map(remove_result.get("geometry_edit_event")),
            "edit_kind": "cut",
            "extensions": {
                **_as_map(_as_map(remove_result.get("geometry_edit_event")).get("extensions")),
                "cut_path": True,
            },
        }
    )
    result = dict(remove_result)
    result["geometry_edit_event"] = edit_event
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def geometry_coupling_effects_for_cell_state(
    row: Mapping[str, object] | None,
    *,
    prior_row: Mapping[str, object] | None = None,
) -> dict:
    current = _as_map(row)
    prior = _as_map(prior_row)
    cell_key = _as_map(current.get("geo_cell_key"))
    occupancy = int(max(0, _as_int(current.get("occupancy_fraction", 0), 0)))
    prior_occupancy = int(max(0, _as_int(prior.get("occupancy_fraction", occupancy), occupancy)))
    excavation_delta = int(max(0, prior_occupancy - occupancy))
    current_material = str(current.get("material_id", _DEFAULT_MATERIAL_ID)).strip() or _DEFAULT_MATERIAL_ID
    permeability_proxy = int(max(0, _as_int(current.get("permeability_proxy", 0), 0)))
    conductance_proxy = int(max(0, _as_int(current.get("conductance_proxy", 0), 0)))
    stability_hazard = int(min(_OCCUPANCY_SCALE, excavation_delta + max(0, _OCCUPANCY_SCALE - occupancy)))
    return {
        "geo_cell_key": cell_key,
        "material_id": current_material,
        "permeability_proxy": permeability_proxy,
        "conductance_proxy": conductance_proxy,
        "stability_hazard": stability_hazard,
        "deterministic_fingerprint": canonical_sha256(
            {
                "geo_cell_key": cell_key,
                "material_id": current_material,
                "permeability_proxy": permeability_proxy,
                "conductance_proxy": conductance_proxy,
                "stability_hazard": stability_hazard,
            }
        ),
    }


def aggregate_geometry_chunk_to_cell(
    chunk_row: Mapping[str, object] | None,
    *,
    fallback_material_id: str = _DEFAULT_SOLID_MATERIAL_ID,
    material_registry: Mapping[str, object] | None = None,
) -> dict:
    row = _as_map(chunk_row)
    parent = _coerce_cell_key(row.get("parent_cell_key"))
    if not parent:
        raise ValueError("chunk_row.parent_cell_key is required")
    payload_ref = _as_map(row.get("chunk_payload_ref"))
    subcells = [dict(item) for item in _as_list(payload_ref.get("subcells")) if isinstance(item, Mapping)]
    if subcells:
        total = 0
        breakdown: Dict[str, int] = {}
        for subcell in sorted(subcells, key=lambda item: int(_as_int(item.get("subcell_index", 0), 0))):
            occupancy = _clamp_fraction(subcell.get("occupancy_fraction", 0))
            total += occupancy
            material_id = str(subcell.get("material_id", "")).strip() or fallback_material_id
            breakdown[material_id] = int(breakdown.get(material_id, 0) + occupancy)
        occupancy_fraction = int(total // max(1, len(subcells)))
        material_id = _dominant_material(breakdown, fallback=fallback_material_id)
    else:
        occupancy_fraction = _clamp_fraction(payload_ref.get("occupancy_fraction", 0))
        material_id = str(payload_ref.get("material_id", "")).strip() or (fallback_material_id if occupancy_fraction > 0 else _DEFAULT_MATERIAL_ID)
    return build_geometry_cell_state(
        geo_cell_key=parent,
        material_id=material_id,
        occupancy_fraction=occupancy_fraction,
        extensions={"aggregated_from_chunk_id": str(row.get("chunk_id", "")).strip()},
        material_registry=material_registry,
    )


def build_micro_geometry_chunk_from_cell_state(
    cell_state: Mapping[str, object] | None,
    *,
    subcell_count: int = 8,
    chunk_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    row = normalize_geometry_cell_state(cell_state)
    count = int(max(1, _as_int(subcell_count, 8)))
    occupancy = int(max(0, _as_int(row.get("occupancy_fraction", 0), 0)))
    remaining_units = int(occupancy * count)
    subcells: List[dict] = []
    for index in range(count):
        slot_value = int(min(_OCCUPANCY_SCALE, max(0, remaining_units)))
        remaining_units -= slot_value
        subcells.append(
            {
                "subcell_index": int(index),
                "material_id": str(row.get("material_id", _DEFAULT_MATERIAL_ID)).strip() or _DEFAULT_MATERIAL_ID,
                "occupancy_fraction": int(slot_value),
            }
        )
    return build_geometry_chunk_state(
        parent_cell_key=_as_map(row.get("geo_cell_key")),
        chunk_payload_ref={
            "schema_id": "dominium.geo.chunk.inline.v1",
            "subcell_count": count,
            "source_cell_occupancy_fraction": occupancy,
            "subcells": subcells,
        },
        chunk_id=chunk_id,
        extensions={"source": "micro_from_macro", **_as_map(extensions)},
    )


def geometry_apply_micro_chunk_edit(
    chunk_row: Mapping[str, object] | None,
    *,
    edit_kind: str,
    volume_amount: int,
    material_id: str = "",
    extensions: Mapping[str, object] | None = None,
    material_registry: Mapping[str, object] | None = None,
) -> dict:
    row = normalize_geometry_chunk_state(chunk_row)
    kind = str(edit_kind or "").strip().lower()
    if kind not in {"remove", "add", "replace", "cut"}:
        raise ValueError("edit_kind is required")
    payload_ref = _as_map(row.get("chunk_payload_ref"))
    subcells = [dict(item) for item in _as_list(payload_ref.get("subcells")) if isinstance(item, Mapping)]
    if not subcells:
        raise ValueError("chunk_row.chunk_payload_ref.subcells is required")
    prior_macro = aggregate_geometry_chunk_to_cell(row, material_registry=material_registry)
    subcell_count = int(max(1, len(subcells)))
    remaining_units = int(max(0, _as_int(volume_amount, 0))) * subcell_count
    material_token = str(material_id or "").strip()
    updated_subcells: List[dict] = []
    for subcell in sorted(subcells, key=lambda item: int(_as_int(item.get("subcell_index", 0), 0))):
        existing = dict(subcell)
        occupancy = int(max(0, _as_int(existing.get("occupancy_fraction", 0), 0)))
        if kind in {"remove", "cut"}:
            delta = int(min(remaining_units, occupancy))
            if delta > 0:
                existing["occupancy_fraction"] = int(max(0, occupancy - delta))
                if int(existing["occupancy_fraction"]) <= 0:
                    existing["material_id"] = _DEFAULT_MATERIAL_ID
                remaining_units -= delta
        elif kind == "add":
            delta = int(min(remaining_units, max(0, _OCCUPANCY_SCALE - occupancy)))
            if delta > 0:
                existing["occupancy_fraction"] = int(min(_OCCUPANCY_SCALE, occupancy + delta))
                if material_token:
                    existing["material_id"] = material_token
                remaining_units -= delta
        else:
            delta = int(min(remaining_units, occupancy))
            if delta > 0 and material_token:
                existing["material_id"] = material_token
                remaining_units -= delta
        updated_subcells.append(existing)
    updated_chunk = build_geometry_chunk_state(
        parent_cell_key=_as_map(row.get("parent_cell_key")),
        chunk_payload_ref={
            **payload_ref,
            "subcells": updated_subcells,
            "last_edit_kind": kind,
        },
        chunk_id=str(row.get("chunk_id", "")).strip(),
        extensions={**_as_map(row.get("extensions")), **_as_map(extensions)},
    )
    aggregated = aggregate_geometry_chunk_to_cell(updated_chunk, material_registry=material_registry)
    applied_volume_amount = int(
        max(
            0,
            abs(
                _as_int(aggregated.get("occupancy_fraction", 0), 0)
                - _as_int(prior_macro.get("occupancy_fraction", 0), 0)
            ),
        )
    )
    return {
        "chunk_state": updated_chunk,
        "aggregated_cell_state": aggregated,
        "applied_volume_amount": applied_volume_amount,
        "deterministic_fingerprint": canonical_sha256(
            {
                "chunk_id": str(updated_chunk.get("chunk_id", "")).strip(),
                "aggregated_cell_state": aggregated,
                "applied_volume_amount": applied_volume_amount,
            }
        ),
    }


__all__ = [
    "REFUSAL_GEO_GEOMETRY_INVALID",
    "aggregate_geometry_chunk_to_cell",
    "build_micro_geometry_chunk_from_cell_state",
    "build_geometry_cell_state",
    "build_geometry_chunk_state",
    "build_geometry_edit_event",
    "geometry_add_volume",
    "geometry_apply_micro_chunk_edit",
    "geometry_cell_state_rows_by_key",
    "geometry_chunk_state_rows_by_id",
    "geometry_coupling_effects_for_cell_state",
    "geometry_cut_volume",
    "geometry_edit_event_hash_chain",
    "geometry_edit_policy_registry_hash",
    "geometry_edit_policy_rows_by_id",
    "geometry_get_cell_state",
    "geometry_get_conductance_proxy",
    "geometry_get_occupancy",
    "geometry_get_permeability_proxy",
    "geometry_remove_volume",
    "geometry_replace_material",
    "geometry_state_hash_surface",
    "normalize_geometry_cell_state",
    "normalize_geometry_cell_state_rows",
    "normalize_geometry_chunk_state",
    "normalize_geometry_chunk_state_rows",
    "normalize_geometry_edit_event",
    "normalize_geometry_edit_event_rows",
]
