"""SERVER-MVP deterministic loopback transport adapter."""

from __future__ import annotations

import os
from typing import Mapping

from src.compat import (
    READ_ONLY_LAW_PROFILE_ID,
    REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
    build_compat_refusal,
    build_default_endpoint_descriptor,
    build_handshake_message,
    build_session_begin_payload,
    negotiate_product_endpoints,
)
from src.net.policies.policy_server_authoritative import POLICY_ID_SERVER_AUTHORITATIVE, join_client_midstream
from src.net.transport.loopback import LoopbackTransport
from src.server.server_boot import REFUSAL_CLIENT_UNAUTHORIZED, build_connection_authority_context
from src.server.server_console import dispatch_server_console_command
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, refusal, write_canonical_json
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


def _artifact_root_abs(server_boot_payload: Mapping[str, object] | None) -> str:
    payload = dict(server_boot_payload or {})
    repo_root = str(payload.get("repo_root", "")).strip()
    runtime = _runtime(server_boot_payload)
    meta = _server_meta(runtime)
    rel = str(meta.get("artifact_root", "")).strip()
    if repo_root and rel:
        return os.path.join(repo_root, rel.replace("/", os.sep))
    save_id = str((dict(runtime or {})).get("save_id", "")).strip() or "save.server.mvp"
    return os.path.join(repo_root or os.getcwd(), "build", "server", save_id)


def _refuse(message: str, *, code: str = REFUSAL_CLIENT_UNAUTHORIZED, details: Mapping[str, object] | None = None, path: str = "$") -> dict:
    relevant_ids = {
        str(key): str(value).strip()
        for key, value in sorted((dict(details or {})).items(), key=lambda item: str(item[0]))
        if str(value).strip()
    }
    return refusal(code, message, "Use the deterministic loopback handshake and retry.", relevant_ids, path)


def _server_tick(runtime: Mapping[str, object] | None) -> int:
    server = dict((dict(runtime or {})).get("server") or {})
    return int(server.get("network_tick", 0) or 0)


def _append_console_log(runtime: Mapping[str, object] | None, event_payload: Mapping[str, object]) -> None:
    if not isinstance(runtime, dict):
        return
    rows = [dict(row) for row in list(runtime.get("server_mvp_console_log") or []) if isinstance(row, dict)]
    rows.append(dict(event_payload or {}))
    rows = sorted(
        rows,
        key=lambda row: (
            int(row.get("tick", 0) or 0),
            str(row.get("event_id", "")).strip(),
        ),
    )[-128:]
    runtime["server_mvp_console_log"] = rows


def _append_negotiation_log(runtime: Mapping[str, object] | None, row_payload: Mapping[str, object]) -> None:
    if not isinstance(runtime, dict):
        return
    rows = [dict(row) for row in list(runtime.get("server_mvp_negotiation_log") or []) if isinstance(row, dict)]
    rows.append(dict(row_payload or {}))
    rows = sorted(
        rows,
        key=lambda row: (
            str(row.get("connection_id", "")).strip(),
            str(row.get("negotiation_record_hash", "")).strip(),
            str(row.get("artifact_path", "")).strip(),
        ),
    )[-128:]
    runtime["server_mvp_negotiation_log"] = rows


def _write_negotiation_artifact(
    server_boot_payload: Mapping[str, object],
    *,
    connection_id: str,
    peer_id: str,
    compatibility_mode_id: str,
    negotiation_record: Mapping[str, object],
    handshake_messages: list[Mapping[str, object]],
    client_endpoint_descriptor_hash: str,
    server_endpoint_descriptor_hash: str,
    client_acknowledged: bool,
    law_profile_id_override: str = "",
    refusal_payload: Mapping[str, object] | None = None,
) -> str:
    runtime = _runtime(server_boot_payload)
    repo_root = str((dict(server_boot_payload or {})).get("repo_root", "")).strip()
    out_dir = os.path.join(_artifact_root_abs(server_boot_payload), "negotiation")
    os.makedirs(out_dir, exist_ok=True)
    record_payload = dict(negotiation_record or {})
    artifact = {
        "schema_version": "1.0.0",
        "connection_id": str(connection_id or "").strip(),
        "peer_id": str(peer_id or "").strip(),
        "compatibility_mode_id": str(compatibility_mode_id or "").strip(),
        "negotiation_record_hash": canonical_sha256(record_payload) if record_payload else "",
        "client_endpoint_descriptor_hash": str(client_endpoint_descriptor_hash or "").strip(),
        "server_endpoint_descriptor_hash": str(server_endpoint_descriptor_hash or "").strip(),
        "client_acknowledged": bool(client_acknowledged),
        "law_profile_id_override": str(law_profile_id_override or "").strip(),
        "negotiation_record": record_payload,
        "handshake_messages": [
            dict(message)
            for message in list(handshake_messages or [])
            if isinstance(message, Mapping)
        ],
        "refusal": dict(refusal_payload or {}),
        "deterministic_fingerprint": "",
        "extensions": {
            "official.exception_event_kind": "compat.read_only"
            if str(compatibility_mode_id or "").strip() == "compat.read_only"
            else "",
        },
    }
    artifact["deterministic_fingerprint"] = canonical_sha256(dict(artifact, deterministic_fingerprint=""))
    out_abs = os.path.join(out_dir, "connection.{}.json".format(str(connection_id or "unknown")))
    write_canonical_json(out_abs, artifact)
    artifact_rel = norm(os.path.relpath(out_abs, repo_root)) if repo_root else out_abs.replace("\\", "/")
    _append_negotiation_log(
        runtime,
        {
            "connection_id": str(connection_id or "").strip(),
            "peer_id": str(peer_id or "").strip(),
            "compatibility_mode_id": str(compatibility_mode_id or "").strip(),
            "negotiation_record_hash": str(artifact.get("negotiation_record_hash", "")).strip(),
            "artifact_path": artifact_rel,
            "client_acknowledged": bool(client_acknowledged),
        },
    )
    return artifact_rel


def _drop_connection(runtime: Mapping[str, object] | None, connection_id: str) -> None:
    if not isinstance(runtime, dict):
        return
    connection_token = str(connection_id or "").strip()
    if not connection_token:
        return
    connections = dict(runtime.get("server_mvp_connections") or {})
    if connection_token in connections:
        connections.pop(connection_token, None)
        runtime["server_mvp_connections"] = dict((key, connections[key]) for key in sorted(connections.keys()))
    live_transports = dict(runtime.get("_server_mvp_live_transports") or {})
    if connection_token in live_transports:
        live_transports.pop(connection_token, None)
        runtime["_server_mvp_live_transports"] = dict((key, live_transports[key]) for key in sorted(live_transports.keys()))


def stream_server_log_event(
    server_boot_payload: Mapping[str, object],
    *,
    tick: int,
    level: str,
    message: str,
    source: str,
    connection_id: str = "",
) -> dict:
    runtime = _runtime(server_boot_payload)
    live_transports = dict(runtime.get("_server_mvp_live_transports") or {})
    event_payload = {
        "schema_version": "1.0.0",
        "event_id": "log.{}.{}".format(int(tick), canonical_sha256({"tick": int(tick), "message": str(message), "source": str(source)})[:12]),
        "tick": int(tick),
        "level": str(level or "info").strip() or "info",
        "message": str(message or "").strip(),
        "source": str(source or "server.mvp").strip() or "server.mvp",
        "connection_id": str(connection_id or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": {},
    }
    event_payload["deterministic_fingerprint"] = canonical_sha256(dict(event_payload, deterministic_fingerprint=""))
    _append_console_log(runtime, event_payload)
    rows = []
    for target_connection_id in sorted(live_transports.keys()):
        transport = live_transports.get(target_connection_id)
        if not isinstance(transport, LoopbackTransport):
            continue
        proto = build_proto_message(
            msg_type="payload",
            msg_id="msg.server.console.log.{}.{}".format(str(target_connection_id), int(tick)),
            sequence=max(1, int(tick)),
            payload_schema_id="server.console.log.stub.v1",
            payload_inline_json=event_payload,
        )
        sent = transport.send(encode_proto_message(proto))
        rows.append(
            {
                "connection_id": str(target_connection_id),
                "result": str(sent.get("result", "")).strip(),
            }
        )
    return {"result": "complete", "event_payload": event_payload, "broadcasts": rows}


def send_client_control_request(
    *,
    client_transport: object,
    request_id: str,
    request_kind: str,
    payload: Mapping[str, object] | None = None,
    sequence: int = 1000,
) -> dict:
    transport = client_transport if isinstance(client_transport, LoopbackTransport) else None
    if transport is None:
        return _refuse(
            "client control request requires an active loopback transport",
            code="refusal.client.control_unavailable",
            path="$.client_transport",
        )
    control_payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "request_kind": str(request_kind or "").strip(),
        "payload": dict(payload or {}),
        "extensions": {},
    }
    message = build_proto_message(
        msg_type="payload",
        msg_id="msg.client.control.{}".format(str(request_id or canonical_sha256(control_payload)[:12])),
        sequence=int(max(1, int(sequence or 1))),
        payload_schema_id="server.control.request.stub.v1",
        payload_inline_json=control_payload,
    )
    sent = transport.send(encode_proto_message(message))
    if str(sent.get("result", "")) != "complete":
        return dict(sent)
    return {"result": "complete", "request_id": str(control_payload.get("request_id", "")), "request_kind": str(control_payload.get("request_kind", ""))}


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
    stream_server_log_event(
        server_boot_payload,
        tick=_server_tick(runtime),
        level="info",
        message="loopback listener bound",
        source="server.loopback.listener",
    )
    return {
        "result": "complete",
        "endpoint": endpoint,
        "server_peer_id": server_peer_id,
        "transport_id": "transport.loopback",
    }


def send_client_hello(
    endpoint: str,
    client_peer_id: str,
    account_id: str = "account.loopback",
    *,
    repo_root: str = "",
    endpoint_descriptor: Mapping[str, object] | None = None,
    allow_read_only: bool = False,
) -> dict:
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
    descriptor_payload = dict(endpoint_descriptor or {})
    if not descriptor_payload:
        descriptor_payload = build_default_endpoint_descriptor(
            str(repo_root or "").strip(),
            product_id="client",
            product_version="0.0.0+client.loopback",
        )
    hello_payload = {
        "schema_version": "1.0.0",
        "client_peer_id": peer_token,
        "account_id": str(account_id or "account.loopback").strip() or "account.loopback",
        "protocol_version": "1.0.0",
        "endpoint_descriptor": descriptor_payload,
        "allow_read_only": bool(allow_read_only),
        "extensions": {},
    }
    hello_message = build_handshake_message(
        message_kind="client_hello",
        protocol_version="1.0.0",
        payload_ref=hello_payload,
        extensions={
            "official.endpoint_descriptor_hash": canonical_sha256(descriptor_payload),
        },
    )
    message = build_proto_message(
        msg_type="handshake_request",
        msg_id="msg.client_hello.{}".format(str(client.connection_id or canonical_sha256(hello_payload)[:16])),
        sequence=1,
        payload_schema_id="compat.handshake.client_hello.v1",
        payload_inline_json=hello_message,
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
        "hello_message": hello_message,
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
    payload_inline = dict((dict(proto_message.get("payload_ref") or {})).get("inline_json") or {})
    hello_message = {}
    if str(payload_inline.get("message_kind", "")).strip() == "client_hello":
        hello_message = dict(payload_inline)
        hello_payload = dict(hello_message.get("payload_ref") or {})
    else:
        hello_payload = dict(payload_inline)
        hello_message = build_handshake_message(
            message_kind="client_hello",
            protocol_version=str(hello_payload.get("protocol_version", "1.0.0")).strip() or "1.0.0",
            payload_ref=hello_payload,
            extensions={},
        )
    peer_id = str(hello_payload.get("client_peer_id", accepted.get("remote_peer_id", ""))).strip()
    account_id = str(hello_payload.get("account_id", "account.loopback")).strip() or "account.loopback"
    connection_id = str(accepted.get("connection_id", "")).strip()
    repo_root = str((dict(server_boot_payload or {})).get("repo_root", "")).strip()

    session_spec = dict((dict(server_boot_payload or {})).get("session_spec") or {})
    client_endpoint_descriptor = dict(hello_payload.get("endpoint_descriptor") or {})
    if not client_endpoint_descriptor:
        client_endpoint_descriptor = build_default_endpoint_descriptor(
            repo_root,
            product_id="client",
            product_version="0.0.0+client.loopback",
        )
    server_endpoint_descriptor = build_default_endpoint_descriptor(
        repo_root,
        product_id="server",
        product_version="0.0.0+server.loopback",
    )
    negotiation = negotiate_product_endpoints(
        repo_root,
        client_endpoint_descriptor,
        server_endpoint_descriptor,
        allow_read_only=bool(hello_payload.get("allow_read_only", False)),
        chosen_contract_bundle_hash=str(session_spec.get("contract_bundle_hash", "")).strip(),
    )
    negotiation_record = dict(negotiation.get("negotiation_record") or {})
    if str(negotiation.get("result", "")) != "complete":
        refusal_payload = dict(negotiation.get("refusal") or {})
        return _refuse(
            str(refusal_payload.get("message", "endpoint capability negotiation refused the loopback connection")).strip()
            or "endpoint capability negotiation refused the loopback connection",
            code=str(refusal_payload.get("reason_code", "refusal.compat.contract_mismatch")).strip()
            or "refusal.compat.contract_mismatch",
            details=dict(refusal_payload.get("relevant_ids") or {}),
            path="$.endpoint_descriptor",
        )

    law_profile_override = ""
    entitlements_override = None
    if str(negotiation.get("compatibility_mode_id", "")) == "compat.read_only":
        law_profile_override = READ_ONLY_LAW_PROFILE_ID
        entitlements_override = []
    authority_context = build_connection_authority_context(
        session_spec=session_spec,
        server_profile=dict(meta.get("server_profile") or {}),
        connection_id=connection_id,
        account_id=account_id,
        law_profile_id_override=law_profile_override,
        entitlements_override=entitlements_override,
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

    server_hello_message = build_handshake_message(
        message_kind="server_hello",
        protocol_version="1.0.0",
        payload_ref={
            "connection_id": connection_id,
            "server_peer_id": server_peer_id,
            "endpoint_descriptor": server_endpoint_descriptor,
            "endpoint_descriptor_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
        },
        extensions={},
    )
    negotiation_result_message = build_handshake_message(
        message_kind="negotiation_result",
        protocol_version="1.0.0",
        payload_ref={
            "negotiation_record": negotiation_record,
            "negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
            "compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
            "compat_refusal": build_compat_refusal(
                refusal_code="",
                remediation_hint="",
                extensions={},
            ),
        },
        extensions={},
    )
    session_begin_payload = build_session_begin_payload(
        connection_id=connection_id,
        compatibility_mode_id=str(negotiation.get("compatibility_mode_id", "")).strip(),
        negotiation_record_hash=str(negotiation.get("negotiation_record_hash", "")).strip(),
        pack_lock_hash=str(session_spec.get("pack_lock_hash", "")).strip(),
        contract_bundle_hash=str(session_spec.get("contract_bundle_hash", "")).strip(),
        semantic_contract_registry_hash=str(session_spec.get("semantic_contract_registry_hash", "")).strip(),
        law_profile_id_override=law_profile_override,
        extensions={
            "official.client_endpoint_descriptor_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
            "official.server_endpoint_descriptor_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
        },
    )
    session_begin_message = build_handshake_message(
        message_kind="session_begin",
        protocol_version="1.0.0",
        payload_ref=session_begin_payload,
        extensions={},
    )
    handshake_messages = [
        dict(hello_message),
        dict(server_hello_message),
        dict(negotiation_result_message),
        dict(session_begin_message),
    ]

    live_transports = dict(runtime.get("_server_mvp_live_transports") or {})
    live_transports[connection_id] = listener
    runtime["_server_mvp_live_transports"] = dict((key, live_transports[key]) for key in sorted(live_transports.keys()))

    connections[connection_id] = {
        "connection_id": connection_id,
        "peer_id": peer_id,
        "account_id": account_id,
        "authority_context": authority_context,
        "compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
        "negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
        "client_endpoint_descriptor_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
        "server_endpoint_descriptor_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
        "snapshot_id": str(joined.get("snapshot_id", "")).strip(),
        "perceived_hash": str(joined.get("perceived_hash", "")).strip(),
        "transport_id": "transport.loopback",
        "client_acknowledged": False,
        "law_profile_id_override": law_profile_override,
        "negotiation_record": dict(negotiation_record),
        "handshake_messages": list(handshake_messages),
        "session_begin_payload": dict(session_begin_payload),
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
        "extensions": {
            "official.compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
            "official.negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
            "official.client_endpoint_descriptor_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
            "official.server_endpoint_descriptor_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
            "official.enabled_capabilities": list(negotiation_record.get("enabled_capabilities") or []),
            "official.disabled_capabilities": list(negotiation_record.get("disabled_capabilities") or []),
            "official.substituted_capabilities": list(negotiation_record.get("substituted_capabilities") or []),
            "official.handshake_messages": handshake_messages,
            "official.session_begin": dict(session_begin_payload),
        },
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
    artifact_path = _write_negotiation_artifact(
        server_boot_payload,
        connection_id=connection_id,
        peer_id=peer_id,
        compatibility_mode_id=str(negotiation.get("compatibility_mode_id", "")).strip(),
        negotiation_record=negotiation_record,
        handshake_messages=handshake_messages,
        client_endpoint_descriptor_hash=str(negotiation.get("endpoint_a_hash", "")).strip(),
        server_endpoint_descriptor_hash=str(negotiation.get("endpoint_b_hash", "")).strip(),
        client_acknowledged=False,
        law_profile_id_override=law_profile_override,
    )
    stream_server_log_event(
        server_boot_payload,
        tick=_server_tick(runtime),
        level="info",
        message="client accepted on deterministic loopback transport",
        source="server.loopback.accept",
        connection_id=connection_id,
    )
    if str(negotiation.get("compatibility_mode_id", "")).strip() == "compat.read_only":
        stream_server_log_event(
            server_boot_payload,
            tick=_server_tick(runtime),
            level="info",
            message="read-only compatibility mode negotiated",
            source="server.loopback.negotiation",
            connection_id=connection_id,
        )
    return {
        "result": "complete",
        "connection_id": connection_id,
        "peer_id": peer_id,
        "account_id": account_id,
        "authority_context": authority_context,
        "compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
        "negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
        "negotiation_record": negotiation_record,
        "handshake_messages": handshake_messages,
        "session_begin_payload": dict(session_begin_payload),
        "ack_payload": ack_payload,
        "negotiation_artifact_path": artifact_path,
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


def service_loopback_control_channel(server_boot_payload: Mapping[str, object]) -> dict:
    runtime = _runtime(server_boot_payload)
    repo_root = str((dict(server_boot_payload or {})).get("repo_root", "")).strip()
    live_transports = dict(runtime.get("_server_mvp_live_transports") or {})
    rows = []
    for connection_id in sorted(live_transports.keys()):
        transport = live_transports.get(connection_id)
        if not isinstance(transport, LoopbackTransport):
            continue
        while True:
            inbound = transport.recv()
            result_token = str((dict(inbound or {})).get("result", "")).strip()
            if result_token != "complete":
                break
            decoded = decode_proto_message(
                repo_root=repo_root,
                message_bytes=bytes((dict(inbound or {})).get("message_bytes") or b""),
            )
            if str(decoded.get("result", "")) != "complete":
                rows.append({"connection_id": str(connection_id), "result": "decode_failed"})
                break
            proto_message = dict(decoded.get("proto_message") or {})
            payload_schema_id = str(proto_message.get("payload_schema_id", "")).strip()
            if payload_schema_id == "compat.handshake.ack.v1":
                ack_payload = dict((dict(proto_message.get("payload_ref") or {})).get("inline_json") or {})
                ack_message = build_handshake_message(
                    message_kind="ack",
                    protocol_version="1.0.0",
                    payload_ref=ack_payload,
                    extensions={},
                )
                connection_rows = dict(runtime.get("server_mvp_connections") or {})
                connection_row = dict(connection_rows.get(str(connection_id), {}) or {})
                negotiated_hash = str(connection_row.get("negotiation_record_hash", "")).strip()
                ack_hash = str(ack_payload.get("negotiation_record_hash", "")).strip()
                if (not connection_row) or (not negotiated_hash):
                    transport.close()
                    _drop_connection(runtime, str(connection_id))
                    rows.append(
                        {
                            "connection_id": str(connection_id),
                            "result": "refused",
                            "reason_code": REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
                        }
                    )
                    continue
                if ack_hash != negotiated_hash:
                    _write_negotiation_artifact(
                        server_boot_payload,
                        connection_id=str(connection_id),
                        peer_id=str(connection_row.get("peer_id", "")).strip(),
                        compatibility_mode_id=str(connection_row.get("compatibility_mode_id", "")).strip(),
                        negotiation_record=dict(connection_row.get("negotiation_record") or {}),
                        handshake_messages=list(connection_row.get("handshake_messages") or []) + [dict(ack_message)],
                        client_endpoint_descriptor_hash=str(connection_row.get("client_endpoint_descriptor_hash", "")).strip(),
                        server_endpoint_descriptor_hash=str(connection_row.get("server_endpoint_descriptor_hash", "")).strip(),
                        client_acknowledged=False,
                        law_profile_id_override=str(connection_row.get("law_profile_id_override", "")).strip(),
                        refusal_payload=build_compat_refusal(
                            refusal_code=REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
                            remediation_hint="Reconnect and accept the deterministic negotiation result before sending intents.",
                            extensions={"connection_id": str(connection_id)},
                        ),
                    )
                    transport.close()
                    _drop_connection(runtime, str(connection_id))
                    stream_server_log_event(
                        server_boot_payload,
                        tick=_server_tick(runtime),
                        level="warn",
                        message="client negotiation ack mismatch refused",
                        source="server.loopback.control",
                        connection_id=str(connection_id),
                    )
                    rows.append(
                        {
                            "connection_id": str(connection_id),
                            "result": "refused",
                            "reason_code": REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
                        }
                    )
                    continue
                if not bool(ack_payload.get("accepted", False)):
                    _write_negotiation_artifact(
                        server_boot_payload,
                        connection_id=str(connection_id),
                        peer_id=str(connection_row.get("peer_id", "")).strip(),
                        compatibility_mode_id=str(connection_row.get("compatibility_mode_id", "")).strip(),
                        negotiation_record=dict(connection_row.get("negotiation_record") or {}),
                        handshake_messages=list(connection_row.get("handshake_messages") or []) + [dict(ack_message)],
                        client_endpoint_descriptor_hash=str(connection_row.get("client_endpoint_descriptor_hash", "")).strip(),
                        server_endpoint_descriptor_hash=str(connection_row.get("server_endpoint_descriptor_hash", "")).strip(),
                        client_acknowledged=False,
                        law_profile_id_override=str(connection_row.get("law_profile_id_override", "")).strip(),
                        refusal_payload=build_compat_refusal(
                            refusal_code="refusal.client.negotiation_declined",
                            remediation_hint="Reconnect and accept the deterministic degrade mode or select a compatible product/profile pair.",
                            extensions={"connection_id": str(connection_id)},
                        ),
                    )
                    transport.close()
                    _drop_connection(runtime, str(connection_id))
                    stream_server_log_event(
                        server_boot_payload,
                        tick=_server_tick(runtime),
                        level="info",
                        message="client refused negotiated compatibility mode",
                        source="server.loopback.control",
                        connection_id=str(connection_id),
                    )
                    rows.append(
                        {
                            "connection_id": str(connection_id),
                            "result": "refused",
                            "reason_code": "refusal.client.negotiation_declined",
                        }
                    )
                    continue
                connection_row["client_acknowledged"] = True
                connection_row["handshake_messages"] = list(connection_row.get("handshake_messages") or []) + [dict(ack_message)]
                connection_rows[str(connection_id)] = dict(connection_row)
                runtime["server_mvp_connections"] = dict((key, connection_rows[key]) for key in sorted(connection_rows.keys()))
                _write_negotiation_artifact(
                    server_boot_payload,
                    connection_id=str(connection_id),
                    peer_id=str(connection_row.get("peer_id", "")).strip(),
                    compatibility_mode_id=str(connection_row.get("compatibility_mode_id", "")).strip(),
                    negotiation_record=dict(connection_row.get("negotiation_record") or {}),
                    handshake_messages=list(connection_row.get("handshake_messages") or []) + [dict(ack_message)],
                    client_endpoint_descriptor_hash=str(connection_row.get("client_endpoint_descriptor_hash", "")).strip(),
                    server_endpoint_descriptor_hash=str(connection_row.get("server_endpoint_descriptor_hash", "")).strip(),
                    client_acknowledged=True,
                    law_profile_id_override=str(connection_row.get("law_profile_id_override", "")).strip(),
                )
                rows.append(
                    {
                        "connection_id": str(connection_id),
                        "result": "complete",
                        "payload_schema_id": payload_schema_id,
                    }
                )
                continue
            if payload_schema_id != "server.control.request.stub.v1":
                rows.append(
                    {
                        "connection_id": str(connection_id),
                        "result": "ignored",
                        "payload_schema_id": payload_schema_id,
                    }
                )
                continue
            request_payload = dict((dict(proto_message.get("payload_ref") or {})).get("inline_json") or {})
            request_id = str(request_payload.get("request_id", "")).strip()
            request_kind = str(request_payload.get("request_kind", "")).strip()
            response_payload = {
                "schema_version": "1.0.0",
                "request_id": request_id,
                "request_kind": request_kind,
                "tick": _server_tick(runtime),
                "result": "",
                "payload": {},
                "extensions": {},
            }
            command_result = dispatch_server_console_command(
                server_boot_payload,
                command=request_kind,
                payload=dict(request_payload.get("payload") or {}),
            )
            response_payload["result"] = str(command_result.get("result", "")).strip() or "refused"
            response_payload["payload"] = dict(command_result)
            response_proto = build_proto_message(
                msg_type="payload",
                msg_id="msg.server.control.{}".format(str(request_id or canonical_sha256(response_payload)[:12])),
                sequence=max(1, int(_server_tick(runtime))),
                payload_schema_id="server.control.response.stub.v1",
                payload_inline_json=response_payload,
            )
            sent = transport.send(encode_proto_message(response_proto))
            stream_server_log_event(
                server_boot_payload,
                tick=_server_tick(runtime),
                level="info",
                message="processed control request {}".format(request_kind or "<unknown>"),
                source="server.loopback.control",
                connection_id=str(connection_id),
            )
            rows.append(
                {
                    "connection_id": str(connection_id),
                    "request_id": request_id,
                    "request_kind": request_kind,
                    "result": str(sent.get("result", "")).strip(),
                }
            )
    return {"result": "complete", "control_rows": rows}
