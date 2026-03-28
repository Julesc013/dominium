"""PHYS-3 deterministic energy ledger and transformation helpers."""

from __future__ import annotations

from typing import Dict, List, Mapping

from meta.numeric import tolerance_abs_for_quantity
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


def _quantity_values_map(value: object) -> Dict[str, int]:
    payload = _as_map(value)
    out: Dict[str, int] = {}
    for key, raw in sorted(payload.items(), key=lambda item: str(item[0])):
        quantity_id = str(key or "").strip()
        if not quantity_id.startswith("quantity."):
            continue
        out[quantity_id] = int(_as_int(raw, 0))
    return out


def _hash_payload(value: Mapping[str, object]) -> str:
    return canonical_sha256(dict(value))


def _is_energy_quantity(quantity_id: str) -> bool:
    token = str(quantity_id or "").strip()
    return (
        token.startswith("quantity.energy_")
        or token in {"quantity.energy_total", "quantity.mass_energy_total"}
    )


def build_energy_transformation(
    *,
    transformation_id: str,
    input_quantities: Mapping[str, object] | None,
    output_quantities: Mapping[str, object] | None,
    boundary_allowed: bool,
    requires_profile_flag: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    token = str(transformation_id or "").strip()
    if not token:
        return {}
    payload = {
        "schema_version": "1.0.0",
        "transformation_id": token,
        "input_quantities": _quantity_values_map(input_quantities),
        "output_quantities": _quantity_values_map(output_quantities),
        "boundary_allowed": bool(boundary_allowed),
        "requires_profile_flag": (str(requires_profile_flag).strip() or None) if requires_profile_flag is not None else None,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_energy_transformation_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("transformation_id", ""))):
        normalized = build_energy_transformation(
            transformation_id=str(row.get("transformation_id", "")).strip(),
            input_quantities=dict(row.get("input_quantities") or {}),
            output_quantities=dict(row.get("output_quantities") or {}),
            boundary_allowed=bool(row.get("boundary_allowed", False)),
            requires_profile_flag=(None if row.get("requires_profile_flag") is None else str(row.get("requires_profile_flag", "")).strip() or None),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("transformation_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def energy_transformation_rows_by_id(rows: object) -> Dict[str, dict]:
    normalized = normalize_energy_transformation_rows(rows)
    return dict(
        (str(row.get("transformation_id", "")).strip(), dict(row))
        for row in normalized
        if str(row.get("transformation_id", "")).strip()
    )


def build_energy_ledger_entry(
    *,
    entry_id: str,
    tick: int,
    transformation_id: str,
    source_id: str,
    input_values: Mapping[str, object] | None,
    output_values: Mapping[str, object] | None,
    energy_total_delta: int,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    entry_token = str(entry_id or "").strip()
    transform_token = str(transformation_id or "").strip()
    source_token = str(source_id or "").strip()
    if (not entry_token) or (not transform_token) or (not source_token):
        return {}
    payload = {
        "schema_version": "1.0.0",
        "entry_id": entry_token,
        "tick": int(max(0, _as_int(tick, 0))),
        "transformation_id": transform_token,
        "source_id": source_token,
        "input_values": _quantity_values_map(input_values),
        "output_values": _quantity_values_map(output_values),
        "energy_total_delta": int(_as_int(energy_total_delta, 0)),
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_energy_ledger_entry_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (
            int(max(0, _as_int(item.get("tick", 0), 0))),
            str(item.get("transformation_id", "")),
            str(item.get("source_id", "")),
            str(item.get("entry_id", "")),
        ),
    ):
        normalized = build_energy_ledger_entry(
            entry_id=str(row.get("entry_id", "")).strip(),
            tick=_as_int(row.get("tick", 0), 0),
            transformation_id=str(row.get("transformation_id", "")).strip(),
            source_id=str(row.get("source_id", "")).strip(),
            input_values=dict(row.get("input_values") or {}),
            output_values=dict(row.get("output_values") or {}),
            energy_total_delta=_as_int(row.get("energy_total_delta", 0), 0),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("entry_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_boundary_flux_event(
    *,
    flux_id: str,
    tick: int,
    quantity_id: str,
    value: int,
    direction: str,
    reason_code: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    flux_token = str(flux_id or "").strip()
    quantity_token = str(quantity_id or "").strip()
    direction_token = str(direction or "").strip().lower()
    reason_token = str(reason_code or "").strip()
    if (not flux_token) or (not quantity_token) or (not reason_token):
        return {}
    if direction_token not in {"in", "out"}:
        direction_token = "in"
    payload = {
        "schema_version": "1.0.0",
        "flux_id": flux_token,
        "tick": int(max(0, _as_int(tick, 0))),
        "quantity_id": quantity_token,
        "value": int(_as_int(value, 0)),
        "direction": direction_token,
        "reason_code": reason_token,
        "deterministic_fingerprint": "",
        "extensions": _canon(_as_map(extensions)),
    }
    payload["deterministic_fingerprint"] = _hash_payload(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_boundary_flux_event_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in rows if isinstance(item, Mapping)),
        key=lambda item: (int(max(0, _as_int(item.get("tick", 0), 0))), str(item.get("flux_id", ""))),
    ):
        normalized = build_boundary_flux_event(
            flux_id=str(row.get("flux_id", "")).strip(),
            tick=_as_int(row.get("tick", 0), 0),
            quantity_id=str(row.get("quantity_id", "")).strip(),
            value=_as_int(row.get("value", 0), 0),
            direction=str(row.get("direction", "in")).strip().lower(),
            reason_code=str(row.get("reason_code", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        if not normalized:
            continue
        out[str(normalized.get("flux_id", "")).strip()] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def evaluate_energy_balance(
    *,
    input_values: Mapping[str, object] | None,
    output_values: Mapping[str, object] | None,
) -> dict:
    in_map = _quantity_values_map(input_values)
    out_map = _quantity_values_map(output_values)
    in_total = int(sum(int(value) for key, value in in_map.items() if _is_energy_quantity(str(key))))
    out_total = int(sum(int(value) for key, value in out_map.items() if _is_energy_quantity(str(key))))
    return {
        "input_total": int(in_total),
        "output_total": int(out_total),
        "energy_total_delta": int(out_total - in_total),
        "conserved": bool(in_total == out_total),
    }


def record_energy_transformation(
    *,
    transformation_rows: object,
    transformation_id: str,
    tick: int,
    source_id: str,
    input_values: Mapping[str, object] | None,
    output_values: Mapping[str, object] | None,
    enforce_conservation: bool,
    tolerance: int = 0,
    quantity_tolerance_registry: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    transform_token = str(transformation_id or "").strip()
    source_token = str(source_id or "").strip()
    if (not transform_token) or (not source_token):
        return {"result": "refused", "reason_code": "refusal.energy.invalid_transform_request"}
    rows_by_id = energy_transformation_rows_by_id(transformation_rows)
    transformation_row = dict(rows_by_id.get(transform_token) or {})
    if not transformation_row:
        return {
            "result": "refused",
            "reason_code": "refusal.energy.transform_unregistered",
            "transformation_id": transform_token,
        }
    balance = evaluate_energy_balance(input_values=input_values, output_values=output_values)
    allowed_delta = int(max(0, _as_int(tolerance, 0)))
    if allowed_delta <= 0:
        allowed_delta = int(
            tolerance_abs_for_quantity(
                quantity_id="quantity.energy_total",
                quantity_tolerance_registry=quantity_tolerance_registry,
                default_value=0,
            )
        )
    delta = int(_as_int(balance.get("energy_total_delta", 0), 0))
    boundary_allowed = bool(transformation_row.get("boundary_allowed", False))
    if bool(enforce_conservation) and (not boundary_allowed) and abs(delta) > allowed_delta:
        return {
            "result": "violation",
            "reason_code": "refusal.energy.conservation_violation",
            "transformation_id": transform_token,
            "source_id": source_token,
            "energy_total_delta": int(delta),
            "tolerance_abs": int(allowed_delta),
            "input_total": int(_as_int(balance.get("input_total", 0), 0)),
            "output_total": int(_as_int(balance.get("output_total", 0), 0)),
        }
    entry_id = "ledger.energy.{}".format(
        canonical_sha256(
            {
                "tick": int(max(0, _as_int(tick, 0))),
                "transformation_id": transform_token,
                "source_id": source_token,
                "input_values": _quantity_values_map(input_values),
                "output_values": _quantity_values_map(output_values),
            }
        )[:16]
    )
    entry = build_energy_ledger_entry(
        entry_id=entry_id,
        tick=int(max(0, _as_int(tick, 0))),
        transformation_id=transform_token,
        source_id=source_token,
        input_values=_quantity_values_map(input_values),
        output_values=_quantity_values_map(output_values),
        energy_total_delta=int(delta),
        extensions=_as_map(extensions),
    )
    if not entry:
        return {
            "result": "refused",
            "reason_code": "refusal.energy.ledger_entry_invalid",
            "transformation_id": transform_token,
            "source_id": source_token,
        }
    return {
        "result": "complete",
        "entry": entry,
        "transformation": transformation_row,
        "balance": dict(balance),
        "tolerance_abs": int(allowed_delta),
    }


__all__ = [
    "build_boundary_flux_event",
    "build_energy_ledger_entry",
    "build_energy_transformation",
    "energy_transformation_rows_by_id",
    "evaluate_energy_balance",
    "normalize_boundary_flux_event_rows",
    "normalize_energy_ledger_entry_rows",
    "normalize_energy_transformation_rows",
    "record_energy_transformation",
]
