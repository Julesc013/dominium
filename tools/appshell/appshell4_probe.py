"""Deterministic APPSHELL-4 IPC attach probe helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from appshell.compat_adapter import build_version_payload, emit_descriptor_payload  # noqa: E402
from appshell.ipc import (  # noqa: E402
    AppShellIPCEndpointServer,
    attach_ipc_endpoint,
    build_console_io_message,
    build_ipc_frame,
    build_ipc_local_address,
    discover_ipc_endpoints,
    query_ipc_log_events,
    query_ipc_status,
    run_ipc_console_command,
)
from appshell.ipc.ipc_transport import connect_ipc_client, recv_frame, send_frame  # noqa: E402
from appshell.logging import (  # noqa: E402
    clear_current_log_engine,
    create_log_engine,
    get_current_log_engine,
    log_emit,
    set_current_log_engine,
)
from compat import build_handshake_message  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


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


def _manifest_path(repo_root: str, suffix: str) -> str:
    return os.path.join(
        repo_root,
        "build",
        "appshell",
        "ipc",
        "ipc_manifest.{}.json".format(str(suffix or "default").strip() or "default"),
    )


def _log_file_path(repo_root: str, suffix: str) -> str:
    return os.path.join(
        repo_root,
        "build",
        "appshell",
        "ipc",
        "ipc_probe.{}.jsonl".format(str(suffix or "default").strip() or "default"),
    )


def _endpoint_row(report: Mapping[str, object], endpoint_id: str) -> dict:
    for row in list(dict(report or {}).get("endpoints") or []):
        row_map = dict(row or {})
        if str(row_map.get("endpoint_id", "")).strip() == str(endpoint_id).strip():
            return row_map
    return {}


def _address_payload(repo_root: str, endpoint_row: Mapping[str, object]) -> dict:
    return build_ipc_local_address(
        repo_root,
        str(dict(endpoint_row or {}).get("product_id", "")).strip(),
        str(dict(endpoint_row or {}).get("session_id", "")).strip(),
    )


def _perform_handshake_request(
    repo_root: str,
    *,
    local_product_id: str,
    endpoint_row: Mapping[str, object],
    request_channel: str,
    request_payload: Mapping[str, object],
    allow_read_only: bool = True,
    accept_degraded: bool = True,
) -> dict:
    local_descriptor = emit_descriptor_payload(repo_root, product_id=str(local_product_id).strip())
    sock = connect_ipc_client(_address_payload(repo_root, endpoint_row), max_attempts=4)
    reader = sock.makefile("r", encoding="utf-8", newline="\n")
    writer = sock.makefile("w", encoding="utf-8", newline="\n")
    try:
        send_frame(
            writer,
            build_ipc_frame(
                channel_id="negotiation",
                seq_no=1,
                payload_ref=build_handshake_message(
                    message_kind="client_hello",
                    protocol_version="1.0.0",
                    payload_ref={"endpoint_descriptor": dict(local_descriptor.get("descriptor") or {})},
                ),
            ),
        )
        server_hello = recv_frame(reader)
        negotiation_result = recv_frame(reader)
        negotiation_payload = dict(dict(negotiation_result).get("payload_ref") or {})
        negotiation_message = dict(negotiation_payload.get("payload_ref") or {})
        compatibility_mode_id = str(negotiation_message.get("compatibility_mode_id", "")).strip()
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
                    protocol_version=str(negotiation_message.get("chosen_protocol_version", "1.0.0")).strip() or "1.0.0",
                    payload_ref={
                        "accepted": bool(accepted),
                        "compatibility_mode_id": compatibility_mode_id,
                        "negotiation_record_hash": str(negotiation_message.get("negotiation_record_hash", "")).strip(),
                    },
                ),
            ),
        )
        session_begin = recv_frame(reader) if accepted and str(negotiation_message.get("result", "")).strip() == "complete" else {}
        responses = []
        if accepted and str(negotiation_message.get("result", "")).strip() == "complete":
            send_frame(
                writer,
                build_ipc_frame(
                    channel_id=str(request_channel).strip(),
                    seq_no=3,
                    payload_ref=dict(_normalize_tree(dict(request_payload or {}))),
                ),
            )
            while True:
                frame = recv_frame(reader)
                if not frame:
                    break
                responses.append(dict(frame))
        return {
            "result": "complete" if accepted and str(negotiation_message.get("result", "")).strip() == "complete" else "refused",
            "server_hello": dict(server_hello),
            "negotiation_result": dict(negotiation_result),
            "session_begin": dict(session_begin),
            "responses": responses,
            "compatibility_mode_id": compatibility_mode_id,
            "negotiation_record_hash": str(negotiation_message.get("negotiation_record_hash", "")).strip(),
            "refusal": dict(negotiation_message.get("refusal") or {}),
        }
    finally:
        writer.close()
        reader.close()
        sock.close()


def _request_without_negotiation(repo_root: str, *, endpoint_row: Mapping[str, object]) -> dict:
    sock = connect_ipc_client(_address_payload(repo_root, endpoint_row), max_attempts=4)
    reader = sock.makefile("r", encoding="utf-8", newline="\n")
    writer = sock.makefile("w", encoding="utf-8", newline="\n")
    try:
        send_frame(writer, build_ipc_frame(channel_id="status", seq_no=1, payload_ref={"request_kind": "status"}))
        return dict(recv_frame(reader) or {})
    finally:
        writer.close()
        reader.close()
        sock.close()


def _neutral_console_payload(console_result: Mapping[str, object]) -> dict:
    stdout = str(dict(console_result or {}).get("stdout", "")).strip()
    payload = {}
    if stdout.startswith("{") and stdout.endswith("}"):
        try:
            decoded = json.loads(stdout)
            if isinstance(decoded, dict):
                payload = decoded
        except ValueError:
            payload = {}
    return {
        "dispatch_exit_code": int(dict(dict(console_result or {}).get("dispatch") or {}).get("exit_code", 0) or 0),
        "stderr": str(dict(console_result or {}).get("stderr", "")).strip(),
        "stdout_payload": dict(_normalize_tree(payload)),
    }


def run_ipc_attach_probe(
    repo_root: str,
    *,
    product_id: str = "server",
    local_product_id: str = "tool.attach_console_stub",
    command_text: str = "version",
    suffix: str = "default",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    manifest_path = _manifest_path(repo_root_abs, suffix)
    if os.path.isfile(manifest_path):
        os.remove(manifest_path)
    session_id = "session.appshell4.{}".format(str(suffix or "default").strip() or "default")
    previous_engine = get_current_log_engine()
    version_payload = build_version_payload(repo_root_abs, product_id=str(product_id).strip())
    logger = create_log_engine(
        product_id=str(product_id).strip(),
        build_id=str(version_payload.get("build_id", "")).strip(),
        session_id=session_id,
        console_enabled=False,
        file_path=_log_file_path(repo_root_abs, suffix),
    )
    set_current_log_engine(logger)
    endpoint_server = AppShellIPCEndpointServer(
        repo_root=repo_root_abs,
        product_id=str(product_id).strip(),
        session_id=session_id,
        mode_id="headless" if str(product_id).strip() == "server" else "cli",
        manifest_path=manifest_path,
        session_metadata={
            "contract_bundle_hash": "hash.contract.bundle.appshell4",
            "pack_lock_hash": "hash.pack.lock.appshell4",
        },
    )
    try:
        start_report = endpoint_server.start()
        endpoint_id = str(start_report.get("endpoint_id", "")).strip()
        endpoints_first = discover_ipc_endpoints(repo_root_abs, manifest_path=manifest_path)
        endpoints_second = discover_ipc_endpoints(repo_root_abs, manifest_path=manifest_path)
        endpoint_row = _endpoint_row(endpoints_first, endpoint_id)
        attach = attach_ipc_endpoint(
            repo_root_abs,
            local_product_id=str(local_product_id).strip(),
            endpoint_id=endpoint_id,
            manifest_path=manifest_path,
        )
        status = query_ipc_status(repo_root_abs, attach)
        logs = query_ipc_log_events(repo_root_abs, attach, limit=8)
        console = run_ipc_console_command(repo_root_abs, attach, str(command_text).strip())
        raw_status = _perform_handshake_request(
            repo_root_abs,
            local_product_id=str(local_product_id).strip(),
            endpoint_row=endpoint_row,
            request_channel="status",
            request_payload={"request_kind": "status"},
        )
        raw_logs = _perform_handshake_request(
            repo_root_abs,
            local_product_id=str(local_product_id).strip(),
            endpoint_row=endpoint_row,
            request_channel="log",
            request_payload={"after_event_id": "", "limit": 8},
        )
        raw_console = _perform_handshake_request(
            repo_root_abs,
            local_product_id=str(local_product_id).strip(),
            endpoint_row=endpoint_row,
            request_channel="console",
            request_payload=build_console_io_message(kind="cmd_request", text=str(command_text).strip(), extensions={}),
        )
        missing_negotiation = _request_without_negotiation(repo_root_abs, endpoint_row=endpoint_row)

        log_events = list(logs.get("events") or [])
        seq_trace = []
        for row in list(raw_status.get("responses") or []) + list(raw_logs.get("responses") or []) + list(raw_console.get("responses") or []):
            seq_trace.append(
                {
                    "channel_id": str(dict(row).get("channel_id", "")).strip(),
                    "seq_no": int(dict(row).get("seq_no", 0) or 0),
                }
            )
        monotonic_by_channel = {}
        for channel_id in sorted(set(str(dict(row).get("channel_id", "")).strip() for row in seq_trace if str(dict(row).get("channel_id", "")).strip())):
            seqs = [int(dict(row).get("seq_no", 0) or 0) for row in seq_trace if str(dict(row).get("channel_id", "")).strip() == channel_id]
            monotonic_by_channel[channel_id] = bool(seqs == sorted(seqs) and len(seqs) == len(set(seqs)))

        normalized_summary = {
            "discovered_endpoint_ids": [
                str(dict(row).get("endpoint_id", "")).strip()
                for row in list(endpoints_first.get("endpoints") or [])
            ],
            "compatibility_mode_id": str(attach.get("compatibility_mode_id", "")).strip(),
            "negotiation_record_hash": str(attach.get("negotiation_record_hash", "")).strip(),
            "missing_negotiation_refusal_code": str(
                dict(dict(missing_negotiation).get("payload_ref") or {}).get("payload_ref", {}).get("refusal", {}).get("refusal_code", "")
            ).strip(),
            "status": {
                "product_id": str(dict(status.get("status") or {}).get("product_id", "")).strip(),
                "session_id": str(dict(status.get("status") or {}).get("session_id", "")).strip(),
                "mode_id": str(dict(status.get("status") or {}).get("mode_id", "")).strip(),
                "attach_count": int(dict(status.get("status") or {}).get("attach_count", 0) or 0),
                "last_tick": int(dict(status.get("status") or {}).get("last_tick", 0) or 0),
            },
            "log_message_keys": [
                str(dict(row).get("message_key", "")).strip()
                for row in log_events
            ],
            "console": _neutral_console_payload(console),
            "seq_trace": seq_trace,
        }

        report = {
            "result": "complete",
            "product_id": str(product_id).strip(),
            "local_product_id": str(local_product_id).strip(),
            "endpoint_id": endpoint_id,
            "manifest_path": manifest_path.replace("\\", "/"),
            "discovery_first": dict(endpoints_first),
            "discovery_second": dict(endpoints_second),
            "attach": dict(attach),
            "status": dict(status),
            "log_events": log_events,
            "console": dict(console),
            "raw_status": dict(raw_status),
            "raw_logs": dict(raw_logs),
            "raw_console": dict(raw_console),
            "missing_negotiation": dict(missing_negotiation),
            "seq_trace": seq_trace,
            "seq_monotonic_by_channel": monotonic_by_channel,
            "cross_platform_ipc_hash": canonical_sha256(normalized_summary),
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
        return report
    finally:
        endpoint_server.stop()
        if previous_engine is None:
            clear_current_log_engine()
        else:
            set_current_log_engine(previous_engine)


def verify_ipc_attach_replay(repo_root: str, *, suffix: str = "replay") -> dict:
    token = str(suffix).strip() or "replay"
    first = run_ipc_attach_probe(repo_root, suffix=token)
    second = run_ipc_attach_probe(repo_root, suffix=token)
    comparable = (
        "cross_platform_ipc_hash",
        "seq_trace",
        "seq_monotonic_by_channel",
    )
    mismatches = [key for key in comparable if first.get(key) != second.get(key)]
    return {
        "result": "complete" if not mismatches else "refused",
        "first": first,
        "second": second,
        "mismatches": mismatches,
        "replay_fingerprint": canonical_sha256(
            {
                "first_hash": str(first.get("cross_platform_ipc_hash", "")).strip(),
                "second_hash": str(second.get("cross_platform_ipc_hash", "")).strip(),
                "mismatches": mismatches,
            }
        ),
    }


__all__ = [
    "run_ipc_attach_probe",
    "verify_ipc_attach_replay",
]
