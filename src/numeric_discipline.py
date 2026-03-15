"""Numeric-discipline helpers safe to import from truth paths."""

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


def normalize_tolerance_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: str(item.get("tol_id", "")),
    ):
        normalized = _normalize_tolerance_row(row)
        if not normalized:
            continue
        out[str(normalized.get("tol_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


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


def debug_assert_no_float_payload(payload: object, *, context: str = "payload", _path: str = "") -> None:
    if isinstance(payload, float):
        if not math.isfinite(payload):
            raise AssertionError(
                "{} contains non-finite float at {}".format(str(context or "payload"), _path or "<root>")
            )
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
    "ROUND_HALF_TO_EVEN",
    "ROUND_CEILING",
    "ROUND_FLOOR",
    "ROUND_TRUNCATE",
    "VALID_ROUNDING_MODES",
    "allowed_error_bound_for_tolerance",
    "debug_assert_no_float_payload",
    "debug_assert_tolerance_bound",
    "normalize_rounding_mode",
    "normalize_tolerance_rows",
    "tolerance_rows_by_id",
]
