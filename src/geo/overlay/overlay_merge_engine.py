"""Deterministic GEO-9 overlay merge helpers."""

from __future__ import annotations

import copy
import json
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256
from src.meta_extensions_engine import normalize_extensions_tree

from src.geo.index.geo_index_engine import _coerce_cell_key, _semantic_cell_key
from src.geo.worldgen.worldgen_engine import normalize_worldgen_result


REFUSAL_GEO_OVERLAY_INVALID = "refusal.geo.overlay_invalid"
REFUSAL_OVERLAY_CONFLICT = "refusal.overlay.conflict"

_OVERLAY_POLICY_REGISTRY_REL = os.path.join("data", "registries", "overlay_policy_registry.json")
_OVERLAY_CONFLICT_POLICY_REGISTRY_REL = os.path.join("data", "registries", "overlay_conflict_policy_registry.json")
_OVERLAY_VERSION = "GEO9-4"
_OVERLAY_CACHE: Dict[str, dict] = {}
_OVERLAY_CACHE_MAX = 256

_LAYER_KIND_RANK = {
    "base": 0,
    "official": 1,
    "mod": 2,
    "save": 3,
}
_OFFICIAL_SIGNATURE_STATUS = {"official", "signed", "verified"}
_IMMUTABLE_PROPERTY_PATHS = {
    "object_id",
    "identity_hash",
    "generator_version_id",
    "topology_profile_id",
    "metric_profile_id",
    "partition_profile_id",
    "projection_profile_id",
}


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return dict(normalize_extensions_tree(json.load(handle)) or {})
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


def _layer_kind_rank(layer_kind: str) -> int:
    return int(_LAYER_KIND_RANK.get(str(layer_kind or "").strip().lower(), 99))


def _jsonable_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _jsonable_value(item)
            for key, item in sorted(dict(value).items(), key=lambda row: str(row[0]))
        }
    if isinstance(value, list):
        return [_jsonable_value(item) for item in list(value)]
    return copy.deepcopy(value)


def _geo_cell_key_hash(value: object) -> str:
    row = _coerce_cell_key(_as_map(value))
    return canonical_sha256(_semantic_cell_key(row)) if row else ""


def _layer_sort_key(value: object) -> Tuple[int, int, str, str]:
    row = _as_map(value)
    return (
        int(max(0, _as_int(row.get("precedence_order", 0), 0))),
        _layer_kind_rank(str(row.get("layer_kind", "")).strip()),
        str(row.get("source_ref", "")).strip(),
        str(row.get("layer_id", "")).strip(),
    )


def _refusal(message: str, details: Mapping[str, object] | None = None, *, refusal_code: str = REFUSAL_GEO_OVERLAY_INVALID) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(refusal_code),
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def overlay_policy_rows_by_id(registry_payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    payload = _as_map(registry_payload) or _registry_payload(_OVERLAY_POLICY_REGISTRY_REL)
    rows = _rows_from_registry(payload, "overlay_policies")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("overlay_policy_id", ""))):
        overlay_policy_id = str(row.get("overlay_policy_id", "")).strip()
        if not overlay_policy_id:
            continue
        normalized = {
            "schema_version": "1.0.0",
            "overlay_policy_id": overlay_policy_id,
            "description": str(row.get("description", "")).strip(),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": {
                str(key): value
                for key, value in sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))
            },
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[overlay_policy_id] = normalized
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def overlay_policy_registry_hash(registry_payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(registry_payload) or _registry_payload(_OVERLAY_POLICY_REGISTRY_REL))


def overlay_conflict_policy_rows_by_id(registry_payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    payload = _as_map(registry_payload) or _registry_payload(_OVERLAY_CONFLICT_POLICY_REGISTRY_REL)
    rows = _rows_from_registry(payload, "overlay_conflict_policies")
    out: Dict[str, dict] = {}
    for row in sorted(rows, key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        normalized = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "mode": str(row.get("mode", "")).strip(),
            "description": str(row.get("description", "")).strip(),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": {
                str(key): value
                for key, value in sorted(_as_map(row.get("extensions")).items(), key=lambda item: str(item[0]))
            },
        }
        if not normalized["deterministic_fingerprint"]:
            normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
        out[policy_id] = normalized
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def overlay_conflict_policy_registry_hash(registry_payload: Mapping[str, object] | None = None) -> str:
    return canonical_sha256(_as_map(registry_payload) or _registry_payload(_OVERLAY_CONFLICT_POLICY_REGISTRY_REL))


def build_overlay_layer(
    *,
    layer_id: str,
    layer_kind: str,
    precedence_order: int,
    source_ref: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    kind_token = str(layer_kind or "").strip().lower()
    if kind_token not in _LAYER_KIND_RANK:
        raise ValueError("layer_kind is invalid")
    payload = {
        "schema_version": "1.0.0",
        "layer_id": str(layer_id or "").strip(),
        "layer_kind": kind_token,
        "precedence_order": int(max(0, _as_int(precedence_order, 0))),
        "source_ref": str(source_ref or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): _jsonable_value(value)
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    if not payload["source_ref"]:
        raise ValueError("source_ref is required")
    if not payload["layer_id"]:
        payload["layer_id"] = "layer.{}.{}".format(
            kind_token,
            canonical_sha256(
                {
                    "layer_kind": kind_token,
                    "precedence_order": int(payload["precedence_order"]),
                    "source_ref": str(payload["source_ref"]),
                }
            )[:16],
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_overlay_layer(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_overlay_layer(
        layer_id=str(payload.get("layer_id", "")).strip(),
        layer_kind=str(payload.get("layer_kind", "")).strip(),
        precedence_order=_as_int(payload.get("precedence_order", 0), 0),
        source_ref=str(payload.get("source_ref", "")).strip(),
        extensions=_as_map(payload.get("extensions")),
    )


def normalize_overlay_layer_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            normalized = normalize_overlay_layer(row)
        except ValueError:
            continue
        out[str(normalized.get("layer_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys(), key=lambda key: _layer_sort_key(out[key]))]


def build_property_patch(
    *,
    target_object_id: str,
    property_path: str,
    operation: str,
    value: object,
    originating_layer_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    property_token = str(property_path or "").strip()
    operation_token = str(operation or "").strip().lower()
    if (not str(target_object_id or "").strip()) or (not property_token):
        raise ValueError("target_object_id and property_path are required")
    if operation_token not in {"set", "add", "remove", "replace"}:
        raise ValueError("operation is invalid")
    if property_token in _IMMUTABLE_PROPERTY_PATHS:
        raise ValueError("immutable property path may not be patched")
    extension_payload = {
        str(key): _jsonable_value(item)
        for key, item in sorted(_as_map(extensions).items(), key=lambda row: str(row[0]))
    }
    if operation_token == "remove" and not str(extension_payload.get("reason", "")).strip():
        raise ValueError("remove patches require explicit reason metadata")
    payload = {
        "schema_version": "1.0.0",
        "target_object_id": str(target_object_id).strip(),
        "property_path": property_token,
        "operation": operation_token,
        "value": _jsonable_value(value),
        "originating_layer_id": str(originating_layer_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": extension_payload,
    }
    if not payload["originating_layer_id"]:
        raise ValueError("originating_layer_id is required")
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_property_patch(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_property_patch(
        target_object_id=str(payload.get("target_object_id", "")).strip(),
        property_path=str(payload.get("property_path", "")).strip(),
        operation=str(payload.get("operation", "")).strip(),
        value=payload.get("value"),
        originating_layer_id=str(payload.get("originating_layer_id", "")).strip(),
        extensions=_as_map(payload.get("extensions")),
    )


def normalize_property_patch_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            normalized = normalize_property_patch(row)
        except ValueError:
            continue
        out[str(normalized.get("deterministic_fingerprint", "")).strip()] = normalized
    return [
        dict(out[key])
        for key in sorted(
            out.keys(),
            key=lambda key: (
                str(out[key].get("originating_layer_id", "")),
                str(out[key].get("property_path", "")),
                str(out[key].get("target_object_id", "")),
                str(out[key].get("deterministic_fingerprint", "")),
            ),
        )
    ]


def property_patch_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_property_patch_rows(rows))


def build_overlay_manifest(
    *,
    universe_id: str,
    layers: object,
    pack_lock_hash: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    universe_token = str(universe_id or "").strip()
    pack_lock_token = str(pack_lock_hash or "").strip()
    if (not universe_token) or (not pack_lock_token):
        raise ValueError("universe_id and pack_lock_hash are required")
    payload = {
        "schema_version": "1.0.0",
        "universe_id": universe_token,
        "layers": normalize_overlay_layer_rows(layers),
        "pack_lock_hash": pack_lock_token,
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): _jsonable_value(value)
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_overlay_manifest(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    return build_overlay_manifest(
        universe_id=str(payload.get("universe_id", "")).strip(),
        layers=payload.get("layers"),
        pack_lock_hash=str(payload.get("pack_lock_hash", "")).strip(),
        extensions=_as_map(payload.get("extensions")),
    )


def overlay_manifest_hash(row: Mapping[str, object] | None) -> str:
    return canonical_sha256(normalize_overlay_manifest(row))


def build_default_overlay_manifest(
    *,
    universe_id: str,
    pack_lock_hash: str,
    save_id: str,
    generator_version_id: str = "",
    official_layer_specs: object = None,
    mod_layer_specs: object = None,
    overlay_policy_id: str = "overlay.default",
    overlay_conflict_policy_id: str = "",
) -> dict:
    layers = [
        build_overlay_layer(
            layer_id="base.worldgen",
            layer_kind="base",
            precedence_order=0,
            source_ref="base.worldgen",
            extensions={
                "generator_version_id": str(generator_version_id or "").strip(),
                "layer_role": "procedural_base",
                "source": "GEO9-3",
            },
        )
    ]
    for idx, row in enumerate(sorted((_as_map(item) for item in _as_list(official_layer_specs)), key=canonical_sha256)):
        pack_hash = str(row.get("pack_hash", row.get("source_ref", ""))).strip()
        layers.append(
            build_overlay_layer(
                layer_id=str(row.get("layer_id", "")).strip() or "official.reality.{}".format(idx),
                layer_kind="official",
                precedence_order=100,
                source_ref=pack_hash or "official.{}".format(idx),
                extensions={
                    "pack_hash": pack_hash,
                    "pack_id": str(row.get("pack_id", "")).strip(),
                    "signature_status": str(row.get("signature_status", "")).strip(),
                    "source": "GEO9-3",
                },
            )
        )
    for idx, row in enumerate(sorted((_as_map(item) for item in _as_list(mod_layer_specs)), key=canonical_sha256)):
        pack_hash = str(row.get("pack_hash", row.get("source_ref", ""))).strip()
        layers.append(
            build_overlay_layer(
                layer_id=str(row.get("layer_id", "")).strip() or "mod.{}".format(idx),
                layer_kind="mod",
                precedence_order=200,
                source_ref=pack_hash or "mod.{}".format(idx),
                extensions={
                    "pack_hash": pack_hash,
                    "pack_id": str(row.get("pack_id", "")).strip(),
                    "signature_status": str(row.get("signature_status", "")).strip(),
                    "source": "GEO9-3",
                },
            )
        )
    layers.append(
        build_overlay_layer(
            layer_id="save.patch",
            layer_kind="save",
            precedence_order=300,
            source_ref=str(save_id or "").strip() or "save.default",
            extensions={
                "save_id": str(save_id or "").strip(),
                "source": "GEO9-3",
            },
        )
    )
    return build_overlay_manifest(
        universe_id=universe_id,
        layers=layers,
        pack_lock_hash=pack_lock_hash,
        extensions={
            "overlay_policy_id": str(overlay_policy_id or "overlay.default").strip() or "overlay.default",
            "overlay_conflict_policy_id": str(overlay_conflict_policy_id or "").strip(),
            "source": "GEO9-3",
        },
    )


def build_effective_object_view(
    *,
    object_id: str,
    object_kind_id: str,
    properties: Mapping[str, object] | None,
    geo_cell_key: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    object_token = str(object_id or "").strip()
    if not object_token:
        raise ValueError("object_id is required")
    payload = {
        "object_id": object_token,
        "object_kind_id": str(object_kind_id or "").strip() or "kind.overlay.added_object",
        "properties": {
            str(key): _jsonable_value(value)
            for key, value in sorted(_as_map(properties).items(), key=lambda item: str(item[0]))
        },
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): _jsonable_value(value)
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    cell_key = _coerce_cell_key(geo_cell_key)
    if cell_key:
        payload["geo_cell_key"] = dict(cell_key)
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_effective_object_view_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            normalized = build_effective_object_view(
                object_id=str(row.get("object_id", "")).strip(),
                object_kind_id=str(row.get("object_kind_id", "")).strip(),
                properties=_as_map(row.get("properties")),
                geo_cell_key=_as_map(row.get("geo_cell_key")),
                extensions=_as_map(row.get("extensions")),
            )
        except ValueError:
            continue
        out[str(normalized.get("object_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def overlay_effective_object_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_effective_object_view_rows(rows))


def overlay_base_objects_from_worldgen_result(
    *,
    worldgen_result: Mapping[str, object],
    generated_object_rows: object = None,
) -> List[dict]:
    result_row = normalize_worldgen_result(worldgen_result)
    object_rows = [dict(item) for item in _as_list(generated_object_rows) if isinstance(item, Mapping)]
    if not object_rows:
        object_rows = [
            dict(item)
            for item in _as_list(_as_map(result_row.get("extensions")).get("generated_object_rows"))
            if isinstance(item, Mapping)
        ]
    out = []
    for row in sorted(object_rows, key=lambda item: (str(item.get("object_id_hash", "")), str(item.get("local_subkey", "")))):
        object_id = str(row.get("object_id_hash", "")).strip()
        if not object_id:
            continue
        out.append(
            build_effective_object_view(
                object_id=object_id,
                object_kind_id=str(row.get("object_kind_id", "")).strip(),
                geo_cell_key=_as_map(row.get("geo_cell_key")),
                properties={
                    "local_subkey": str(row.get("local_subkey", "")).strip(),
                    "generator_version_id": str(result_row.get("generator_version_id", "")).strip(),
                    "realism_profile_id": str(result_row.get("realism_profile_id", "")).strip(),
                    "worldgen_result_id": str(result_row.get("result_id", "")).strip(),
                    "geo_cell_key_hash": _geo_cell_key_hash(row.get("geo_cell_key")),
                },
                extensions={
                    "source_layer_id": "base.worldgen",
                    "source": "GEO9-3",
                },
            )
        )
    return normalize_effective_object_view_rows(out)


def build_overlay_conflict_artifact(
    *,
    object_id: str,
    property_path: str,
    involved_patches: object,
    mode: str,
    conflict_id: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    object_token = str(object_id or "").strip()
    property_token = str(property_path or "").strip()
    mode_token = str(mode or "").strip()
    if not object_token or not property_token or mode_token not in {"last_wins", "refuse", "prompt_stub"}:
        raise ValueError("overlay conflict artifact inputs are invalid")
    patch_rows = []
    for row in _as_list(involved_patches):
        payload = _as_map(row)
        patch_rows.append(
            {
                "layer_id": str(payload.get("layer_id", "")).strip(),
                "layer_kind": str(payload.get("layer_kind", "")).strip(),
                "layer_order": list(_layer_sort_key(payload.get("layer_row")) if payload.get("layer_row") else tuple(payload.get("layer_order") or [])),
                "precedence_order": int(max(0, _as_int(payload.get("precedence_order", 0), 0))),
                "source_ref": str(payload.get("source_ref", "")).strip(),
                "patch_hash": str(payload.get("patch_hash", "")).strip(),
                "operation": str(payload.get("operation", "")).strip(),
                "value": _jsonable_value(payload.get("value")),
            }
        )
    normalized_patches = sorted(
        patch_rows,
        key=lambda row: (
            object_token,
            property_token,
            tuple(row.get("layer_order") or []),
            str(row.get("patch_hash", "")),
        ),
    )
    payload = {
        "schema_version": "1.0.0",
        "conflict_id": str(conflict_id or "").strip(),
        "object_id": object_token,
        "property_path": property_token,
        "involved_patches": normalized_patches,
        "mode": mode_token,
        "deterministic_fingerprint": "",
        "extensions": {
            str(key): _jsonable_value(value)
            for key, value in sorted(_as_map(extensions).items(), key=lambda item: str(item[0]))
        },
    }
    if not payload["conflict_id"]:
        payload["conflict_id"] = "conflict.overlay.{}".format(
            canonical_sha256(
                {
                    "object_id": object_token,
                    "property_path": property_token,
                    "involved_patches": normalized_patches,
                    "mode": mode_token,
                }
            )[:16]
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_overlay_conflict_artifact_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        try:
            normalized = build_overlay_conflict_artifact(
                object_id=str(row.get("object_id", "")).strip(),
                property_path=str(row.get("property_path", "")).strip(),
                involved_patches=_as_list(row.get("involved_patches")),
                mode=str(row.get("mode", "")).strip(),
                conflict_id=str(row.get("conflict_id", "")).strip(),
                extensions=_as_map(row.get("extensions")),
            )
        except ValueError:
            continue
        out[str(normalized.get("conflict_id", "")).strip()] = normalized
    return [
        dict(out[key])
        for key in sorted(
            out.keys(),
            key=lambda key: (
                str(out[key].get("object_id", "")),
                str(out[key].get("property_path", "")),
                str(out[key].get("conflict_id", "")),
            ),
        )
    ]


def overlay_conflict_artifact_hash_chain(rows: object) -> str:
    return canonical_sha256(normalize_overlay_conflict_artifact_rows(rows))


def _resolved_pack_rows(resolved_packs: object) -> List[dict]:
    rows = [
        {
            "pack_id": str(dict(row).get("pack_id", "")).strip(),
            "canonical_hash": str(dict(row).get("canonical_hash", "")).strip(),
            "signature_status": str(dict(row).get("signature_status", "")).strip(),
        }
        for row in _as_list(resolved_packs)
        if isinstance(row, Mapping)
    ]
    return sorted(rows, key=lambda row: (str(row.get("canonical_hash", "")), str(row.get("pack_id", ""))))


def validate_overlay_manifest_trust(
    *,
    overlay_manifest: Mapping[str, object],
    resolved_packs: object = None,
    expected_pack_lock_hash: str = "",
    overlay_policy_id: str = "",
    overlay_policy_registry_payload: Mapping[str, object] | None = None,
    overlay_conflict_policy_id: str = "",
    overlay_conflict_policy_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    manifest = normalize_overlay_manifest(overlay_manifest)
    policy_rows = overlay_policy_rows_by_id(overlay_policy_registry_payload)
    conflict_policy_rows = overlay_conflict_policy_rows_by_id(overlay_conflict_policy_registry_payload)
    resolved_policy_id = str(
        overlay_policy_id or _as_map(manifest.get("extensions")).get("overlay_policy_id", "overlay.default")
    ).strip() or "overlay.default"
    policy_row = dict(policy_rows.get(resolved_policy_id) or {})
    if not policy_row:
        return _refusal("overlay_policy_id is not declared", {"overlay_policy_id": resolved_policy_id})
    policy_ext = _as_map(policy_row.get("extensions"))
    resolved_conflict_policy_id = str(
        overlay_conflict_policy_id
        or _as_map(manifest.get("extensions")).get("overlay_conflict_policy_id", "")
        or policy_ext.get("overlay_conflict_policy_id", "")
        or "overlay.conflict.last_wins"
    ).strip() or "overlay.conflict.last_wins"
    conflict_policy_row = dict(conflict_policy_rows.get(resolved_conflict_policy_id) or {})
    if not conflict_policy_row:
        return _refusal(
            "overlay_conflict_policy_id is not declared",
            {"overlay_conflict_policy_id": resolved_conflict_policy_id},
            refusal_code="refusal.overlay.conflict_policy_missing",
        )
    overlay_conflict_mode = str(conflict_policy_row.get("mode", "")).strip()
    if overlay_conflict_mode not in {"last_wins", "refuse", "prompt_stub"}:
        return _refusal(
            "overlay_conflict_policy_id resolves to an invalid mode",
            {
                "overlay_conflict_policy_id": resolved_conflict_policy_id,
                "mode": overlay_conflict_mode,
            },
            refusal_code="refusal.overlay.conflict_policy_invalid",
        )
    if str(expected_pack_lock_hash or "").strip() and str(manifest.get("pack_lock_hash", "")).strip() != str(expected_pack_lock_hash).strip():
        return _refusal(
            "overlay manifest pack_lock_hash does not match expected lock hash",
            {
                "manifest_pack_lock_hash": str(manifest.get("pack_lock_hash", "")).strip(),
                "expected_pack_lock_hash": str(expected_pack_lock_hash).strip(),
            },
            refusal_code="refusal.geo.overlay_pack_lock_mismatch",
        )
    allow_unsigned_mods = bool(policy_ext.get("allow_unsigned_mods", True))
    require_official_signature = bool(policy_ext.get("require_official_signature", True))
    pack_rows = _resolved_pack_rows(resolved_packs)
    pack_by_hash = dict((str(row.get("canonical_hash", "")).strip(), dict(row)) for row in pack_rows if str(row.get("canonical_hash", "")).strip())
    pack_by_id = dict((str(row.get("pack_id", "")).strip(), dict(row)) for row in pack_rows if str(row.get("pack_id", "")).strip())
    normalized_layers = []
    unsigned_mod_layers: List[str] = []
    trust_categories: Dict[str, str] = {}
    for layer in normalize_overlay_layer_rows(manifest.get("layers")):
        ext = _as_map(layer.get("extensions"))
        layer_kind = str(layer.get("layer_kind", "")).strip()
        pack_hash = str(ext.get("pack_hash", layer.get("source_ref", ""))).strip()
        pack_id = str(ext.get("pack_id", "")).strip()
        pack_row = dict(pack_by_hash.get(pack_hash) or pack_by_id.get(pack_id) or {})
        signature_status = str(ext.get("signature_status", pack_row.get("signature_status", ""))).strip()
        trust_category = str(ext.get("trust_category", "")).strip()
        if not trust_category:
            if layer_kind == "official":
                trust_category = "official"
            elif layer_kind == "mod":
                trust_category = "unsigned" if signature_status in {"", "unsigned"} else "signed"
            elif layer_kind == "save":
                trust_category = "save"
            else:
                trust_category = "base"
        if layer_kind == "official":
            if pack_rows and not pack_row:
                return _refusal(
                    "official overlay layer is not backed by the active lockfile",
                    {"layer_id": str(layer.get("layer_id", "")).strip(), "source_ref": str(layer.get("source_ref", "")).strip()},
                    refusal_code="refusal.geo.overlay_official_missing_from_lock",
                )
            if require_official_signature and signature_status not in _OFFICIAL_SIGNATURE_STATUS:
                return _refusal(
                    "official overlay layer requires signed or official trust status",
                    {
                        "layer_id": str(layer.get("layer_id", "")).strip(),
                        "signature_status": signature_status,
                    },
                    refusal_code="refusal.geo.overlay_official_signature_required",
                )
        if layer_kind == "mod" and signature_status in {"", "unsigned"}:
            unsigned_mod_layers.append(str(layer.get("layer_id", "")).strip())
            if not allow_unsigned_mods:
                return _refusal(
                    "overlay policy forbids unsigned mod layers",
                    {"layer_id": str(layer.get("layer_id", "")).strip()},
                    refusal_code="refusal.geo.overlay_unsigned_mod_forbidden",
                )
        trust_categories[str(layer.get("layer_id", "")).strip()] = trust_category
        normalized_layers.append(
            build_overlay_layer(
                layer_id=str(layer.get("layer_id", "")).strip(),
                layer_kind=layer_kind,
                precedence_order=_as_int(layer.get("precedence_order", 0), 0),
                source_ref=str(layer.get("source_ref", "")).strip(),
                extensions={
                    **ext,
                    "pack_hash": pack_hash,
                    "pack_id": pack_id or str(pack_row.get("pack_id", "")).strip(),
                    "signature_status": signature_status,
                    "trust_category": trust_category,
                },
            )
        )
    validated_manifest = build_overlay_manifest(
        universe_id=str(manifest.get("universe_id", "")).strip(),
        layers=normalized_layers,
        pack_lock_hash=str(manifest.get("pack_lock_hash", "")).strip(),
        extensions={
            **_as_map(manifest.get("extensions")),
            "overlay_policy_id": resolved_policy_id,
            "overlay_conflict_policy_id": resolved_conflict_policy_id,
            "unsigned_mod_layer_ids": sorted(set(unsigned_mod_layers)),
            "trust_categories": dict((key, trust_categories[key]) for key in sorted(trust_categories.keys())),
        },
    )
    return {
        "result": "complete",
        "overlay_manifest": validated_manifest,
        "overlay_policy_id": resolved_policy_id,
        "overlay_conflict_policy_id": resolved_conflict_policy_id,
        "overlay_conflict_mode": overlay_conflict_mode,
        "unsigned_mod_layer_ids": sorted(set(unsigned_mod_layers)),
        "trust_categories": dict((key, trust_categories[key]) for key in sorted(trust_categories.keys())),
        "deterministic_fingerprint": canonical_sha256(
            {
                "overlay_manifest": validated_manifest,
                "overlay_policy_id": resolved_policy_id,
                "overlay_conflict_policy_id": resolved_conflict_policy_id,
                "overlay_conflict_mode": overlay_conflict_mode,
                "unsigned_mod_layer_ids": sorted(set(unsigned_mod_layers)),
                "trust_categories": dict((key, trust_categories[key]) for key in sorted(trust_categories.keys())),
            }
        ),
    }


def _property_path_tokens(property_path: str) -> List[str]:
    return [token for token in str(property_path or "").split(".") if token]


def _get_property(properties: Mapping[str, object], property_path: str) -> Tuple[bool, object]:
    current: object = _as_map(properties)
    tokens = _property_path_tokens(property_path)
    for token in tokens:
        if not isinstance(current, Mapping) or token not in current:
            return False, None
        current = current[token]
    return True, _jsonable_value(current)


def _set_property(properties: Mapping[str, object], property_path: str, value: object) -> dict:
    tokens = _property_path_tokens(property_path)
    if not tokens:
        return _as_map(properties)
    out = copy.deepcopy(_as_map(properties))
    current = out
    for token in tokens[:-1]:
        next_value = current.get(token)
        if not isinstance(next_value, Mapping):
            next_value = {}
            current[token] = next_value
        current = next_value
    current[tokens[-1]] = _jsonable_value(value)
    return out


def _remove_property(properties: Mapping[str, object], property_path: str) -> Tuple[dict, bool]:
    tokens = _property_path_tokens(property_path)
    if not tokens:
        return _as_map(properties), False
    out = copy.deepcopy(_as_map(properties))
    current = out
    for token in tokens[:-1]:
        next_value = current.get(token)
        if not isinstance(next_value, Mapping):
            return out, False
        current = next_value
    if tokens[-1] not in current:
        return out, False
    current.pop(tokens[-1], None)
    return out, True


def _add_property_value(current_found: bool, current_value: object, patch_value: object) -> object:
    if not current_found:
        return _jsonable_value(patch_value)
    if isinstance(current_value, list):
        items = list(current_value)
        if isinstance(patch_value, list):
            items.extend(_jsonable_value(patch_value))
        else:
            items.append(_jsonable_value(patch_value))
        return items
    if isinstance(current_value, Mapping) and isinstance(patch_value, Mapping):
        merged = dict(_as_map(current_value))
        for key, value in sorted(_as_map(patch_value).items(), key=lambda item: str(item[0])):
            merged[str(key)] = _jsonable_value(value)
        return merged
    if isinstance(current_value, int) and isinstance(patch_value, int):
        return int(current_value + patch_value)
    return _jsonable_value(patch_value)


def _flatten_properties(prefix: str, value: object) -> List[Tuple[str, object]]:
    if isinstance(value, Mapping):
        out: List[Tuple[str, object]] = []
        for key, item in sorted(dict(value).items(), key=lambda row: str(row[0])):
            token = "{}.{}".format(prefix, str(key)) if prefix else str(key)
            out.extend(_flatten_properties(token, item))
        return out
    return [(prefix, _jsonable_value(value))]


def _normalize_base_objects(rows: object) -> List[dict]:
    return normalize_effective_object_view_rows(rows)


def _ordered_patches_for_manifest(manifest: Mapping[str, object], property_patches: object) -> Tuple[List[dict], Dict[str, dict]]:
    layer_rows = normalize_overlay_layer_rows(_as_map(manifest).get("layers"))
    layer_by_id = dict((str(row.get("layer_id", "")).strip(), dict(row)) for row in layer_rows)
    sortable = []
    for row in normalize_property_patch_rows(property_patches):
        layer_id = str(row.get("originating_layer_id", "")).strip()
        layer_row = dict(layer_by_id.get(layer_id) or {})
        if not layer_row:
            continue
        sortable.append(
            (
                _layer_sort_key(layer_row),
                str(row.get("property_path", "")),
                str(row.get("target_object_id", "")),
                str(row.get("deterministic_fingerprint", "")),
                dict(row),
            )
        )
    return [dict(item[-1]) for item in sorted(sortable)], layer_by_id


def _detect_overlay_conflicts(
    ordered_patches: Sequence[Mapping[str, object]],
    layer_by_id: Mapping[str, Mapping[str, object]],
    *,
    conflict_mode: str,
) -> List[dict]:
    grouped: Dict[Tuple[str, str, int], List[dict]] = {}
    for patch in ordered_patches:
        patch_row = _as_map(patch)
        layer_row = _as_map(layer_by_id.get(str(patch_row.get("originating_layer_id", "")).strip()))
        if not layer_row:
            continue
        precedence_order = _as_int(layer_row.get("precedence_order", 0), 0)
        grouped.setdefault(
            (
                str(patch_row.get("target_object_id", "")).strip(),
                str(patch_row.get("property_path", "")).strip(),
                precedence_order,
            ),
            [],
        ).append(
            {
                "layer_id": str(layer_row.get("layer_id", "")).strip(),
                "layer_kind": str(layer_row.get("layer_kind", "")).strip(),
                "layer_order": list(_layer_sort_key(layer_row)),
                "layer_row": dict(layer_row),
                "precedence_order": precedence_order,
                "source_ref": str(layer_row.get("source_ref", "")).strip(),
                "patch_hash": str(patch_row.get("deterministic_fingerprint", "")).strip(),
                "operation": str(patch_row.get("operation", "")).strip(),
                "value": _jsonable_value(patch_row.get("value")),
            }
        )
    artifacts = []
    for (object_id, property_path, precedence_order) in sorted(grouped.keys()):
        involved = sorted(
            grouped[(object_id, property_path, precedence_order)],
            key=lambda row: (
                tuple(row.get("layer_order") or []),
                str(row.get("patch_hash", "")),
            ),
        )
        if len(involved) < 2:
            continue
        artifacts.append(
            build_overlay_conflict_artifact(
                object_id=object_id,
                property_path=property_path,
                involved_patches=involved,
                mode=conflict_mode,
                extensions={
                    "precedence_order": precedence_order,
                    "source": "COMPAT-SEM-3",
                },
            )
        )
    return normalize_overlay_conflict_artifact_rows(artifacts)


def _overlay_conflict_index(rows: object) -> Dict[str, dict]:
    artifacts = normalize_overlay_conflict_artifact_rows(rows)
    out: Dict[str, dict] = {}
    for row in artifacts:
        object_id = str(row.get("object_id", "")).strip()
        property_path = str(row.get("property_path", "")).strip()
        if not object_id or not property_path:
            continue
        out.setdefault(object_id, {}).setdefault(property_path, []).append(dict(row))
    return {
        object_id: {
            property_path: list(out[object_id][property_path])
            for property_path in sorted(out[object_id].keys())
        }
        for object_id in sorted(out.keys())
    }


def _merge_cache_lookup(cache_key: str) -> dict | None:
    cached = _OVERLAY_CACHE.get(str(cache_key))
    if not isinstance(cached, dict):
        return None
    return copy.deepcopy(cached)


def _merge_cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _OVERLAY_CACHE[str(cache_key)] = copy.deepcopy(dict(payload))
    if len(_OVERLAY_CACHE) > _OVERLAY_CACHE_MAX:
        for stale_key in sorted(_OVERLAY_CACHE.keys())[:-_OVERLAY_CACHE_MAX]:
            _OVERLAY_CACHE.pop(stale_key, None)
    return copy.deepcopy(dict(payload))


def overlay_cache_clear() -> None:
    _OVERLAY_CACHE.clear()


def overlay_cache_snapshot() -> dict:
    return dict((key, copy.deepcopy(_OVERLAY_CACHE[key])) for key in sorted(_OVERLAY_CACHE.keys()))


def merge_overlay_view(
    *,
    base_objects: object,
    overlay_manifest: Mapping[str, object],
    property_patches: object,
    resolved_packs: object = None,
    expected_pack_lock_hash: str = "",
    overlay_policy_id: str = "",
    overlay_policy_registry_payload: Mapping[str, object] | None = None,
    overlay_conflict_policy_id: str = "",
    overlay_conflict_policy_registry_payload: Mapping[str, object] | None = None,
    cache_enabled: bool = True,
) -> dict:
    validated = validate_overlay_manifest_trust(
        overlay_manifest=overlay_manifest,
        resolved_packs=resolved_packs,
        expected_pack_lock_hash=expected_pack_lock_hash,
        overlay_policy_id=overlay_policy_id,
        overlay_policy_registry_payload=overlay_policy_registry_payload,
        overlay_conflict_policy_id=overlay_conflict_policy_id,
        overlay_conflict_policy_registry_payload=overlay_conflict_policy_registry_payload,
    )
    if str(validated.get("result", "")) != "complete":
        return dict(validated)
    manifest = dict(validated.get("overlay_manifest") or {})
    normalized_base = _normalize_base_objects(base_objects)
    normalized_patches = normalize_property_patch_rows(property_patches)
    cache_key = canonical_sha256(
        {
            "base_objects": normalized_base,
            "overlay_manifest_hash": overlay_manifest_hash(manifest),
            "property_patch_hash_chain": property_patch_hash_chain(normalized_patches),
            "overlay_policy_id": str(validated.get("overlay_policy_id", "")).strip(),
            "overlay_conflict_policy_id": str(validated.get("overlay_conflict_policy_id", "")).strip(),
            "version": _OVERLAY_VERSION,
        }
    )
    cached = _merge_cache_lookup(cache_key) if cache_enabled else None
    if cached is not None:
        payload = dict(cached)
        payload["cache_hit"] = True
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    ordered_patches, layer_by_id = _ordered_patches_for_manifest(manifest, normalized_patches)
    overlay_conflict_policy_id_token = str(validated.get("overlay_conflict_policy_id", "")).strip()
    overlay_conflict_mode = str(validated.get("overlay_conflict_mode", "")).strip()
    overlay_conflict_artifacts = _detect_overlay_conflicts(
        ordered_patches,
        layer_by_id,
        conflict_mode=overlay_conflict_mode,
    )
    overlay_conflict_index = _overlay_conflict_index(overlay_conflict_artifacts)
    overlay_conflict_artifact_hash = overlay_conflict_artifact_hash_chain(overlay_conflict_artifacts)
    if overlay_conflict_artifacts and overlay_conflict_mode in {"refuse", "prompt_stub"}:
        remediation_hint = (
            "remedy.overlay.add_explicit_resolver_layer"
            if overlay_conflict_mode == "prompt_stub"
            else "remedy.overlay.resolve_conflict_or_change_policy"
        )
        refusal = {
            "result": "refused",
            "refusal_code": REFUSAL_OVERLAY_CONFLICT,
            "message": "overlay merge conflict detected under strict conflict policy",
            "details": {
                "overlay_conflict_policy_id": overlay_conflict_policy_id_token,
                "overlay_conflict_mode": overlay_conflict_mode,
                "overlay_conflict_count": len(overlay_conflict_artifacts),
            },
            "remediation_hint": remediation_hint,
            "overlay_manifest": manifest,
            "overlay_manifest_hash": overlay_manifest_hash(manifest),
            "property_patch_hash_chain": property_patch_hash_chain(normalized_patches),
            "overlay_policy_id": str(validated.get("overlay_policy_id", "")).strip(),
            "overlay_conflict_policy_id": overlay_conflict_policy_id_token,
            "overlay_conflict_mode": overlay_conflict_mode,
            "overlay_conflict_artifacts": overlay_conflict_artifacts,
            "overlay_conflict_index": overlay_conflict_index,
            "overlay_conflict_artifact_hash_chain": overlay_conflict_artifact_hash,
            "deterministic_fingerprint": "",
        }
        refusal["deterministic_fingerprint"] = canonical_sha256(dict(refusal, deterministic_fingerprint=""))
        return refusal
    object_map: Dict[str, dict] = {}
    property_history_index: Dict[Tuple[str, str], List[dict]] = {}
    base_layer_id = str(
        next(
            (
                str(row.get("layer_id", "")).strip()
                for row in normalize_overlay_layer_rows(manifest.get("layers"))
                if str(row.get("layer_kind", "")).strip() == "base"
            ),
            "base.worldgen",
        )
    )
    for row in normalized_base:
        object_id = str(row.get("object_id", "")).strip()
        if not object_id:
            continue
        object_map[object_id] = {
            "object_id": object_id,
            "object_kind_id": str(row.get("object_kind_id", "")).strip(),
            "geo_cell_key": _as_map(row.get("geo_cell_key")),
            "properties": _as_map(row.get("properties")),
            "extensions": _as_map(row.get("extensions")),
        }
        for property_path, property_value in _flatten_properties("", _as_map(row.get("properties"))):
            property_history_index.setdefault((object_id, property_path), []).append(
                {
                    "layer_id": base_layer_id,
                    "layer_kind": "base",
                    "source_ref": "base.worldgen",
                    "pack_hash": "",
                    "pack_id": "",
                    "operation": "base",
                    "value": _jsonable_value(property_value),
                    "previous_value": None,
                }
            )

    applied_patch_log: List[dict] = []
    for patch in ordered_patches:
        object_id = str(patch.get("target_object_id", "")).strip()
        layer_id = str(patch.get("originating_layer_id", "")).strip()
        layer_row = dict(layer_by_id.get(layer_id) or {})
        if not object_id or not layer_row:
            continue
        current_object = dict(object_map.get(object_id) or {})
        if not current_object and str(patch.get("operation", "")).strip() in {"set", "replace", "add"}:
            current_object = {
                "object_id": object_id,
                "object_kind_id": str(_as_map(patch.get("extensions")).get("object_kind_id", "kind.overlay.added_object")).strip()
                or "kind.overlay.added_object",
                "geo_cell_key": _as_map(_as_map(patch.get("extensions")).get("geo_cell_key")),
                "properties": {},
                "extensions": {"source_layer_id": layer_id, "source": "GEO9-3"},
            }
        if not current_object:
            continue
        property_path = str(patch.get("property_path", "")).strip()
        operation = str(patch.get("operation", "")).strip()
        found, previous_value = _get_property(_as_map(current_object.get("properties")), property_path)
        if operation == "remove":
            next_properties, removed = _remove_property(_as_map(current_object.get("properties")), property_path)
            applied_value = None
            applied = bool(removed)
        elif operation == "add":
            applied_value = _add_property_value(found, previous_value, patch.get("value"))
            next_properties = _set_property(_as_map(current_object.get("properties")), property_path, applied_value)
            applied = True
        else:
            applied_value = _jsonable_value(patch.get("value"))
            next_properties = _set_property(_as_map(current_object.get("properties")), property_path, applied_value)
            applied = True
        current_object["properties"] = next_properties
        object_map[object_id] = current_object
        history_entry = {
            "layer_id": layer_id,
            "layer_kind": str(layer_row.get("layer_kind", "")).strip(),
            "source_ref": str(layer_row.get("source_ref", "")).strip(),
            "pack_hash": str(_as_map(layer_row.get("extensions")).get("pack_hash", "")).strip(),
            "pack_id": str(_as_map(layer_row.get("extensions")).get("pack_id", "")).strip(),
            "operation": operation,
            "value": _jsonable_value(applied_value),
            "previous_value": _jsonable_value(previous_value) if found else None,
            "patch_hash": str(patch.get("deterministic_fingerprint", "")).strip(),
        }
        property_history_index.setdefault((object_id, property_path), []).append(history_entry)
        applied_patch_log.append(
            {
                "target_object_id": object_id,
                "property_path": property_path,
                "operation": operation,
                "originating_layer_id": layer_id,
                "layer_kind": str(layer_row.get("layer_kind", "")).strip(),
                "source_ref": str(layer_row.get("source_ref", "")).strip(),
                "patch_hash": str(patch.get("deterministic_fingerprint", "")).strip(),
                "previous_value": _jsonable_value(previous_value) if found else None,
                "applied_value": _jsonable_value(applied_value),
                "applied": bool(applied),
            }
        )

    object_id_tokens = sorted(set([key[0] for key in property_history_index.keys()]))
    property_origin_index = {
        object_id: {
            property_path: list(property_history_index[(object_id, property_path)])
            for property_path in sorted([key[1] for key in property_history_index.keys() if key[0] == object_id])
        }
        for object_id in object_id_tokens
    }
    effective_object_views = normalize_effective_object_view_rows(
        [
            build_effective_object_view(
                object_id=str(row.get("object_id", "")).strip(),
                object_kind_id=str(row.get("object_kind_id", "")).strip(),
                properties=_as_map(row.get("properties")),
                geo_cell_key=_as_map(row.get("geo_cell_key")),
                extensions=_as_map(row.get("extensions")),
            )
            for row in sorted(object_map.values(), key=lambda item: str(item.get("object_id", "")))
        ]
    )
    result = {
        "result": "complete",
        "cache_hit": False,
        "overlay_manifest": manifest,
        "effective_object_views": effective_object_views,
        "applied_patch_log": sorted(
            applied_patch_log,
            key=lambda row: (
                str(row.get("originating_layer_id", "")),
                str(row.get("property_path", "")),
                str(row.get("target_object_id", "")),
                str(row.get("patch_hash", "")),
            ),
        ),
        "property_origin_index": property_origin_index,
        "overlay_manifest_hash": overlay_manifest_hash(manifest),
        "property_patch_hash_chain": property_patch_hash_chain(normalized_patches),
        "overlay_merge_result_hash_chain": overlay_effective_object_hash_chain(effective_object_views),
        "overlay_policy_id": str(validated.get("overlay_policy_id", "")).strip(),
        "overlay_conflict_policy_id": overlay_conflict_policy_id_token,
        "overlay_conflict_mode": overlay_conflict_mode,
        "overlay_conflict_artifacts": overlay_conflict_artifacts,
        "overlay_conflict_index": overlay_conflict_index,
        "overlay_conflict_artifact_hash_chain": overlay_conflict_artifact_hash,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return _merge_cache_store(cache_key, result) if cache_enabled else result


def explain_property_origin(
    *,
    merge_result: Mapping[str, object],
    object_id: str,
    property_path: str,
) -> dict:
    payload = _as_map(merge_result)
    object_token = str(object_id or "").strip()
    property_token = str(property_path or "").strip()
    origin_index = {
        str(key): _as_map(value)
        for key, value in sorted(_as_map(payload.get("property_origin_index")).items(), key=lambda item: str(item[0]))
    }
    conflict_index = {
        str(key): _as_map(value)
        for key, value in sorted(_as_map(payload.get("overlay_conflict_index")).items(), key=lambda item: str(item[0]))
    }
    history = _as_list(_as_map(origin_index.get(object_token)).get(property_token))
    conflicts = _as_list(_as_map(conflict_index.get(object_token)).get(property_token))
    if not history:
        return _refusal(
            "property origin is unknown for the requested object/property path",
            {"object_id": object_token, "property_path": property_token},
            refusal_code="refusal.geo.overlay_property_origin_missing",
        )
    current = dict(history[-1]) if history else {}
    report = {
        "result": "complete",
        "object_id": object_token,
        "property_path": property_token,
        "current_layer_id": str(current.get("layer_id", "")).strip(),
        "current_source_ref": str(current.get("source_ref", "")).strip(),
        "current_pack_hash": str(current.get("pack_hash", "")).strip(),
        "current_pack_id": str(current.get("pack_id", "")).strip(),
        "current_value": _jsonable_value(current.get("value")),
        "prior_value_chain": [dict(item) for item in history],
        "overlay_conflict_policy_id": str(payload.get("overlay_conflict_policy_id", "")).strip(),
        "overlay_conflict_mode": str(payload.get("overlay_conflict_mode", "")).strip(),
        "overlay_conflict_count": len(conflicts),
        "overlay_conflicts": [dict(item) for item in conflicts],
        "conflict_note": (
            "explain.overlay_conflict"
            if conflicts and str(payload.get("overlay_conflict_mode", "")).strip() in {"last_wins", "refuse", "prompt_stub"}
            else ""
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def overlay_proof_surface(
    *,
    overlay_manifest: Mapping[str, object] | None,
    property_patches: object,
    effective_object_views: object = None,
    overlay_conflict_artifacts: object = None,
) -> dict:
    payload = {
        "overlay_manifest_hash": overlay_manifest_hash(overlay_manifest) if overlay_manifest else "",
        "property_patch_hash_chain": property_patch_hash_chain(property_patches),
        "overlay_merge_result_hash_chain": overlay_effective_object_hash_chain(effective_object_views or []),
        "overlay_conflict_artifact_hash_chain": overlay_conflict_artifact_hash_chain(overlay_conflict_artifacts or []),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "REFUSAL_GEO_OVERLAY_INVALID",
    "REFUSAL_OVERLAY_CONFLICT",
    "build_default_overlay_manifest",
    "build_effective_object_view",
    "build_overlay_conflict_artifact",
    "build_overlay_layer",
    "build_overlay_manifest",
    "build_property_patch",
    "explain_property_origin",
    "merge_overlay_view",
    "normalize_effective_object_view_rows",
    "normalize_overlay_conflict_artifact_rows",
    "normalize_overlay_layer",
    "normalize_overlay_layer_rows",
    "normalize_overlay_manifest",
    "normalize_property_patch",
    "normalize_property_patch_rows",
    "overlay_base_objects_from_worldgen_result",
    "overlay_cache_clear",
    "overlay_cache_snapshot",
    "overlay_conflict_artifact_hash_chain",
    "overlay_conflict_policy_registry_hash",
    "overlay_conflict_policy_rows_by_id",
    "overlay_effective_object_hash_chain",
    "overlay_manifest_hash",
    "overlay_policy_registry_hash",
    "overlay_policy_rows_by_id",
    "overlay_proof_surface",
    "property_patch_hash_chain",
    "validate_overlay_manifest_trust",
]
