"""Deterministic GEO-3 distance and geodesic query engine."""

from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from typing import Dict, List, Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.frame.frame_engine import (
    _frame_nodes_by_id,
    _lowest_common_ancestor,
    frame_graph_hash,
    normalize_position_ref,
    position_ref_hash,
    position_to_frame,
)
from src.geo.metric.metric_cache import metric_cache_lookup, metric_cache_store
from src.geo.kernel.geo_kernel import (
    _DEFAULT_METRIC_PROFILE_ID,
    _DEFAULT_TOPOLOGY_PROFILE_ID,
    _as_int,
    _as_map,
    _default_registry_payload,
    _dimension_from_topology,
    _metric_row,
    _normalize_position,
    _query_record,
    _topology_row,
    _wrapped_delta,
)
from src.numeric_discipline import allowed_error_bound_for_tolerance, tolerance_rows_by_id


REFUSAL_GEO_METRIC_INVALID = "refusal.geo.metric_invalid"

_TOLERANCE_POLICY_REGISTRY_REL = "data/registries/tolerance_policy_registry.json"
_ENGINE_TOLERANCE_REGISTRY_REL = "data/registries/tolerance_registry.json"
_METRIC_POLICY_REGISTRY_REL = "data/registries/metric_policy_registry.json"
_GEODESIC_POLICY_REGISTRY_REL = "data/registries/geodesic_approx_policy_registry.json"
_METRIC_ENGINE_VERSION = "GEO3-3"
_METRIC_CACHE_VERSION = "GEO3-5"


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


@lru_cache(maxsize=None)
def _registry_payload(rel_path: str) -> dict:
    abs_path = os.path.join(_repo_root(), str(rel_path).replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _rows_by_id(
    payload: Mapping[str, object] | None,
    *,
    row_key: str,
    id_key: str,
) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get(row_key)
    if not isinstance(rows, list):
        rows = _as_map(body.get("record")).get(row_key)
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get(id_key, "")),
    ):
        token = str(row.get(id_key, "")).strip()
        if token:
            out[token] = dict(row)
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _tolerance_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(_TOLERANCE_POLICY_REGISTRY_REL),
        row_key="tolerance_policies",
        id_key="tolerance_policy_id",
    )


def _engine_tolerance_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return tolerance_rows_by_id(_as_map(payload) or _registry_payload(_ENGINE_TOLERANCE_REGISTRY_REL))


def _metric_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(_METRIC_POLICY_REGISTRY_REL),
        row_key="metric_policies",
        id_key="metric_policy_id",
    )


def _geodesic_policy_rows(payload: Mapping[str, object] | None = None) -> Dict[str, dict]:
    return _rows_by_id(
        _as_map(payload) or _registry_payload(_GEODESIC_POLICY_REGISTRY_REL),
        row_key="geodesic_approx_policies",
        id_key="geodesic_approx_policy_id",
    )


def _refusal(*, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_METRIC_INVALID,
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _missing_profile(*, profile_kind: str, profile_id: str) -> dict:
    return _refusal(
        message="{} '{}' is missing".format(str(profile_kind), str(profile_id)),
        details={
            "profile_kind": str(profile_kind),
            "profile_id": str(profile_id),
        },
    )


def _metric_policy_id(metric_row: Mapping[str, object]) -> str:
    ext = _as_map(_as_map(metric_row).get("extensions"))
    token = str(ext.get("metric_policy_id", "")).strip()
    if token:
        return token
    kind = str(_as_map(metric_row).get("metric_kind", "euclidean")).strip().lower()
    return {
        "euclidean": "metric.euclidean_exact",
        "torus_wrap": "metric.torus_wrap_exact",
        "spherical_stub": "metric.spherical_geodesic_stub",
        "custom": "metric.custom_plugin_stub",
    }.get(kind, "metric.euclidean_exact")


def _geodesic_policy_id(metric_row: Mapping[str, object]) -> str:
    ext = _as_map(_as_map(metric_row).get("extensions"))
    token = str(ext.get("geodesic_approx_policy_id", "")).strip()
    if token:
        return token
    kind = str(_as_map(metric_row).get("metric_kind", "euclidean")).strip().lower()
    if kind == "spherical_stub":
        return "geodesic.spherical_linear_approx"
    if kind == "custom":
        return "geodesic.iterative_stub"
    return "geodesic.none"


def _tolerance_rounding(tolerance_policy_id: str, tolerance_policy_registry_payload: Mapping[str, object] | None = None) -> tuple[str, int]:
    row = dict(_tolerance_rows(tolerance_policy_registry_payload).get(str(tolerance_policy_id).strip()) or {})
    rounding = _as_map(row.get("rounding_rules"))
    mode = str(rounding.get("default_mode", "nearest_even")).strip().lower() or "nearest_even"
    scale = int(max(1, _as_int(rounding.get("scale", 1), 1)))
    return mode, scale


def _quantize_nonnegative(value: int, *, scale: int, mode: str) -> int:
    token = int(max(0, int(value)))
    divisor = int(max(1, int(scale)))
    if divisor == 1:
        return token
    quotient = token // divisor
    remainder = token % divisor
    if str(mode) == "toward_zero":
        return int(quotient * divisor)
    if str(mode) == "nearest_even":
        double = remainder * 2
        if double < divisor:
            return int(quotient * divisor)
        if double > divisor:
            return int((quotient + 1) * divisor)
        return int((quotient if (quotient % 2 == 0) else (quotient + 1)) * divisor)
    return int(quotient * divisor)


def _nearest_integer_sqrt(squared_distance: int) -> int:
    squared = int(max(0, int(squared_distance)))
    root = int(math.isqrt(squared))
    lower_error = squared - (root * root)
    upper_root = root + 1
    upper_error = (upper_root * upper_root) - squared
    if lower_error < upper_error:
        return root
    if upper_error < lower_error:
        return upper_root
    return root if (root % 2 == 0) else upper_root


def _wrap_periods(metric_row: Mapping[str, object], dimension: int) -> List[int]:
    params = _as_map(_as_map(metric_row).get("parameters"))
    raw = params.get("fundamental_period_mm", 0)
    if isinstance(raw, list):
        out = [int(_as_int(value, 0)) for value in raw[:dimension]]
    else:
        out = [int(_as_int(raw, 0))] * int(max(1, dimension))
    while len(out) < int(max(1, dimension)):
        out.append(0)
    return out


def _normalize_lon_delta_mdeg(delta_mdeg: int) -> int:
    raw = int(delta_mdeg)
    while raw > 180000:
        raw -= 360000
    while raw < -180000:
        raw += 360000
    return raw


def _spherical_arc_mm(coords_a: Sequence[int], coords_b: Sequence[int], radius_mm: int) -> int:
    lat_a = float(int(coords_a[0] if len(coords_a) > 0 else 0)) / 1000.0
    lon_a = float(int(coords_a[1] if len(coords_a) > 1 else 0)) / 1000.0
    lat_b = float(int(coords_b[0] if len(coords_b) > 0 else 0)) / 1000.0
    lon_b = float(int(coords_b[1] if len(coords_b) > 1 else 0)) / 1000.0
    dlat = math.radians(lat_b - lat_a)
    dlon = math.radians(float(_normalize_lon_delta_mdeg(int(round((lon_b - lon_a) * 1000.0)))) / 1000.0)
    lat_a_rad = math.radians(lat_a)
    lat_b_rad = math.radians(lat_b)
    hav = (math.sin(dlat * 0.5) ** 2) + math.cos(lat_a_rad) * math.cos(lat_b_rad) * (math.sin(dlon * 0.5) ** 2)
    angle = 2.0 * math.asin(min(1.0, math.sqrt(max(0.0, hav))))
    if __debug__ and (not math.isfinite(hav) or not math.isfinite(angle)):
        raise AssertionError("geo_projection_bridge produced non-finite spherical arc state")
    return int(round(float(max(1, int(radius_mm))) * float(angle)))


def _custom_distance_mm(coords_a: Sequence[int], coords_b: Sequence[int], metric_row: Mapping[str, object]) -> int:
    deltas = [int(coords_a[idx]) - int(coords_b[idx]) for idx in range(min(len(coords_a), len(coords_b)))]
    base = _nearest_integer_sqrt(sum(int(delta) * int(delta) for delta in deltas))
    params = _as_map(_as_map(metric_row).get("parameters"))
    curvature_permille = int(_as_int(params.get("curvature_permille", 0), 0))
    curvature_mag = abs(curvature_permille)
    if curvature_mag <= 0:
        return int(base)
    return int(base + ((int(base) * int(curvature_mag)) // 10000))


def _metric_distance_mm(
    *,
    coords_a: Sequence[int],
    coords_b: Sequence[int],
    metric_row: Mapping[str, object],
) -> int:
    metric_kind = str(_as_map(metric_row).get("metric_kind", "euclidean")).strip().lower() or "euclidean"
    deltas = [int(coords_a[idx]) - int(coords_b[idx]) for idx in range(min(len(coords_a), len(coords_b)))]
    if metric_kind == "torus_wrap":
        periods = _wrap_periods(metric_row, len(deltas))
        return _nearest_integer_sqrt(
            sum(int(_wrapped_delta(delta, periods[idx])) ** 2 for idx, delta in enumerate(deltas))
        )
    if metric_kind == "spherical_stub":
        params = _as_map(_as_map(metric_row).get("parameters"))
        return _spherical_arc_mm(coords_a, coords_b, int(_as_int(params.get("radius_mm", 6371000000), 6371000000)))
    if metric_kind == "custom":
        return _custom_distance_mm(coords_a, coords_b, metric_row)
    return _nearest_integer_sqrt(sum(int(delta) * int(delta) for delta in deltas))


def _metric_geodesic_mm(
    *,
    coords_a: Sequence[int],
    coords_b: Sequence[int],
    metric_row: Mapping[str, object],
) -> int:
    metric_kind = str(_as_map(metric_row).get("metric_kind", "euclidean")).strip().lower() or "euclidean"
    if metric_kind == "spherical_stub":
        params = _as_map(_as_map(metric_row).get("parameters"))
        return _spherical_arc_mm(coords_a, coords_b, int(_as_int(params.get("radius_mm", 6371000000), 6371000000)))
    return _metric_distance_mm(coords_a=coords_a, coords_b=coords_b, metric_row=metric_row)


def _bounded_error_mm(
    *,
    metric_row: Mapping[str, object],
    metric_policy_row: Mapping[str, object],
    geodesic_policy_row: Mapping[str, object],
    tolerance_scale: int,
    query_kind: str,
) -> int:
    ext = _as_map(_as_map(metric_row).get("extensions"))
    metric_bound = int(max(0, _as_int(ext.get("bounded_error_mm", 0), 0)))
    policy_bound = int(max(0, _as_int(_as_map(metric_policy_row).get("bounded_error_mm", 0), 0)))
    geodesic_bound = int(max(0, _as_int(_as_map(geodesic_policy_row).get("bounded_error_mm", 0), 0)))
    bound = max(metric_bound, policy_bound, geodesic_bound if str(query_kind) == "geodesic" else 0)
    quantization_bound = int(max(0, int(max(1, tolerance_scale)) - 1))
    resolved_bound = int(max(bound, quantization_bound))
    if __debug__:
        allowed_bound = allowed_error_bound_for_tolerance(
            tolerance_id="tol.geo_projection",
            tolerance_registry={"tolerances": list(_engine_tolerance_rows().values())},
            default_value=resolved_bound,
        )
        if resolved_bound > allowed_bound:
            raise AssertionError(
                "geo projection bound exceeded tol.geo_projection (resolved={}, allowed={})".format(
                    int(resolved_bound),
                    int(allowed_bound),
                )
            )
    return resolved_bound


def _normalize_raw_positions(
    *,
    pos_a: Mapping[str, object] | None,
    pos_b: Mapping[str, object] | None,
    topology_row: Mapping[str, object],
) -> tuple[List[int], List[int]]:
    dimension = max(1, _dimension_from_topology(topology_row))
    coords_a = _normalize_position(pos_a, dimension)
    coords_b = _normalize_position(pos_b, dimension)
    return coords_a, coords_b


def _frame_context(
    *,
    pos_a_ref: Mapping[str, object],
    pos_b_ref: Mapping[str, object],
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    nodes = _frame_nodes_by_id(frame_nodes, topology_registry_payload=topology_registry_payload)
    pos_a = normalize_position_ref(
        pos_a_ref,
        frame_nodes=list(nodes.values()),
        topology_registry_payload=topology_registry_payload,
    )
    pos_b = normalize_position_ref(
        pos_b_ref,
        frame_nodes=list(nodes.values()),
        topology_registry_payload=topology_registry_payload,
    )
    if pos_a is None or pos_b is None:
        return _refusal(message="position_ref is invalid")
    frame_a = str(pos_a.get("frame_id", "")).strip()
    frame_b = str(pos_b.get("frame_id", "")).strip()
    if frame_a not in nodes or frame_b not in nodes:
        return _refusal(
            message="position_ref references missing frame node",
            details={"frame_a": frame_a, "frame_b": frame_b},
        )
    version = str(graph_version or "").strip() or frame_graph_hash(
        frame_nodes=list(nodes.values()),
        frame_transform_rows=frame_transform_rows,
        topology_registry_payload=topology_registry_payload,
    )
    comparison_frame_id = _lowest_common_ancestor(frame_a, frame_b, nodes) or min(frame_a, frame_b)
    conv_a = position_to_frame(
        pos_a,
        comparison_frame_id,
        frame_nodes=list(nodes.values()),
        frame_transform_rows=frame_transform_rows,
        graph_version=version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(conv_a.get("result", "")) != "complete":
        return conv_a
    conv_b = position_to_frame(
        pos_b,
        comparison_frame_id,
        frame_nodes=list(nodes.values()),
        frame_transform_rows=frame_transform_rows,
        graph_version=version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(conv_b.get("result", "")) != "complete":
        return conv_b
    comparison_frame = dict(nodes.get(comparison_frame_id) or {})
    return {
        "result": "complete",
        "graph_version": version,
        "comparison_frame_id": comparison_frame_id,
        "comparison_frame": comparison_frame,
        "position_a_in_frame": _as_map(conv_a.get("target_position_ref")),
        "position_b_in_frame": _as_map(conv_b.get("target_position_ref")),
        "position_a_hash": position_ref_hash(pos_a),
        "position_b_hash": position_ref_hash(pos_b),
    }


def _metric_result(
    *,
    query_kind: str,
    coords_a: Sequence[int],
    coords_b: Sequence[int],
    topology_profile_id: str,
    metric_profile_id: str,
    metric_row: Mapping[str, object],
    topology_row: Mapping[str, object],
    metric_policy_registry_payload: Mapping[str, object] | None = None,
    geodesic_policy_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    comparison_frame_id: str = "",
    position_a_in_frame: Mapping[str, object] | None = None,
    position_b_in_frame: Mapping[str, object] | None = None,
    seed_extensions: Mapping[str, object] | None = None,
    cache_enabled: bool | None = None,
    reference_mode: str = "",
    cache_max_entries: int | None = None,
) -> dict:
    del topology_row
    metric_policy_id = _metric_policy_id(metric_row)
    geodesic_policy_id = _geodesic_policy_id(metric_row)
    metric_policy_row = dict(_metric_policy_rows(metric_policy_registry_payload).get(metric_policy_id) or {})
    geodesic_policy_row = dict(_geodesic_policy_rows(geodesic_policy_registry_payload).get(geodesic_policy_id) or {})
    tolerance_policy_id = str(_as_map(metric_row).get("tolerance_policy_id", "tol.default")).strip() or "tol.default"
    rounding_mode, rounding_scale = _tolerance_rounding(
        tolerance_policy_id,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
    )
    seed = {
        "query_kind": str(query_kind),
        "topology_profile_id": str(topology_profile_id),
        "metric_profile_id": str(metric_profile_id),
        "metric_policy_id": metric_policy_id,
        "geodesic_approx_policy_id": geodesic_policy_id,
        "tolerance_policy_id": tolerance_policy_id,
        "coords_a": [int(value) for value in list(coords_a)],
        "coords_b": [int(value) for value in list(coords_b)],
        "comparison_frame_id": str(comparison_frame_id),
        "engine_version": _METRIC_ENGINE_VERSION,
        **dict(_as_map(seed_extensions)),
    }
    cached = metric_cache_lookup(
        "geo.metric.{}".format(str(query_kind)),
        seed,
        cache_enabled=cache_enabled,
        reference_mode=reference_mode,
        version=_METRIC_CACHE_VERSION,
    )
    if cached is not None:
        return cached
    raw_value = (
        _metric_geodesic_mm(coords_a=coords_a, coords_b=coords_b, metric_row=metric_row)
        if str(query_kind) == "geodesic"
        else _metric_distance_mm(coords_a=coords_a, coords_b=coords_b, metric_row=metric_row)
    )
    quantized_value = _quantize_nonnegative(raw_value, scale=rounding_scale, mode=rounding_mode)
    error_bound_mm = _bounded_error_mm(
        metric_row=metric_row,
        metric_policy_row=metric_policy_row,
        geodesic_policy_row=geodesic_policy_row,
        tolerance_scale=rounding_scale,
        query_kind=query_kind,
    )
    algorithm_row = geodesic_policy_row if str(query_kind) == "geodesic" else metric_policy_row
    algorithm_id = str(_as_map(algorithm_row).get("algorithm_id", "")).strip() or "geo.metric.unknown"
    if str(query_kind) == "geodesic":
        outputs = {"geodesic_mm": int(quantized_value), "error_bound_mm": int(error_bound_mm)}
    else:
        outputs = {"distance_mm": int(quantized_value), "error_bound_mm": int(error_bound_mm)}
    payload = {
        "result": "complete",
        "query_kind": str(query_kind),
        "topology_profile_id": str(topology_profile_id),
        "metric_profile_id": str(metric_profile_id),
        "metric_policy_id": metric_policy_id,
        "geodesic_approx_policy_id": geodesic_policy_id,
        "tolerance_policy_id": tolerance_policy_id,
        "algorithm_id": algorithm_id,
        "comparison_frame_id": str(comparison_frame_id) or None,
        "distance_value": int(quantized_value),
        "distance_mm": int(quantized_value),
        "geodesic_value": int(quantized_value),
        "geodesic_mm": int(quantized_value),
        "raw_value_mm": int(raw_value),
        "error_bound": {"unit": "mm", "value": int(error_bound_mm)},
        "error_bound_mm": int(error_bound_mm),
        "position_a_in_frame": _as_map(position_a_in_frame),
        "position_b_in_frame": _as_map(position_b_in_frame),
        "query_record": _query_record(str(query_kind), seed, outputs),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return metric_cache_store(
        "geo.metric.{}".format(str(query_kind)),
        seed,
        payload,
        cache_enabled=cache_enabled,
        reference_mode=reference_mode,
        version=_METRIC_CACHE_VERSION,
        max_entries=cache_max_entries,
    )


def geo_distance(
    pos_a_ref: Mapping[str, object] | None,
    pos_b_ref: Mapping[str, object] | None,
    topology_profile_id: str = "",
    metric_profile_id: str = "",
    *,
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    metric_policy_registry_payload: Mapping[str, object] | None = None,
    geodesic_approx_policy_registry_payload: Mapping[str, object] | None = None,
    cache_enabled: bool | None = None,
    reference_mode: str = "",
    cache_max_entries: int | None = None,
) -> dict:
    if bool(frame_nodes) and bool(frame_transform_rows):
        context = _frame_context(
            pos_a_ref=_as_map(pos_a_ref),
            pos_b_ref=_as_map(pos_b_ref),
            frame_nodes=frame_nodes,
            frame_transform_rows=frame_transform_rows,
            graph_version=str(graph_version or ""),
            topology_registry_payload=topology_registry_payload,
        )
        if str(context.get("result", "")) != "complete":
            return context
        comparison_frame = _as_map(context.get("comparison_frame"))
        topology_token = str(topology_profile_id or comparison_frame.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
        metric_token = str(metric_profile_id or comparison_frame.get("metric_profile_id", "")).strip() or _DEFAULT_METRIC_PROFILE_ID
        topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
        if not topology_row:
            return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
        metric_row = _metric_row(metric_token, registry_payload=metric_registry_payload)
        if not metric_row:
            return _missing_profile(profile_kind="metric_profile_id", profile_id=metric_token)
        coords_a, coords_b = _normalize_raw_positions(
            pos_a={"coords": list(_as_map(context.get("position_a_in_frame")).get("local_position") or [])},
            pos_b={"coords": list(_as_map(context.get("position_b_in_frame")).get("local_position") or [])},
            topology_row=topology_row,
        )
        return _metric_result(
            query_kind="distance",
            coords_a=coords_a,
            coords_b=coords_b,
            topology_profile_id=topology_token,
            metric_profile_id=metric_token,
            metric_row=metric_row,
            topology_row=topology_row,
            metric_policy_registry_payload=metric_policy_registry_payload,
            geodesic_policy_registry_payload=geodesic_approx_policy_registry_payload,
            tolerance_policy_registry_payload=tolerance_policy_registry_payload,
            comparison_frame_id=str(context.get("comparison_frame_id", "")),
            position_a_in_frame=_as_map(context.get("position_a_in_frame")),
            position_b_in_frame=_as_map(context.get("position_b_in_frame")),
            seed_extensions={
                "position_a_hash": str(context.get("position_a_hash", "")),
                "position_b_hash": str(context.get("position_b_hash", "")),
                "graph_version": str(context.get("graph_version", "")),
            },
            cache_enabled=cache_enabled,
            reference_mode=reference_mode,
            cache_max_entries=cache_max_entries,
        )

    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    metric_token = str(metric_profile_id or "").strip() or _DEFAULT_METRIC_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
    metric_row = _metric_row(metric_token, registry_payload=metric_registry_payload)
    if not metric_row:
        return _missing_profile(profile_kind="metric_profile_id", profile_id=metric_token)
    coords_a, coords_b = _normalize_raw_positions(pos_a=pos_a_ref, pos_b=pos_b_ref, topology_row=topology_row)
    return _metric_result(
        query_kind="distance",
        coords_a=coords_a,
        coords_b=coords_b,
        topology_profile_id=topology_token,
        metric_profile_id=metric_token,
        metric_row=metric_row,
        topology_row=topology_row,
        metric_policy_registry_payload=metric_policy_registry_payload,
        geodesic_policy_registry_payload=geodesic_approx_policy_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        cache_enabled=cache_enabled,
        reference_mode=reference_mode,
        cache_max_entries=cache_max_entries,
    )


def geo_geodesic(
    pos_a_ref: Mapping[str, object] | None,
    pos_b_ref: Mapping[str, object] | None,
    topology_profile_id: str = "",
    metric_profile_id: str = "",
    *,
    frame_nodes: object = None,
    frame_transform_rows: object = None,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    metric_policy_registry_payload: Mapping[str, object] | None = None,
    geodesic_approx_policy_registry_payload: Mapping[str, object] | None = None,
    cache_enabled: bool | None = None,
    reference_mode: str = "",
    cache_max_entries: int | None = None,
) -> dict:
    if bool(frame_nodes) and bool(frame_transform_rows):
        context = _frame_context(
            pos_a_ref=_as_map(pos_a_ref),
            pos_b_ref=_as_map(pos_b_ref),
            frame_nodes=frame_nodes,
            frame_transform_rows=frame_transform_rows,
            graph_version=str(graph_version or ""),
            topology_registry_payload=topology_registry_payload,
        )
        if str(context.get("result", "")) != "complete":
            return context
        comparison_frame = _as_map(context.get("comparison_frame"))
        topology_token = str(topology_profile_id or comparison_frame.get("topology_profile_id", "")).strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
        metric_token = str(metric_profile_id or comparison_frame.get("metric_profile_id", "")).strip() or _DEFAULT_METRIC_PROFILE_ID
        topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
        if not topology_row:
            return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
        metric_row = _metric_row(metric_token, registry_payload=metric_registry_payload)
        if not metric_row:
            return _missing_profile(profile_kind="metric_profile_id", profile_id=metric_token)
        coords_a, coords_b = _normalize_raw_positions(
            pos_a={"coords": list(_as_map(context.get("position_a_in_frame")).get("local_position") or [])},
            pos_b={"coords": list(_as_map(context.get("position_b_in_frame")).get("local_position") or [])},
            topology_row=topology_row,
        )
        return _metric_result(
            query_kind="geodesic",
            coords_a=coords_a,
            coords_b=coords_b,
            topology_profile_id=topology_token,
            metric_profile_id=metric_token,
            metric_row=metric_row,
            topology_row=topology_row,
            metric_policy_registry_payload=metric_policy_registry_payload,
            geodesic_policy_registry_payload=geodesic_approx_policy_registry_payload,
            tolerance_policy_registry_payload=tolerance_policy_registry_payload,
            comparison_frame_id=str(context.get("comparison_frame_id", "")),
            position_a_in_frame=_as_map(context.get("position_a_in_frame")),
            position_b_in_frame=_as_map(context.get("position_b_in_frame")),
            seed_extensions={
                "position_a_hash": str(context.get("position_a_hash", "")),
                "position_b_hash": str(context.get("position_b_hash", "")),
                "graph_version": str(context.get("graph_version", "")),
            },
            cache_enabled=cache_enabled,
            reference_mode=reference_mode,
            cache_max_entries=cache_max_entries,
        )

    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    metric_token = str(metric_profile_id or "").strip() or _DEFAULT_METRIC_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
    metric_row = _metric_row(metric_token, registry_payload=metric_registry_payload)
    if not metric_row:
        return _missing_profile(profile_kind="metric_profile_id", profile_id=metric_token)
    coords_a, coords_b = _normalize_raw_positions(pos_a=pos_a_ref, pos_b=pos_b_ref, topology_row=topology_row)
    return _metric_result(
        query_kind="geodesic",
        coords_a=coords_a,
        coords_b=coords_b,
        topology_profile_id=topology_token,
        metric_profile_id=metric_token,
        metric_row=metric_row,
        topology_row=topology_row,
        metric_policy_registry_payload=metric_policy_registry_payload,
        geodesic_policy_registry_payload=geodesic_approx_policy_registry_payload,
        tolerance_policy_registry_payload=tolerance_policy_registry_payload,
        cache_enabled=cache_enabled,
        reference_mode=reference_mode,
        cache_max_entries=cache_max_entries,
    )


def metric_query_proof_surface(query_rows: object) -> dict:
    rows = []
    topology_profile_ids: List[str] = []
    metric_profile_ids: List[str] = []
    for row in list(query_rows or []):
        payload = _as_map(row)
        if str(payload.get("result", "")).strip() != "complete":
            continue
        topology_profile_id = str(payload.get("topology_profile_id", "")).strip()
        metric_profile_id = str(payload.get("metric_profile_id", "")).strip()
        if topology_profile_id:
            topology_profile_ids.append(topology_profile_id)
        if metric_profile_id:
            metric_profile_ids.append(metric_profile_id)
        query_record = _as_map(payload.get("query_record"))
        rows.append(
            {
                "query_kind": str(payload.get("query_kind", "")).strip(),
                "topology_profile_id": topology_profile_id,
                "metric_profile_id": metric_profile_id,
                "metric_policy_id": str(payload.get("metric_policy_id", "")).strip(),
                "geodesic_approx_policy_id": str(payload.get("geodesic_approx_policy_id", "")).strip(),
                "comparison_frame_id": str(payload.get("comparison_frame_id", "") or "").strip(),
                "distance_mm": int(max(0, _as_int(payload.get("distance_mm", 0), 0))),
                "geodesic_mm": int(max(0, _as_int(payload.get("geodesic_mm", 0), 0))),
                "error_bound_mm": int(max(0, _as_int(payload.get("error_bound_mm", 0), 0))),
                "query_inputs_hash": str(query_record.get("inputs_hash", "")).strip(),
                "query_outputs_hash": str(query_record.get("outputs_hash", "")).strip(),
                "query_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
            }
        )
    normalized_rows = sorted(
        rows,
        key=lambda item: (
            str(item.get("query_kind", "")),
            str(item.get("topology_profile_id", "")),
            str(item.get("metric_profile_id", "")),
            str(item.get("comparison_frame_id", "")),
            str(item.get("query_inputs_hash", "")),
            str(item.get("query_outputs_hash", "")),
            str(item.get("query_fingerprint", "")),
        ),
    )
    topology_ids = sorted(set(str(token).strip() for token in topology_profile_ids if str(token).strip()))
    metric_ids = sorted(set(str(token).strip() for token in metric_profile_ids if str(token).strip()))
    payload = {
        "query_count": int(len(normalized_rows)),
        "topology_profile_ids": topology_ids,
        "metric_profile_ids": metric_ids,
        "metric_query_hash_chain": canonical_sha256(normalized_rows),
        "deterministic_fingerprint": "",
    }
    if len(topology_ids) == 1:
        payload["topology_profile_id"] = str(topology_ids[0])
    if len(metric_ids) == 1:
        payload["metric_profile_id"] = str(metric_ids[0])
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "REFUSAL_GEO_METRIC_INVALID",
    "geo_distance",
    "geo_geodesic",
    "metric_query_proof_surface",
]
