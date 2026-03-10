"""Deterministic local IPC client and discovery helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from src.appshell.compat_adapter import emit_descriptor_payload
from src.compat import build_handshake_message

from .ipc_transport import (
    build_console_io_message,
    build_ipc_frame,
    connect_ipc_client,
    discover_ipc_manifest,
    recv_frame,
    send_frame,
)


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in value]
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


def _endpoint_lookup(repo_root: str, endpoint_id: str, manifest_path: str = "") -> dict:
    manifest = discover_ipc_manifest(repo_root, manifest_path)
    for row in list(dict(manifest.get("record") or {}).get("endpoints") or []):
        row_map = dict(row)
        if str(row_map.get("endpoint_id", "")).strip() == str(endpoint_id).strip():
            return row_map
    return {}


def _address_payload(endpoint_row: Mapping[str, object]) -> dict:
    extensions = dict(_normalize_tree(dict(dict(endpoint_row or {}).get("extensions") or {})))
    transport_id = str(extensions.get("official.transport_id", "")).strip()
    address = str(dict(endpoint_row or {}).get("address", "")).strip()
    if transport_id == "ipc.unix_socket":
        return {
            "family": "unix",
            "bind_target": address.replace("/", os.sep),
            "address": address,
        }
    host, port = "127.0.0.1", 0
    if address.startswith("tcp://"):
        host_port = address[len("tcp://") :]
        if ":" in host_port:
            host, port_text = host_port.rsplit(":", 1)
            port = int(port_text or 0)
    return {
        "family": "tcp",
        "bind_target": (host or "127.0.0.1", int(port or 0)),
        "address": address,
    }


def discover_ipc_endpoints(repo_root: str, manifest_path: str = "") -> dict:
    manifest = discover_ipc_manifest(repo_root, manifest_path)
    return {
        "result": "complete",
        "manifest_path": os.path.normpath(
            os.path.abspath(
                str(manifest_path)
                if str(manifest_path or "").strip()
                else os.path.join(str(repo_root or "."), "dist", "runtime", "ipc_endpoints.json")
            )
        ).replace("\\", "/"),
        "endpoints": list(dict(manifest.get("record") or {}).get("endpoints") or []),
    }


def _perform_handshake(
    repo_root: str,
    *,
    local_product_id: str,
    endpoint_row: Mapping[str, object],
    allow_read_only: bool,
    accept_degraded: bool,
) -> tuple[dict, object, object, object]:
    sock = connect_ipc_client(_address_payload(endpoint_row), max_attempts=4)
    reader = sock.makefile("r", encoding="utf-8", newline="\n")
    writer = sock.makefile("w", encoding="utf-8", newline="\n")
    local_descriptor_payload = emit_descriptor_payload(repo_root, product_id=str(local_product_id).strip())
    send_frame(
        writer,
        build_ipc_frame(
            channel_id="negotiation",
            seq_no=1,
            payload_ref=build_handshake_message(
                message_kind="client_hello",
                protocol_version="1.0.0",
                payload_ref={"endpoint_descriptor": dict(local_descriptor_payload.get("descriptor") or {})},
            ),
        ),
    )
    server_hello = recv_frame(reader)
    negotiation_result = recv_frame(reader)
    negotiation_payload = dict(dict(negotiation_result).get("payload_ref") or {})
    negotiation_message = dict(negotiation_payload.get("payload_ref") or {})
    negotiation_record = dict(negotiation_message.get("negotiation_record") or {})
    compatibility_mode_id = str(negotiation_message.get("compatibility_mode_id", "")).strip()
    refusal_payload = dict(negotiation_message.get("refusal") or {})
    accepted = True
    if compatibility_mode_id == "compat.read_only" and not bool(allow_read_only):
        accepted = False
    if compatibility_mode_id == "compat.degraded" and not bool(accept_degraded):
        accepted = False
    send_frame(
        writer,
        build_ipc_frame(
            channel_id="negotiation",
            seq_no=2,
            payload_ref=build_handshake_message(
                message_kind="ack",
                protocol_version=str(negotiation_record.get("chosen_protocol_version", "1.0.0")).strip() or "1.0.0",
                payload_ref={
                    "accepted": bool(accepted),
                    "compatibility_mode_id": compatibility_mode_id,
                    "negotiation_record_hash": str(negotiation_message.get("negotiation_record_hash", "")).strip(),
                },
            ),
        ),
    )
    session_begin = recv_frame(reader) if accepted else {}
    attach_report = {
        "result": "complete" if accepted and str(negotiation_message.get("result", "")).strip() == "complete" else "refused",
        "endpoint_id": str(dict(endpoint_row).get("endpoint_id", "")).strip(),
        "local_product_id": str(local_product_id).strip(),
        "peer_product_id": str(dict(endpoint_row).get("product_id", "")).strip(),
        "compatibility_mode_id": compatibility_mode_id,
        "negotiation_record": negotiation_record,
        "negotiation_record_hash": str(negotiation_message.get("negotiation_record_hash", "")).strip(),
        "endpoint_descriptor_hashes": {
            "endpoint_a_hash": str(negotiation_message.get("endpoint_a_hash", "")).strip(),
            "endpoint_b_hash": str(negotiation_message.get("endpoint_b_hash", "")).strip(),
        },
        "refusal": refusal_payload,
        "refusal_code": str(refusal_payload.get("refusal_code", "")).strip(),
        "read_only_mode": compatibility_mode_id == "compat.read_only",
        "server_hello": dict(server_hello),
        "session_begin": dict(session_begin),
        "endpoint": dict(endpoint_row),
        "local_descriptor_hash": str(local_descriptor_payload.get("descriptor_hash", "")).strip(),
    }
    return attach_report, sock, reader, writer


def attach_ipc_endpoint(
    repo_root: str,
    *,
    local_product_id: str,
    endpoint_id: str,
    manifest_path: str = "",
    allow_read_only: bool = True,
    accept_degraded: bool = True,
) -> dict:
    endpoint_row = _endpoint_lookup(repo_root, endpoint_id, manifest_path)
    if not endpoint_row:
        return {
            "result": "refused",
            "refusal_code": "refusal.io.endpoint_not_found",
            "reason": "requested IPC endpoint was not found in the discovery manifest",
            "details": {"endpoint_id": str(endpoint_id).strip()},
        }
    attach_report, sock, reader, writer = _perform_handshake(
        repo_root,
        local_product_id=local_product_id,
        endpoint_row=endpoint_row,
        allow_read_only=allow_read_only,
        accept_degraded=accept_degraded,
    )
    writer.close()
    reader.close()
    sock.close()
    return attach_report


def query_ipc_status(repo_root: str, attach_record: Mapping[str, object]) -> dict:
    endpoint_row = dict(dict(attach_record or {}).get("endpoint") or {})
    attach_report, sock, reader, writer = _perform_handshake(
        repo_root,
        local_product_id=str(dict(attach_record or {}).get("local_product_id", "")).strip() or "tool.attach_console_stub",
        endpoint_row=endpoint_row,
        allow_read_only=True,
        accept_degraded=True,
    )
    if str(attach_report.get("result", "")).strip() != "complete":
        writer.close()
        reader.close()
        sock.close()
        return attach_report
    send_frame(writer, build_ipc_frame(channel_id="status", seq_no=3, payload_ref={"request_kind": "status"}))
    response = recv_frame(reader)
    writer.close()
    reader.close()
    sock.close()
    return {
        "result": "complete",
        "status": dict(dict(response).get("payload_ref") or {}),
        "attach": attach_report,
    }


def query_ipc_log_events(repo_root: str, attach_record: Mapping[str, object], *, after_event_id: str = "", limit: int = 8) -> dict:
    endpoint_row = dict(dict(attach_record or {}).get("endpoint") or {})
    attach_report, sock, reader, writer = _perform_handshake(
        repo_root,
        local_product_id=str(dict(attach_record or {}).get("local_product_id", "")).strip() or "tool.attach_console_stub",
        endpoint_row=endpoint_row,
        allow_read_only=True,
        accept_degraded=True,
    )
    if str(attach_report.get("result", "")).strip() != "complete":
        writer.close()
        reader.close()
        sock.close()
        return attach_report
    send_frame(
        writer,
        build_ipc_frame(
            channel_id="log",
            seq_no=3,
            payload_ref={"after_event_id": str(after_event_id).strip(), "limit": int(max(1, int(limit or 8)))},
        ),
    )
    rows = []
    while True:
        response = recv_frame(reader)
        if not response:
            break
        if str(dict(response).get("channel_id", "")).strip() != "log":
            continue
        rows.append(dict(dict(response).get("payload_ref") or {}))
    writer.close()
    reader.close()
    sock.close()
    return {"result": "complete", "events": rows, "attach": attach_report}


def run_ipc_console_command(repo_root: str, attach_record: Mapping[str, object], command_text: str) -> dict:
    endpoint_row = dict(dict(attach_record or {}).get("endpoint") or {})
    attach_report, sock, reader, writer = _perform_handshake(
        repo_root,
        local_product_id=str(dict(attach_record or {}).get("local_product_id", "")).strip() or "tool.attach_console_stub",
        endpoint_row=endpoint_row,
        allow_read_only=True,
        accept_degraded=True,
    )
    if str(attach_report.get("result", "")).strip() != "complete":
        writer.close()
        reader.close()
        sock.close()
        return attach_report
    send_frame(
        writer,
        build_ipc_frame(
            channel_id="console",
            seq_no=3,
            payload_ref=build_console_io_message(kind="cmd_request", text=str(command_text or "").strip(), extensions={}),
        ),
    )
    messages = []
    while True:
        response = recv_frame(reader)
        if not response:
            break
        if str(dict(response).get("channel_id", "")).strip() != "console":
            continue
        messages.append(dict(dict(response).get("payload_ref") or {}))
    writer.close()
    reader.close()
    sock.close()
    stdout = "\n".join(str(dict(row).get("text", "")) for row in messages if str(dict(row).get("kind", "")).strip() == "stdout").strip()
    stderr = "\n".join(str(dict(row).get("text", "")) for row in messages if str(dict(row).get("kind", "")).strip() == "stderr").strip()
    response_rows = [dict(row) for row in messages if str(dict(row).get("kind", "")).strip() == "cmd_response"]
    dispatch = {}
    if response_rows:
        dispatch = dict(dict(response_rows[-1]).get("extensions") or {}).get("official.dispatch") or {}
    return {
        "result": "complete",
        "stdout": stdout,
        "stderr": stderr,
        "messages": messages,
        "dispatch": dict(_normalize_tree(dict(dispatch or {}))),
        "attach": attach_report,
    }


def detach_ipc_session(attach_record: Mapping[str, object]) -> dict:
    endpoint_row = dict(dict(attach_record or {}).get("endpoint") or {})
    return {
        "result": "complete",
        "session_id": "ipc.{}".format(str(dict(endpoint_row).get("endpoint_id", "")).strip()),
        "endpoint_id": str(dict(endpoint_row).get("endpoint_id", "")).strip(),
    }


__all__ = [
    "attach_ipc_endpoint",
    "detach_ipc_session",
    "discover_ipc_endpoints",
    "query_ipc_log_events",
    "query_ipc_status",
    "run_ipc_console_command",
]
