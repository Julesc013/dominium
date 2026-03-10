"""SERVER-MVP-0 deterministic loopback transport adapter."""

from __future__ import annotations

from typing import Mapping

from src.net.policies.policy_server_authoritative import POLICY_ID_SERVER_AUTHORITATIVE, join_client_midstream
from src.net.transport.loopback import LoopbackTransport
from src.server.server_boot import REFUSAL_CLIENT_UNAUTHORIZED, build_connection_authority_context
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import refusal
from tools.xstack.sessionx.net_protocol import build_proto_message, decode_proto_message, encode_proto_message


def _runtime(server_boot_payload: Mapping[str, object] | None) -> dict:
    runtime = (dict(server_boot_payload or {})).get("runtime")
    if isinstance(runtime, dict):
        return runtime
    return {}


def _server_meta(runtime: Mapping[str, object] | None) -> dict:
    if not isinstance(runtime, dict):
        return {}
    meta = runtime.get("server_mvp")
    if isinstance(meta, dict):
        return meta
    meta = {}
    runtime["server_mvp"] = meta
    return meta


def _listener_config(server_boot_payload: Mapping[str, object] | None) -> tuple[str, str]:
    runtime = _runtime(server_boot_payload)
    meta = _server_meta(runtime)
    endpoint = str(meta.get("listener_endpoint", "")).strip()
    server_peer_id = str(meta.get("listener_peer_id", "")).strip()
    return endpoint, server_peer_id


def _refuse(message: str, *, code: str = REFUSAL_CLIENT_UNAUTHORIZED, details: Mapping[str, object] | None = None, path: str = "$") -> dict:
    relevant_ids = {
        str(key): str(value).strip()
        for key, value in sorted((dict(details or {})).items(), key=lambda item: str(item[0]))
        if str(value).strip()
    }
    return refusal(code, message, "Use the deterministic loopback handshake and retry.", relevant_ids, path)


def create_loopback_listener(server_boot_payload: Mapping[str, object]) -> dict:
    runtime = _runtime(server_boot_payload)
    endpoint, server_peer_id = _listener_config(server_boot_payload)
    if (not endpoint) or (not server_peer_id):
        return _refuse(
            "server loopback listener requires endpoint and server peer id",
            details={"endpoint": endpoint or "<empty>", "server_peer_id": server_peer_id or "<empty>"},
            path="$.network",
        )
    LoopbackTransport.listen(endpoint=endpoint, server_peer_id=server_peer_id)
    meta = _server_meta(runtime)
    meta["listener_bound"] = True
    runtime["server_mvp"] = meta
    return {
        "result": "complete",
        "endpoint": endpoint,
        "server_peer_id": server_peer_id,
        "transport_id": "transport.loopback",
    }


def send_client_hello(endpoint: str, client_peer_id: str, account_id: str = "account.loopback") -> dict:
    endpoint_token = str(endpoint or "").strip()
    peer_token = str(client_peer_id or "").strip()
    if (not endpoint_token) or (not peer_token):
        return _refuse(
            "client hello requires endpoint and client_peer_id",
            details={"endpoint": endpoint_token or "<empty>", "client_peer_id": peer_token or "<empty>"},
            path="$.client_hello",
        )
    client = LoopbackTransport(peer_id=peer_token, role="client")
    connected = client.connect(endpoint_token)
    if str(connected.get("result", "")) != "complete":
        return dict(connected)
    hello_payload = {
        "schema_version": "1.0.0",
        "client_peer_id": peer_token,
        "account_id": str(account_id or "account.loopback").strip() or "account.loopback",
        "protocol_version": "1.0.0",
        "extensions": {},
    }
    message = build_proto_message(
        msg_type="handshake_request",
        msg_id="msg.client_hello.{}".format(str(client.connection_id or canonical_sha256(hello_payload)[:16])),
        sequence=1,
        payload_schema_id="server.loopback.hello.v1",
        payload_inline_json=hello_payload,
    )
    sent = client.send(encode_proto_message(message))
    if str(sent.get("result", "")) != "complete":
        return dict(sent)
    return {
        "result": "complete",
        "client_transport": client,
        "connection_id": str(client.connection_id),
        "client_peer_id": peer_token,
        "hello_payload": hello_payload,
    }


def accept_loopback_connection(server_boot_payload: Mapping[str, object]) -> dict:
    runtime = _runtime(server_boot_payload)
    meta = _server_meta(runtime)
    server_config = dict(meta.get("server_config") or {})
    endpoint, server_peer_id = _listener_config(server_boot_payload)
    if (not endpoint) or (not server_peer_id):
        return _refuse(
            "server loopback accept requires a bound endpoint",
            details={"endpoint": endpoint or "<empty>", "server_peer_id": server_peer_id or "<empty>"},
            path="$.network",
        )

    max_clients = int(server_config.get("max_clients", 1) or 1)
    connections = dict(runtime.get("server_mvp_connections") or {})
    if len(connections) >= max_clients:
        return _refuse(
            "server max_clients limit reached",
            code="refusal.client.capacity_exceeded",
            details={"max_clients": str(max_clients)},
            path="$.max_clients",
        )

    listener = LoopbackTransport.listen(endpoint=endpoint, server_peer_id=server_peer_id)
    accepted = listener.accept()
    if str(accepted.get("result", "")) == "empty":
        return dict(accepted)
    if str(accepted.get("result", "")) != "complete":
        return dict(accepted)
    inbound = listener.recv()
    if str(inbound.get("result", "")) != "complete":
        return dict(inbound)
    decoded = decode_proto_message(
        repo_root=str((dict(server_boot_payload or {})).get("repo_root", "")),
        message_bytes=bytes(inbound.get("message_bytes") or b""),
    )
    if str(decoded.get("result", "")) != "complete":
        return dict(decoded)
    proto_message = dict(decoded.get("proto_message") or {})
    hello_payload = dict((dict(proto_message.get("payload_ref") or {})).get("inline_json") or {})
    peer_id = str(hello_payload.get("client_peer_id", accepted.get("remote_peer_id", ""))).strip()
    account_id = str(hello_payload.get("account_id", "account.loopback")).strip() or "account.loopback"
    connection_id = str(accepted.get("connection_id", "")).strip()

    session_spec = dict((dict(server_boot_payload or {})).get("session_spec") or {})
    authority_context = build_connection_authority_context(
        session_spec=session_spec,
        server_profile=dict(meta.get("server_profile") or {}),
        connection_id=connection_id,
        account_id=account_id,
    )
    joined = join_client_midstream(
        repo_root=str((dict(server_boot_payload or {})).get("repo_root", "")),
        runtime=runtime,
        peer_id=peer_id,
        authority_context=authority_context,
        law_profile=dict(meta.get("law_profile") or {}),
        lens_profile=dict(meta.get("lens_profile") or {}),
        negotiated_policy_id=POLICY_ID_SERVER_AUTHORITATIVE,
    )
    if str(joined.get("result", "")) != "complete":
        return dict(joined)

    live_transports = dict(runtime.get("_server_mvp_live_transports") or {})
    live_transports[connection_id] = listener
    runtime["_server_mvp_live_transports"] = dict((key, live_transports[key]) for key in sorted(live_transports.keys()))

    connections[connection_id] = {
        "connection_id": connection_id,
        "peer_id": peer_id,
        "account_id": account_id,
        "authority_context": authority_context,
        "snapshot_id": str(joined.get("snapshot_id", "")).strip(),
        "perceived_hash": str(joined.get("perceived_hash", "")).strip(),
        "transport_id": "transport.loopback",
    }
    runtime["server_mvp_connections"] = dict((key, connections[key]) for key in sorted(connections.keys()))

    server = dict(runtime.get("server") or {})
    ack_payload = {
        "schema_version": "1.0.0",
        "connection_id": connection_id,
        "peer_id": peer_id,
        "account_id": account_id,
        "tick": int(server.get("network_tick", 0) or 0),
        "session_info": {
            "save_id": str(session_spec.get("save_id", "")).strip(),
            "universe_id": str(session_spec.get("universe_id", "")).strip(),
            "pack_lock_hash": str(session_spec.get("pack_lock_hash", "")).strip(),
            "contract_bundle_hash": str(session_spec.get("contract_bundle_hash", "")).strip(),
        },
        "extensions": {},
    }
    ack_message = build_proto_message(
        msg_type="handshake_response",
        msg_id="msg.server_hello_ack.{}".format(connection_id),
        sequence=2,
        payload_schema_id="server.loopback.ack.v1",
        payload_inline_json=ack_payload,
    )
    sent = listener.send(encode_proto_message(ack_message))
    if str(sent.get("result", "")) != "complete":
        return dict(sent)
    return {
        "result": "complete",
        "connection_id": connection_id,
        "peer_id": peer_id,
        "account_id": account_id,
        "authority_context": authority_context,
        "ack_payload": ack_payload,
    }


def broadcast_tick_stream(server_boot_payload: Mapping[str, object], *, tick: int, tick_hash: str) -> dict:
    runtime = _runtime(server_boot_payload)
    live_transports = dict(runtime.get("_server_mvp_live_transports") or {})
    rows = []
    for connection_id in sorted(live_transports.keys()):
        transport = live_transports.get(connection_id)
        if not isinstance(transport, LoopbackTransport):
            continue
        payload = {
            "schema_version": "1.0.0",
            "connection_id": str(connection_id),
            "tick": int(tick),
            "tick_hash": str(tick_hash or "").strip(),
            "extensions": {},
        }
        message = build_proto_message(
            msg_type="payload",
            msg_id="msg.tick_stream_stub.{}.{}".format(str(connection_id), int(tick)),
            sequence=int(tick),
            payload_schema_id="server.tick_stream.stub.v1",
            payload_inline_json=payload,
        )
        sent = transport.send(encode_proto_message(message))
        rows.append(
            {
                "connection_id": str(connection_id),
                "result": str(sent.get("result", "")),
                "tick": int(tick),
            }
        )
    return {
        "result": "complete",
        "broadcasts": rows,
    }
