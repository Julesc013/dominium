"""Client-side deterministic loopback handshake helpers."""

from __future__ import annotations

from typing import Mapping

from src.net.transport.loopback import LoopbackTransport
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.net_protocol import build_proto_message, decode_proto_message, encode_proto_message


def _decode(repo_root: str, recv_result: Mapping[str, object]) -> dict:
    if str((dict(recv_result or {})).get("result", "")).strip() != "complete":
        return {}
    decoded = decode_proto_message(
        repo_root=str(repo_root or "").strip(),
        message_bytes=bytes((dict(recv_result or {})).get("message_bytes") or b""),
    )
    if str(decoded.get("result", "")) != "complete":
        return {}
    return dict(decoded.get("proto_message") or {})


def read_loopback_handshake_response(repo_root: str, client_transport: object) -> dict:
    transport = client_transport if isinstance(client_transport, LoopbackTransport) else None
    if transport is None:
        return {"result": "refused", "reason_code": "refusal.client.loopback_transport_missing"}
    proto = _decode(repo_root, transport.recv())
    if not proto:
        return {"result": "empty"}
    payload = dict((dict(proto.get("payload_ref") or {})).get("inline_json") or {})
    extensions = dict(payload.get("extensions") or {})
    return {
        "result": "complete",
        "proto_message": proto,
        "payload": payload,
        "handshake_messages": [
            dict(row) for row in list(extensions.get("official.handshake_messages") or []) if isinstance(row, Mapping)
        ],
        "session_begin_payload": dict(extensions.get("official.session_begin") or {}),
    }


def send_loopback_client_ack(
    *,
    client_transport: object,
    connection_id: str,
    negotiation_record_hash: str,
    accepted: bool,
    compatibility_mode_id: str,
    sequence: int = 3,
) -> dict:
    transport = client_transport if isinstance(client_transport, LoopbackTransport) else None
    if transport is None:
        return {"result": "refused", "reason_code": "refusal.client.loopback_transport_missing"}
    payload = {
        "schema_version": "1.0.0",
        "connection_id": str(connection_id or "").strip(),
        "negotiation_record_hash": str(negotiation_record_hash or "").strip(),
        "accepted": bool(accepted),
        "compatibility_mode_id": str(compatibility_mode_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    message = build_proto_message(
        msg_type="handshake_ack",
        msg_id="msg.client_ack.{}".format(str(connection_id or canonical_sha256(payload)[:12])),
        sequence=max(1, int(sequence or 1)),
        payload_schema_id="compat.handshake.ack.v1",
        payload_inline_json=payload,
    )
    return transport.send(encode_proto_message(message))
