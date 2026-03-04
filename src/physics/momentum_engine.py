"""PHYS-1 deterministic momentum substrate helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


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


def _div_toward_zero(value: int, divisor: int) -> int:
    den = int(max(1, _as_int(divisor, 1)))
    num = int(_as_int(value, 0))
    if num < 0:
        return -int(abs(num) // den)
    return int(num // den)


def build_momentum_state(
    *,
    assembly_id: str,
    mass_value: int,
    momentum_linear: Mapping[str, object] | None = None,
    momentum_angular: object = 0,
    last_update_tick: int = 0,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    assembly_token = str(assembly_id or "").strip()
    if not assembly_token:
        return {}
    angular_value: object
    if isinstance(momentum_angular, Mapping):
        angular_value = _vector3_int(momentum_angular)
    else:
        angular_value = int(_as_int(momentum_angular, 0))
    payload = {
        "schema_version": "1.0.0",
        "assembly_id": assembly_token,
        "mass_value": int(max(1, _as_int(mass_value, 1))),
        "momentum_linear": _vector3_int(momentum_linear, {"x": 0, "y": 0, "z": 0}),
        "momentum_angular": angular_value,
        "last_update_tick": int(max(0, _as_int(last_update_tick, 0))),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_momentum_state_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("assembly_id", ""))):
        normalized = build_momentum_state(
            assembly_id=str(row.get("assembly_id", "")).strip(),
            mass_value=_as_int(row.get("mass_value", 1), 1),
            momentum_linear=row.get("momentum_linear"),
            momentum_angular=row.get("momentum_angular", 0),
            last_update_tick=_as_int(row.get("last_update_tick", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("assembly_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def momentum_state_rows_by_assembly_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_momentum_state_rows(rows)
    return dict(
        (str(row.get("assembly_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("assembly_id", "")).strip()
    )


def build_force_application(
    *,
    application_id: str,
    target_assembly_id: str,
    force_vector: Mapping[str, object] | None,
    duration_ticks: int,
    torque: object = None,
    originating_process_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    app_token = str(application_id or "").strip()
    target_token = str(target_assembly_id or "").strip()
    process_token = str(originating_process_id or "").strip()
    if (not app_token) or (not target_token) or (not process_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "application_id": app_token,
        "target_assembly_id": target_token,
        "force_vector": _vector3_int(force_vector, {"x": 0, "y": 0, "z": 0}),
        "duration_ticks": int(max(1, _as_int(duration_ticks, 1))),
        "torque": None if torque is None else int(_as_int(torque, 0)),
        "originating_process_id": process_token,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_force_application_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("application_id", ""))):
        normalized = build_force_application(
            application_id=str(row.get("application_id", "")).strip(),
            target_assembly_id=str(row.get("target_assembly_id", "")).strip(),
            force_vector=row.get("force_vector"),
            duration_ticks=_as_int(row.get("duration_ticks", 1), 1),
            torque=row.get("torque"),
            originating_process_id=str(row.get("originating_process_id", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("application_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_impulse_application(
    *,
    application_id: str,
    target_assembly_id: str,
    impulse_vector: Mapping[str, object] | None,
    torque_impulse: object = None,
    originating_process_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    app_token = str(application_id or "").strip()
    target_token = str(target_assembly_id or "").strip()
    process_token = str(originating_process_id or "").strip()
    if (not app_token) or (not target_token) or (not process_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "application_id": app_token,
        "target_assembly_id": target_token,
        "impulse_vector": _vector3_int(impulse_vector, {"x": 0, "y": 0, "z": 0}),
        "torque_impulse": None if torque_impulse is None else int(_as_int(torque_impulse, 0)),
        "originating_process_id": process_token,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_impulse_application_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("application_id", ""))):
        normalized = build_impulse_application(
            application_id=str(row.get("application_id", "")).strip(),
            target_assembly_id=str(row.get("target_assembly_id", "")).strip(),
            impulse_vector=row.get("impulse_vector"),
            torque_impulse=row.get("torque_impulse"),
            originating_process_id=str(row.get("originating_process_id", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("application_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def apply_force_to_momentum_state(
    *,
    momentum_state_row: Mapping[str, object],
    force_application_row: Mapping[str, object],
    tick: int,
) -> dict:
    momentum_row = dict(momentum_state_row or {})
    force_row = dict(force_application_row or {})
    assembly_id = str(momentum_row.get("assembly_id", "")).strip() or str(force_row.get("target_assembly_id", "")).strip()
    mass_value = int(max(1, _as_int(momentum_row.get("mass_value", 1), 1)))
    base_linear = _vector3_int(momentum_row.get("momentum_linear"), {"x": 0, "y": 0, "z": 0})
    duration_ticks = int(max(1, _as_int(force_row.get("duration_ticks", 1), 1)))
    force_vector = _vector3_int(force_row.get("force_vector"), {"x": 0, "y": 0, "z": 0})
    delta_linear = {
        "x": int(force_vector["x"]) * int(duration_ticks),
        "y": int(force_vector["y"]) * int(duration_ticks),
        "z": int(force_vector["z"]) * int(duration_ticks),
    }
    torque = int(_as_int(force_row.get("torque", 0), 0))
    angular_base = momentum_row.get("momentum_angular", 0)
    angular_value = int(_as_int(angular_base, 0))
    angular_delta = int(torque) * int(duration_ticks)
    updated = build_momentum_state(
        assembly_id=assembly_id,
        mass_value=mass_value,
        momentum_linear={
            "x": int(base_linear["x"]) + int(delta_linear["x"]),
            "y": int(base_linear["y"]) + int(delta_linear["y"]),
            "z": int(base_linear["z"]) + int(delta_linear["z"]),
        },
        momentum_angular=int(angular_value + angular_delta),
        last_update_tick=int(max(0, _as_int(tick, 0))),
        extensions=_as_map(momentum_row.get("extensions")),
    )
    return {
        "momentum_state": updated,
        "delta_momentum_linear": delta_linear,
        "delta_momentum_angular": int(angular_delta),
    }


def apply_impulse_to_momentum_state(
    *,
    momentum_state_row: Mapping[str, object],
    impulse_application_row: Mapping[str, object],
    tick: int,
) -> dict:
    momentum_row = dict(momentum_state_row or {})
    impulse_row = dict(impulse_application_row or {})
    assembly_id = str(momentum_row.get("assembly_id", "")).strip() or str(impulse_row.get("target_assembly_id", "")).strip()
    mass_value = int(max(1, _as_int(momentum_row.get("mass_value", 1), 1)))
    base_linear = _vector3_int(momentum_row.get("momentum_linear"), {"x": 0, "y": 0, "z": 0})
    impulse_vector = _vector3_int(impulse_row.get("impulse_vector"), {"x": 0, "y": 0, "z": 0})
    torque_impulse = int(_as_int(impulse_row.get("torque_impulse", 0), 0))
    angular_base = int(_as_int(momentum_row.get("momentum_angular", 0), 0))
    updated = build_momentum_state(
        assembly_id=assembly_id,
        mass_value=mass_value,
        momentum_linear={
            "x": int(base_linear["x"]) + int(impulse_vector["x"]),
            "y": int(base_linear["y"]) + int(impulse_vector["y"]),
            "z": int(base_linear["z"]) + int(impulse_vector["z"]),
        },
        momentum_angular=int(angular_base + torque_impulse),
        last_update_tick=int(max(0, _as_int(tick, 0))),
        extensions=_as_map(momentum_row.get("extensions")),
    )
    return {
        "momentum_state": updated,
        "delta_momentum_linear": dict(impulse_vector),
        "delta_momentum_angular": int(torque_impulse),
    }


def velocity_from_momentum_state(momentum_state_row: Mapping[str, object]) -> dict:
    row = dict(momentum_state_row or {})
    momentum_linear = _vector3_int(row.get("momentum_linear"), {"x": 0, "y": 0, "z": 0})
    mass_value = int(max(1, _as_int(row.get("mass_value", 1), 1)))
    return {
        "x": int(_div_toward_zero(int(momentum_linear["x"]), mass_value)),
        "y": int(_div_toward_zero(int(momentum_linear["y"]), mass_value)),
        "z": int(_div_toward_zero(int(momentum_linear["z"]), mass_value)),
    }


def kinetic_energy_from_momentum_state(momentum_state_row: Mapping[str, object]) -> int:
    row = dict(momentum_state_row or {})
    momentum_linear = _vector3_int(row.get("momentum_linear"), {"x": 0, "y": 0, "z": 0})
    mass_value = int(max(1, _as_int(row.get("mass_value", 1), 1)))
    magnitude_sq = (
        int(momentum_linear["x"]) * int(momentum_linear["x"])
        + int(momentum_linear["y"]) * int(momentum_linear["y"])
        + int(momentum_linear["z"]) * int(momentum_linear["z"])
    )
    return int(magnitude_sq // int(max(1, 2 * mass_value)))


def build_exception_event(
    *,
    exception_id: str,
    tick: int,
    exception_kind: str,
    affected_quantities: Mapping[str, object],
    reason_code: str,
    originating_process_id: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "exception_id": str(exception_id or "").strip(),
        "tick": int(max(0, _as_int(tick, 0))),
        "exception_kind": str(exception_kind or "").strip() or "custom",
        "affected_quantities": dict(
            (str(key).strip(), int(_as_int(value, 0)))
            for key, value in sorted(dict(affected_quantities or {}).items(), key=lambda item: str(item[0]))
            if str(key).strip()
        ),
        "reason_code": str(reason_code or "").strip(),
        "originating_process_id": str(originating_process_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    if (not payload["exception_id"]) or (not payload["reason_code"]) or (not payload["originating_process_id"]):
        return {}
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_exception_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("exception_id", ""))):
        normalized = build_exception_event(
            exception_id=str(row.get("exception_id", "")).strip(),
            tick=_as_int(row.get("tick", 0), 0),
            exception_kind=str(row.get("exception_kind", "custom")).strip() or "custom",
            affected_quantities=dict(row.get("affected_quantities") or {}),
            reason_code=str(row.get("reason_code", "")).strip(),
            originating_process_id=str(row.get("originating_process_id", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("exception_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


__all__ = [
    "apply_force_to_momentum_state",
    "apply_impulse_to_momentum_state",
    "build_exception_event",
    "build_force_application",
    "build_impulse_application",
    "build_momentum_state",
    "kinetic_energy_from_momentum_state",
    "momentum_state_rows_by_assembly_id",
    "normalize_exception_event_rows",
    "normalize_force_application_rows",
    "normalize_impulse_application_rows",
    "normalize_momentum_state_rows",
    "velocity_from_momentum_state",
]
