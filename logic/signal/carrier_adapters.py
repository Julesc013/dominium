"""LOGIC-1 carrier adapter seams."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


REFUSAL_CARRIER_ADAPTER_INVALID = "refusal.logic.carrier_adapter_invalid"


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> List[object]:
    return list(value) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _canon(value: object):
    if isinstance(value, Mapping):
        return dict((str(key), _canon(value[key])) for key in sorted(value.keys(), key=lambda item: str(item)))
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def build_transducer_binding_row(
    *,
    transducer_binding_id: str,
    carrier_type_id: str,
    transducer_id: str,
    direction: str,
    interface_signature_id: str | None = None,
    model_binding_ids: object = None,
    delay_policy_id: str | None = None,
    noise_policy_id: str | None = None,
    access_policy_id: str | None = None,
    extensions: Mapping[str, object] | None = None,
    deterministic_fingerprint: str = "",
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "transducer_binding_id": _token(transducer_binding_id),
        "carrier_type_id": _token(carrier_type_id),
        "transducer_id": _token(transducer_id),
        "direction": _token(direction).lower() or "read",
        "interface_signature_id": None if interface_signature_id is None else _token(interface_signature_id) or None,
        "model_binding_ids": sorted(_token(item) for item in _as_list(model_binding_ids) if _token(item)),
        "delay_policy_id": None if delay_policy_id is None else _token(delay_policy_id) or None,
        "noise_policy_id": None if noise_policy_id is None else _token(noise_policy_id) or None,
        "access_policy_id": None if access_policy_id is None else _token(access_policy_id) or None,
        "extensions": _canon(_as_map(extensions)),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
    }
    if payload["direction"] not in {"read", "write"}:
        payload["direction"] = "read"
    if not payload["transducer_binding_id"] or not payload["carrier_type_id"] or not payload["transducer_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_transducer_binding_rows(rows: object) -> List[dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in _as_list(rows) if isinstance(item, Mapping)), key=lambda item: _token(item.get("transducer_binding_id"))):
        normalized = build_transducer_binding_row(
            transducer_binding_id=_token(row.get("transducer_binding_id")),
            carrier_type_id=_token(row.get("carrier_type_id")),
            transducer_id=_token(row.get("transducer_id")),
            direction=_token(row.get("direction")),
            interface_signature_id=(None if row.get("interface_signature_id") is None else _token(row.get("interface_signature_id")) or None),
            model_binding_ids=row.get("model_binding_ids"),
            delay_policy_id=(None if row.get("delay_policy_id") is None else _token(row.get("delay_policy_id")) or None),
            noise_policy_id=(None if row.get("noise_policy_id") is None else _token(row.get("noise_policy_id")) or None),
            access_policy_id=(None if row.get("access_policy_id") is None else _token(row.get("access_policy_id")) or None),
            extensions=_as_map(row.get("extensions")),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
        )
        if normalized:
            out[_token(normalized.get("transducer_binding_id"))] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def sig_receipt_to_message_value_payload(receipt_row: Mapping[str, object]) -> dict:
    row = _as_map(receipt_row)
    artifact_id = _token(row.get("artifact_id"))
    if not artifact_id:
        return {}
    return {
        "artifact_id": artifact_id,
        "receipt_id": None if row.get("receipt_id") is None else _token(row.get("receipt_id")) or None,
        "receipt_metadata": {
            "subject_id": _token(row.get("subject_id")) or None,
            "envelope_id": _token(row.get("envelope_id")) or None,
            "delivery_event_id": _token(row.get("delivery_event_id")) or None,
            "acquired_tick": int(max(0, _as_int(row.get("acquired_tick", 0), 0))),
            "trust_weight": row.get("trust_weight"),
            "verification_state": _token(row.get("verification_state")) or None,
        },
    }


def sig_receipt_to_signal_request(
    *,
    network_id: str,
    element_id: str,
    port_id: str,
    receipt_row: Mapping[str, object],
    signal_id: str | None = None,
    delay_policy_id: str = "delay.sig_delivery",
    noise_policy_id: str = "noise.none",
    protocol_id: str | None = "protocol.none",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    value_payload = sig_receipt_to_message_value_payload(receipt_row)
    if not value_payload:
        return {}
    ext = _as_map(extensions)
    ext["adapter_kind"] = "carrier.sig.receipt_to_message"
    ext["receipt_subject_id"] = _token(_as_map(receipt_row).get("subject_id")) or None
    return {
        "signal_id": None if signal_id is None else _token(signal_id) or None,
        "network_id": _token(network_id),
        "element_id": _token(element_id),
        "port_id": _token(port_id),
        "signal_type_id": "signal.message",
        "carrier_type_id": "carrier.sig",
        "delay_policy_id": _token(delay_policy_id) or "delay.sig_delivery",
        "noise_policy_id": _token(noise_policy_id) or "noise.none",
        "protocol_id": None if protocol_id is None else _token(protocol_id) or None,
        "value_payload": value_payload,
        "extensions": _canon(ext),
    }


def adapt_signal_row_to_transducer_write(
    *,
    signal_row: Mapping[str, object],
    transducer_binding_row: Mapping[str, object],
    current_tick: int,
) -> dict:
    signal = _as_map(signal_row)
    binding = _as_map(transducer_binding_row)
    if _token(binding.get("direction")) != "write":
        return {"result": "refused", "reason_code": REFUSAL_CARRIER_ADAPTER_INVALID}
    return {
        "result": "complete",
        "adapter_kind": "carrier.transducer.write",
        "transducer_id": _token(binding.get("transducer_id")),
        "carrier_type_id": _token(binding.get("carrier_type_id")),
        "requested_tick": int(max(0, _as_int(current_tick, 0))),
        "interface_signature_id": _token(binding.get("interface_signature_id")) or None,
        "model_binding_ids": list(binding.get("model_binding_ids") or []),
        "value_ref": _canon(_as_map(signal.get("value_ref"))),
        "signal_id": _token(signal.get("signal_id")),
        "extensions": {
            "delay_policy_id": _token(_as_map(signal.get("extensions")).get("delay_policy_id")) or None,
            "noise_policy_id": _token(_as_map(signal.get("extensions")).get("noise_policy_id")) or None,
            "adapter_source": "logic.signal.carrier_adapters",
        },
        "deterministic_fingerprint": canonical_sha256(
            {
                "transducer_id": _token(binding.get("transducer_id")),
                "signal_id": _token(signal.get("signal_id")),
                "tick": int(max(0, _as_int(current_tick, 0))),
            }
        ),
    }


def adapt_transducer_measurement_to_signal_request(
    *,
    transducer_binding_row: Mapping[str, object],
    measurement_payload: Mapping[str, object],
    network_id: str,
    element_id: str,
    port_id: str,
    signal_type_id: str,
    carrier_type_id: str | None = None,
    delay_policy_id: str | None = None,
    noise_policy_id: str | None = None,
    bus_id: str | None = None,
    protocol_id: str | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    binding = _as_map(transducer_binding_row)
    if _token(binding.get("direction")) != "read":
        return {}
    ext = _as_map(extensions)
    ext["adapter_kind"] = "carrier.transducer.read_to_signal"
    ext["transducer_id"] = _token(binding.get("transducer_id"))
    ext["model_binding_ids"] = list(binding.get("model_binding_ids") or [])
    return {
        "network_id": _token(network_id),
        "element_id": _token(element_id),
        "port_id": _token(port_id),
        "signal_type_id": _token(signal_type_id),
        "carrier_type_id": _token(carrier_type_id) or _token(binding.get("carrier_type_id")),
        "delay_policy_id": _token(delay_policy_id) or _token(binding.get("delay_policy_id")) or "delay.none",
        "noise_policy_id": _token(noise_policy_id) or _token(binding.get("noise_policy_id")) or "noise.none",
        "bus_id": None if bus_id is None else _token(bus_id) or None,
        "protocol_id": None if protocol_id is None else _token(protocol_id) or None,
        "value_payload": _canon(_as_map(measurement_payload)),
        "extensions": _canon(ext),
    }


__all__ = [
    "REFUSAL_CARRIER_ADAPTER_INVALID",
    "adapt_signal_row_to_transducer_write",
    "adapt_transducer_measurement_to_signal_request",
    "build_transducer_binding_row",
    "normalize_transducer_binding_rows",
    "sig_receipt_to_message_value_payload",
    "sig_receipt_to_signal_request",
]
