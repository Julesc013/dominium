"""Deterministic MOB-7 micro free-motion helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple

from src.meta.numeric import deterministic_divide
from tools.xstack.compatx.canonical_json import canonical_sha256


_VALID_CORRIDOR_ENFORCEMENT_MODES = {"clamp", "refuse", "warn"}


class FreeMotionError(ValueError):
    """Deterministic free-motion refusal/error."""

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


def _vector3_int(value: object, default_value: Mapping[str, object] | None = None) -> dict:
    payload = _as_map(value)
    fallback = _as_map(default_value)
    return {
        "x": int(_as_int(payload.get("x", fallback.get("x", 0)), fallback.get("x", 0))),
        "y": int(_as_int(payload.get("y", fallback.get("y", 0)), fallback.get("y", 0))),
        "z": int(_as_int(payload.get("z", fallback.get("z", 0)), fallback.get("z", 0))),
    }


def _normalize_corridor_mode(value: object) -> str:
    token = str(value or "").strip()
    if token in _VALID_CORRIDOR_ENFORCEMENT_MODES:
        return token
    return "clamp"


def _subject_id(*, subject_id: object, vehicle_id: object, agent_id: object) -> str:
    explicit = str(subject_id or "").strip()
    if explicit:
        return explicit
    vehicle_token = str(vehicle_id or "").strip()
    if vehicle_token:
        return vehicle_token
    return str(agent_id or "").strip()


def build_free_motion_state(
    *,
    subject_id: str | None = None,
    vehicle_id: str | None = None,
    agent_id: str | None = None,
    body_id: str,
    velocity: Mapping[str, object] | None,
    acceleration: Mapping[str, object] | None,
    corridor_geometry_id: str | None = None,
    volume_geometry_id: str | None = None,
    last_update_tick: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    vehicle_token = str(vehicle_id or "").strip() or None
    agent_token = str(agent_id or "").strip() or None
    if vehicle_token and agent_token:
        raise FreeMotionError(
            "refusal.mob.network_invalid",
            "free motion state requires vehicle_id xor agent_id",
            {"vehicle_id": vehicle_token, "agent_id": agent_token},
        )
    if not vehicle_token and not agent_token:
        raise FreeMotionError(
            "refusal.mob.network_invalid",
            "free motion state requires vehicle_id or agent_id",
            {"vehicle_id": vehicle_token, "agent_id": agent_token},
        )
    payload = {
        "schema_version": "1.0.0",
        "subject_id": _subject_id(subject_id=subject_id, vehicle_id=vehicle_token, agent_id=agent_token),
        "vehicle_id": vehicle_token,
        "agent_id": agent_token,
        "body_id": str(body_id or "").strip(),
        "velocity": _vector3_int(velocity, {"x": 0, "y": 0, "z": 0}),
        "acceleration": _vector3_int(acceleration, {"x": 0, "y": 0, "z": 0}),
        "corridor_geometry_id": None if corridor_geometry_id is None else str(corridor_geometry_id).strip() or None,
        "volume_geometry_id": None if volume_geometry_id is None else str(volume_geometry_id).strip() or None,
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if not str(payload.get("subject_id", "")).strip():
        raise FreeMotionError(
            "refusal.mob.network_invalid",
            "free motion state subject_id is empty",
            {"body_id": str(body_id or "").strip()},
        )
    if not str(payload.get("body_id", "")).strip():
        raise FreeMotionError(
            "refusal.mob.network_invalid",
            "free motion state body_id is required",
            {"subject_id": str(payload.get("subject_id", ""))},
        )
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_free_motion_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            str(item.get("subject_id", "")),
            str(item.get("vehicle_id", "")),
            str(item.get("agent_id", "")),
            str(item.get("body_id", "")),
        ),
    ):
        try:
            normalized = build_free_motion_state(
                subject_id=str(row.get("subject_id", "")).strip() or None,
                vehicle_id=(None if row.get("vehicle_id") is None else str(row.get("vehicle_id", "")).strip() or None),
                agent_id=(None if row.get("agent_id") is None else str(row.get("agent_id", "")).strip() or None),
                body_id=str(row.get("body_id", "")).strip(),
                velocity=_as_map(row.get("velocity")),
                acceleration=_as_map(row.get("acceleration")),
                corridor_geometry_id=(
                    None if row.get("corridor_geometry_id") is None else str(row.get("corridor_geometry_id", "")).strip() or None
                ),
                volume_geometry_id=(
                    None if row.get("volume_geometry_id") is None else str(row.get("volume_geometry_id", "")).strip() or None
                ),
                last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
                extensions=_as_map(row.get("extensions")),
            )
        except FreeMotionError:
            continue
        out[str(normalized.get("subject_id", "")).strip()] = dict(normalized)
    return [dict(out[key]) for key in sorted(out.keys())]


def free_motion_rows_by_subject_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_free_motion_state_rows(rows)
    return dict(
        (str(row.get("subject_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("subject_id", "")).strip()
    )


def free_motion_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("free_motion_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("free_motion_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if not policy_id:
            continue
        ext = _as_map(row.get("extensions"))
        out[policy_id] = {
            "schema_version": "1.0.0",
            "policy_id": policy_id,
            "max_speed": int(max(1, _as_int(ext.get("max_speed", 1200), 1200))),
            "max_accel": int(max(1, _as_int(ext.get("max_accel", 96), 96))),
            "traction_model_id": str(ext.get("traction_model_id", "traction.basic_friction")).strip() or "traction.basic_friction",
            "wind_model_id": str(ext.get("wind_model_id", "wind.basic_drift")).strip() or "wind.basic_drift",
            "wind_scale_permille": int(max(0, _as_int(ext.get("wind_scale_permille", 300), 300))),
            "corridor_enforcement_mode": _normalize_corridor_mode(ext.get("corridor_enforcement_mode", "clamp")),
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def traction_model_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("traction_models")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("traction_models")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("traction_model_id", ""))):
        model_id = str(row.get("traction_model_id", "")).strip()
        if not model_id:
            continue
        ext = _as_map(row.get("extensions"))
        out[model_id] = {
            "schema_version": "1.0.0",
            "traction_model_id": model_id,
            "min_friction_permille": int(max(1, _as_int(ext.get("min_friction_permille", 100), 100))),
            "max_friction_permille": int(max(1, _as_int(ext.get("max_friction_permille", 1200), 1200))),
            "traction_scale_permille": int(max(1, _as_int(ext.get("traction_scale_permille", 1000), 1000))),
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def wind_model_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("wind_models")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("wind_models")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("wind_model_id", ""))):
        model_id = str(row.get("wind_model_id", "")).strip()
        if not model_id:
            continue
        ext = _as_map(row.get("extensions"))
        out[model_id] = {
            "schema_version": "1.0.0",
            "wind_model_id": model_id,
            "wind_scale_permille": int(max(0, _as_int(ext.get("wind_scale_permille", 1000), 1000))),
            "max_drift_mm_per_tick2": int(max(0, _as_int(ext.get("max_drift_mm_per_tick2", 512), 512))),
            "extensions": _canon(ext),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def resolve_free_motion_policy(
    *,
    registry_payload: Mapping[str, object] | None,
    policy_id: str | None,
) -> dict:
    rows = free_motion_policy_rows_by_id(registry_payload)
    token = str(policy_id or "").strip() or "free.default_ground"
    row = dict(rows.get(token) or {})
    if row:
        return row
    return {
        "schema_version": "1.0.0",
        "policy_id": "free.default_ground",
        "max_speed": 1200,
        "max_accel": 96,
        "traction_model_id": "traction.basic_friction",
        "wind_model_id": "wind.basic_drift",
        "wind_scale_permille": 300,
        "corridor_enforcement_mode": "clamp",
        "extensions": {},
    }


def _geometry_points_mm(geometry_row: Mapping[str, object] | None) -> List[dict]:
    row = _as_map(geometry_row)
    parameters = _as_map(row.get("parameters"))
    for key in ("control_points_mm", "points_mm", "path_points_mm"):
        rows = [dict(item) for item in list(parameters.get(key) or []) if isinstance(item, Mapping)]
        if rows:
            return [_vector3_int(item) for item in rows]
    start_mm = _as_map(parameters.get("start_mm"))
    end_mm = _as_map(parameters.get("end_mm"))
    if start_mm and end_mm:
        return [_vector3_int(start_mm), _vector3_int(end_mm)]
    return []


def _geometry_bounds_mm(geometry_row: Mapping[str, object] | None) -> dict:
    row = _as_map(geometry_row)
    bounds = _as_map(row.get("bounds"))
    min_mm = bounds.get("min_mm")
    max_mm = bounds.get("max_mm")
    if isinstance(min_mm, Mapping) and isinstance(max_mm, Mapping):
        return {
            "min_mm": _vector3_int(min_mm),
            "max_mm": _vector3_int(max_mm),
        }
    points = _geometry_points_mm(row)
    if not points:
        return {
            "min_mm": {"x": 0, "y": 0, "z": 0},
            "max_mm": {"x": 0, "y": 0, "z": 0},
        }
    xs = [int(point.get("x", 0)) for point in points]
    ys = [int(point.get("y", 0)) for point in points]
    zs = [int(point.get("z", 0)) for point in points]
    return {
        "min_mm": {"x": min(xs), "y": min(ys), "z": min(zs)},
        "max_mm": {"x": max(xs), "y": max(ys), "z": max(zs)},
    }


def _point_outside_bounds(point: Mapping[str, object], bounds: Mapping[str, object], axes: Sequence[str]) -> bool:
    payload = _vector3_int(point)
    min_mm = _vector3_int(_as_map(bounds).get("min_mm"))
    max_mm = _vector3_int(_as_map(bounds).get("max_mm"))
    for axis in axes:
        value = int(payload.get(axis, 0))
        if value < int(min_mm.get(axis, 0)) or value > int(max_mm.get(axis, 0)):
            return True
    return False


def _clamp_point_to_bounds(point: Mapping[str, object], bounds: Mapping[str, object], axes: Sequence[str]) -> dict:
    payload = _vector3_int(point)
    min_mm = _vector3_int(_as_map(bounds).get("min_mm"))
    max_mm = _vector3_int(_as_map(bounds).get("max_mm"))
    out = dict(payload)
    for axis in axes:
        out[axis] = int(max(int(min_mm.get(axis, 0)), min(int(max_mm.get(axis, 0)), int(payload.get(axis, 0)))))
    return out


def _desired_accel_vector(control_input: Mapping[str, object] | None, max_accel: int) -> dict:
    payload = _as_map(control_input)
    explicit = _vector3_int(payload.get("desired_accel_mm_per_tick2"))
    if explicit != {"x": 0, "y": 0, "z": 0}:
        return {
            "x": int(max(-max_accel, min(max_accel, int(explicit["x"])))),
            "y": int(max(-max_accel, min(max_accel, int(explicit["y"])))),
            "z": int(max(-max_accel, min(max_accel, int(explicit["z"])))),
        }
    move_permille = _vector3_int(payload.get("move_vector_permille"))
    if move_permille != {"x": 0, "y": 0, "z": 0}:
        return {
            "x": int((int(move_permille["x"]) * int(max_accel)) // 1000),
            "y": int((int(move_permille["y"]) * int(max_accel)) // 1000),
            "z": int((int(move_permille["z"]) * int(max_accel)) // 1000),
        }
    throttle = int(max(0, min(1000, _as_int(payload.get("throttle_permille", 0), 0))))
    brake = int(max(0, min(1000, _as_int(payload.get("brake_permille", 0), 0))))
    strafe = int(max(-1000, min(1000, _as_int(payload.get("strafe_permille", 0), 0))))
    lift = int(max(-1000, min(1000, _as_int(payload.get("lift_permille", 0), 0))))
    forward = int(throttle) - int(brake)
    return {
        "x": int((int(forward) * int(max_accel)) // 1000),
        "y": int((int(strafe) * int(max_accel)) // 1000),
        "z": int((int(lift) * int(max_accel)) // 1000),
    }


def _speed_cap_mm_per_tick(
    *,
    policy_row: Mapping[str, object],
    field_values: Mapping[str, object] | None,
    effect_modifiers: Mapping[str, object] | None,
) -> int:
    policy = _as_map(policy_row)
    fields = _as_map(field_values)
    effects = _as_map(effect_modifiers)
    max_speed = int(max(1, _as_int(policy.get("max_speed", 1200), 1200)))
    speed_cap_permille = int(max(50, min(1000, _as_int(effects.get("max_speed_permille", 1000), 1000))))
    visibility_permille = int(max(0, min(1000, _as_int(fields.get("visibility_permille", 1000), 1000))))
    if visibility_permille < 1000:
        speed_cap_permille = min(speed_cap_permille, max(200, int(visibility_permille) + 100))
    return int(max(1, (int(max_speed) * int(speed_cap_permille)) // 1000))


def _field_friction_permille(
    *,
    field_values: Mapping[str, object] | None,
    effect_modifiers: Mapping[str, object] | None,
    traction_model_row: Mapping[str, object] | None,
) -> int:
    fields = _as_map(field_values)
    effects = _as_map(effect_modifiers)
    model = _as_map(traction_model_row)
    friction = int(
        max(
            1,
            _as_int(
                fields.get("friction_permille", fields.get("traction_permille", 1000)),
                1000,
            ),
        )
    )
    traction_permille = int(max(1, _as_int(effects.get("traction_permille", 1000), 1000)))
    model_min = int(max(1, _as_int(model.get("min_friction_permille", 100), 100)))
    model_max = int(max(model_min, _as_int(model.get("max_friction_permille", 1200), 1200)))
    out = int(min(friction, traction_permille))
    out = int(max(model_min, min(model_max, out)))
    return out


def _wind_drift_accel(
    *,
    field_values: Mapping[str, object] | None,
    policy_row: Mapping[str, object] | None,
    wind_model_row: Mapping[str, object] | None,
) -> dict:
    fields = _as_map(field_values)
    policy = _as_map(policy_row)
    model = _as_map(wind_model_row)
    wind_vector = _vector3_int(fields.get("wind_vector", fields.get("wind")))
    policy_scale = int(max(0, _as_int(policy.get("wind_scale_permille", 300), 300)))
    model_scale = int(max(0, _as_int(model.get("wind_scale_permille", 1000), 1000)))
    max_drift = int(max(0, _as_int(model.get("max_drift_mm_per_tick2", 512), 512)))
    out = {
        "x": int((int(wind_vector["x"]) * int(policy_scale) * int(model_scale)) // 1_000_000),
        "y": int((int(wind_vector["y"]) * int(policy_scale) * int(model_scale)) // 1_000_000),
        "z": int((int(wind_vector["z"]) * int(policy_scale) * int(model_scale)) // 1_000_000),
    }
    for axis in ("x", "y", "z"):
        out[axis] = int(max(-max_drift, min(max_drift, int(out[axis]))))
    return out


def step_free_motion(
    *,
    free_motion_row: Mapping[str, object],
    body_row: Mapping[str, object],
    control_input: Mapping[str, object] | None,
    policy_row: Mapping[str, object],
    traction_model_row: Mapping[str, object] | None,
    wind_model_row: Mapping[str, object] | None,
    field_values: Mapping[str, object] | None,
    effect_modifiers: Mapping[str, object] | None,
    corridor_geometry_row: Mapping[str, object] | None,
    volume_geometry_row: Mapping[str, object] | None,
    dt_ticks: int,
    current_tick: int,
    mass_value: int = 1,
    momentum_linear: Mapping[str, object] | None = None,
    momentum_angular: object = 0,
) -> dict:
    row = dict(free_motion_row or {})
    body = dict(body_row or {})
    policy = _as_map(policy_row)
    fields = _as_map(field_values)
    effects = _as_map(effect_modifiers)
    dt = int(max(1, _as_int(dt_ticks, 1)))
    max_accel = int(max(1, _as_int(policy.get("max_accel", 96), 96)))
    desired_accel = _desired_accel_vector(control_input=control_input, max_accel=max_accel)

    traction_scale_permille = int(max(1, _as_int(_as_map(traction_model_row).get("traction_scale_permille", 1000), 1000)))
    friction_permille = _field_friction_permille(
        field_values=fields,
        effect_modifiers=effects,
        traction_model_row=traction_model_row,
    )
    traction_accel = {
        "x": int((int(desired_accel["x"]) * int(friction_permille) * int(traction_scale_permille)) // 1_000_000),
        "y": int((int(desired_accel["y"]) * int(friction_permille) * int(traction_scale_permille)) // 1_000_000),
        "z": int((int(desired_accel["z"]) * int(friction_permille) * int(traction_scale_permille)) // 1_000_000),
    }
    drift_accel = _wind_drift_accel(
        field_values=fields,
        policy_row=policy,
        wind_model_row=wind_model_row,
    )
    accel = {
        "x": int(traction_accel["x"]) + int(drift_accel["x"]),
        "y": int(traction_accel["y"]) + int(drift_accel["y"]),
        "z": int(traction_accel["z"]) + int(drift_accel["z"]),
    }
    mass = int(max(1, _as_int(mass_value, 1)))
    if isinstance(momentum_linear, Mapping):
        momentum_p0 = _vector3_int(momentum_linear)
    else:
        v0 = _vector3_int(row.get("velocity"), _vector3_int(body.get("velocity_mm_per_tick")))
        momentum_p0 = {
            "x": int(v0["x"]) * int(mass),
            "y": int(v0["y"]) * int(mass),
            "z": int(v0["z"]) * int(mass),
        }
    momentum_p1 = {
        "x": int(momentum_p0["x"]) + int(accel["x"]) * int(dt) * int(mass),
        "y": int(momentum_p0["y"]) + int(accel["y"]) * int(dt) * int(mass),
        "z": int(momentum_p0["z"]) + int(accel["z"]) * int(dt) * int(mass),
    }
    v1 = {
        "x": int(deterministic_divide(int(momentum_p1["x"]), int(mass), rounding_mode="truncate")),
        "y": int(deterministic_divide(int(momentum_p1["y"]), int(mass), rounding_mode="truncate")),
        "z": int(deterministic_divide(int(momentum_p1["z"]), int(mass), rounding_mode="truncate")),
    }
    speed_cap = _speed_cap_mm_per_tick(policy_row=policy, field_values=fields, effect_modifiers=effects)
    for axis in ("x", "y", "z"):
        v1[axis] = int(max(-int(speed_cap), min(int(speed_cap), int(v1[axis]))))
        momentum_p1[axis] = int(v1[axis]) * int(mass)

    position_p0 = _vector3_int(body.get("transform_mm"))
    position_p1 = {
        "x": int(position_p0["x"]) + int(v1["x"]) * int(dt),
        "y": int(position_p0["y"]) + int(v1["y"]) * int(dt),
        "z": int(position_p0["z"]) + int(v1["z"]) * int(dt),
    }
    enforcement_mode = _normalize_corridor_mode(
        _as_map(policy).get(
            "corridor_enforcement_mode",
            _as_map(_as_map(row).get("extensions")).get("corridor_enforcement_mode", "clamp"),
        )
    )
    corridor_status = "none"
    volume_status = "none"
    if isinstance(corridor_geometry_row, Mapping):
        corridor_bounds = _geometry_bounds_mm(corridor_geometry_row)
        outside = _point_outside_bounds(position_p1, corridor_bounds, ("x", "y"))
        if outside:
            if enforcement_mode == "clamp":
                position_p1 = _clamp_point_to_bounds(position_p1, corridor_bounds, ("x", "y"))
                corridor_status = "clamped"
            elif enforcement_mode == "refuse":
                position_p1 = dict(position_p0)
                v1 = {"x": 0, "y": 0, "z": 0}
                accel = {"x": 0, "y": 0, "z": 0}
                momentum_p1 = {"x": 0, "y": 0, "z": 0}
                corridor_status = "refused"
            else:
                corridor_status = "warned"
    if isinstance(volume_geometry_row, Mapping):
        volume_bounds = _geometry_bounds_mm(volume_geometry_row)
        outside = _point_outside_bounds(position_p1, volume_bounds, ("x", "y", "z"))
        if outside:
            if enforcement_mode == "clamp":
                position_p1 = _clamp_point_to_bounds(position_p1, volume_bounds, ("x", "y", "z"))
                volume_status = "clamped"
            elif enforcement_mode == "refuse":
                position_p1 = dict(position_p0)
                v1 = {"x": 0, "y": 0, "z": 0}
                accel = {"x": 0, "y": 0, "z": 0}
                momentum_p1 = {"x": 0, "y": 0, "z": 0}
                volume_status = "refused"
            else:
                volume_status = "warned"

    next_row = build_free_motion_state(
        subject_id=str(row.get("subject_id", "")).strip() or None,
        vehicle_id=(None if row.get("vehicle_id") is None else str(row.get("vehicle_id", "")).strip() or None),
        agent_id=(None if row.get("agent_id") is None else str(row.get("agent_id", "")).strip() or None),
        body_id=str(row.get("body_id", "")).strip(),
        velocity=v1,
        acceleration=accel,
        corridor_geometry_id=(
            None if row.get("corridor_geometry_id") is None else str(row.get("corridor_geometry_id", "")).strip() or None
        ),
        volume_geometry_id=(
            None if row.get("volume_geometry_id") is None else str(row.get("volume_geometry_id", "")).strip() or None
        ),
        last_update_tick=int(max(0, _as_int(current_tick, 0))),
        extensions=_as_map(row.get("extensions")),
    )
    return {
        "free_motion_state": dict(next_row),
        "candidate_transform_mm": dict(position_p1),
        "momentum_linear": dict(momentum_p1),
        "momentum_angular": int(_as_int(momentum_angular, 0)),
        "mass_value": int(mass),
        "telemetry": {
            "speed_cap_mm_per_tick": int(speed_cap),
            "friction_permille": int(friction_permille),
            "traction_accel": dict(traction_accel),
            "drift_accel": dict(drift_accel),
            "momentum_linear": dict(momentum_p1),
            "mass_value": int(mass),
            "corridor_status": corridor_status,
            "volume_status": volume_status,
            "corridor_enforcement_mode": enforcement_mode,
            "visibility_permille": int(max(0, _as_int(fields.get("visibility_permille", 1000), 1000))),
        },
    }


__all__ = [
    "FreeMotionError",
    "build_free_motion_state",
    "free_motion_policy_rows_by_id",
    "free_motion_rows_by_subject_id",
    "normalize_free_motion_state_rows",
    "resolve_free_motion_policy",
    "step_free_motion",
    "traction_model_rows_by_id",
    "wind_model_rows_by_id",
]
