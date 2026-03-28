"""Deterministic MOB-1 GuideGeometry helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from geo import geo_distance
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_GEOMETRY_TYPES = {
    "geo.spline1D",
    "geo.corridor2D",
    "geo.volume3D",
    "geo.orbital_path",
    "geo.field_following",
}
_VALID_JUNCTION_TYPES = {
    "junc.endpoint",
    "junc.switch",
    "junc.merge",
    "junc.split",
    "junc.station",
}
_VALID_SNAP_POLICIES = {
    "snap.none",
    "snap.endpoint",
    "snap.grid",
    "snap.spec_compliant",
}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
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


def _point3(value: object) -> dict:
    payload = _as_map(value)
    return {
        "x": int(_as_int(payload.get("x", 0), 0)),
        "y": int(_as_int(payload.get("y", 0), 0)),
        "z": int(_as_int(payload.get("z", 0), 0)),
    }


def _geo_distance_mm(a: Mapping[str, object], b: Mapping[str, object]) -> int:
    distance_row = geo_distance(a, b, "geo.topology.r3_infinite", "geo.metric.euclidean")
    return int(max(0, _as_int(distance_row.get("distance_mm", 0), 0)))


def _normalize_geometry_type_id(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_GEOMETRY_TYPES:
        return token
    return "geo.spline1D"


def _normalize_junction_type_id(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_JUNCTION_TYPES:
        return token
    return "junc.endpoint"


def _normalize_snap_policy_id(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_SNAP_POLICIES:
        return token
    return "snap.none"


def _geometry_points(parameters: Mapping[str, object] | None) -> List[dict]:
    payload = _as_map(parameters)
    out: List[dict] = []
    for key in ("control_points_mm", "points_mm", "path_points_mm"):
        rows = payload.get(key)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, Mapping):
                    out.append(_point3(row))
        if out:
            break
    if out:
        return out
    start = payload.get("start_mm")
    end = payload.get("end_mm")
    if isinstance(start, Mapping) and isinstance(end, Mapping):
        return [_point3(start), _point3(end)]
    return []


def _bounds_from_points(points: Sequence[Mapping[str, object]]) -> dict | None:
    rows = [_point3(row) for row in list(points or [])]
    if not rows:
        return None
    xs = [int(row.get("x", 0)) for row in rows]
    ys = [int(row.get("y", 0)) for row in rows]
    zs = [int(row.get("z", 0)) for row in rows]
    return {
        "min_mm": {"x": min(xs), "y": min(ys), "z": min(zs)},
        "max_mm": {"x": max(xs), "y": max(ys), "z": max(zs)},
    }


def geometry_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("geometry_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("geometry_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("geometry_type_id", ""))):
        geometry_type_id = str(row.get("geometry_type_id", "")).strip()
        if not geometry_type_id:
            continue
        out[geometry_type_id] = {
            "schema_version": "1.0.0",
            "geometry_type_id": geometry_type_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def junction_type_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("junction_types")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("junction_types")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("junction_type_id", ""))):
        junction_type_id = str(row.get("junction_type_id", "")).strip()
        if not junction_type_id:
            continue
        out[junction_type_id] = {
            "schema_version": "1.0.0",
            "junction_type_id": junction_type_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def geometry_snap_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("snap_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("snap_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("snap_policy_id", ""))):
        snap_policy_id = str(row.get("snap_policy_id", "")).strip()
        if not snap_policy_id:
            continue
        out[snap_policy_id] = {
            "schema_version": "1.0.0",
            "snap_policy_id": snap_policy_id,
            "schema_ref": str(row.get("schema_ref", "")).strip(),
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_geometry_id(
    *,
    formalization_id: str,
    candidate_id: str,
    spec_id: str | None,
    created_tick_bucket: int,
) -> str:
    digest = canonical_sha256(
        {
            "formalization_id": str(formalization_id or "").strip(),
            "candidate_id": str(candidate_id or "").strip(),
            "spec_id": str(spec_id or "").strip(),
            "created_tick_bucket": int(max(0, _as_int(created_tick_bucket, 0))),
        }
    )
    return "geometry.{}".format(digest[:16])


def build_guide_geometry(
    *,
    geometry_id: str,
    geometry_type_id: str,
    parent_spatial_id: str,
    spec_id: str | None = None,
    parameters: Mapping[str, object] | None = None,
    bounds: Mapping[str, object] | None = None,
    junction_refs: object = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    params = _canon(_as_map(parameters))
    points = _geometry_points(params)
    derived_bounds = _bounds_from_points(points)
    payload = {
        "schema_version": "1.0.0",
        "geometry_id": str(geometry_id).strip(),
        "geometry_type_id": _normalize_geometry_type_id(geometry_type_id),
        "parent_spatial_id": str(parent_spatial_id).strip(),
        "spec_id": None if spec_id is None else str(spec_id).strip() or None,
        "parameters": params,
        "bounds": _canon(_as_map(bounds)) if isinstance(bounds, Mapping) else derived_bounds,
        "junction_refs": _sorted_tokens(junction_refs),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_guide_geometry_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("geometry_id", ""))):
        geometry_id = str(row.get("geometry_id", "")).strip()
        parent_spatial_id = str(row.get("parent_spatial_id", "")).strip()
        if (not geometry_id) or (not parent_spatial_id):
            continue
        out[geometry_id] = build_guide_geometry(
            geometry_id=geometry_id,
            geometry_type_id=str(row.get("geometry_type_id", "")).strip(),
            parent_spatial_id=parent_spatial_id,
            spec_id=(None if row.get("spec_id") is None else str(row.get("spec_id", "")).strip() or None),
            parameters=_as_map(row.get("parameters")),
            bounds=_as_map(row.get("bounds")),
            junction_refs=row.get("junction_refs"),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def build_junction(
    *,
    junction_id: str,
    parent_spatial_id: str,
    connected_geometry_ids: object,
    junction_type_id: str,
    state_machine_id: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "junction_id": str(junction_id).strip(),
        "parent_spatial_id": str(parent_spatial_id).strip(),
        "connected_geometry_ids": _sorted_tokens(connected_geometry_ids),
        "junction_type_id": _normalize_junction_type_id(junction_type_id),
        "state_machine_id": None if state_machine_id is None else str(state_machine_id).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_junction_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("junction_id", ""))):
        junction_id = str(row.get("junction_id", "")).strip()
        parent_spatial_id = str(row.get("parent_spatial_id", "")).strip()
        connected = _sorted_tokens(row.get("connected_geometry_ids"))
        if (not junction_id) or (not parent_spatial_id) or (not connected):
            continue
        out[junction_id] = build_junction(
            junction_id=junction_id,
            parent_spatial_id=parent_spatial_id,
            connected_geometry_ids=connected,
            junction_type_id=str(row.get("junction_type_id", "")).strip(),
            state_machine_id=(None if row.get("state_machine_id") is None else str(row.get("state_machine_id", "")).strip() or None),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def build_geometry_candidate(
    *,
    candidate_id: str,
    formalization_id: str,
    geometry_preview_ref: str,
    proposed_spec_id: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "candidate_id": str(candidate_id).strip(),
        "formalization_id": str(formalization_id).strip(),
        "geometry_preview_ref": str(geometry_preview_ref).strip(),
        "proposed_spec_id": None if proposed_spec_id is None else str(proposed_spec_id).strip() or None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_geometry_candidate_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("candidate_id", ""))):
        candidate_id = str(row.get("candidate_id", "")).strip()
        formalization_id = str(row.get("formalization_id", "")).strip()
        preview_ref = str(row.get("geometry_preview_ref", "")).strip()
        if (not candidate_id) or (not formalization_id) or (not preview_ref):
            continue
        out[candidate_id] = build_geometry_candidate(
            candidate_id=candidate_id,
            formalization_id=formalization_id,
            geometry_preview_ref=preview_ref,
            proposed_spec_id=(None if row.get("proposed_spec_id") is None else str(row.get("proposed_spec_id", "")).strip() or None),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def _snap_to_grid(point: Mapping[str, object], grid_mm: int) -> dict:
    grid = max(1, _as_int(grid_mm, 1000))
    p = _point3(point)
    return {
        "x": int(round(float(p["x"]) / float(grid))) * int(grid),
        "y": int(round(float(p["y"]) / float(grid))) * int(grid),
        "z": int(round(float(p["z"]) / float(grid))) * int(grid),
    }


def _endpoint_candidates(existing_geometry_rows: object) -> List[Tuple[str, int, dict]]:
    rows = normalize_guide_geometry_rows(existing_geometry_rows)
    out: List[Tuple[str, int, dict]] = []
    for row in rows:
        geometry_id = str(row.get("geometry_id", "")).strip()
        points = _geometry_points(_as_map(row.get("parameters")))
        if not geometry_id or not points:
            continue
        out.append((geometry_id, 0, _point3(points[0])))
        if len(points) > 1:
            out.append((geometry_id, 1, _point3(points[-1])))
    return sorted(out, key=lambda item: (item[0], item[1], item[2]["x"], item[2]["y"], item[2]["z"]))


def _snap_to_endpoint(point: Mapping[str, object], endpoints: Sequence[Tuple[str, int, dict]], tolerance_mm: int) -> dict:
    tol = max(0, _as_int(tolerance_mm, 0))
    if tol <= 0 or not endpoints:
        return _point3(point)
    best = None
    for geometry_id, endpoint_index, endpoint_point in endpoints:
        distance_mm = _geo_distance_mm(point, endpoint_point)
        candidate = (int(distance_mm), str(geometry_id), int(endpoint_index), _point3(endpoint_point))
        if (best is None) or (candidate < best):
            best = candidate
    if best is None:
        return _point3(point)
    if int(best[0]) <= int(tol):
        return _point3(best[3])
    return _point3(point)


def snap_geometry_parameters(
    *,
    parameters: Mapping[str, object] | None,
    snap_policy_id: str,
    existing_geometry_rows: object,
    snap_policy_registry: Mapping[str, object] | None = None,
    spec_tolerance_mm: int = 0,
) -> dict:
    policy_id = _normalize_snap_policy_id(snap_policy_id)
    params = _canon(_as_map(parameters))
    points = _geometry_points(params)
    if not points:
        return params
    policy_rows = geometry_snap_policy_rows_by_id(snap_policy_registry)
    policy_row = dict(policy_rows.get(policy_id) or {})
    policy_ext = _as_map(policy_row.get("extensions"))
    tolerance_mm = max(0, _as_int(spec_tolerance_mm, 0))
    if tolerance_mm <= 0:
        tolerance_mm = max(0, _as_int(policy_ext.get("endpoint_tolerance_mm", 500), 500))
    grid_mm = max(1, _as_int(policy_ext.get("grid_size_mm", 1000), 1000))
    endpoints = _endpoint_candidates(existing_geometry_rows)
    snapped_points = [_point3(row) for row in points]
    if policy_id in {"snap.grid", "snap.spec_compliant"}:
        snapped_points[0] = _snap_to_grid(snapped_points[0], grid_mm)
        snapped_points[-1] = _snap_to_grid(snapped_points[-1], grid_mm)
    if policy_id in {"snap.endpoint", "snap.spec_compliant"}:
        snapped_points[0] = _snap_to_endpoint(snapped_points[0], endpoints, tolerance_mm)
        snapped_points[-1] = _snap_to_endpoint(snapped_points[-1], endpoints, tolerance_mm)
    out = _as_map(params)
    out["control_points_mm"] = [dict(row) for row in snapped_points]
    return _canon(out)


def _length_mm(points: Sequence[Mapping[str, object]]) -> int:
    rows = [_point3(row) for row in points]
    if len(rows) < 2:
        return 0
    total = 0
    for idx in range(len(rows) - 1):
        a = rows[idx]
        b = rows[idx + 1]
        total += _geo_distance_mm(a, b)
    return int(max(0, total))


def _curvature_summary(points: Sequence[Mapping[str, object]]) -> dict:
    rows = [_point3(row) for row in points]
    if len(rows) < 3:
        return {
            "min_curvature_radius_mm": 0,
            "band_low_count": 0,
            "band_medium_count": 0,
            "band_high_count": 0,
        }
    min_radius = None
    low = 0
    medium = 0
    high = 0
    for idx in range(len(rows) - 2):
        a = rows[idx]
        b = rows[idx + 1]
        c = rows[idx + 2]
        v1 = (int(b["x"]) - int(a["x"]), int(b["y"]) - int(a["y"]), int(b["z"]) - int(a["z"]))
        v2 = (int(c["x"]) - int(b["x"]), int(c["y"]) - int(b["y"]), int(c["z"]) - int(b["z"]))
        len1 = _geo_distance_mm({"x": 0, "y": 0, "z": 0}, {"x": v1[0], "y": v1[1], "z": v1[2]})
        len2 = _geo_distance_mm({"x": 0, "y": 0, "z": 0}, {"x": v2[0], "y": v2[1], "z": v2[2]})
        if len1 <= 0 or len2 <= 0:
            continue
        cross_x = int(v1[1] * v2[2] - v1[2] * v2[1])
        cross_y = int(v1[2] * v2[0] - v1[0] * v2[2])
        cross_z = int(v1[0] * v2[1] - v1[1] * v2[0])
        cross_mag = _geo_distance_mm({"x": 0, "y": 0, "z": 0}, {"x": cross_x, "y": cross_y, "z": cross_z})
        denom = int(max(1, len1 + len2))
        turn_permille = int(min(1000, (cross_mag * 1000) // max(1, denom)))
        if turn_permille <= 150:
            low += 1
        elif turn_permille <= 400:
            medium += 1
        else:
            high += 1
        seg_len = int(min(len1, len2))
        radius = int(max(1, (seg_len * 1000) // max(1, turn_permille)))
        if min_radius is None or radius < min_radius:
            min_radius = radius
    return {
        "min_curvature_radius_mm": int(max(0, _as_int(min_radius, 0))),
        "band_low_count": int(low),
        "band_medium_count": int(medium),
        "band_high_count": int(high),
    }


def build_geometry_metric_row(
    *,
    geometry_row: Mapping[str, object],
    current_tick: int,
    max_cost_units: int,
    cost_units_per_metric: int = 1,
) -> dict:
    row = build_guide_geometry(
        geometry_id=str(geometry_row.get("geometry_id", "")).strip(),
        geometry_type_id=str(geometry_row.get("geometry_type_id", "")).strip(),
        parent_spatial_id=str(geometry_row.get("parent_spatial_id", "")).strip(),
        spec_id=(None if geometry_row.get("spec_id") is None else str(geometry_row.get("spec_id", "")).strip() or None),
        parameters=_as_map(geometry_row.get("parameters")),
        bounds=_as_map(geometry_row.get("bounds")),
        junction_refs=geometry_row.get("junction_refs"),
        extensions=_as_map(geometry_row.get("extensions")),
    )
    geometry_hash = canonical_sha256(dict(row, deterministic_fingerprint=""))
    points = _geometry_points(_as_map(row.get("parameters")))
    params = _as_map(row.get("parameters"))
    unit_cost = max(1, _as_int(cost_units_per_metric, 1))
    budget = max(0, _as_int(max_cost_units, 0))
    available_metrics = int(budget // unit_cost) if budget > 0 else 0

    length_mm = 0
    curvature = {"min_curvature_radius_mm": 0, "band_low_count": 0, "band_medium_count": 0, "band_high_count": 0}
    clearance = {"width_mm": 3000, "height_mm": 4000}
    metrics_attempted = 3
    metrics_computed = 0

    if available_metrics > 0:
        length_mm = _length_mm(points)
        metrics_computed += 1
    if available_metrics > 1:
        curvature = _curvature_summary(points)
        metrics_computed += 1
    if available_metrics > 2:
        clearance = {
            "width_mm": int(max(0, _as_int(params.get("clearance_width_mm", params.get("width_mm", 3000)), 3000))),
            "height_mm": int(max(0, _as_int(params.get("clearance_height_mm", params.get("height_mm", 4000)), 4000))),
        }
        metrics_computed += 1

    degraded = bool(metrics_computed < metrics_attempted)
    payload = {
        "schema_version": "1.0.0",
        "geometry_id": str(row.get("geometry_id", "")).strip(),
        "geometry_hash": geometry_hash,
        "computed_tick": int(max(0, _as_int(current_tick, 0))),
        "length_mm": int(max(0, _as_int(length_mm, 0))),
        "min_curvature_radius_mm": int(max(0, _as_int(curvature.get("min_curvature_radius_mm", 0), 0))),
        "curvature_bands": {
            "low": int(max(0, _as_int(curvature.get("band_low_count", 0), 0))),
            "medium": int(max(0, _as_int(curvature.get("band_medium_count", 0), 0))),
            "high": int(max(0, _as_int(curvature.get("band_high_count", 0), 0))),
        },
        "clearance_envelope": {
            "width_mm": int(max(0, _as_int(clearance.get("width_mm", 0), 0))),
            "height_mm": int(max(0, _as_int(clearance.get("height_mm", 0), 0))),
        },
        "cost_units_used": int(max(0, metrics_computed * unit_cost)),
        "degraded": bool(degraded),
        "degrade_reason": "degrade.geometry.metrics_budget" if degraded else None,
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_geometry_metric_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("geometry_id", ""))):
        geometry_id = str(row.get("geometry_id", "")).strip()
        geometry_hash = str(row.get("geometry_hash", "")).strip()
        if (not geometry_id) or (not geometry_hash):
            continue
        payload = {
            "schema_version": "1.0.0",
            "geometry_id": geometry_id,
            "geometry_hash": geometry_hash,
            "computed_tick": int(max(0, _as_int(row.get("computed_tick", 0), 0))),
            "length_mm": int(max(0, _as_int(row.get("length_mm", 0), 0))),
            "min_curvature_radius_mm": int(max(0, _as_int(row.get("min_curvature_radius_mm", 0), 0))),
            "curvature_bands": {
                "low": int(max(0, _as_int(_as_map(row.get("curvature_bands")).get("low", 0), 0))),
                "medium": int(max(0, _as_int(_as_map(row.get("curvature_bands")).get("medium", 0), 0))),
                "high": int(max(0, _as_int(_as_map(row.get("curvature_bands")).get("high", 0), 0))),
            },
            "clearance_envelope": {
                "width_mm": int(max(0, _as_int(_as_map(row.get("clearance_envelope")).get("width_mm", 0), 0))),
                "height_mm": int(max(0, _as_int(_as_map(row.get("clearance_envelope")).get("height_mm", 0), 0))),
            },
            "cost_units_used": int(max(0, _as_int(row.get("cost_units_used", 0), 0))),
            "degraded": bool(row.get("degraded", False)),
            "degrade_reason": None if row.get("degrade_reason") is None else str(row.get("degrade_reason", "")).strip() or None,
            "deterministic_fingerprint": "",
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        out[geometry_id] = payload
    return [dict(out[key]) for key in sorted(out.keys())]


__all__ = [
    "build_geometry_candidate",
    "build_geometry_metric_row",
    "build_guide_geometry",
    "build_junction",
    "deterministic_geometry_id",
    "geometry_snap_policy_rows_by_id",
    "geometry_type_rows_by_id",
    "junction_type_rows_by_id",
    "normalize_geometry_candidate_rows",
    "normalize_geometry_metric_rows",
    "normalize_guide_geometry_rows",
    "normalize_junction_rows",
    "snap_geometry_parameters",
]
