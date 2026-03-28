"""LOGIC-9 protocol row builders and normalizers."""

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


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _canon(value: object):
    if isinstance(value, Mapping):
        return {str(key): _canon(value[key]) for key in sorted(value.keys(), key=lambda item: str(item))}
    if isinstance(value, list):
        return [_canon(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def build_protocol_frame_row(
    *,
    frame_id: str,
    protocol_id: str,
    src_endpoint_id: str,
    dst_address: Mapping[str, object],
    payload_ref: Mapping[str, object],
    checksum: str,
    tick_sent: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "frame_id": _token(frame_id),
        "protocol_id": _token(protocol_id),
        "src_endpoint_id": _token(src_endpoint_id),
        "dst_address": _canon(_as_map(dst_address)),
        "payload_ref": _canon(_as_map(payload_ref)),
        "checksum": _token(checksum),
        "tick_sent": int(max(0, _as_int(tick_sent, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["frame_id"] or not payload["protocol_id"] or not payload["src_endpoint_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_protocol_frame_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick_sent"), 0), _token(item.get("frame_id"))),
    ):
        normalized = build_protocol_frame_row(
            frame_id=_token(row.get("frame_id")),
            protocol_id=_token(row.get("protocol_id")),
            src_endpoint_id=_token(row.get("src_endpoint_id")),
            dst_address=_as_map(row.get("dst_address")),
            payload_ref=_as_map(row.get("payload_ref")),
            checksum=_token(row.get("checksum")),
            tick_sent=_as_int(row.get("tick_sent"), 0),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        frame_id = _token(normalized.get("frame_id"))
        if frame_id:
            out[frame_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_arbitration_state_row(
    *,
    bus_id: str,
    policy_id: str,
    token_holder: str | None = None,
    last_winner: str | None = None,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "bus_id": _token(bus_id),
        "policy_id": _token(policy_id),
        "token_holder": None if token_holder is None else _token(token_holder) or None,
        "last_winner": None if last_winner is None else _token(last_winner) or None,
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    if not payload["bus_id"] or not payload["policy_id"]:
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_arbitration_state_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_token(item.get("bus_id")), _token(item.get("policy_id"))),
    ):
        normalized = build_arbitration_state_row(
            bus_id=_token(row.get("bus_id")),
            policy_id=_token(row.get("policy_id")),
            token_holder=(None if row.get("token_holder") is None else _token(row.get("token_holder")) or None),
            last_winner=(None if row.get("last_winner") is None else _token(row.get("last_winner")) or None),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        bus_id = _token(normalized.get("bus_id"))
        if bus_id:
            out[bus_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


def build_protocol_event_record_row(
    *,
    event_id: str,
    protocol_id: str,
    bus_id: str,
    frame_id: str,
    result: str,
    tick: int,
    deterministic_fingerprint: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    result_token = _token(result).lower() or "dropped"
    if result_token not in {"delivered", "dropped", "blocked", "corrupted"}:
        result_token = "dropped"
    payload = {
        "schema_version": "1.0.0",
        "event_id": _token(event_id),
        "protocol_id": _token(protocol_id),
        "bus_id": _token(bus_id),
        "frame_id": _token(frame_id),
        "result": result_token,
        "tick": int(max(0, _as_int(tick, 0))),
        "deterministic_fingerprint": _token(deterministic_fingerprint),
        "extensions": _canon(_as_map(extensions)),
    }
    required = (
        payload["event_id"],
        payload["protocol_id"],
        payload["bus_id"],
        payload["frame_id"],
        payload["result"],
    )
    if any(not item for item in required):
        return {}
    if not payload["deterministic_fingerprint"]:
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def normalize_protocol_event_record_rows(rows: object) -> list[dict]:
    out: Dict[str, dict] = {}
    for row in sorted(
        (dict(item) for item in _as_list(rows) if isinstance(item, Mapping)),
        key=lambda item: (_as_int(item.get("tick"), 0), _token(item.get("event_id"))),
    ):
        normalized = build_protocol_event_record_row(
            event_id=_token(row.get("event_id")),
            protocol_id=_token(row.get("protocol_id")),
            bus_id=_token(row.get("bus_id")),
            frame_id=_token(row.get("frame_id")),
            result=_token(row.get("result")),
            tick=_as_int(row.get("tick"), 0),
            deterministic_fingerprint=_token(row.get("deterministic_fingerprint")),
            extensions=_as_map(row.get("extensions")),
        )
        event_id = _token(normalized.get("event_id"))
        if event_id:
            out[event_id] = normalized
    return [dict(out[key]) for key in sorted(out.keys())]


__all__ = [
    "build_arbitration_state_row",
    "build_protocol_event_record_row",
    "build_protocol_frame_row",
    "normalize_arbitration_state_rows",
    "normalize_protocol_event_record_rows",
    "normalize_protocol_frame_rows",
]
