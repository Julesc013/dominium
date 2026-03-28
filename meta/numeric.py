"""Deterministic fixed-point rounding, tolerance, and numeric assertion helpers."""

from __future__ import annotations

import math
from typing import Dict, List, Mapping


ROUND_HALF_TO_EVEN = "round_half_to_even"
ROUND_FLOOR = "floor"
ROUND_CEILING = "ceiling"
ROUND_TRUNCATE = "truncate"
VALID_ROUNDING_MODES = {
    ROUND_HALF_TO_EVEN,
    ROUND_FLOOR,
    ROUND_CEILING,
    ROUND_TRUNCATE,
}

OVERFLOW_FAIL = "fail"
OVERFLOW_SATURATE = "saturate"
VALID_OVERFLOW_POLICIES = {OVERFLOW_FAIL, OVERFLOW_SATURATE}


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def normalize_rounding_mode(mode: object, default_mode: str = ROUND_HALF_TO_EVEN) -> str:
    token = str(mode or "").strip().lower()
    if token in VALID_ROUNDING_MODES:
        return token
    return str(default_mode if default_mode in VALID_ROUNDING_MODES else ROUND_HALF_TO_EVEN)


def normalize_overflow_policy(policy: object, default_policy: str = OVERFLOW_FAIL) -> str:
    token = str(policy or "").strip().lower()
    if token in VALID_OVERFLOW_POLICIES:
        return token
    return str(default_policy if default_policy in VALID_OVERFLOW_POLICIES else OVERFLOW_FAIL)


def deterministic_divide(value: int, divisor: int, rounding_mode: str = ROUND_TRUNCATE) -> int:
    den = int(max(1, _as_int(divisor, 1)))
    num = int(_as_int(value, 0))
    mode = normalize_rounding_mode(rounding_mode, ROUND_TRUNCATE)
    if num == 0:
        return 0
    sign = -1 if num < 0 else 1
    abs_num = abs(num)
    q_abs = int(abs_num // den)
    r_abs = int(abs_num % den)
    if mode == ROUND_TRUNCATE:
        rounded_abs = q_abs
    elif mode == ROUND_FLOOR:
        if sign < 0 and r_abs:
            return int(-(q_abs + 1))
        rounded_abs = q_abs
    elif mode == ROUND_CEILING:
        if sign > 0 and r_abs:
            return int(q_abs + 1)
        rounded_abs = q_abs
    else:
        twice = int(r_abs * 2)
        if twice < den:
            rounded_abs = q_abs
        elif twice > den:
            rounded_abs = int(q_abs + 1)
        else:
            rounded_abs = int(q_abs if (q_abs % 2 == 0) else (q_abs + 1))
    return int(rounded_abs if sign > 0 else -rounded_abs)


def deterministic_mul_div(
    value: int,
    multiplier: int,
    divisor: int,
    rounding_mode: str = ROUND_HALF_TO_EVEN,
) -> int:
    num = int(_as_int(value, 0)) * int(_as_int(multiplier, 0))
    den = int(max(1, _as_int(divisor, 1)))
    return int(deterministic_divide(num, den, rounding_mode=rounding_mode))


def deterministic_round(
    *,
    quantity_id: str,
    numerator: int,
    denominator: int = 1,
    quantity_tolerance_registry: Mapping[str, object] | None = None,
    default_mode: str = ROUND_HALF_TO_EVEN,
) -> int:
    rounding_mode = rounding_mode_for_quantity(
        quantity_id=str(quantity_id).strip(),
        quantity_tolerance_registry=quantity_tolerance_registry,
        default_mode=default_mode,
    )
    return int(deterministic_divide(int(_as_int(numerator, 0)), int(max(1, _as_int(denominator, 1))), rounding_mode=rounding_mode))


def apply_overflow_policy(
    value: int,
    *,
    min_value: int,
    max_value: int,
    overflow_policy: str,
) -> tuple[int, bool]:
    low = int(min(min_value, max_value))
    high = int(max(min_value, max_value))
    policy = normalize_overflow_policy(overflow_policy, OVERFLOW_FAIL)
    token = int(_as_int(value, 0))
    if low <= token <= high:
        return token, False
    if policy == OVERFLOW_SATURATE:
        return int(max(low, min(high, token))), True
    raise OverflowError("deterministic overflow")


def _normalize_quantity_tolerance_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    quantity_id = str(payload.get("quantity_id", "")).strip()
    if not quantity_id:
        return {}
    rounding_mode = normalize_rounding_mode(payload.get("rounding_mode"), ROUND_HALF_TO_EVEN)
    overflow_policy = normalize_overflow_policy(payload.get("overflow_policy"), OVERFLOW_FAIL)
    return {
        "schema_version": "1.0.0",
        "quantity_id": quantity_id,
        "base_resolution": int(max(1, _as_int(payload.get("base_resolution", 1), 1))),
        "tolerance_abs": int(max(0, _as_int(payload.get("tolerance_abs", 0), 0))),
        "tolerance_rel": int(max(0, _as_int(payload.get("tolerance_rel", 0), 0))),
        "rounding_mode": rounding_mode,
        "overflow_policy": overflow_policy,
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": _as_map(payload.get("extensions")),
    }


def _normalize_tolerance_row(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    tol_id = str(payload.get("tol_id", "")).strip()
    if not tol_id:
        return {}
    rounding_mode = normalize_rounding_mode(payload.get("rounding_mode"), ROUND_HALF_TO_EVEN)
    return {
        "schema_version": "1.0.0",
        "tol_id": tol_id,
        "domain_id": str(payload.get("domain_id", "")).strip(),
        "allowed_error_bound": int(max(0, _as_int(payload.get("allowed_error_bound", 0), 0))),
        "rounding_mode": rounding_mode,
        "deterministic_fingerprint": str(payload.get("deterministic_fingerprint", "")).strip(),
        "extensions": _as_map(payload.get("extensions")),
    }


def normalize_quantity_tolerance_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("quantity_id", ""))):
        normalized = _normalize_quantity_tolerance_row(row)
        if not normalized:
            continue
        out[str(normalized.get("quantity_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def normalize_tolerance_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("tol_id", ""))):
        normalized = _normalize_tolerance_row(row)
        if not normalized:
            continue
        out[str(normalized.get("tol_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def quantity_tolerance_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("quantity_tolerances")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("quantity_tolerances")
    if not isinstance(rows, list):
        rows = []
    return dict(
        (str(row.get("quantity_id", "")).strip(), dict(row))
        for row in normalize_quantity_tolerance_rows(rows)
        if str(row.get("quantity_id", "")).strip()
    )


def tolerance_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("tolerances")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("tolerances")
    if not isinstance(rows, list):
        rows = []
    return dict(
        (str(row.get("tol_id", "")).strip(), dict(row))
        for row in normalize_tolerance_rows(rows)
        if str(row.get("tol_id", "")).strip()
    )


def rounding_mode_for_quantity(
    *,
    quantity_id: str,
    quantity_tolerance_registry: Mapping[str, object] | None,
    default_mode: str = ROUND_TRUNCATE,
) -> str:
    rows = quantity_tolerance_rows_by_id(quantity_tolerance_registry)
    row = dict(rows.get(str(quantity_id).strip()) or {})
    return normalize_rounding_mode(row.get("rounding_mode"), default_mode)


def tolerance_abs_for_quantity(
    *,
    quantity_id: str,
    quantity_tolerance_registry: Mapping[str, object] | None,
    default_value: int = 0,
) -> int:
    rows = quantity_tolerance_rows_by_id(quantity_tolerance_registry)
    row = dict(rows.get(str(quantity_id).strip()) or {})
    if not row:
        return int(max(0, _as_int(default_value, 0)))
    return int(max(0, _as_int(row.get("tolerance_abs", default_value), default_value)))


def overflow_policy_for_quantity(
    *,
    quantity_id: str,
    quantity_tolerance_registry: Mapping[str, object] | None,
    default_policy: str = OVERFLOW_FAIL,
) -> str:
    rows = quantity_tolerance_rows_by_id(quantity_tolerance_registry)
    row = dict(rows.get(str(quantity_id).strip()) or {})
    return normalize_overflow_policy(row.get("overflow_policy"), default_policy)


def allowed_error_bound_for_tolerance(
    *,
    tolerance_id: str,
    tolerance_registry: Mapping[str, object] | None,
    default_value: int = 0,
) -> int:
    rows = tolerance_rows_by_id(tolerance_registry)
    row = dict(rows.get(str(tolerance_id).strip()) or {})
    if not row:
        return int(max(0, _as_int(default_value, 0)))
    return int(max(0, _as_int(row.get("allowed_error_bound", default_value), default_value)))


def rounding_mode_for_tolerance(
    *,
    tolerance_id: str,
    tolerance_registry: Mapping[str, object] | None,
    default_mode: str = ROUND_HALF_TO_EVEN,
) -> str:
    rows = tolerance_rows_by_id(tolerance_registry)
    row = dict(rows.get(str(tolerance_id).strip()) or {})
    return normalize_rounding_mode(row.get("rounding_mode"), default_mode)


def debug_assert_no_float_payload(payload: object, *, context: str = "payload", _path: str = "") -> None:
    if isinstance(payload, float):
        if not math.isfinite(payload):
            raise AssertionError("{} contains non-finite float at {}".format(str(context or "payload"), _path or "<root>"))
        raise AssertionError("{} contains float at {}".format(str(context or "payload"), _path or "<root>"))
    if isinstance(payload, Mapping):
        for key in sorted(payload.keys(), key=lambda item: str(item)):
            child_path = "{}.{}".format(_path, key) if _path else str(key)
            debug_assert_no_float_payload(payload[key], context=context, _path=child_path)
        return
    if isinstance(payload, list):
        for index, item in enumerate(_as_list(payload)):
            child_path = "{}[{}]".format(_path, index) if _path else "[{}]".format(index)
            debug_assert_no_float_payload(item, context=context, _path=child_path)
        return
    if isinstance(payload, tuple):
        for index, item in enumerate(list(payload)):
            child_path = "{}[{}]".format(_path, index) if _path else "[{}]".format(index)
            debug_assert_no_float_payload(item, context=context, _path=child_path)


def debug_assert_tolerance_bound(
    *,
    tolerance_id: str,
    observed: int,
    expected: int,
    tolerance_registry: Mapping[str, object] | None,
    default_allowed_error: int = 0,
    context: str = "numeric_tolerance",
) -> None:
    allowed = allowed_error_bound_for_tolerance(
        tolerance_id=str(tolerance_id).strip(),
        tolerance_registry=tolerance_registry,
        default_value=default_allowed_error,
    )
    delta = abs(int(_as_int(observed, 0)) - int(_as_int(expected, 0)))
    if delta > allowed:
        raise AssertionError(
            "{} exceeded tolerance '{}' (observed={}, expected={}, delta={}, allowed={})".format(
                str(context or "numeric_tolerance"),
                str(tolerance_id or "").strip(),
                int(_as_int(observed, 0)),
                int(_as_int(expected, 0)),
                int(delta),
                int(allowed),
            )
        )


__all__ = [
    "OVERFLOW_FAIL",
    "OVERFLOW_SATURATE",
    "ROUND_CEILING",
    "ROUND_FLOOR",
    "ROUND_HALF_TO_EVEN",
    "ROUND_TRUNCATE",
    "VALID_OVERFLOW_POLICIES",
    "VALID_ROUNDING_MODES",
    "apply_overflow_policy",
    "allowed_error_bound_for_tolerance",
    "debug_assert_no_float_payload",
    "debug_assert_tolerance_bound",
    "deterministic_divide",
    "deterministic_mul_div",
    "deterministic_round",
    "normalize_overflow_policy",
    "normalize_tolerance_rows",
    "normalize_quantity_tolerance_rows",
    "normalize_rounding_mode",
    "overflow_policy_for_quantity",
    "quantity_tolerance_rows_by_id",
    "rounding_mode_for_tolerance",
    "rounding_mode_for_quantity",
    "tolerance_rows_by_id",
    "tolerance_abs_for_quantity",
]
