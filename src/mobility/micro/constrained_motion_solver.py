"""Deterministic MOB-6 constrained micro motion helpers."""

from __future__ import annotations

import math
from typing import Dict, List, Mapping

from src.geo import geo_distance
from src.models.model_engine import compute_derailment_threshold_units, compute_lateral_accel_units
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_DIRECTIONS = {"forward", "back"}


class MicroMotionError(ValueError):
    """Deterministic micro motion refusal/error."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda token: str(token)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _point_mm(value: object) -> dict | None:
    if not isinstance(value, Mapping):
        return None
    return {
        "x": int(_as_int(value.get("x", 0), 0)),
        "y": int(_as_int(value.get("y", 0), 0)),
        "z": int(_as_int(value.get("z", 0), 0)),
    }


def _geo_distance_mm(a: Mapping[str, object], b: Mapping[str, object]) -> int:
    distance_row = geo_distance(a, b, "geo.topology.r3_infinite", "geo.metric.euclidean")
    return int(max(0, _as_int(distance_row.get("distance_mm", 0), 0)))


def _normalize_direction(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_DIRECTIONS:
        return token
    return "forward"


def _geometry_points_mm(geometry_row: Mapping[str, object] | None) -> List[dict]:
    row = dict(geometry_row or {})
    parameters = _as_map(row.get("parameters"))
    for key in ("control_points_mm", "points_mm", "path_points_mm"):
        rows = [dict(item) for item in list(parameters.get(key) or []) if isinstance(item, Mapping)]
        points = [_point_mm(item) for item in rows]
        points = [dict(item) for item in points if isinstance(item, Mapping)]
        if points:
            return points
    start_mm = _point_mm(parameters.get("start_mm"))
    end_mm = _point_mm(parameters.get("end_mm"))
    if start_mm and end_mm:
        return [start_mm, end_mm]
    return []


def _length_from_points_mm(points: List[Mapping[str, object]]) -> int:
    if len(points) < 2:
        return 1
    total = 0
    for idx in range(1, len(points)):
        prev = dict(points[idx - 1])
        cur = dict(points[idx])
        total += _geo_distance_mm(prev, cur)
    return int(max(1, total))


def geometry_length_mm(*, geometry_row: Mapping[str, object] | None, metric_row: Mapping[str, object] | None) -> int:
    metric = dict(metric_row or {})
    token = int(max(0, _as_int(metric.get("length_mm", 0), 0)))
    if token > 0:
        return token
    return _length_from_points_mm(_geometry_points_mm(geometry_row))


def geometry_heading_yaw_mdeg(*, geometry_row: Mapping[str, object] | None, direction: str = "forward") -> int:
    points = _geometry_points_mm(geometry_row)
    if len(points) < 2:
        return 0
    first = dict(points[0])
    last = dict(points[-1])
    dx = int(_as_int(last.get("x", 0), 0)) - int(_as_int(first.get("x", 0), 0))
    dy = int(_as_int(last.get("y", 0), 0)) - int(_as_int(first.get("y", 0), 0))
    angle_rad = math.atan2(float(dy), float(dx))
    yaw_mdeg = int(round(math.degrees(angle_rad) * 1000.0))
    if _normalize_direction(direction) == "back":
        yaw_mdeg = int(yaw_mdeg + 180000)
    return int(yaw_mdeg % 360000)


def curvature_radius_mm(metric_row: Mapping[str, object] | None) -> int:
    metric = dict(metric_row or {})
    radius = int(max(0, _as_int(metric.get("min_curvature_radius_mm", 0), 0)))
    if radius > 0:
        return radius
    return 1_000_000_000


def build_micro_motion_state(
    *,
    vehicle_id: str,
    geometry_id: str,
    s_param: int,
    velocity: int,
    acceleration: int,
    direction: str,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "vehicle_id": str(vehicle_id).strip(),
        "geometry_id": str(geometry_id).strip(),
        "s_param": int(max(0, _as_int(s_param, 0))),
        "velocity": int(_as_int(velocity, 0)),
        "acceleration": int(_as_int(acceleration, 0)),
        "direction": _normalize_direction(direction),
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_micro_motion_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("vehicle_id", ""))):
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        geometry_id = str(row.get("geometry_id", "")).strip()
        if (not vehicle_id) or (not geometry_id):
            continue
        out[vehicle_id] = build_micro_motion_state(
            vehicle_id=vehicle_id,
            geometry_id=geometry_id,
            s_param=_as_int(row.get("s_param", 0), 0),
            velocity=_as_int(row.get("velocity", 0), 0),
            acceleration=_as_int(row.get("acceleration", 0), 0),
            direction=str(row.get("direction", "forward")).strip() or "forward",
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def micro_motion_rows_by_vehicle_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_micro_motion_state_rows(rows)
    return dict((str(row.get("vehicle_id", "")).strip(), dict(row)) for row in normalized if str(row.get("vehicle_id", "")).strip())


def deterministic_coupling_constraint_id(
    *,
    vehicle_a_id: str,
    vehicle_b_id: str,
    coupling_type_id: str,
    created_tick_bucket: int,
) -> str:
    left, right = sorted([str(vehicle_a_id or "").strip(), str(vehicle_b_id or "").strip()])
    digest = canonical_sha256(
        {
            "vehicle_a_id": left,
            "vehicle_b_id": right,
            "coupling_type_id": str(coupling_type_id or "").strip(),
            "created_tick_bucket": int(max(0, _as_int(created_tick_bucket, 0))),
        }
    )
    return "constraint.coupling.{}".format(digest[:16])


def build_coupling_constraint(
    *,
    constraint_id: str,
    vehicle_a_id: str,
    vehicle_b_id: str,
    coupling_type_id: str,
    active: bool,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    left, right = sorted([str(vehicle_a_id).strip(), str(vehicle_b_id).strip()])
    payload = {
        "schema_version": "1.0.0",
        "constraint_id": str(constraint_id).strip(),
        "vehicle_a_id": left,
        "vehicle_b_id": right,
        "coupling_type_id": str(coupling_type_id).strip() or "coupler.basic",
        "active": bool(active),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_coupling_constraint_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("constraint_id", ""))):
        constraint_id = str(row.get("constraint_id", "")).strip()
        vehicle_a_id = str(row.get("vehicle_a_id", "")).strip()
        vehicle_b_id = str(row.get("vehicle_b_id", "")).strip()
        if (not constraint_id) or (not vehicle_a_id) or (not vehicle_b_id):
            continue
        out[constraint_id] = build_coupling_constraint(
            constraint_id=constraint_id,
            vehicle_a_id=vehicle_a_id,
            vehicle_b_id=vehicle_b_id,
            coupling_type_id=str(row.get("coupling_type_id", "coupler.basic")).strip() or "coupler.basic",
            active=bool(row.get("active", True)),
            extensions=_as_map(row.get("extensions")),
        )
    return [dict(out[key]) for key in sorted(out.keys())]


def coupling_constraint_rows_by_vehicle(rows: object) -> Dict[str, List[dict]]:
    normalized = normalize_coupling_constraint_rows(rows)
    out: Dict[str, List[dict]] = {}
    for row in normalized:
        left = str(row.get("vehicle_a_id", "")).strip()
        right = str(row.get("vehicle_b_id", "")).strip()
        if left:
            out.setdefault(left, []).append(dict(row))
        if right:
            out.setdefault(right, []).append(dict(row))
    for key in list(out.keys()):
        out[key] = sorted(out[key], key=lambda item: str(item.get("constraint_id", "")))
    return out


def derailment_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("derailment_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("derailment_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("derail_policy_id", ""))):
        policy_id = str(row.get("derail_policy_id", "")).strip()
        if not policy_id:
            continue
        ext = _as_map(row.get("extensions"))
        out[policy_id] = {
            "schema_version": "1.0.0",
            "derail_policy_id": policy_id,
            "threshold_model_id": str(ext.get("threshold_model_id", "threshold.lateral_accel.v1")).strip() or "threshold.lateral_accel.v1",
            "allow_stochastic": bool(ext.get("allow_stochastic", False)),
            "rng_stream_name": None if ext.get("rng_stream_name") is None else str(ext.get("rng_stream_name", "")).strip() or None,
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def resolve_derailment_policy(*, registry_payload: Mapping[str, object] | None, derail_policy_id: str) -> dict:
    rows = derailment_policy_rows_by_id(registry_payload)
    token = str(derail_policy_id or "").strip() or "derail.strict_threshold"
    row = dict(rows.get(token) or {})
    if row:
        return row
    return {
        "schema_version": "1.0.0",
        "derail_policy_id": "derail.strict_threshold",
        "threshold_model_id": "threshold.lateral_accel.v1",
        "allow_stochastic": False,
        "rng_stream_name": None,
        "extensions": {},
    }


def lateral_accel_units(*, velocity_mm_per_tick: int, radius_mm: int) -> int:
    return int(
        compute_lateral_accel_units(
            velocity_mm_per_tick=int(velocity_mm_per_tick),
            radius_mm=int(radius_mm),
        )
    )


def derailment_threshold_units(
    *,
    base_threshold: int,
    track_wear_permille: int,
    friction_permille: int,
    maintenance_permille: int,
) -> int:
    return int(
        compute_derailment_threshold_units(
            base_threshold=int(base_threshold),
            track_wear_permille=int(track_wear_permille),
            friction_permille=int(friction_permille),
            maintenance_permille=int(maintenance_permille),
        )
    )


def evaluate_derailment(
    *,
    velocity_mm_per_tick: int,
    radius_mm: int,
    base_threshold: int,
    track_wear_permille: int,
    friction_permille: int,
    maintenance_permille: int,
) -> dict:
    lateral = lateral_accel_units(
        velocity_mm_per_tick=int(velocity_mm_per_tick),
        radius_mm=int(radius_mm),
    )
    threshold = derailment_threshold_units(
        base_threshold=int(base_threshold),
        track_wear_permille=int(track_wear_permille),
        friction_permille=int(friction_permille),
        maintenance_permille=int(maintenance_permille),
    )
    return {
        "lateral_accel_units": int(lateral),
        "threshold_units": int(threshold),
        "derail": bool(int(lateral) > int(threshold)),
    }


def _speed_cap_from_effects(effect_modifiers: Mapping[str, object] | None) -> int:
    payload = _as_map(effect_modifiers)
    cap = int(max(100, min(5000, _as_int(payload.get("speed_cap_mm_per_tick", 1000), 1000))))
    cap_permille = int(max(100, min(1000, _as_int(payload.get("max_speed_permille", 1000), 1000))))
    return int(max(1, (cap * cap_permille) // 1000))


def _friction_permille(*, field_values: Mapping[str, object] | None, effect_modifiers: Mapping[str, object] | None) -> int:
    field_payload = _as_map(field_values)
    effect_payload = _as_map(effect_modifiers)
    from_field = int(max(100, min(1200, _as_int(field_payload.get("friction_permille", 1000), 1000))))
    from_effect = int(max(100, min(1200, _as_int(effect_payload.get("traction_permille", 1000), 1000))))
    return int(min(from_field, from_effect))


def step_micro_motion(
    *,
    motion_row: Mapping[str, object],
    geometry_row: Mapping[str, object] | None,
    metric_row: Mapping[str, object] | None,
    control_input: Mapping[str, object] | None,
    effect_modifiers: Mapping[str, object] | None,
    field_values: Mapping[str, object] | None,
    dt_ticks: int,
    current_tick: int,
) -> dict:
    row = dict(motion_row or {})
    control = _as_map(control_input)
    effects = _as_map(effect_modifiers)
    fields = _as_map(field_values)

    s0 = int(max(0, _as_int(row.get("s_param", 0), 0)))
    v0 = int(_as_int(row.get("velocity", 0), 0))
    direction = _normalize_direction(row.get("direction"))

    throttle = int(max(0, min(1000, _as_int(control.get("throttle_permille", 0), 0))))
    brake = int(max(0, min(1000, _as_int(control.get("brake_permille", 0), 0))))
    max_accel = int(max(1, _as_int(control.get("max_accel_mm_per_tick2", 16), 16)))
    max_brake = int(max(1, _as_int(control.get("max_brake_mm_per_tick2", 24), 24)))

    desired = int((throttle * max_accel) // 1000) - int((brake * max_brake) // 1000)
    friction_permille = _friction_permille(field_values=fields, effect_modifiers=effects)
    if desired > 0:
        desired = int((desired * friction_permille) // 1000)

    dt = int(max(1, _as_int(dt_ticks, 1)))
    speed_cap = _speed_cap_from_effects(effects)
    v1 = int(v0 + desired * dt)
    if v1 > 0:
        v1 = int(min(v1, speed_cap))
    elif v1 < 0:
        v1 = int(max(v1, -speed_cap))

    if direction == "forward" and v1 < 0:
        v1 = 0
    if direction == "back" and v1 > 0:
        v1 = 0

    length_mm = geometry_length_mm(geometry_row=geometry_row, metric_row=metric_row)
    s1 = int(s0 + v1 * dt)
    blocked = False
    if s1 < 0:
        s1 = 0
        v1 = 0
        blocked = True
    if s1 > length_mm:
        s1 = int(length_mm)
        v1 = 0
        blocked = True

    next_direction = direction
    if v1 > 0:
        next_direction = "forward"
    elif v1 < 0:
        next_direction = "back"

    updated = build_micro_motion_state(
        vehicle_id=str(row.get("vehicle_id", "")).strip(),
        geometry_id=str(row.get("geometry_id", "")).strip(),
        s_param=int(s1),
        velocity=int(v1),
        acceleration=int(desired),
        direction=next_direction,
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=_as_map(row.get("extensions")),
    )
    telemetry = {
        "speed_cap_mm_per_tick": int(speed_cap),
        "friction_permille": int(friction_permille),
        "blocked": bool(blocked),
        "length_mm": int(length_mm),
        "heading_yaw_mdeg": int(geometry_heading_yaw_mdeg(geometry_row=geometry_row, direction=next_direction)),
    }
    return {
        "motion_state": dict(updated),
        "telemetry": telemetry,
    }


def apply_consist_offsets(
    *,
    lead_row: Mapping[str, object],
    trailing_rows: List[Mapping[str, object]],
    offset_mm_by_vehicle_id: Mapping[str, object] | None,
    geometry_length_mm_value: int,
    current_tick: int,
) -> List[dict]:
    lead = dict(lead_row or {})
    s_lead = int(max(0, _as_int(lead.get("s_param", 0), 0)))
    velocity = int(_as_int(lead.get("velocity", 0), 0))
    direction = _normalize_direction(lead.get("direction"))
    length = int(max(1, _as_int(geometry_length_mm_value, 1)))
    offsets = _as_map(offset_mm_by_vehicle_id)
    out: List[dict] = []
    for row in sorted((dict(item) for item in list(trailing_rows or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("vehicle_id", ""))):
        vehicle_id = str(row.get("vehicle_id", "")).strip()
        if not vehicle_id:
            continue
        offset_mm = int(max(0, _as_int(offsets.get(vehicle_id, 0), 0)))
        s_value = int(max(0, min(length, s_lead - offset_mm)))
        out.append(
            build_micro_motion_state(
                vehicle_id=vehicle_id,
                geometry_id=str(row.get("geometry_id", "")).strip(),
                s_param=s_value,
                velocity=velocity,
                acceleration=int(_as_int(lead.get("acceleration", 0), 0)),
                direction=direction,
                last_update_tick=int(max(0, _as_int(current_tick, 0))),
                extensions=_as_map(row.get("extensions")),
            )
        )
    return out


__all__ = [
    "MicroMotionError",
    "apply_consist_offsets",
    "build_coupling_constraint",
    "build_micro_motion_state",
    "coupling_constraint_rows_by_vehicle",
    "curvature_radius_mm",
    "derailment_policy_rows_by_id",
    "derailment_threshold_units",
    "deterministic_coupling_constraint_id",
    "evaluate_derailment",
    "geometry_heading_yaw_mdeg",
    "geometry_length_mm",
    "lateral_accel_units",
    "micro_motion_rows_by_vehicle_id",
    "normalize_coupling_constraint_rows",
    "normalize_micro_motion_state_rows",
    "resolve_derailment_policy",
    "step_micro_motion",
]
