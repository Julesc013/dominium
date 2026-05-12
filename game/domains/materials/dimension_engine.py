"""Deterministic dimension and fixed-point quantity operations for materials."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Mapping, Tuple


INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
DEFAULT_FRACTIONAL_BITS = 24

REFUSAL_DIMENSION_MISMATCH = "refusal.dimension.mismatch"
REFUSAL_UNIT_INVALID_CONVERSION = "refusal.unit.invalid_conversion"
REFUSAL_NUMERIC_OVERFLOW = "refusal.numeric.fixed_point_overflow"


class DimensionError(ValueError):
    """Deterministic dimension validation refusal."""

    def __init__(self, reason_code: str, message: str, details: Mapping[str, object] | None = None):
        super().__init__(message)
        self.reason_code = str(reason_code)
        self.details = dict(details or {})


class FixedPointOverflow(DimensionError):
    """Deterministic fixed-point overflow refusal."""

    def __init__(self, message: str, details: Mapping[str, object] | None = None):
        super().__init__(REFUSAL_NUMERIC_OVERFLOW, message, details=details)


@dataclass(frozen=True)
class FixedPointConfig:
    """Canonical fixed-point storage policy for invariant quantities."""

    fractional_bits: int = DEFAULT_FRACTIONAL_BITS
    storage_bits: int = 64
    overflow_behavior: str = "refuse"
    error_budget_max: int = 0

    @property
    def scale(self) -> int:
        return 1 << int(self.fractional_bits)


def fixed_point_config_from_policy(policy_row: Mapping[str, object] | None) -> FixedPointConfig:
    row = dict(policy_row or {})
    fixed_point = dict(row.get("fixed_point") or {})
    fractional_bits = int(fixed_point.get("fractional_bits", DEFAULT_FRACTIONAL_BITS) or DEFAULT_FRACTIONAL_BITS)
    storage_bits = int(fixed_point.get("storage_bits", 64) or 64)
    overflow_behavior = str(fixed_point.get("overflow_behavior", "refuse") or "refuse")
    error_budget_max = int(fixed_point.get("error_budget_max", 0) or 0)
    if fractional_bits < 0 or fractional_bits > 32:
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "fixed_point.fractional_bits out of supported range",
            {"fractional_bits": fractional_bits},
        )
    if storage_bits != 64:
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "fixed_point.storage_bits must remain 64 for invariant channels",
            {"storage_bits": storage_bits},
        )
    if overflow_behavior != "refuse":
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "overflow_behavior must be 'refuse' for invariant channels",
            {"overflow_behavior": overflow_behavior},
        )
    return FixedPointConfig(
        fractional_bits=int(fractional_bits),
        storage_bits=int(storage_bits),
        overflow_behavior=str(overflow_behavior),
        error_budget_max=max(0, int(error_budget_max)),
    )


def _check_int64(value: int, *, context: str) -> int:
    token = int(value)
    if token < INT64_MIN or token > INT64_MAX:
        raise FixedPointOverflow(
            "{} overflowed signed 64-bit fixed-point range".format(context),
            {"value": str(token)},
        )
    return token


def fixed_point_type(value_raw: int, config: FixedPointConfig | None = None) -> int:
    del config
    return _check_int64(int(value_raw), context="fixed_point_type")


def _round_div_away_from_zero(numerator: int, denominator: int) -> Tuple[int, int]:
    if int(denominator) == 0:
        raise DimensionError(
            REFUSAL_UNIT_INVALID_CONVERSION,
            "division by zero in fixed-point operation",
            {"denominator": str(denominator)},
        )
    n = int(numerator)
    d = int(denominator)
    sign = -1 if (n < 0) ^ (d < 0) else 1
    abs_n = abs(n)
    abs_d = abs(d)
    quotient = abs_n // abs_d
    remainder = abs_n % abs_d
    # Deterministic tie-break: half-away-from-zero.
    if remainder * 2 >= abs_d:
        quotient += 1
    result = sign * quotient
    signed_remainder = n - (result * d)
    return int(result), int(signed_remainder)


def fixed_point_add(a_raw: int, b_raw: int, *, config: FixedPointConfig | None = None) -> int:
    del config
    return _check_int64(int(a_raw) + int(b_raw), context="fixed_point_add")


def fixed_point_mul(a_raw: int, b_raw: int, *, config: FixedPointConfig | None = None) -> int:
    policy = config or FixedPointConfig()
    result, _ = _round_div_away_from_zero(int(a_raw) * int(b_raw), int(policy.scale))
    return _check_int64(int(result), context="fixed_point_mul")


def fixed_point_div(a_raw: int, b_raw: int, *, config: FixedPointConfig | None = None) -> int:
    policy = config or FixedPointConfig()
    result, _ = _round_div_away_from_zero(int(a_raw) * int(policy.scale), int(b_raw))
    return _check_int64(int(result), context="fixed_point_div")


def _normalize_exponents(payload: Mapping[str, object] | None) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key in sorted((payload or {}).keys()):
        token = str(key).strip()
        if not token:
            continue
        exponent = int((payload or {}).get(key, 0) or 0)
        if exponent != 0:
            out[token] = int(exponent)
    return out


def _dimension_vector(dimension: Mapping[str, object] | None) -> Dict[str, int]:
    row = dict(dimension or {})
    if "base_exponents" in row and isinstance(row.get("base_exponents"), Mapping):
        return _normalize_exponents(dict(row.get("base_exponents") or {}))
    return _normalize_exponents(row)


def dimension_equals(a: Mapping[str, object] | None, b: Mapping[str, object] | None) -> bool:
    return _dimension_vector(a) == _dimension_vector(b)


def dimension_add(a: Mapping[str, object] | None, b: Mapping[str, object] | None) -> Dict[str, int]:
    if not dimension_equals(a, b):
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "addition/subtraction requires identical dimensions",
            {"left": _dimension_vector(a), "right": _dimension_vector(b)},
        )
    return _dimension_vector(a)


def dimension_mul(a: Mapping[str, object] | None, b: Mapping[str, object] | None) -> Dict[str, int]:
    left = _dimension_vector(a)
    right = _dimension_vector(b)
    out: Dict[str, int] = {}
    for key in sorted(set(left.keys()) | set(right.keys())):
        exponent = int(left.get(key, 0)) + int(right.get(key, 0))
        if exponent != 0:
            out[key] = int(exponent)
    return out


def dimension_div(a: Mapping[str, object] | None, b: Mapping[str, object] | None) -> Dict[str, int]:
    left = _dimension_vector(a)
    right = _dimension_vector(b)
    out: Dict[str, int] = {}
    for key in sorted(set(left.keys()) | set(right.keys())):
        exponent = int(left.get(key, 0)) - int(right.get(key, 0))
        if exponent != 0:
            out[key] = int(exponent)
    return out


def _rows_by_id(rows: object, key_field: str) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get(key_field, ""))):
        key = str(row.get(key_field, "")).strip()
        if key:
            out[key] = dict(row)
    return out


def _lookup_unit(unit_registry: Mapping[str, object], unit_id: str) -> dict:
    rows = _rows_by_id((unit_registry or {}).get("units"), "unit_id")
    return dict(rows.get(str(unit_id).strip()) or {})


def _lookup_dimension(dimension_registry: Mapping[str, object], dimension_id: str) -> dict:
    rows = _rows_by_id((dimension_registry or {}).get("dimensions"), "dimension_id")
    return dict(rows.get(str(dimension_id).strip()) or {})


def _lookup_quantity_type(quantity_type_registry: Mapping[str, object], quantity_id: str) -> dict:
    rows = _rows_by_id((quantity_type_registry or {}).get("quantity_types"), "quantity_id")
    return dict(rows.get(str(quantity_id).strip()) or {})


def _apply_error_budget(
    *,
    numeric_error_state: dict | None,
    policy: FixedPointConfig,
    quantity_id: str,
    residual: int,
    ledger_exception_sink: Callable[..., None] | None,
) -> None:
    if not isinstance(numeric_error_state, dict):
        return
    bucket = dict(numeric_error_state.get("error_by_quantity") or {})
    token = str(quantity_id).strip() or "quantity.unknown"
    current = int(bucket.get(token, 0) or 0)
    bucket[token] = int(current + abs(int(residual)))
    numeric_error_state["error_by_quantity"] = dict(bucket)
    if int(policy.error_budget_max) <= 0:
        return
    if int(bucket[token]) <= int(policy.error_budget_max):
        return
    if callable(ledger_exception_sink):
        ledger_exception_sink(
            quantity_id=str(token),
            delta=0,
            exception_type_id="exception.numeric_error_budget",
            domain_id="domain.reality",
            process_id="process.numeric.fixed_point",
            reason_code="numeric.error_budget.exceeded",
            evidence=[
                "residual={}".format(int(residual)),
                "budget={}".format(int(policy.error_budget_max)),
            ],
        )


def quantity_convert(
    quantity: Mapping[str, object],
    target_unit_id: str,
    *,
    unit_registry: Mapping[str, object],
    dimension_registry: Mapping[str, object],
    numeric_policy: Mapping[str, object] | None = None,
    numeric_error_state: dict | None = None,
    ledger_exception_sink: Callable[..., None] | None = None,
) -> Dict[str, object]:
    row = dict(quantity or {})
    source_unit_id = str(row.get("unit_id", "")).strip()
    target_unit_token = str(target_unit_id).strip()
    if not source_unit_id or not target_unit_token:
        raise DimensionError(
            REFUSAL_UNIT_INVALID_CONVERSION,
            "quantity conversion requires source and target unit ids",
            {"source_unit_id": source_unit_id, "target_unit_id": target_unit_token},
        )

    source_unit = _lookup_unit(unit_registry, source_unit_id)
    target_unit = _lookup_unit(unit_registry, target_unit_token)
    if not source_unit or not target_unit:
        raise DimensionError(
            REFUSAL_UNIT_INVALID_CONVERSION,
            "unit conversion references unknown unit_id",
            {"source_unit_id": source_unit_id, "target_unit_id": target_unit_token},
        )

    source_dimension_id = str(source_unit.get("dimension_id", "")).strip()
    target_dimension_id = str(target_unit.get("dimension_id", "")).strip()
    if source_dimension_id != target_dimension_id:
        raise DimensionError(
            REFUSAL_UNIT_INVALID_CONVERSION,
            "unit conversion dimensions do not match",
            {
                "source_unit_id": source_unit_id,
                "target_unit_id": target_unit_token,
                "source_dimension_id": source_dimension_id,
                "target_dimension_id": target_dimension_id,
            },
        )

    source_dimension = _lookup_dimension(dimension_registry, source_dimension_id)
    target_dimension = _lookup_dimension(dimension_registry, target_dimension_id)
    if not source_dimension or not target_dimension or not dimension_equals(source_dimension, target_dimension):
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "dimension registry drift detected during unit conversion",
            {"dimension_id": source_dimension_id},
        )

    value_raw = fixed_point_type(int(row.get("value_raw", 0) or 0))
    source_scale = int(source_unit.get("scale_factor_to_canonical", 0) or 0)
    target_scale = int(target_unit.get("scale_factor_to_canonical", 0) or 0)
    if source_scale <= 0 or target_scale <= 0:
        raise DimensionError(
            REFUSAL_UNIT_INVALID_CONVERSION,
            "scale_factor_to_canonical must be > 0 for conversion",
            {
                "source_unit_id": source_unit_id,
                "target_unit_id": target_unit_token,
            },
        )

    converted_raw, residual = _round_div_away_from_zero(int(value_raw) * int(source_scale), int(target_scale))
    converted_raw = _check_int64(int(converted_raw), context="quantity_convert")

    policy = fixed_point_config_from_policy(numeric_policy)
    if int(residual) != 0:
        _apply_error_budget(
            numeric_error_state=numeric_error_state,
            policy=policy,
            quantity_id=str(row.get("quantity_id", "")),
            residual=int(residual),
            ledger_exception_sink=ledger_exception_sink,
        )

    out = dict(row)
    out["unit_id"] = target_unit_token
    out["dimension_id"] = source_dimension_id
    out["value_raw"] = int(converted_raw)
    return out


def _resolve_quantity_dimension(
    quantity: Mapping[str, object],
    *,
    quantity_type_registry: Mapping[str, object],
    unit_registry: Mapping[str, object],
) -> str:
    row = dict(quantity or {})
    explicit_dimension_id = str(row.get("dimension_id", "")).strip()
    if explicit_dimension_id:
        return explicit_dimension_id

    quantity_id = str(row.get("quantity_id", "")).strip()
    quantity_type_row = _lookup_quantity_type(quantity_type_registry, quantity_id)
    dimension_id = str(quantity_type_row.get("dimension_id", "")).strip()
    if dimension_id:
        return dimension_id

    unit_id = str(row.get("unit_id", "")).strip()
    unit_row = _lookup_unit(unit_registry, unit_id)
    return str(unit_row.get("dimension_id", "")).strip()


def quantity_add(
    q1: Mapping[str, object],
    q2: Mapping[str, object],
    *,
    quantity_type_registry: Mapping[str, object],
    unit_registry: Mapping[str, object],
    dimension_registry: Mapping[str, object],
    numeric_policy: Mapping[str, object] | None = None,
    numeric_error_state: dict | None = None,
    ledger_exception_sink: Callable[..., None] | None = None,
) -> Dict[str, object]:
    left = dict(q1 or {})
    right = dict(q2 or {})

    left_quantity_id = str(left.get("quantity_id", "")).strip()
    right_quantity_id = str(right.get("quantity_id", "")).strip()
    if left_quantity_id != right_quantity_id:
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "quantity_add requires identical quantity_id channels",
            {"left_quantity_id": left_quantity_id, "right_quantity_id": right_quantity_id},
        )

    left_dimension_id = _resolve_quantity_dimension(
        left,
        quantity_type_registry=quantity_type_registry,
        unit_registry=unit_registry,
    )
    right_dimension_id = _resolve_quantity_dimension(
        right,
        quantity_type_registry=quantity_type_registry,
        unit_registry=unit_registry,
    )
    if left_dimension_id != right_dimension_id:
        raise DimensionError(
            REFUSAL_DIMENSION_MISMATCH,
            "quantity_add dimension mismatch",
            {"left_dimension_id": left_dimension_id, "right_dimension_id": right_dimension_id},
        )

    target_unit_id = str(left.get("unit_id", "")).strip()
    if not target_unit_id:
        quantity_type_row = _lookup_quantity_type(quantity_type_registry, left_quantity_id)
        target_unit_id = str(quantity_type_row.get("default_unit_id", "")).strip()
    if not target_unit_id:
        raise DimensionError(
            REFUSAL_UNIT_INVALID_CONVERSION,
            "quantity_add missing target unit_id",
            {"quantity_id": left_quantity_id},
        )

    converted_right = quantity_convert(
        quantity=right,
        target_unit_id=target_unit_id,
        unit_registry=unit_registry,
        dimension_registry=dimension_registry,
        numeric_policy=numeric_policy,
        numeric_error_state=numeric_error_state,
        ledger_exception_sink=ledger_exception_sink,
    )

    policy = fixed_point_config_from_policy(numeric_policy)
    summed_raw = fixed_point_add(int(left.get("value_raw", 0) or 0), int(converted_right.get("value_raw", 0) or 0), config=policy)
    out = dict(left)
    out["unit_id"] = target_unit_id
    out["dimension_id"] = left_dimension_id
    out["value_raw"] = int(summed_raw)
    return out

