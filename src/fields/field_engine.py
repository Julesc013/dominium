"""Deterministic FIELD-1 / GEO-4 field layer engine."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from src.geo import (
    field_sampling_cell_key,
    field_sampling_position,
    geo_cell_key_from_position,
    geo_distance,
    geo_neighbors,
    geo_partition_cell_key,
)
from src.models.model_engine import evaluate_field_modifier_curve
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_RESOLUTION_LEVELS = {"macro", "meso", "micro"}
_VALID_FIELD_VALUE_KINDS = {"scalar", "vector"}
_VALID_FIELD_TIERS = {"F0", "F1", "F2"}
_LEGACY_POLICY_TO_CANONICAL = {
    "field.static": "field.static_default",
    "field.scheduled": "field.scheduled_linear",
}
_CANONICAL_POLICY_TO_LEGACY = dict((value, key) for key, value in _LEGACY_POLICY_TO_CANONICAL.items())
_DEFAULT_FIELD_DIMENSION_VECTOR = {"M": 0, "L": 0, "T": 0, "Q": 0, "THETA": 0, "I": 0}
_DEFAULT_TOPOLOGY_PROFILE_ID = "geo.topology.r3_infinite"
_DEFAULT_PARTITION_PROFILE_ID = "geo.partition.grid_zd"
_DEFAULT_INTERPOLATION_POLICY_ID = "interp.nearest"
_DEFAULT_FIELD_CHART_ID = "chart.global"


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_bool(value: object, default_value: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    token = str(value or "").strip().lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return bool(default_value)


def _sorted_unique_strings(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _normalize_resolution_level(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_RESOLUTION_LEVELS:
        return token
    return "macro"


def _normalize_value_kind(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_FIELD_VALUE_KINDS:
        return token
    return "scalar"


def _normalize_field_tier(value: object) -> str:
    token = str(value or "").strip().upper()
    if token in _VALID_FIELD_TIERS:
        return token
    return "F0"


def _canonical_update_policy_id(value: object) -> str:
    token = str(value or "").strip()
    if not token:
        return "field.static_default"
    return str(_LEGACY_POLICY_TO_CANONICAL.get(token, token)).strip() or "field.static_default"


def _normalize_dimension_vector(value: object) -> dict:
    payload = _as_map(value)
    merged = dict(_DEFAULT_FIELD_DIMENSION_VECTOR)
    for axis in list(_DEFAULT_FIELD_DIMENSION_VECTOR.keys()):
        merged[axis] = int(_as_int(payload.get(axis, merged[axis]), merged[axis]))
    # Preserve any custom declared dimensions while staying deterministic.
    for key in sorted(str(token).strip() for token in payload.keys() if str(token).strip()):
        if key in merged:
            continue
        merged[key] = int(_as_int(payload.get(key, 0), 0))
    return merged


def _vector3(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


def _normalize_cell_value(value: object, *, value_kind: str):
    kind = _normalize_value_kind(value_kind)
    if kind == "vector":
        return _vector3(value)
    if isinstance(value, bool):
        return 1 if value else 0
    return int(_as_int(value, 0))


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def _normalize_geo_chart_id(chart_id: object, topology_profile_id: object) -> str:
    chart_token = str(chart_id or "").strip() or _DEFAULT_FIELD_CHART_ID
    topology_token = str(topology_profile_id or "").strip().lower()
    if chart_token != _DEFAULT_FIELD_CHART_ID:
        return chart_token
    if ".r1" in topology_token:
        return "chart.global.r1"
    if ".r2" in topology_token:
        return "chart.global.r2"
    if ".r3" in topology_token:
        return "chart.global.r3"
    if ".r4" in topology_token:
        return "chart.global.r4"
    return chart_token


def field_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("field_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("field_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("field_id", "")).strip() or str(item.get("field_type_id", "")).strip(),
            str(item.get("field_type_id", "")).strip(),
        ),
    ):
        field_id = str(row.get("field_id", "")).strip() or str(row.get("field_type_id", "")).strip()
        if not field_id:
            continue
        update_policy_id = str(row.get("update_policy_id", "")).strip()
        if not update_policy_id:
            update_policy_id = (
                str((dict(row.get("extensions") or {})).get("update_policy_id", "")).strip()
                or "field.static_default"
            )
        normalized_row = {
            "schema_version": "1.0.0",
            "field_id": field_id,
            "field_type_id": str(row.get("field_type_id", "")).strip() or field_id,
            "description": str(row.get("description", "")).strip(),
            "value_kind": _normalize_value_kind(row.get("value_kind")),
            "dimension_vector": _normalize_dimension_vector(row.get("dimension_vector")),
            "default_value": _canon(row.get("default_value")),
            "update_policy_id": _canonical_update_policy_id(update_policy_id),
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        out[field_id] = normalized_row
        field_type_id = str(normalized_row.get("field_type_id", "")).strip()
        if field_type_id and field_type_id not in out:
            out[field_type_id] = dict(normalized_row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def field_binding_rows_by_field_id(registry_payload: Mapping[str, object] | None) -> Dict[str, List[dict]]:
    payload = _as_map(registry_payload)
    record = _as_map(payload.get("record"))
    rows = record.get("field_bindings")
    if not isinstance(rows, list):
        rows = payload.get("field_bindings")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, List[dict]] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("field_id", "")).strip(),
            str(item.get("topology_profile_id", "")).strip(),
            str(item.get("partition_profile_id", "")).strip(),
        ),
    ):
        field_id = str(row.get("field_id", "")).strip()
        if not field_id:
            continue
        normalized = {
            "schema_version": "1.0.0",
            "field_id": field_id,
            "topology_profile_id": str(row.get("topology_profile_id", _DEFAULT_TOPOLOGY_PROFILE_ID)).strip()
            or _DEFAULT_TOPOLOGY_PROFILE_ID,
            "partition_profile_id": str(row.get("partition_profile_id", _DEFAULT_PARTITION_PROFILE_ID)).strip()
            or _DEFAULT_PARTITION_PROFILE_ID,
            "storage_kind": str(row.get("storage_kind", "cell")).strip() or "cell",
            "interpolation_policy_id": str(row.get("interpolation_policy_id", _DEFAULT_INTERPOLATION_POLICY_ID)).strip()
            or _DEFAULT_INTERPOLATION_POLICY_ID,
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        out.setdefault(field_id, []).append(normalized)
    return dict(
        (
            key,
            [dict(item) for item in sorted(out.get(key, []), key=lambda row: (str(row.get("topology_profile_id", "")), str(row.get("partition_profile_id", ""))))],
        )
        for key in sorted(out.keys())
    )


def interpolation_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    record = _as_map(payload.get("record"))
    rows = record.get("interpolation_policies")
    if not isinstance(rows, list):
        rows = payload.get("interpolation_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "kind": str(row.get("kind", "nearest")).strip() or "nearest",
            "deterministic_fingerprint": str(row.get("deterministic_fingerprint", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    if _DEFAULT_INTERPOLATION_POLICY_ID not in out:
        out[_DEFAULT_INTERPOLATION_POLICY_ID] = {
            "schema_version": "1.0.0",
            "policy_id": _DEFAULT_INTERPOLATION_POLICY_ID,
            "kind": "nearest",
            "deterministic_fingerprint": "",
            "extensions": {"source": "default"},
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _field_binding_row(
    *,
    layer_row: Mapping[str, object],
    field_binding_registry: Mapping[str, object] | None = None,
) -> dict:
    layer = dict(layer_row or {})
    ext = _as_map(layer.get("extensions"))
    layer_field_id = str(layer.get("field_id", "")).strip()
    field_type_id = str(layer.get("field_type_id", "")).strip() or layer_field_id
    topology_token = str(ext.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    partition_token = str(ext.get("partition_profile_id", "")).strip() or _DEFAULT_PARTITION_PROFILE_ID
    storage_kind = str(ext.get("storage_kind", "")).strip() or "cell"
    interpolation_policy_id = str(ext.get("interpolation_policy_id", "")).strip() or _DEFAULT_INTERPOLATION_POLICY_ID
    bindings_by_field = field_binding_rows_by_field_id(field_binding_registry)
    candidates = list(bindings_by_field.get(layer_field_id) or []) + list(bindings_by_field.get(field_type_id) or [])
    selected = {}
    for row in list(candidates or []):
        key = "{}::{}::{}".format(
            str(row.get("field_id", "")).strip(),
            str(row.get("topology_profile_id", "")).strip(),
            str(row.get("partition_profile_id", "")).strip(),
        )
        selected[key] = dict(row)
    ordered = [dict(selected[key]) for key in sorted(selected.keys())]
    exact = next(
        (
            dict(row)
            for row in ordered
            if str(row.get("topology_profile_id", "")).strip() == topology_token
            and str(row.get("partition_profile_id", "")).strip() == partition_token
        ),
        {},
    )
    if not exact:
        exact = next(
            (
                dict(row)
                for row in ordered
                if str(row.get("topology_profile_id", "")).strip() == topology_token
            ),
            {},
        )
    row = dict(exact or {})
    out = {
        "field_id": str(row.get("field_id", layer_field_id or field_type_id)).strip() or layer_field_id or field_type_id,
        "topology_profile_id": str(row.get("topology_profile_id", topology_token)).strip() or topology_token,
        "partition_profile_id": str(row.get("partition_profile_id", partition_token)).strip() or partition_token,
        "storage_kind": str(row.get("storage_kind", storage_kind)).strip() or storage_kind,
        "interpolation_policy_id": str(row.get("interpolation_policy_id", interpolation_policy_id)).strip()
        or interpolation_policy_id,
        "extensions": {
            **_as_map(row.get("extensions")),
            **ext,
        },
    }
    out["extensions"]["chart_id"] = _normalize_geo_chart_id(
        _as_map(out.get("extensions")).get("chart_id", _DEFAULT_FIELD_CHART_ID),
        out.get("topology_profile_id", topology_token),
    )
    return out


def field_update_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("policy_id", "")).strip() or str(item.get("update_policy_id", "")).strip(),
            str(item.get("update_policy_id", "")).strip(),
        ),
    ):
        policy_id = str(row.get("policy_id", "")).strip() or str(row.get("update_policy_id", "")).strip()
        if not policy_id:
            continue
        canonical_policy_id = _canonical_update_policy_id(policy_id)
        deterministic_function_id = str(row.get("deterministic_function_id", "")).strip()
        if not deterministic_function_id:
            deterministic_function_id = (
                str((dict(row.get("extensions") or {})).get("deterministic_function_id", "")).strip()
                or "deterministic.identity"
            )
        normalized_row = {
            "schema_version": "1.0.0",
            "update_policy_id": policy_id,
            "policy_id": canonical_policy_id,
            "description": str(row.get("description", "")).strip(),
            "schedule_id": None if row.get("schedule_id") is None else str(row.get("schedule_id", "")).strip() or None,
            "update_schedule_id": None
            if row.get("update_schedule_id") is None
            else str(row.get("update_schedule_id", "")).strip() or None,
            "flow_channel_ref": None
            if row.get("flow_channel_ref") is None
            else str(row.get("flow_channel_ref", "")).strip() or None,
            "hazard_ref": None if row.get("hazard_ref") is None else str(row.get("hazard_ref", "")).strip() or None,
            "tier": _normalize_field_tier(row.get("tier")),
            "deterministic_function_id": deterministic_function_id,
            "uses_rng_stream": bool(_as_bool(row.get("uses_rng_stream", False), False)),
            "rng_stream_name": None
            if row.get("rng_stream_name") in {None, ""}
            else str(row.get("rng_stream_name", "")).strip() or None,
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        out[policy_id] = normalized_row
        out[canonical_policy_id] = dict(normalized_row, update_policy_id=canonical_policy_id, policy_id=canonical_policy_id)
        legacy_alias = _CANONICAL_POLICY_TO_LEGACY.get(canonical_policy_id)
        if legacy_alias:
            out[legacy_alias] = dict(normalized_row, update_policy_id=legacy_alias, policy_id=canonical_policy_id)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def build_field_layer(
    *,
    field_id: str,
    field_type_id: str,
    spatial_scope_id: str,
    resolution_level: str,
    update_policy_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    normalized_policy_id = str(update_policy_id).strip() or "field.static_default"
    payload = {
        "schema_version": "1.0.0",
        "field_id": str(field_id).strip(),
        "field_type_id": str(field_type_id).strip(),
        "spatial_scope_id": str(spatial_scope_id).strip(),
        "resolution_level": _normalize_resolution_level(resolution_level),
        "update_policy_id": normalized_policy_id,
        "deterministic_fingerprint": "",
        "extensions": _canon(dict(extensions or {})),
    }
    return _with_fingerprint(payload)


def _coerce_geo_cell_key(value: object) -> dict:
    payload = _as_map(value)
    partition_profile_id = str(payload.get("partition_profile_id", "")).strip()
    topology_profile_id = str(payload.get("topology_profile_id", "")).strip()
    chart_id = _normalize_geo_chart_id(payload.get("chart_id", ""), topology_profile_id)
    index_tuple = payload.get("index_tuple")
    if (
        (not partition_profile_id)
        or (not topology_profile_id)
        or (not chart_id)
        or (not isinstance(index_tuple, list))
        or (not index_tuple)
    ):
        return {}
    row = {
        "schema_version": "1.0.0",
        "partition_profile_id": partition_profile_id,
        "topology_profile_id": topology_profile_id,
        "chart_id": chart_id,
        "index_tuple": [int(_as_int(item, 0)) for item in list(index_tuple)],
        "refinement_level": int(max(0, _as_int(payload.get("refinement_level", 0), 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(payload.get("extensions"))),
    }
    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
    return row


def _semantic_geo_cell_key(value: object) -> dict:
    row = _coerce_geo_cell_key(value)
    if not row:
        return {}
    return {
        "schema_version": "1.0.0",
        "partition_profile_id": str(row.get("partition_profile_id", "")).strip(),
        "topology_profile_id": str(row.get("topology_profile_id", "")).strip(),
        "chart_id": str(row.get("chart_id", "")).strip(),
        "index_tuple": [int(_as_int(item, 0)) for item in list(row.get("index_tuple") or [])],
        "refinement_level": int(max(0, _as_int(row.get("refinement_level", 0), 0))),
    }


def _geo_cell_key_hash(value: object) -> str:
    payload = _semantic_geo_cell_key(value)
    if not payload:
        return ""
    return canonical_sha256(payload)


def _legacy_cell_alias_from_geo_cell_key(value: object) -> str:
    row = _coerce_geo_cell_key(value)
    if not row:
        return ""
    ext = _as_map(row.get("extensions"))
    alias = str(ext.get("legacy_cell_alias", "")).strip()
    if alias:
        return alias
    chart_id = str(row.get("chart_id", "")).strip()
    index_tuple = [int(_as_int(item, 0)) for item in list(row.get("index_tuple") or [])]
    if chart_id and ("atlas" in chart_id or "north" in chart_id or "south" in chart_id):
        chart_token = "north" if "north" in chart_id else "south" if "south" in chart_id else chart_id.replace(".", "_")
        u_idx = int(index_tuple[0] if len(index_tuple) > 0 else 0)
        v_idx = int(index_tuple[1] if len(index_tuple) > 1 else 0)
        return "atlas.{}.{}.{}".format(chart_token, u_idx, v_idx)
    if index_tuple:
        return "cell.{}".format(".".join(str(int(value)) for value in index_tuple))
    return ""


def _geo_cell_key_sort_tuple(value: object) -> Tuple[str, Tuple[int, ...], int]:
    row = _coerce_geo_cell_key(value)
    if not row:
        return ("", tuple(), 0)
    return (
        str(row.get("chart_id", "")).strip(),
        tuple(int(_as_int(item, 0)) for item in list(row.get("index_tuple") or [])),
        int(max(0, _as_int(row.get("refinement_level", 0), 0))),
    )


def _field_lookup_key(*, field_id: str, cell_id: str = "", geo_cell_key: object = None) -> str:
    geo_hash = _geo_cell_key_hash(geo_cell_key)
    if geo_hash:
        return "{}::geo::{}".format(str(field_id).strip(), geo_hash)
    return "{}::alias::{}".format(str(field_id).strip(), str(cell_id).strip())


def _field_cell_sort_key(row: Mapping[str, object]) -> Tuple[str, int, str, Tuple[int, ...], int, str]:
    field_id = str(row.get("field_id", "")).strip()
    geo_cell_key = _coerce_geo_cell_key(_as_map(_as_map(row.get("extensions")).get("geo_cell_key")))
    if geo_cell_key:
        chart_id, index_tuple, refinement_level = _geo_cell_key_sort_tuple(geo_cell_key)
        return (field_id, 0, chart_id, index_tuple, refinement_level, str(row.get("cell_id", "")).strip())
    return (field_id, 1, "", tuple(), 0, str(row.get("cell_id", "")).strip())


def _legacy_geo_cell_key_from_alias(
    *,
    cell_id: str,
    topology_profile_id: str,
    partition_profile_id: str,
    chart_id: str,
) -> dict:
    token = str(cell_id or "").strip()
    if not token:
        return {}
    if token.startswith("cell."):
        parts = token.split(".")[1:]
        try:
            index_tuple = [int(part) for part in parts]
        except ValueError:
            return {}
        row = {
            "partition_profile_id": str(partition_profile_id or _DEFAULT_PARTITION_PROFILE_ID).strip()
            or _DEFAULT_PARTITION_PROFILE_ID,
            "topology_profile_id": str(topology_profile_id or _DEFAULT_TOPOLOGY_PROFILE_ID).strip()
            or _DEFAULT_TOPOLOGY_PROFILE_ID,
            "chart_id": str(chart_id or _DEFAULT_FIELD_CHART_ID).strip() or _DEFAULT_FIELD_CHART_ID,
            "index_tuple": index_tuple,
            "refinement_level": 0,
            "extensions": {"legacy_cell_alias": token},
        }
        return _coerce_geo_cell_key(row)
    if token.startswith("atlas."):
        parts = token.split(".")
        if len(parts) != 4:
            return {}
        try:
            chart_token = str(parts[1]).strip()
            index_tuple = [int(parts[2]), int(parts[3])]
        except ValueError:
            return {}
        row = {
            "partition_profile_id": str(partition_profile_id or "geo.partition.atlas_tiles").strip() or "geo.partition.atlas_tiles",
            "topology_profile_id": str(topology_profile_id or _DEFAULT_TOPOLOGY_PROFILE_ID).strip()
            or _DEFAULT_TOPOLOGY_PROFILE_ID,
            "chart_id": "chart.atlas.{}".format(chart_token) if not chart_token.startswith("chart.") else chart_token,
            "index_tuple": index_tuple,
            "refinement_level": 0,
            "extensions": {"legacy_cell_alias": token},
        }
        return _coerce_geo_cell_key(row)
    return {}


def normalize_field_layer_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("field_id", ""))):
        field_id = str(row.get("field_id", "")).strip()
        field_type_id = str(row.get("field_type_id", "")).strip()
        spatial_scope_id = str(row.get("spatial_scope_id", "")).strip()
        if (not field_id) or (not field_type_id) or (not spatial_scope_id):
            continue
        out[field_id] = build_field_layer(
            field_id=field_id,
            field_type_id=field_type_id,
            spatial_scope_id=spatial_scope_id,
            resolution_level=str(row.get("resolution_level", "macro")).strip(),
            update_policy_id=str(
                row.get(
                    "update_policy_id",
                    row.get("policy_id", "field.static_default"),
                )
            ).strip(),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def build_field_cell(
    *,
    field_id: str,
    cell_id: str = "",
    value: object,
    last_updated_tick: int,
    value_kind: str = "scalar",
    geo_cell_key: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    normalized_geo_cell_key = _coerce_geo_cell_key(geo_cell_key)
    alias = str(cell_id).strip() or _legacy_cell_alias_from_geo_cell_key(normalized_geo_cell_key)
    ext = _as_map(extensions)
    if normalized_geo_cell_key:
        ext["geo_cell_key"] = dict(normalized_geo_cell_key)
        ext["legacy_cell_alias"] = alias
    payload = {
        "schema_version": "1.0.0",
        "field_id": str(field_id).strip(),
        "cell_id": alias,
        "value": _normalize_cell_value(value, value_kind=_normalize_value_kind(value_kind)),
        "last_updated_tick": int(max(0, _as_int(last_updated_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(ext),
    }
    return _with_fingerprint(payload)


def _field_cell_geo_cell_key(row: Mapping[str, object] | None) -> dict:
    return _coerce_geo_cell_key(_as_map(_as_map(row).get("extensions")).get("geo_cell_key"))


def _field_sample_geo_cell_key(row: Mapping[str, object] | None) -> dict:
    return _coerce_geo_cell_key(_as_map(_as_map(row).get("extensions")).get("geo_cell_key"))


def _field_geo_cell_key_for_alias(
    *,
    layer_row: Mapping[str, object],
    cell_id: str,
    field_binding_registry: Mapping[str, object] | None = None,
) -> dict:
    binding_row = _field_binding_row(layer_row=layer_row, field_binding_registry=field_binding_registry)
    chart_id = str(_as_map(binding_row.get("extensions")).get("chart_id", "")).strip() or _DEFAULT_FIELD_CHART_ID
    return _legacy_geo_cell_key_from_alias(
        cell_id=str(cell_id).strip(),
        topology_profile_id=str(binding_row.get("topology_profile_id", _DEFAULT_TOPOLOGY_PROFILE_ID)).strip()
        or _DEFAULT_TOPOLOGY_PROFILE_ID,
        partition_profile_id=str(binding_row.get("partition_profile_id", _DEFAULT_PARTITION_PROFILE_ID)).strip()
        or _DEFAULT_PARTITION_PROFILE_ID,
        chart_id=chart_id,
    )


def normalize_field_cell_rows(
    rows: object,
    *,
    field_layer_rows: object = None,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    layer_rows = normalize_field_layer_rows(field_layer_rows)
    layer_by_field_id = dict((str(row.get("field_id", "")).strip(), dict(row)) for row in layer_rows)
    field_type_rows = field_type_rows_by_id(field_type_registry)
    value_kind_by_field_id: Dict[str, str] = {}
    for field_id, layer_row in layer_by_field_id.items():
        field_type_id = str(layer_row.get("field_type_id", "")).strip()
        value_kind = _normalize_value_kind((dict(field_type_rows.get(field_type_id) or {})).get("value_kind"))
        value_kind_by_field_id[field_id] = value_kind

    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (str(item.get("field_id", "")), str(item.get("cell_id", ""))),
    ):
        field_id = str(row.get("field_id", "")).strip()
        cell_id = str(row.get("cell_id", "")).strip()
        ext = _as_map(row.get("extensions"))
        geo_cell_key = _coerce_geo_cell_key(ext.get("geo_cell_key"))
        if (not field_id) or ((not cell_id) and (not geo_cell_key)):
            continue
        value_kind = str(value_kind_by_field_id.get(field_id, "scalar"))
        layer_row = dict(layer_by_field_id.get(field_id) or {})
        if not geo_cell_key:
            geo_cell_key = _field_geo_cell_key_for_alias(
                layer_row=layer_row,
                cell_id=cell_id,
                field_binding_registry=field_binding_registry,
            )
        canonical_cell_id = str(cell_id).strip() or _legacy_cell_alias_from_geo_cell_key(geo_cell_key)
        key = _field_lookup_key(field_id=field_id, cell_id=cell_id, geo_cell_key=geo_cell_key)
        out[key] = build_field_cell(
            field_id=field_id,
            cell_id=canonical_cell_id,
            value=row.get("value"),
            last_updated_tick=_as_int(row.get("last_updated_tick", 0), 0),
            value_kind=value_kind,
            geo_cell_key=geo_cell_key,
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(row) for row in sorted((dict(item) for item in out.values()), key=_field_cell_sort_key)]


def _field_geo_cell_key_for_position(
    *,
    layer_row: Mapping[str, object],
    spatial_position: Mapping[str, object] | None,
    field_binding_registry: Mapping[str, object] | None = None,
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    payload = _as_map(spatial_position)
    explicit_geo_cell_key = _coerce_geo_cell_key(payload.get("geo_cell_key") or payload.get("cell_key"))
    if explicit_geo_cell_key:
        return explicit_geo_cell_key
    explicit = str(payload.get("cell_id", "")).strip()
    binding_row = _field_binding_row(layer_row=layer_row, field_binding_registry=field_binding_registry)
    if explicit:
        explicit_geo = _field_geo_cell_key_for_alias(
            layer_row=layer_row,
            cell_id=explicit,
            field_binding_registry=field_binding_registry,
        )
        if explicit_geo:
            return explicit_geo
    if not payload:
        return {}
    chart_id = str(payload.get("chart_id", "")).strip() or str(_as_map(binding_row.get("extensions")).get("chart_id", "")).strip()
    if not chart_id:
        chart_id = _DEFAULT_FIELD_CHART_ID
    cell_payload = geo_cell_key_from_position(
        payload,
        str(binding_row.get("topology_profile_id", _DEFAULT_TOPOLOGY_PROFILE_ID)).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID,
        str(binding_row.get("partition_profile_id", _DEFAULT_PARTITION_PROFILE_ID)).strip() or _DEFAULT_PARTITION_PROFILE_ID,
        chart_id,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if str(cell_payload.get("result", "")).strip() == "complete":
        return _coerce_geo_cell_key(cell_payload.get("cell_key"))
    return {}


def _field_cell_id_for_position(
    *,
    layer_row: Mapping[str, object],
    spatial_position: Mapping[str, object] | None,
    field_binding_registry: Mapping[str, object] | None = None,
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> str:
    payload = _as_map(spatial_position)
    explicit = str(payload.get("cell_id", "")).strip()
    if explicit:
        return explicit
    geo_cell_key = _field_geo_cell_key_for_position(
        layer_row=layer_row,
        spatial_position=spatial_position,
        field_binding_registry=field_binding_registry,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if geo_cell_key:
        return _legacy_cell_alias_from_geo_cell_key(geo_cell_key)
    layer_ext = _as_map(layer_row.get("extensions"))
    partition_result = geo_partition_cell_key(
        payload,
        str(layer_ext.get("partition_profile_id", _DEFAULT_PARTITION_PROFILE_ID)).strip() or _DEFAULT_PARTITION_PROFILE_ID,
        topology_profile_id=str(layer_ext.get("topology_profile_id", _DEFAULT_TOPOLOGY_PROFILE_ID)).strip()
        or _DEFAULT_TOPOLOGY_PROFILE_ID,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    return str(partition_result.get("cell_key", "")).strip()


def geo_field_sample_position(
    position_ref: Mapping[str, object] | None,
    target_frame_id: str,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    return field_sampling_position(
        position_ref,
        target_frame_id,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
    )


def geo_field_sample_cell_key(
    position_ref: Mapping[str, object] | None,
    target_frame_id: str,
    partition_profile_id: str,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    return field_sampling_cell_key(
        position_ref,
        target_frame_id,
        partition_profile_id,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )


def geo_field_distance_mm(
    pos_a: Mapping[str, object] | None,
    pos_b: Mapping[str, object] | None,
    *,
    topology_profile_id: str = "geo.topology.r3_infinite",
    metric_profile_id: str = "geo.metric.euclidean",
) -> dict:
    return geo_distance(
        pos_a,
        pos_b,
        topology_profile_id=topology_profile_id,
        metric_profile_id=metric_profile_id,
    )


def _default_value_for_field(
    *,
    field_id: str,
    layer_by_field_id: Mapping[str, dict],
    field_type_rows: Mapping[str, dict],
):
    layer_row = dict(layer_by_field_id.get(field_id) or {})
    layer_ext = _as_map(layer_row.get("extensions"))
    field_type_id = str(layer_row.get("field_type_id", "")).strip()
    field_type_row = dict(field_type_rows.get(field_type_id) or {})
    default_value = layer_ext.get("default_value", field_type_row.get("default_value"))
    value_kind = _normalize_value_kind(field_type_row.get("value_kind"))
    return _normalize_cell_value(default_value, value_kind=value_kind)


def get_field_value(
    *,
    spatial_position: Mapping[str, object] | None,
    field_id: str,
    field_layer_rows: object,
    field_cell_rows: object,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
    geo_cell_key: Mapping[str, object] | None = None,
    position_ref: Mapping[str, object] | None = None,
    target_frame_id: str = "",
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    tick: int | None = None,
    spatial_node_id: str | None = None,
    sample_cache: Mapping[str, object] | None = None,
) -> dict:
    field_token = str(field_id).strip()
    layers = normalize_field_layer_rows(field_layer_rows)
    layer_by_field_id = dict((str(row.get("field_id", "")).strip(), dict(row)) for row in layers)
    field_type_rows = field_type_rows_by_id(field_type_registry)
    layer_row = dict(layer_by_field_id.get(field_token) or {})
    if not layer_row:
        field_type_row = dict(field_type_rows.get(field_token) or {})
        value_kind = _normalize_value_kind(field_type_row.get("value_kind"))
        default_value = _normalize_cell_value(field_type_row.get("default_value"), value_kind=value_kind)
        if default_value in (None, {}):
            default_value = 0
        out = {
            "field_id": field_token,
            "present": False,
            "sampled_cell_id": "",
            "sampled_geo_cell_key": {},
            "value": _canon(default_value),
            "query_cost_units": 1,
            "deterministic_fingerprint": "",
        }
        out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
        return out
    binding_row = _field_binding_row(layer_row=layer_row, field_binding_registry=field_binding_registry)
    interpolation_rows = interpolation_policy_rows_by_id(interpolation_policy_registry)
    interpolation_policy_id = str(binding_row.get("interpolation_policy_id", _DEFAULT_INTERPOLATION_POLICY_ID)).strip()
    interpolation_row = dict(interpolation_rows.get(interpolation_policy_id) or interpolation_rows.get(_DEFAULT_INTERPOLATION_POLICY_ID) or {})
    sampled_geo_cell_key = _coerce_geo_cell_key(geo_cell_key)
    if (not sampled_geo_cell_key) and isinstance(position_ref, Mapping) and str(target_frame_id or "").strip():
        sample_payload = geo_field_sample_cell_key(
            position_ref,
            str(target_frame_id or "").strip(),
            str(binding_row.get("partition_profile_id", _DEFAULT_PARTITION_PROFILE_ID)).strip()
            or _DEFAULT_PARTITION_PROFILE_ID,
            frame_nodes=frame_nodes,
            frame_transform_rows=frame_transform_rows,
            graph_version=graph_version,
            topology_registry_payload=topology_registry_payload,
            partition_registry_payload=partition_registry_payload,
        )
        if str(sample_payload.get("result", "")).strip() == "complete":
            sampled_geo_cell_key = _coerce_geo_cell_key(sample_payload.get("cell_key"))
    if not sampled_geo_cell_key:
        sampled_geo_cell_key = _field_geo_cell_key_for_position(
            layer_row=layer_row,
            spatial_position=spatial_position,
            field_binding_registry=field_binding_registry,
            topology_registry_payload=topology_registry_payload,
            partition_registry_payload=partition_registry_payload,
        )
    sampled_cell_id = _legacy_cell_alias_from_geo_cell_key(sampled_geo_cell_key)
    if not sampled_cell_id:
        sampled_cell_id = _field_cell_id_for_position(
            layer_row=layer_row,
            spatial_position=spatial_position,
            field_binding_registry=field_binding_registry,
            topology_registry_payload=topology_registry_payload,
            partition_registry_payload=partition_registry_payload,
        )
    node_token = str(spatial_node_id or sampled_cell_id).strip() or sampled_cell_id
    tick_value = None if tick is None else int(max(0, _as_int(tick, 0)))
    sample_key = None
    if tick_value is not None:
        sample_key = "{}::{}::{}".format(field_token, node_token, int(tick_value))
        if isinstance(sample_cache, Mapping):
            cached_row = dict(sample_cache.get(sample_key) or {})  # type: ignore[index]
            if cached_row:
                cached_geo_cell_key = _field_sample_geo_cell_key(cached_row)
                out = {
                    "field_id": field_token,
                    "present": True,
                    "sampled_cell_id": str(cached_row.get("sampled_cell_id", sampled_cell_id)).strip() or sampled_cell_id,
                    "sampled_geo_cell_key": dict(cached_geo_cell_key),
                    "value": _canon(cached_row.get("sampled_value")),
                    "has_cell": bool(cached_row.get("has_cell", True)),
                    "interpolation_policy_id": str(interpolation_row.get("policy_id", interpolation_policy_id)).strip()
                    or interpolation_policy_id,
                    "query_cost_units": 1,
                    "deterministic_fingerprint": "",
                }
                out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
                return out
    normalized_cells = normalize_field_cell_rows(
        field_cell_rows,
        field_layer_rows=layers,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
    )
    cell_by_key = dict(
        (
            _field_lookup_key(
                field_id=str(row.get("field_id", "")).strip(),
                cell_id=str(row.get("cell_id", "")).strip(),
                geo_cell_key=_field_cell_geo_cell_key(row),
            ),
            dict(row),
        )
        for row in normalized_cells
    )
    key = _field_lookup_key(field_id=field_token, cell_id=sampled_cell_id, geo_cell_key=sampled_geo_cell_key)
    alias_key = _field_lookup_key(field_id=field_token, cell_id=sampled_cell_id)
    fallback_key = _field_lookup_key(field_id=field_token, cell_id="cell.default")
    cell_row = dict(cell_by_key.get(key) or cell_by_key.get(alias_key) or cell_by_key.get(fallback_key) or {})
    if cell_row:
        value = _canon(cell_row.get("value"))
        present = True
        sampled = str(cell_row.get("cell_id", "")).strip()
        sampled_geo_cell_key = _field_cell_geo_cell_key(cell_row) or sampled_geo_cell_key
    else:
        value = _default_value_for_field(field_id=field_token, layer_by_field_id=layer_by_field_id, field_type_rows=field_type_rows)
        present = False
        sampled = sampled_cell_id
    out = {
        "field_id": field_token,
        "present": True,
        "sampled_cell_id": sampled,
        "sampled_geo_cell_key": dict(sampled_geo_cell_key),
        "value": value,
        "has_cell": bool(present),
        "interpolation_policy_id": str(interpolation_row.get("policy_id", interpolation_policy_id)).strip() or interpolation_policy_id,
        "query_cost_units": 1,
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    if (tick_value is not None) and sample_key and isinstance(sample_cache, dict):
        sample_cache[sample_key] = build_field_sample(
            field_id=field_token,
            spatial_node_id=node_token,
            tick=int(tick_value),
            sampled_value=out.get("value"),
            has_cell=bool(out.get("has_cell", False)),
            sampled_cell_id=str(out.get("sampled_cell_id", "")).strip(),
            sampled_geo_cell_key=_as_map(out.get("sampled_geo_cell_key")),
            extensions={
                "interpolation_policy_id": str(out.get("interpolation_policy_id", interpolation_policy_id)).strip()
                or interpolation_policy_id,
            },
        )
    return out


def build_field_sample(
    *,
    field_id: str,
    spatial_node_id: str,
    tick: int,
    sampled_value: object,
    has_cell: bool = False,
    sampled_cell_id: str = "",
    sampled_geo_cell_key: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    ext = _as_map(extensions)
    normalized_geo_cell_key = _coerce_geo_cell_key(sampled_geo_cell_key)
    if normalized_geo_cell_key:
        ext["geo_cell_key"] = dict(normalized_geo_cell_key)
    payload = {
        "schema_version": "1.0.0",
        "field_id": str(field_id).strip(),
        "spatial_node_id": str(spatial_node_id).strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "sampled_value": _canon(sampled_value),
        "has_cell": bool(has_cell),
        "sampled_cell_id": str(sampled_cell_id).strip() or _legacy_cell_alias_from_geo_cell_key(normalized_geo_cell_key),
        "deterministic_fingerprint": "",
        "extensions": _canon(ext),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_field_sample_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("field_id", "")),
            str(item.get("spatial_node_id", "")),
            _as_int(item.get("tick", 0), 0),
        ),
    ):
        field_id = str(row.get("field_id", "")).strip()
        spatial_node_id = str(row.get("spatial_node_id", "")).strip()
        if (not field_id) or (not spatial_node_id):
            continue
        geo_cell_key = _field_sample_geo_cell_key(row)
        sample_row = build_field_sample(
            field_id=field_id,
            spatial_node_id=spatial_node_id,
            tick=_as_int(row.get("tick", 0), 0),
            sampled_value=row.get("sampled_value"),
            has_cell=bool(row.get("has_cell", False)),
            sampled_cell_id=str(row.get("sampled_cell_id", "")).strip(),
            sampled_geo_cell_key=geo_cell_key,
            extensions=_as_map(row.get("extensions")),
        )
        key = "{}::{}::{}".format(
            str(sample_row.get("field_id", "")).strip(),
            str(sample_row.get("spatial_node_id", "")).strip(),
            int(_as_int(sample_row.get("tick", 0), 0)),
        )
        out[key] = sample_row
    return [dict(out[key]) for key in sorted(out.keys())]


def field_get_value(
    *,
    field_id: str,
    geo_cell_key: Mapping[str, object],
    field_layer_rows: object,
    field_cell_rows: object,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
) -> dict:
    return get_field_value(
        spatial_position={"geo_cell_key": _as_map(geo_cell_key)},
        geo_cell_key=geo_cell_key,
        field_id=field_id,
        field_layer_rows=field_layer_rows,
        field_cell_rows=field_cell_rows,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
        interpolation_policy_registry=interpolation_policy_registry,
    )


def field_set_value(
    *,
    field_id: str,
    geo_cell_key: Mapping[str, object],
    value: object,
    last_updated_tick: int,
    field_layer_rows: object,
    field_type_registry: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    layers = normalize_field_layer_rows(field_layer_rows)
    layer_by_field_id = dict((str(row.get("field_id", "")).strip(), dict(row)) for row in layers)
    field_type_rows = field_type_rows_by_id(field_type_registry)
    layer_row = dict(layer_by_field_id.get(str(field_id).strip()) or {})
    field_type_id = str(layer_row.get("field_type_id", "")).strip() or str(field_id).strip()
    value_kind = _normalize_value_kind((dict(field_type_rows.get(field_type_id) or field_type_rows.get(field_id) or {})).get("value_kind"))
    return build_field_cell(
        field_id=field_id,
        cell_id=_legacy_cell_alias_from_geo_cell_key(geo_cell_key),
        value=value,
        last_updated_tick=last_updated_tick,
        value_kind=value_kind,
        geo_cell_key=geo_cell_key,
        extensions=extensions,
    )


def field_sample_position_ref(
    *,
    position_ref: Mapping[str, object] | None,
    target_frame_id: str,
    field_id: str,
    field_layer_rows: object,
    field_cell_rows: object,
    frame_nodes: object,
    frame_transform_rows: object,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    tick: int | None = None,
    spatial_node_id: str | None = None,
    sample_cache: Mapping[str, object] | None = None,
) -> dict:
    return get_field_value(
        spatial_position=None,
        position_ref=position_ref,
        target_frame_id=target_frame_id,
        field_id=field_id,
        field_layer_rows=field_layer_rows,
        field_cell_rows=field_cell_rows,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
        interpolation_policy_registry=interpolation_policy_registry,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
        tick=tick,
        spatial_node_id=spatial_node_id,
        sample_cache=sample_cache,
    )


def field_sample_neighborhood(
    *,
    field_id: str,
    center_cell_key: Mapping[str, object],
    radius: int,
    field_layer_rows: object,
    field_cell_rows: object,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
    metric_profile_id: str = "geo.metric.euclidean",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    normalized_center = _coerce_geo_cell_key(center_cell_key)
    if not normalized_center:
        return {
            "result": "refusal",
            "field_id": str(field_id).strip(),
            "samples": [],
            "reason_code": "refusal.field.geo_cell_key_required",
            "deterministic_fingerprint": canonical_sha256(
                {
                    "field_id": str(field_id).strip(),
                    "reason_code": "refusal.field.geo_cell_key_required",
                }
            ),
        }
    neighbor_payload = geo_neighbors(
        normalized_center,
        str(normalized_center.get("topology_profile_id", _DEFAULT_TOPOLOGY_PROFILE_ID)).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID,
        int(max(0, _as_int(radius, 0))),
        metric_profile_id=metric_profile_id,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
        metric_registry_payload=metric_registry_payload,
    )
    neighbor_rows = [
        _coerce_geo_cell_key(row)
        for row in list(neighbor_payload.get("neighbors") or [])
        if isinstance(row, Mapping)
    ]
    samples = [
        field_get_value(
            field_id=field_id,
            geo_cell_key=row,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
        )
        for row in sorted(neighbor_rows, key=_geo_cell_key_sort_tuple)
        if row
    ]
    out = {
        "result": "complete",
        "field_id": str(field_id).strip(),
        "center_cell_key": dict(normalized_center),
        "radius": int(max(0, _as_int(radius, 0))),
        "samples": [dict(row) for row in list(samples or [])],
        "neighbor_count": int(len(samples)),
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


def _candidate_cell_ids_for_field(
    *,
    field_id: str,
    existing_cells: Sequence[dict],
    flow_quantities: Mapping[str, object],
    hazard_states: Mapping[str, object],
) -> List[str]:
    ids = [str(row.get("cell_id", "")).strip() for row in existing_cells if str(row.get("cell_id", "")).strip()]
    for source in (flow_quantities.get(field_id), hazard_states.get(field_id)):
        if isinstance(source, Mapping):
            has_vector_axes = set(source.keys()) >= {"x", "y", "z"}
            if has_vector_axes:
                continue
            ids.extend(str(key).strip() for key in source.keys() if str(key).strip())
    if not ids:
        ids.append("cell.default")
    return sorted(set(ids))


def _source_value_for_field_cell(source: object, cell_id: str):
    if isinstance(source, Mapping):
        payload = _as_map(source)
        if set(payload.keys()) >= {"x", "y", "z"}:
            return _vector3(payload)
        if str(cell_id).strip() in payload:
            return payload.get(str(cell_id).strip())
        if "default" in payload:
            return payload.get("default")
    return source


def _clamp_scalar(value: int, layer_ext: Mapping[str, object]) -> int:
    minimum = layer_ext.get("min_value")
    maximum = layer_ext.get("max_value")
    out = int(value)
    if minimum is not None:
        out = max(out, int(_as_int(minimum, out)))
    if maximum is not None:
        out = min(out, int(_as_int(maximum, out)))
    return int(out)


def _scheduled_next_value(current_value: object, delta_value: object, *, value_kind: str):
    kind = _normalize_value_kind(value_kind)
    if kind == "vector":
        current_vec = _vector3(current_value)
        delta_vec = _vector3(delta_value)
        return {
            "x": int(current_vec.get("x", 0)) + int(delta_vec.get("x", 0)),
            "y": int(current_vec.get("y", 0)) + int(delta_vec.get("y", 0)),
            "z": int(current_vec.get("z", 0)) + int(delta_vec.get("z", 0)),
        }
    return int(_as_int(current_value, 0)) + int(_as_int(delta_value, 0))


def _priority_for_field(field_id: str, critical_field_ids: Sequence[str]) -> int:
    return 0 if str(field_id).strip() in set(_sorted_unique_strings(list(critical_field_ids or []))) else 1


def update_field_layers(
    *,
    current_tick: int,
    field_layer_rows: object,
    field_cell_rows: object,
    field_update_policy_registry: Mapping[str, object] | None = None,
    field_type_registry: Mapping[str, object] | None = None,
    field_binding_registry: Mapping[str, object] | None = None,
    flow_quantities: Mapping[str, object] | None = None,
    hazard_states: Mapping[str, object] | None = None,
    max_cost_units: int = 0,
    cost_units_per_cell: int = 1,
    critical_field_ids: Sequence[str] | None = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    layers = normalize_field_layer_rows(field_layer_rows)
    field_type_rows = field_type_rows_by_id(field_type_registry)
    policy_rows = field_update_policy_rows_by_id(field_update_policy_registry)
    flow_payload = _as_map(flow_quantities)
    hazard_payload = _as_map(hazard_states)
    normalized_cells = normalize_field_cell_rows(
        field_cell_rows,
        field_layer_rows=layers,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
    )

    layer_by_field_id = dict((str(row.get("field_id", "")).strip(), dict(row)) for row in layers)
    cells_by_field_id: Dict[str, List[dict]] = {}
    for row in normalized_cells:
        field_id = str(row.get("field_id", "")).strip()
        if not field_id:
            continue
        cells_by_field_id.setdefault(field_id, []).append(dict(row))
    for field_id in sorted(cells_by_field_id.keys()):
        cells_by_field_id[field_id] = sorted(
            (dict(item) for item in cells_by_field_id[field_id]),
            key=_field_cell_sort_key,
        )

    default_critical = ["field.friction", "field.visibility", "field.temperature"]
    critical_ids = _sorted_unique_strings(list(critical_field_ids or default_critical))
    unit_cost = int(max(1, _as_int(cost_units_per_cell, 1)))
    budget = int(max(0, _as_int(max_cost_units, 0)))

    update_ops: List[dict] = []
    for field_id in sorted(layer_by_field_id.keys()):
        layer_row = dict(layer_by_field_id.get(field_id) or {})
        policy_id = str(layer_row.get("update_policy_id", "field.static")).strip() or "field.static"
        policy_row = dict(policy_rows.get(policy_id) or {})
        policy_mode = "static"
        canonical_policy_id = _canonical_update_policy_id(policy_id)
        if canonical_policy_id == "field.scheduled_linear":
            policy_mode = "scheduled"
        elif policy_id == "field.flow_linked":
            policy_mode = "flow_linked"
        elif policy_id == "field.hazard_linked":
            policy_mode = "hazard_linked"
        elif str(policy_row.get("update_schedule_id", "")).strip() or str(policy_row.get("schedule_id", "")).strip():
            policy_mode = "scheduled"
        elif str(policy_row.get("flow_channel_ref", "")).strip():
            policy_mode = "flow_linked"
        elif str(policy_row.get("hazard_ref", "")).strip():
            policy_mode = "hazard_linked"
        elif canonical_policy_id == "field.profile_defined":
            profile_mode = str((dict(policy_row.get("extensions") or {})).get("profile_mode", "")).strip().lower()
            if profile_mode in {"scheduled", "flow_linked", "hazard_linked"}:
                policy_mode = profile_mode
        if policy_mode == "static":
            continue

        layer_ext = _as_map(layer_row.get("extensions"))
        if policy_mode == "scheduled":
            interval = max(1, _as_int(layer_ext.get("schedule_interval_ticks", 1), 1))
            if int(tick % interval) != 0:
                continue
        field_cells = list(cells_by_field_id.get(field_id) or [])
        candidate_cell_ids = _candidate_cell_ids_for_field(
            field_id=field_id,
            existing_cells=field_cells,
            flow_quantities=flow_payload,
            hazard_states=hazard_payload,
        )
        for cell_id in candidate_cell_ids:
            current_row = next(
                (
                    dict(row)
                    for row in list(field_cells or [])
                    if str(row.get("cell_id", "")).strip() == str(cell_id).strip()
                ),
                {},
            )
            geo_cell_key = _field_cell_geo_cell_key(current_row)
            if not geo_cell_key:
                geo_cell_key = _field_geo_cell_key_for_alias(
                    layer_row=layer_row,
                    cell_id=str(cell_id),
                    field_binding_registry=field_binding_registry,
                )
            update_ops.append(
                {
                    "priority": _priority_for_field(field_id, critical_ids),
                    "field_id": field_id,
                    "cell_id": str(cell_id),
                    "geo_cell_key": dict(geo_cell_key),
                    "mode": policy_mode,
                }
            )

    update_ops = sorted(
        update_ops,
        key=lambda row: (
            int(_as_int(row.get("priority", 1), 1)),
            str(row.get("field_id", "")),
            _geo_cell_key_sort_tuple(row.get("geo_cell_key")),
            str(row.get("cell_id", "")),
        ),
    )
    if budget <= 0:
        max_ops = 0
    else:
        max_ops = int(max(0, budget // unit_cost))
    selected_ops = list(update_ops[:max_ops])
    skipped_ops = list(update_ops[max_ops:])

    existing_by_key = dict(
        (
            _field_lookup_key(
                field_id=str(row.get("field_id", "")).strip(),
                cell_id=str(row.get("cell_id", "")).strip(),
                geo_cell_key=_field_cell_geo_cell_key(row),
            ),
            dict(row),
        )
        for row in normalized_cells
    )
    touched_field_ids = set()
    touched_geo_cell_keys: Dict[str, dict] = {}
    for op in selected_ops:
        field_id = str(op.get("field_id", "")).strip()
        cell_id = str(op.get("cell_id", "")).strip()
        mode = str(op.get("mode", "static")).strip()
        if (not field_id) or (not cell_id):
            continue
        layer_row = dict(layer_by_field_id.get(field_id) or {})
        field_type_id = str(layer_row.get("field_type_id", "")).strip()
        value_kind = _normalize_value_kind((dict(field_type_rows.get(field_type_id) or {})).get("value_kind"))
        layer_ext = _as_map(layer_row.get("extensions"))
        geo_cell_key = _coerce_geo_cell_key(op.get("geo_cell_key"))
        if not geo_cell_key:
            geo_cell_key = _field_geo_cell_key_for_alias(
                layer_row=layer_row,
                cell_id=cell_id,
                field_binding_registry=field_binding_registry,
            )
        key = _field_lookup_key(field_id=field_id, cell_id=cell_id, geo_cell_key=geo_cell_key)
        current_row = dict(existing_by_key.get(key) or {})
        if (not current_row) and geo_cell_key:
            current_row = dict(existing_by_key.get(_field_lookup_key(field_id=field_id, geo_cell_key=geo_cell_key)) or {})
        if (not current_row) and cell_id:
            current_row = dict(existing_by_key.get(_field_lookup_key(field_id=field_id, cell_id=cell_id)) or {})
        current_value = current_row.get("value")
        if current_value is None:
            current_value = _default_value_for_field(
                field_id=field_id,
                layer_by_field_id=layer_by_field_id,
                field_type_rows=field_type_rows,
            )

        next_value = current_value
        if mode == "scheduled":
            delta_value = layer_ext.get("scheduled_delta", 0)
            next_value = _scheduled_next_value(current_value, delta_value, value_kind=value_kind)
        elif mode == "flow_linked":
            source_value = _source_value_for_field_cell(flow_payload.get(field_id), cell_id)
            if source_value is not None:
                next_value = source_value
        elif mode == "hazard_linked":
            source_value = _source_value_for_field_cell(hazard_payload.get(field_id), cell_id)
            if source_value is not None:
                next_value = source_value

        normalized_value = _normalize_cell_value(next_value, value_kind=value_kind)
        if value_kind == "scalar":
            normalized_value = _clamp_scalar(int(_as_int(normalized_value, 0)), layer_ext)
        next_row = build_field_cell(
            field_id=field_id,
            cell_id=cell_id,
            value=normalized_value,
            value_kind=value_kind,
            last_updated_tick=tick,
            geo_cell_key=geo_cell_key,
            extensions=_as_map(current_row.get("extensions")),
        )
        existing_by_key[_field_lookup_key(field_id=field_id, cell_id=cell_id, geo_cell_key=geo_cell_key)] = dict(next_row)
        touched_field_ids.add(field_id)
        geo_hash = _geo_cell_key_hash(geo_cell_key)
        if geo_hash:
            touched_geo_cell_keys[geo_hash] = dict(geo_cell_key)

    updated_cells = normalize_field_cell_rows(
        list(existing_by_key.values()),
        field_layer_rows=layers,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
    )
    skipped_field_ids = sorted(set(str(row.get("field_id", "")).strip() for row in skipped_ops if str(row.get("field_id", "")).strip()))
    result = {
        "field_layer_rows": layers,
        "field_cell_rows": updated_cells,
        "evaluated_field_ids": sorted(set(str(token).strip() for token in touched_field_ids if str(token).strip())),
        "relevant_coupling_field_ids": sorted(set(str(token).strip() for token in touched_field_ids if str(token).strip())),
        "relevant_coupling_geo_cell_keys": [
            dict(touched_geo_cell_keys[key]) for key in sorted(touched_geo_cell_keys.keys())
        ],
        "skipped_field_ids": skipped_field_ids,
        "cost_units_used": int(len(selected_ops) * unit_cost),
        "degraded": bool(len(skipped_ops) > 0),
        "degrade_reason": "degrade.field.budget" if skipped_ops else None,
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return result


def _value_as_int(value: object, default_value: int = 0) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return int(value)
    return int(_as_int(value, default_value))


def _field_scalar(
    *,
    field_id: str,
    spatial_position: Mapping[str, object],
    field_layer_rows: object,
    field_cell_rows: object,
    field_type_registry: Mapping[str, object],
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
    default_value: int,
) -> int:
    row = get_field_value(
        spatial_position=spatial_position,
        field_id=field_id,
        field_layer_rows=field_layer_rows,
        field_cell_rows=field_cell_rows,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
        interpolation_policy_registry=interpolation_policy_registry,
    )
    return int(_value_as_int(row.get("value"), default_value))


def _field_vector(
    *,
    field_id: str,
    spatial_position: Mapping[str, object],
    field_layer_rows: object,
    field_cell_rows: object,
    field_type_registry: Mapping[str, object],
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
) -> dict:
    row = get_field_value(
        spatial_position=spatial_position,
        field_id=field_id,
        field_layer_rows=field_layer_rows,
        field_cell_rows=field_cell_rows,
        field_type_registry=field_type_registry,
        field_binding_registry=field_binding_registry,
        interpolation_policy_registry=interpolation_policy_registry,
    )
    return _vector3(row.get("value"))


def _resolve_field_id_for_type(
    *,
    field_type_id: str,
    field_layer_rows: object,
) -> str:
    token = str(field_type_id or "").strip()
    rows = normalize_field_layer_rows(field_layer_rows)
    layer_ids = sorted(
        set(str(row.get("field_id", "")).strip() for row in rows if str(row.get("field_id", "")).strip())
    )
    if token in set(layer_ids):
        return token
    global_token = "{}.global".format(token)
    if global_token in set(layer_ids):
        return global_token
    for row in rows:
        if str(row.get("field_type_id", "")).strip() == token:
            field_id = str(row.get("field_id", "")).strip()
            if field_id:
                return field_id
    return token


def field_modifier_snapshot(
    *,
    field_layer_rows: object,
    field_cell_rows: object,
    field_type_registry: Mapping[str, object] | None,
    field_binding_registry: Mapping[str, object] | None = None,
    interpolation_policy_registry: Mapping[str, object] | None = None,
    sample_rows: object,
) -> dict:
    rows = [dict(item) for item in list(sample_rows or []) if isinstance(item, Mapping)]
    temperature_field_id = _resolve_field_id_for_type(
        field_type_id="field.temperature",
        field_layer_rows=field_layer_rows,
    )
    moisture_field_id = _resolve_field_id_for_type(
        field_type_id="field.moisture",
        field_layer_rows=field_layer_rows,
    )
    friction_field_id = _resolve_field_id_for_type(
        field_type_id="field.friction",
        field_layer_rows=field_layer_rows,
    )
    radiation_field_id = _resolve_field_id_for_type(
        field_type_id="field.radiation",
        field_layer_rows=field_layer_rows,
    )
    visibility_field_id = _resolve_field_id_for_type(
        field_type_id="field.visibility",
        field_layer_rows=field_layer_rows,
    )
    wind_field_id = _resolve_field_id_for_type(
        field_type_id="field.wind",
        field_layer_rows=field_layer_rows,
    )
    out_rows: List[dict] = []
    for row in sorted(rows, key=lambda item: str(item.get("target_id", ""))):
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        position = _as_map(row.get("spatial_position"))
        temperature = _field_scalar(
            field_id=temperature_field_id,
            spatial_position=position,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
            default_value=20,
        )
        moisture = _field_scalar(
            field_id=moisture_field_id,
            spatial_position=position,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
            default_value=0,
        )
        friction = _field_scalar(
            field_id=friction_field_id,
            spatial_position=position,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
            default_value=1000,
        )
        radiation = _field_scalar(
            field_id=radiation_field_id,
            spatial_position=position,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
            default_value=0,
        )
        visibility = _field_scalar(
            field_id=visibility_field_id,
            spatial_position=position,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
            default_value=1000,
        )
        wind = _field_vector(
            field_id=wind_field_id,
            spatial_position=position,
            field_layer_rows=field_layer_rows,
            field_cell_rows=field_cell_rows,
            field_type_registry=field_type_registry,
            field_binding_registry=field_binding_registry,
            interpolation_policy_registry=interpolation_policy_registry,
        )

        modifier_curve = evaluate_field_modifier_curve(
            temperature=int(temperature),
            moisture=int(moisture),
            friction=int(friction),
            wind_vector=wind,
        )
        icing_active = bool(modifier_curve.get("icing_active", False))
        traction_permille = int(_as_int(modifier_curve.get("traction_permille", 1000), 1000))
        wind_drift_permille = int(_as_int(modifier_curve.get("wind_drift_permille", 0), 0))
        stress_capacity_permille = int(_as_int(modifier_curve.get("stress_capacity_permille", 1000), 1000))
        corrosion_risk_permille = int(_as_int(modifier_curve.get("corrosion_risk_permille", 0), 0))

        payload = {
            "target_id": target_id,
            "temperature": int(temperature),
            "moisture": int(moisture),
            "friction": int(friction),
            "radiation": int(radiation),
            "visibility": int(max(0, int(visibility))),
            "wind": dict(wind),
            "traction_permille": int(max(0, traction_permille)),
            "wind_drift_permille": int(max(0, wind_drift_permille)),
            "stress_capacity_permille": int(max(0, stress_capacity_permille)),
            "corrosion_risk_permille": int(max(0, corrosion_risk_permille)),
            "icing_active": bool(icing_active),
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out_rows.append(payload)

    out = {
        "rows": sorted((dict(item) for item in out_rows), key=lambda item: str(item.get("target_id", ""))),
        "deterministic_fingerprint": "",
    }
    out["deterministic_fingerprint"] = canonical_sha256(dict(out, deterministic_fingerprint=""))
    return out


__all__ = [
    "build_field_cell",
    "build_field_layer",
    "build_field_sample",
    "field_modifier_snapshot",
    "field_type_rows_by_id",
    "field_update_policy_rows_by_id",
    "geo_field_distance_mm",
    "geo_field_sample_cell_key",
    "geo_field_sample_position",
    "get_field_value",
    "normalize_field_cell_rows",
    "normalize_field_layer_rows",
    "normalize_field_sample_rows",
    "update_field_layers",
]
