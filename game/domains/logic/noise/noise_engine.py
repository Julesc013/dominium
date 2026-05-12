"""LOGIC-8 deterministic noise application helpers."""

from __future__ import annotations

from typing import Dict, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _token(value: object) -> str:
    return str(value or "").strip()


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if isinstance(value, float):
        return int(round(float(value)))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return str(value)


def logic_noise_policy_rows_by_id(payload: Mapping[str, object] | None) -> Dict[str, dict]:
    body = _as_map(payload)
    rows = body.get("logic_noise_policies")
    if not isinstance(rows, list):
        rows = body.get("noise_policies")
    if not isinstance(rows, list):
        record = _as_map(body.get("record"))
        rows = record.get("logic_noise_policies")
        if not isinstance(rows, list):
            rows = record.get("noise_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: _token(item.get("noise_policy_id"))):
        noise_policy_id = _token(row.get("noise_policy_id"))
        if not noise_policy_id:
            continue
        payload_row = {
            "schema_version": "1.0.0",
            "noise_policy_id": noise_policy_id,
            "kind": _token(row.get("kind")) or "none",
            "magnitude": int(max(0, _as_int(row.get("magnitude"), 0))),
            "rng_stream_name": None if row.get("rng_stream_name") is None else _token(row.get("rng_stream_name")) or None,
            "extensions": _canon(_as_map(row.get("extensions"))),
        }
        payload_row["deterministic_fingerprint"] = canonical_sha256(dict(payload_row, deterministic_fingerprint=""))
        out[noise_policy_id] = payload_row
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def apply_noise_policy_to_value(
    *,
    current_tick: int,
    network_id: str,
    element_id: str,
    port_id: str,
    signal_type_id: str,
    value_ref: Mapping[str, object],
    noise_policy_row: Mapping[str, object] | None,
    allow_named_rng: bool,
    field_modifier_stubs: Mapping[str, object] | None = None,
) -> dict:
    row = dict(noise_policy_row or {})
    policy_id = _token(row.get("noise_policy_id")) or "noise.none"
    kind = _token(row.get("kind")) or "none"
    magnitude = int(max(0, _as_int(row.get("magnitude"), 0)))
    modifiers = _as_map(field_modifier_stubs)
    magnetic_flux = int(max(0, _as_int(modifiers.get("field.magnetic_flux_stub"), 0)))
    effective_magnitude = int(max(0, magnitude + magnetic_flux))
    source_value_ref = _canon(_as_map(value_ref))
    next_value_ref = _canon(source_value_ref)
    rng_stream_name = None if row.get("rng_stream_name") is None else _token(row.get("rng_stream_name")) or None
    rng_seed_hash = ""
    decision_reason = "none"
    rng_used = False
    if kind == "quantize" and _token(_as_map(source_value_ref).get("value_kind")) == "scalar" and effective_magnitude > 0:
        raw_value = int(_as_int(_as_map(source_value_ref).get("value_fixed"), 0))
        scale = max(1, effective_magnitude)
        quantized = int(((raw_value + (scale // 2)) // scale) * scale) if raw_value >= 0 else int(-(((-raw_value) + (scale // 2)) // scale) * scale)
        next_value_ref = dict(_as_map(source_value_ref))
        next_value_ref["value_fixed"] = int(quantized)
        decision_reason = "quantized"
    elif kind == "named_rng" and _token(_as_map(source_value_ref).get("value_kind")) == "scalar":
        if allow_named_rng and rng_stream_name:
            rng_seed_hash = canonical_sha256(
                {
                    "network_id": _token(network_id),
                    "element_id": _token(element_id),
                    "port_id": _token(port_id),
                    "signal_type_id": _token(signal_type_id),
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "rng_stream_name": rng_stream_name,
                }
            )
            jitter_span = max(1, effective_magnitude or 1)
            jitter = int(int(rng_seed_hash[:8], 16) % ((jitter_span * 2) + 1)) - jitter_span
            raw_value = int(_as_int(_as_map(source_value_ref).get("value_fixed"), 0))
            next_value_ref = dict(_as_map(source_value_ref))
            next_value_ref["value_fixed"] = int(max(0, raw_value + jitter))
            decision_reason = "named_rng_applied"
            rng_used = True
        else:
            decision_reason = "named_rng_blocked"
    decision_row = {
        "decision_id": "decision.logic.noise.{}".format(
            canonical_sha256(
                {
                    "tick": int(max(0, _as_int(current_tick, 0))),
                    "network_id": _token(network_id),
                    "element_id": _token(element_id),
                    "port_id": _token(port_id),
                    "noise_policy_id": policy_id,
                }
            )[:16]
        ),
        "tick": int(max(0, _as_int(current_tick, 0))),
        "network_id": _token(network_id),
        "slot_key": "{}|{}|{}".format(_token(network_id), _token(element_id), _token(port_id)),
        "noise_policy_id": policy_id,
        "signal_type_id": _token(signal_type_id),
        "reason": decision_reason,
        "rng_stream_name": rng_stream_name,
        "rng_seed_hash": rng_seed_hash or None,
        "input_value_hash": canonical_sha256(_canon(source_value_ref)),
        "output_value_hash": canonical_sha256(_canon(next_value_ref)),
        "extensions": {
            "kind": kind,
            "magnitude": int(magnitude),
            "effective_magnitude": int(effective_magnitude),
            "rng_used": bool(rng_used),
        },
    }
    decision_row["deterministic_fingerprint"] = canonical_sha256(dict(decision_row, deterministic_fingerprint=""))
    return {
        "value_ref": _canon(next_value_ref),
        "decision_row": decision_row,
        "rng_used": bool(rng_used),
        "decision_reason": decision_reason,
    }


__all__ = [
    "apply_noise_policy_to_value",
    "logic_noise_policy_rows_by_id",
]
