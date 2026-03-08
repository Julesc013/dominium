"""Pure deterministic GEO kernel for topology, metric, partition, and projection queries."""

from __future__ import annotations

import copy
import itertools
import json
import math
import os
from functools import lru_cache
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_GEO_INVALID = "refusal.geo.invalid"
REFUSAL_GEO_PROFILE_MISSING = "refusal.geo.profile_missing"

_AXIS_LABELS = ("x", "y", "z", "w", "v", "u")
_DEFAULT_TOPOLOGY_PROFILE_ID = "geo.topology.r3_infinite"
_DEFAULT_METRIC_PROFILE_ID = "geo.metric.euclidean"
_DEFAULT_PARTITION_PROFILE_ID = "geo.partition.grid_zd"
_DEFAULT_PROJECTION_PROFILE_ID = "geo.projection.perspective_3d"
_REGISTRY_PATHS = {
    "topology": "data/registries/space_topology_profile_registry.json",
    "metric": "data/registries/metric_profile_registry.json",
    "partition": "data/registries/partition_profile_registry.json",
    "projection": "data/registries/projection_profile_registry.json",
}
_QUERY_CACHE: Dict[str, dict] = {}


def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "..", ".."))


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _sorted_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _deepcopy(payload: object) -> object:
    return copy.deepcopy(payload)


@lru_cache(maxsize=None)
def _default_registry_payload(kind: str) -> dict:
    rel_path = _REGISTRY_PATHS.get(str(kind).strip())
    if not rel_path:
        return {}
    abs_path = os.path.join(_repo_root(), rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}


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


def _profiles_by_id(payload: Mapping[str, object] | None, row_key: str, id_key: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted(_rows_from_registry(payload, row_key), key=lambda item: str(item.get(id_key, ""))):
        profile_id = str(row.get(id_key, "")).strip()
        if profile_id:
            out[profile_id] = dict(row)
    return out


def _topology_row(profile_id: str, registry_payload: Mapping[str, object] | None = None) -> dict:
    payload = _as_map(registry_payload) or _default_registry_payload("topology")
    rows = _profiles_by_id(payload, "topology_profiles", "topology_profile_id")
    return dict(rows.get(str(profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID) or {})


def _metric_row(profile_id: str, registry_payload: Mapping[str, object] | None = None) -> dict:
    payload = _as_map(registry_payload) or _default_registry_payload("metric")
    rows = _profiles_by_id(payload, "metric_profiles", "metric_profile_id")
    return dict(rows.get(str(profile_id or "").strip() or _DEFAULT_METRIC_PROFILE_ID) or {})


def _partition_row(profile_id: str, registry_payload: Mapping[str, object] | None = None) -> dict:
    payload = _as_map(registry_payload) or _default_registry_payload("partition")
    rows = _profiles_by_id(payload, "partition_profiles", "partition_profile_id")
    return dict(rows.get(str(profile_id or "").strip() or _DEFAULT_PARTITION_PROFILE_ID) or {})


def _projection_row(profile_id: str, registry_payload: Mapping[str, object] | None = None) -> dict:
    payload = _as_map(registry_payload) or _default_registry_payload("projection")
    rows = _profiles_by_id(payload, "projection_profiles", "projection_profile_id")
    return dict(rows.get(str(profile_id or "").strip() or _DEFAULT_PROJECTION_PROFILE_ID) or {})


def _query_cache_key(kind: str, seed: Mapping[str, object]) -> str:
    return "{}::{}".format(str(kind), str(canonical_sha256(seed)))


def _query_record(query_kind: str, seed: Mapping[str, object], outputs: Mapping[str, object]) -> dict:
    inputs_hash = canonical_sha256(seed)
    outputs_hash = canonical_sha256(outputs)
    payload = {
        "schema_version": "1.0.0",
        "query_kind": str(query_kind),
        "inputs_hash": str(inputs_hash),
        "outputs_hash": str(outputs_hash),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _cache_lookup(cache_key: str) -> dict | None:
    cached = _QUERY_CACHE.get(str(cache_key))
    if not isinstance(cached, dict):
        return None
    return _deepcopy(cached)


def _cache_store(cache_key: str, payload: Mapping[str, object]) -> dict:
    _QUERY_CACHE[str(cache_key)] = _deepcopy(dict(payload))
    return _deepcopy(dict(payload))


def _refusal(*, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_INVALID,
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _missing_profile(*, profile_kind: str, profile_id: str) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": REFUSAL_GEO_PROFILE_MISSING,
        "message": "{} '{}' is missing".format(str(profile_kind), str(profile_id)),
        "details": {
            "profile_kind": str(profile_kind),
            "profile_id": str(profile_id),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _dimension_from_topology(topology_row: Mapping[str, object]) -> int:
    return max(1, _as_int(_as_map(topology_row).get("dimension_D", 3), 3))


def _axis_labels(dimension: int) -> Sequence[str]:
    if dimension <= len(_AXIS_LABELS):
        return _AXIS_LABELS[:dimension]
    return tuple("a{}".format(idx) for idx in range(int(dimension)))


def _normalize_position(position: Mapping[str, object] | None, dimension: int) -> List[int]:
    payload = _as_map(position)
    if isinstance(payload.get("position_mm"), Mapping):
        payload = _as_map(payload.get("position_mm"))
    coords = payload.get("coords")
    if isinstance(coords, list):
        values = [_as_int(value, 0) for value in coords[:dimension]]
        while len(values) < dimension:
            values.append(0)
        return values
    values = []
    for axis in _axis_labels(dimension):
        values.append(_as_int(payload.get(axis, 0), 0))
    return values


def _position_payload(coords: Sequence[int], dimension: int) -> dict:
    labels = _axis_labels(dimension)
    payload = {"coords": [int(value) for value in list(coords[:dimension])]}
    for idx, axis in enumerate(labels):
        payload[axis] = int(payload["coords"][idx])
    return payload


def _parse_grid_cell_key(cell_key: str) -> List[int] | None:
    token = str(cell_key or "").strip()
    if not token.startswith("cell."):
        return None
    parts = token.split(".")[1:]
    if not parts:
        return None
    out: List[int] = []
    for part in parts:
        if part in {"", "cell"}:
            return None
        try:
            out.append(int(part))
        except ValueError:
            return None
    return out


def _format_grid_cell_key(coords: Sequence[int]) -> str:
    return "cell.{}".format(".".join(str(int(value)) for value in list(coords)))


def _parse_atlas_cell_key(cell_key: str) -> Tuple[str, int, int] | None:
    token = str(cell_key or "").strip()
    parts = token.split(".")
    if len(parts) != 4 or parts[0] != "atlas":
        return None
    try:
        return str(parts[1]), int(parts[2]), int(parts[3])
    except ValueError:
        return None


def _format_atlas_cell_key(chart_id: str, u_idx: int, v_idx: int) -> str:
    return "atlas.{}.{}.{}".format(str(chart_id), int(u_idx), int(v_idx))


def _neighbor_offsets(policy_id: str, radius: int, dimension: int) -> List[Tuple[int, ...]]:
    radius_value = max(0, int(radius))
    if radius_value == 0:
        return []
    policy = str(policy_id or "").strip().lower()
    offsets: List[Tuple[int, ...]] = []
    for offset in itertools.product(range(-radius_value, radius_value + 1), repeat=max(1, int(dimension))):
        if not any(int(value) != 0 for value in offset):
            continue
        max_abs = max(abs(int(value)) for value in offset)
        manhattan = sum(abs(int(value)) for value in offset)
        if "moore" in policy:
            if max_abs <= radius_value:
                offsets.append(tuple(int(value) for value in offset))
        elif ("von_neumann" in policy) or ("axis_aligned" in policy) or ("linear" in policy):
            if manhattan <= radius_value:
                offsets.append(tuple(int(value) for value in offset))
        else:
            if manhattan <= radius_value:
                offsets.append(tuple(int(value) for value in offset))
    return sorted(
        set(offsets),
        key=lambda item: (
            max(abs(int(value)) for value in item),
            sum(abs(int(value)) for value in item),
            tuple(int(value) for value in item),
        ),
    )


def _periods_from_topology(topology_row: Mapping[str, object], dimension: int) -> List[int]:
    ext = _as_map(_as_map(topology_row).get("extensions"))
    periods = ext.get("period_cell_counts")
    if not isinstance(periods, list):
        return []
    out = [_as_int(value, 0) for value in periods[:dimension]]
    while len(out) < dimension:
        out.append(0)
    return out


def _periodic_coord(value: int, period: int) -> int:
    if int(period) <= 0:
        return int(value)
    return int(value) % int(period)


def _atlas_neighbors(cell_key: str, topology_row: Mapping[str, object], radius: int) -> List[str]:
    parsed = _parse_atlas_cell_key(cell_key)
    if parsed is None:
        return []
    chart_id, u_idx, v_idx = parsed
    offsets = _neighbor_offsets(str(_as_map(topology_row).get("neighbor_policy_id", "")), radius, 2)
    atlas_resolution = max(2, _as_int(_as_map(_as_map(topology_row).get("extensions")).get("atlas_resolution", 8), 8))
    seam_pair = {
        "north": "south",
        "south": "north",
    }
    out: List[str] = []
    for du, dv in offsets:
        next_chart = str(chart_id)
        next_u = int(u_idx + int(du))
        next_v = int(v_idx + int(dv))
        if next_u < 0 or next_u >= atlas_resolution or next_v < 0 or next_v >= atlas_resolution:
            next_chart = seam_pair.get(str(chart_id), str(chart_id))
            next_u = int(next_u % atlas_resolution)
            next_v = int(next_v % atlas_resolution)
        out.append(_format_atlas_cell_key(next_chart, next_u, next_v))
    return sorted(set(out))


def _grid_neighbors(cell_key: str, topology_row: Mapping[str, object], radius: int) -> List[str]:
    coords = _parse_grid_cell_key(cell_key)
    if coords is None:
        return []
    dimension = len(coords)
    periods = _periods_from_topology(topology_row, dimension)
    offsets = _neighbor_offsets(str(_as_map(topology_row).get("neighbor_policy_id", "")), radius, dimension)
    boundary_rule_id = str(_as_map(topology_row).get("boundary_rule_id", "")).strip().lower()
    out: List[str] = []
    for offset in offsets:
        next_coords = [int(coords[idx]) + int(offset[idx]) for idx in range(dimension)]
        if "periodic" in boundary_rule_id:
            next_coords = [_periodic_coord(next_coords[idx], periods[idx]) for idx in range(dimension)]
        out.append(_format_grid_cell_key(next_coords))
    return sorted(set(out))


def _wrapped_delta(delta: int, period: int) -> int:
    if int(period) <= 0:
        return abs(int(delta))
    raw = abs(int(delta))
    return min(raw, abs(int(period) - raw))


def _metric_distance(coords_a: Sequence[int], coords_b: Sequence[int], topology_row: Mapping[str, object], metric_row: Mapping[str, object]) -> int:
    metric_kind = str(_as_map(metric_row).get("metric_kind", "euclidean")).strip().lower()
    params = _as_map(_as_map(metric_row).get("parameters"))
    deltas = [int(coords_a[idx]) - int(coords_b[idx]) for idx in range(min(len(coords_a), len(coords_b)))]

    if metric_kind == "torus_wrap":
        raw_period = params.get("fundamental_period_mm", 0)
        if isinstance(raw_period, list):
            periods = [_as_int(value, 0) for value in raw_period[: len(deltas)]]
        else:
            periods = [_as_int(raw_period, 0)] * len(deltas)
        squared = sum(int(_wrapped_delta(delta, periods[idx])) ** 2 for idx, delta in enumerate(deltas))
        return int(math.isqrt(max(0, int(squared))))

    if metric_kind == "spherical_stub":
        radius_mm = max(1, _as_int(params.get("radius_mm", 6371000000), 6371000000))
        lat_a = float(int(coords_a[0])) / 1000.0
        lon_a = float(int(coords_a[1] if len(coords_a) > 1 else 0)) / 1000.0
        lat_b = float(int(coords_b[0])) / 1000.0
        lon_b = float(int(coords_b[1] if len(coords_b) > 1 else 0)) / 1000.0
        dlat = math.radians(lat_b - lat_a)
        dlon = math.radians(lon_b - lon_a)
        lat_a_rad = math.radians(lat_a)
        lat_b_rad = math.radians(lat_b)
        hav = (math.sin(dlat * 0.5) ** 2) + math.cos(lat_a_rad) * math.cos(lat_b_rad) * (math.sin(dlon * 0.5) ** 2)
        angle = 2.0 * math.asin(min(1.0, math.sqrt(max(0.0, hav))))
        return int(round(float(radius_mm) * float(angle)))

    if metric_kind == "custom":
        base = int(math.isqrt(max(0, sum(int(delta) * int(delta) for delta in deltas))))
        curvature = abs(_as_int(params.get("curvature_permille", 0), 0))
        if curvature <= 0:
            return base
        return int(base + ((base * curvature) // 10000))

    squared = sum(int(delta) * int(delta) for delta in deltas)
    return int(math.isqrt(max(0, int(squared))))


def _rotation_radians(orientation_mdeg: Mapping[str, object]) -> Tuple[float, float, float]:
    yaw = math.radians(float(_as_int(_as_map(orientation_mdeg).get("yaw", 0), 0)) / 1000.0)
    pitch = math.radians(float(_as_int(_as_map(orientation_mdeg).get("pitch", 0), 0)) / 1000.0)
    roll = math.radians(float(_as_int(_as_map(orientation_mdeg).get("roll", 0), 0)) / 1000.0)
    return yaw, pitch, roll


def _rot_x(x_value: float, y_value: float, z_value: float, angle_rad: float) -> Tuple[float, float, float]:
    cos_angle = math.cos(float(angle_rad))
    sin_angle = math.sin(float(angle_rad))
    return x_value, (y_value * cos_angle) - (z_value * sin_angle), (y_value * sin_angle) + (z_value * cos_angle)


def _rot_y(x_value: float, y_value: float, z_value: float, angle_rad: float) -> Tuple[float, float, float]:
    cos_angle = math.cos(float(angle_rad))
    sin_angle = math.sin(float(angle_rad))
    return (x_value * cos_angle) + (z_value * sin_angle), y_value, (-x_value * sin_angle) + (z_value * cos_angle)


def _rot_z(x_value: float, y_value: float, z_value: float, angle_rad: float) -> Tuple[float, float, float]:
    cos_angle = math.cos(float(angle_rad))
    sin_angle = math.sin(float(angle_rad))
    return (x_value * cos_angle) - (y_value * sin_angle), (x_value * sin_angle) + (y_value * cos_angle), z_value


def _perspective_projection(position: Sequence[int], projection_parameters: Mapping[str, object] | None) -> dict:
    params = _as_map(projection_parameters)
    camera_position = _normalize_position(_as_map(params.get("camera_position_mm")), 3)
    camera_orientation = _as_map(params.get("camera_orientation_mdeg"))
    viewport_width = max(16, _as_int(params.get("viewport_width", 1000), 1000))
    viewport_height = max(16, _as_int(params.get("viewport_height", 1000), 1000))
    fov_deg = max(20.0, min(120.0, float(_as_int(params.get("fov_deg", 60), 60))))

    x_value = float(int(position[0]) - int(camera_position[0]))
    y_value = float(int(position[1]) - int(camera_position[1]))
    z_value = float(int(position[2] if len(position) > 2 else 0) - int(camera_position[2]))

    yaw, pitch, roll = _rotation_radians(camera_orientation)
    x_value, y_value, z_value = _rot_z(x_value, y_value, z_value, -yaw)
    x_value, y_value, z_value = _rot_y(x_value, y_value, z_value, -pitch)
    x_value, y_value, z_value = _rot_x(x_value, y_value, z_value, -roll)

    depth = max(1.0, float(z_value))
    focal = (float(viewport_height) * 0.5) / math.tan(math.radians(fov_deg * 0.5))
    screen_x = (float(viewport_width) * 0.5) + (x_value * focal / depth)
    screen_y = (float(viewport_height) * 0.5) - (y_value * focal / depth)
    return {
        "x_px": int(round(screen_x)),
        "y_px": int(round(screen_y)),
        "depth_mm": int(round(depth)),
        "camera_space_mm": {
            "x": int(round(x_value)),
            "y": int(round(y_value)),
            "z": int(round(z_value)),
        },
    }


def geo_neighbors(
    cell_key: str,
    topology_profile_id: str,
    radius: int,
    metric_profile_id: str,
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    metric_token = str(metric_profile_id or "").strip() or _DEFAULT_METRIC_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
    metric_row = _metric_row(metric_token, registry_payload=metric_registry_payload)
    if not metric_row:
        return _missing_profile(profile_kind="metric_profile_id", profile_id=metric_token)

    radius_cap = max(0, _as_int(_as_map(_as_map(topology_row).get("extensions")).get("radius_cap", 16), 16))
    radius_value = max(0, min(_as_int(radius, 0), radius_cap))
    seed = {
        "query_kind": "neighbors",
        "cell_key": str(cell_key),
        "topology_profile_id": topology_token,
        "metric_profile_id": metric_token,
        "radius": int(radius_value),
    }
    cache_key = _query_cache_key("neighbors", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    atlas_neighbors = _atlas_neighbors(str(cell_key), topology_row, radius_value)
    if atlas_neighbors:
        neighbors = atlas_neighbors
    else:
        neighbors = _grid_neighbors(str(cell_key), topology_row, radius_value)
    outputs = {
        "neighbors": list(neighbors),
        "count": len(neighbors),
    }
    payload = {
        "result": "complete",
        "query_kind": "neighbors",
        "cell_key": str(cell_key),
        "topology_profile_id": topology_token,
        "metric_profile_id": metric_token,
        "radius": int(radius_value),
        "neighbors": list(neighbors),
        "count": len(neighbors),
        "query_record": _query_record("neighbors", seed, outputs),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def geo_distance(
    pos_a: Mapping[str, object] | None,
    pos_b: Mapping[str, object] | None,
    topology_profile_id: str,
    metric_profile_id: str,
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    metric_token = str(metric_profile_id or "").strip() or _DEFAULT_METRIC_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
    metric_row = _metric_row(metric_token, registry_payload=metric_registry_payload)
    if not metric_row:
        return _missing_profile(profile_kind="metric_profile_id", profile_id=metric_token)

    dimension = _dimension_from_topology(topology_row)
    coords_a = _normalize_position(pos_a, dimension)
    coords_b = _normalize_position(pos_b, dimension)
    seed = {
        "query_kind": "distance",
        "topology_profile_id": topology_token,
        "metric_profile_id": metric_token,
        "coords_a": list(coords_a),
        "coords_b": list(coords_b),
    }
    cache_key = _query_cache_key("distance", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    distance_mm = _metric_distance(coords_a, coords_b, topology_row, metric_row)
    outputs = {"distance_mm": int(distance_mm)}
    payload = {
        "result": "complete",
        "query_kind": "distance",
        "topology_profile_id": topology_token,
        "metric_profile_id": metric_token,
        "distance_mm": int(distance_mm),
        "query_record": _query_record("distance", seed, outputs),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def geo_transform(
    pos: Mapping[str, object] | None,
    from_chart: str,
    to_chart: str,
) -> dict:
    from_chart_token = str(from_chart or "").strip()
    to_chart_token = str(to_chart or "").strip()
    if not from_chart_token or not to_chart_token:
        return _refusal(message="from_chart and to_chart are required")
    payload = _as_map(pos)
    coords = _normalize_position(payload, max(2, len(_as_list(payload.get("coords"))) or 3))
    seed = {
        "query_kind": "transform",
        "from_chart": from_chart_token,
        "to_chart": to_chart_token,
        "coords": list(coords),
    }
    cache_key = _query_cache_key("transform", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    next_coords = list(coords)
    if from_chart_token != to_chart_token:
        if {from_chart_token, to_chart_token} == {"chart.atlas.north", "chart.atlas.south"}:
            if len(next_coords) > 1:
                next_coords[1] = -int(next_coords[1])

    outputs = {"position": _position_payload(next_coords, len(next_coords))}
    result = {
        "result": "complete",
        "query_kind": "transform",
        "from_chart": from_chart_token,
        "to_chart": to_chart_token,
        "position": outputs["position"],
        "query_record": _query_record("transform", seed, outputs),
        "deterministic_fingerprint": "",
    }
    result["deterministic_fingerprint"] = canonical_sha256(dict(result, deterministic_fingerprint=""))
    return _cache_store(cache_key, result)


def geo_project(
    pos: Mapping[str, object] | None,
    topology_profile_id: str,
    projection_profile_id: str,
    *,
    topology_registry_payload: Mapping[str, object] | None = None,
    projection_registry_payload: Mapping[str, object] | None = None,
    projection_request: Mapping[str, object] | None = None,
) -> dict:
    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    projection_token = str(projection_profile_id or "").strip() or _DEFAULT_PROJECTION_PROFILE_ID
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)
    projection_row = _projection_row(projection_token, registry_payload=projection_registry_payload)
    if not projection_row:
        return _missing_profile(profile_kind="projection_profile_id", profile_id=projection_token)

    dimension = _dimension_from_topology(topology_row)
    coords = _normalize_position(pos, max(3, dimension))
    request = _as_map(projection_request)
    params = dict(_as_map(projection_row.get("parameters")))
    params.update(request)
    seed = {
        "query_kind": "project",
        "topology_profile_id": topology_token,
        "projection_profile_id": projection_token,
        "coords": list(coords),
        "projection_request": dict(sorted(params.items(), key=lambda item: str(item[0]))),
    }
    cache_key = _query_cache_key("project", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    projection_kind = str(projection_row.get("projection_kind", "ortho_2d")).strip().lower()
    if projection_kind == "ortho_2d":
        projected = {
            "x_mm": int(coords[0]),
            "y_mm": int(coords[1] if len(coords) > 1 else 0),
            "depth_mm": int(coords[2] if len(coords) > 2 else 0),
        }
    elif projection_kind == "atlas_unwrap":
        projected = {
            "u_mm": int(coords[0]),
            "v_mm": int(coords[1] if len(coords) > 1 else 0),
            "chart_id": str(request.get("chart_id", _as_map(pos).get("chart_id", ""))),
        }
    elif projection_kind == "slice_nd_stub":
        keep_axes = _as_list(params.get("keep_axes")) or ["x", "y", "z"]
        axis_lookup = dict(zip(_axis_labels(len(coords)), coords))
        projected = dict((str(axis), int(axis_lookup.get(str(axis), 0))) for axis in _sorted_strings(keep_axes)[:3])
        projected["slice_axes"] = _sorted_strings(params.get("slice_axes"))
    else:
        projected = _perspective_projection(coords[:3], params)

    outputs = {"projected_position": dict(projected)}
    payload = {
        "result": "complete",
        "query_kind": "project",
        "topology_profile_id": topology_token,
        "projection_profile_id": projection_token,
        "projection_kind": projection_kind,
        "projected_position": dict(projected),
        "query_record": _query_record("project", seed, outputs),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)


def geo_partition_cell_key(
    pos: Mapping[str, object] | None,
    partition_profile_id: str,
    *,
    topology_profile_id: str = "",
    partition_registry_payload: Mapping[str, object] | None = None,
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    partition_token = str(partition_profile_id or "").strip() or _DEFAULT_PARTITION_PROFILE_ID
    topology_token = str(topology_profile_id or "").strip() or _DEFAULT_TOPOLOGY_PROFILE_ID
    partition_row = _partition_row(partition_token, registry_payload=partition_registry_payload)
    if not partition_row:
        return _missing_profile(profile_kind="partition_profile_id", profile_id=partition_token)
    topology_row = _topology_row(topology_token, registry_payload=topology_registry_payload)
    if not topology_row:
        return _missing_profile(profile_kind="topology_profile_id", profile_id=topology_token)

    dimension = _dimension_from_topology(topology_row)
    coords = _normalize_position(pos, dimension)
    params = _as_map(partition_row.get("parameters"))
    partition_kind = str(partition_row.get("partition_kind", "grid")).strip().lower()
    cell_size_mm = max(1, _as_int(params.get("cell_size_mm", 10000), 10000))
    seed = {
        "query_kind": "partition_cell_key",
        "partition_profile_id": partition_token,
        "topology_profile_id": topology_token,
        "coords": list(coords),
    }
    cache_key = _query_cache_key("partition_cell_key", seed)
    cached = _cache_lookup(cache_key)
    if cached is not None:
        return cached

    if partition_kind == "atlas":
        chart_id = str(_as_map(pos).get("chart_id", "default")).strip() or "default"
        u_idx = int(math.floor(float(coords[0]) / float(cell_size_mm)))
        v_idx = int(math.floor(float(coords[1] if len(coords) > 1 else 0) / float(cell_size_mm)))
        cell_key = _format_atlas_cell_key(chart_id, u_idx, v_idx)
    else:
        cell_coords = [int(math.floor(float(value) / float(cell_size_mm))) for value in coords]
        cell_key = _format_grid_cell_key(cell_coords)

    outputs = {"cell_key": str(cell_key)}
    payload = {
        "result": "complete",
        "query_kind": "partition_cell_key",
        "partition_profile_id": partition_token,
        "topology_profile_id": topology_token,
        "cell_key": str(cell_key),
        "query_record": {
            "query_kind": "partition_cell_key",
            "inputs_hash": canonical_sha256(seed),
            "outputs_hash": canonical_sha256(outputs),
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        "deterministic_fingerprint": "",
    }
    payload["query_record"]["deterministic_fingerprint"] = canonical_sha256(
        dict(payload["query_record"], deterministic_fingerprint="")
    )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return _cache_store(cache_key, payload)
