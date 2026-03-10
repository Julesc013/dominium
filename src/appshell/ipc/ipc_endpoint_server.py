"""Deterministic local IPC endpoint server for AppShell products."""

from __future__ import annotations

import json
import os
import threading
from typing import Mapping

from src.appshell.compat_adapter import emit_descriptor_payload
from src.appshell.logging import get_current_log_engine, log_emit
from src.compat import (
    COMPAT_MODE_READ_ONLY,
    REFUSAL_CONNECTION_NO_NEGOTIATION,
    REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
    build_compat_refusal,
    build_handshake_message,
    build_session_begin_payload,
    descriptor_json_text,
    negotiate_product_endpoints,
)

from .ipc_transport import (
    build_console_io_message,
    build_ipc_endpoint_descriptor,
    build_ipc_frame,
    build_ipc_local_address,
    connect_ipc_client,
    open_ipc_listener,
    recv_frame,
    remove_ipc_manifest_entry,
    resolve_ipc_session_id,
    send_frame,
    upsert_ipc_manifest_entry,
)


_CURRENT_IPC_ENDPOINT_SERVER = None
_READ_ONLY_SAFE_COMMAND_PREFIXES = (
    "compat-status",
    "console sessions",
    "descriptor",
    "diag",
    "help",
    "packs list",
    "packs verify",
    "profiles",
    "verify",
    "version",
)


def set_current_ipc_endpoint_server(server: "AppShellIPCEndpointServer | None") -> None:
    global _CURRENT_IPC_ENDPOINT_SERVER
    _CURRENT_IPC_ENDPOINT_SERVER = server


def get_current_ipc_endpoint_server() -> "AppShellIPCEndpointServer | None":
    return _CURRENT_IPC_ENDPOINT_SERVER


def clear_current_ipc_endpoint_server() -> None:
    set_current_ipc_endpoint_server(None)


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


def _read_only_command_allowed(command_text: str) -> bool:
    token = " ".join(str(command_text or "").strip().split()).strip()
    if not token:
        return False
    return any(token == prefix or token.startswith(prefix + " ") for prefix in _READ_ONLY_SAFE_COMMAND_PREFIXES)


class AppShellIPCEndpointServer:
    """Process-local deterministic IPC endpoint."""

    def __init__(
        self,
        *,
        repo_root: str,
        product_id: str,
        session_id: str = "",
        mode_id: str = "cli",
        manifest_path: str = "",
        session_metadata: Mapping[str, object] | None = None,
    ) -> None:
        self.repo_root = os.path.normpath(os.path.abspath(str(repo_root or ".")))
        self.product_id = str(product_id or "").strip()
        self.session_id = resolve_ipc_session_id(self.product_id, session_id)
        self.mode_id = str(mode_id or "cli").strip() or "cli"
        self.manifest_path = str(manifest_path or "").strip()
        self.session_metadata = dict(_normalize_tree(dict(session_metadata or {})))
        self.descriptor_payload = emit_descriptor_payload(self.repo_root, product_id=self.product_id)
        self.address_payload = build_ipc_local_address(self.repo_root, self.product_id, self.session_id)
        self.endpoint_id = "ipc.{}.{}".format(self.product_id, self.session_id)
        self.endpoint_descriptor = build_ipc_endpoint_descriptor(
            endpoint_id=self.endpoint_id,
            product_id=self.product_id,
            session_id=self.session_id,
            address=str(self.address_payload.get("address", "")).strip(),
            extensions={
                "official.transport_id": str(self.address_payload.get("transport_id", "")).strip(),
                "official.descriptor_hash": str(self.descriptor_payload.get("descriptor_hash", "")).strip(),
            },
        )
        self.listener = None
        self._thread = None
        self._stop_event = threading.Event()
        self._seq_lock = threading.Lock()
        self._channel_seq = {"console": 0, "log": 0, "negotiation": 0, "status": 0}
        self._attach_records: list[dict] = []

    def _next_seq(self, channel_id: str) -> int:
        with self._seq_lock:
            token = str(channel_id).strip()
            self._channel_seq[token] = int(self._channel_seq.get(token, 0) or 0) + 1
            return int(self._channel_seq[token])

    def _send(self, handle, channel_id: str, payload_ref: Mapping[str, object], *, extensions: Mapping[str, object] | None = None) -> dict:
        frame = build_ipc_frame(
            channel_id=str(channel_id).strip(),
            seq_no=self._next_seq(str(channel_id).strip()),
            payload_ref=dict(_normalize_tree(dict(payload_ref or {}))),
            extensions=dict(_normalize_tree(dict(extensions or {}))),
        )
        send_frame(handle, frame)
        return frame

    def _status_payload(self) -> dict:
        logger = get_current_log_engine()
        log_rows = list(logger.ring_events() if logger is not None else [])
        ticks = [int(row.get("tick", 0) or 0) for row in log_rows if row.get("tick") is not None]
        return {
            "result": "complete",
            "endpoint_id": self.endpoint_id,
            "product_id": self.product_id,
            "session_id": self.session_id,
            "mode_id": self.mode_id,
            "descriptor_hash": str(self.descriptor_payload.get("descriptor_hash", "")).strip(),
            "compatibility_mode_id": "compat.full",
            "effective_ui_mode": self.mode_id,
            "log_event_count": int(len(log_rows)),
            "last_tick": int(max(ticks, default=0)),
            "attach_count": int(len(self._attach_records)),
            "extensions": {
                "official.address": str(self.address_payload.get("address", "")).strip(),
                "official.transport_id": str(self.address_payload.get("transport_id", "")).strip(),
            },
        }

    def _log_events_payload(self, payload_ref: Mapping[str, object]) -> list[dict]:
        logger = get_current_log_engine()
        if logger is None:
            return []
        after_event_id = str(dict(payload_ref or {}).get("after_event_id", "")).strip()
        limit = max(1, min(32, int(dict(payload_ref or {}).get("limit", 16) or 16)))
        rows = sorted(list(logger.ring_events()), key=lambda row: str(dict(row).get("event_id", "")).strip())
        if after_event_id:
            rows = [dict(row) for row in rows if str(dict(row).get("event_id", "")).strip() > after_event_id]
        return [dict(_normalize_tree(dict(row))) for row in rows[:limit]]

    def _dispatch_console(self, negotiation_record: Mapping[str, object], payload_ref: Mapping[str, object]) -> list[dict]:
        from src.appshell.commands.command_engine import dispatch_registered_command

        message = dict(_normalize_tree(dict(payload_ref or {})))
        command_text = str(message.get("text", "")).strip()
        mode_id = str(dict(negotiation_record or {}).get("compatibility_mode_id", "")).strip()
        if mode_id == COMPAT_MODE_READ_ONLY and not _read_only_command_allowed(command_text):
            refusal = {
                "result": "refused",
                "refusal_code": "refusal.law.attach_denied",
                "reason": "read-only IPC attach forbids mutation-capable or privileged commands",
                "remediation_hint": "Use a full-compat attach or run a read-only-safe command such as help, version, or compat-status.",
                "details": {
                    "command_text": command_text,
                    "compatibility_mode_id": mode_id,
                },
            }
            return [
                {
                    "kind": "stderr",
                    "text": json.dumps(refusal, indent=2, sort_keys=True),
                    "extensions": {"official.refusal_code": "refusal.law.attach_denied"},
                },
                {
                    "kind": "cmd_response",
                    "text": json.dumps(refusal, sort_keys=True),
                    "extensions": {"official.dispatch": refusal},
                },
            ]
        dispatch = dispatch_registered_command(
            self.repo_root,
            product_id=self.product_id,
            mode_id="cli",
            command_tokens=command_text.split(),
        )
        dispatch_kind = str(dict(dispatch or {}).get("dispatch_kind", "")).strip()
        output_text = (
            str(dict(dispatch or {}).get("text", ""))
            if dispatch_kind == "text"
            else descriptor_json_text(dict(dict(dispatch or {}).get("payload") or {}))
        )
        stdout_kind = "stdout" if int(dict(dispatch or {}).get("exit_code", 0) or 0) == 0 else "stderr"
        return [
            {
                "kind": stdout_kind,
                "text": output_text,
                "extensions": {"official.dispatch_kind": dispatch_kind},
            },
            {
                "kind": "cmd_response",
                "text": json.dumps(
                    {
                        "result": "complete",
                        "dispatch_kind": dispatch_kind,
                        "exit_code": int(dict(dispatch or {}).get("exit_code", 0) or 0),
                    },
                    sort_keys=True,
                ),
                "extensions": {
                    "official.dispatch": dict(_normalize_tree(dict(dispatch or {}))),
                },
            },
        ]

    def _record_attach(self, negotiation_record: Mapping[str, object], endpoint_hashes: Mapping[str, object]) -> None:
        row = {
            "endpoint_id": self.endpoint_id,
            "session_id": self.session_id,
            "compatibility_mode_id": str(dict(negotiation_record or {}).get("compatibility_mode_id", "")).strip(),
            "negotiation_record_hash": str(endpoint_hashes.get("negotiation_record_hash", "")).strip(),
            "endpoint_descriptor_hashes": {
                "endpoint_a_hash": str(endpoint_hashes.get("endpoint_a_hash", "")).strip(),
                "endpoint_b_hash": str(endpoint_hashes.get("endpoint_b_hash", "")).strip(),
            },
        }
        self._attach_records.append(dict(row))
        self._attach_records = list(self._attach_records[-16:])

    def recent_attach_records(self) -> list[dict]:
        return [dict(row) for row in self._attach_records]

    def _handle_connection(self, conn) -> None:
        with conn:
            reader = conn.makefile("r", encoding="utf-8", newline="\n")
            writer = conn.makefile("w", encoding="utf-8", newline="\n")
            try:
                client_frame = recv_frame(reader)
                client_channel_id = str(dict(client_frame).get("channel_id", "")).strip()
                client_message = dict(dict(client_frame).get("payload_ref") or {})
                client_payload = dict(client_message.get("payload_ref") or {})
                client_descriptor = client_payload.get("endpoint_descriptor")
                if client_channel_id != "negotiation" or str(client_message.get("message_kind", "")).strip() != "client_hello" or not isinstance(client_descriptor, Mapping):
                    refusal = build_compat_refusal(
                        refusal_code=REFUSAL_CONNECTION_NO_NEGOTIATION,
                        remediation_hint="Begin IPC attach with a CAP-NEG client_hello before requesting console, log, or status channels.",
                        extensions={"official.endpoint_id": self.endpoint_id},
                    )
                    refusal_payload = build_handshake_message(
                        message_kind="negotiation_result",
                        protocol_version="1.0.0",
                        payload_ref={
                            "result": "refused",
                            "compatibility_mode_id": "compat.refuse",
                            "negotiation_record": {},
                            "negotiation_record_hash": "",
                            "endpoint_a_hash": "",
                            "endpoint_b_hash": "",
                            "refusal": refusal,
                        },
                    )
                    self._send(writer, "negotiation", refusal_payload)
                    log_emit(
                        category="ipc",
                        severity="warn",
                        message_key="ipc.attach.refused",
                        params={
                            "product_id": self.product_id,
                            "endpoint_id": self.endpoint_id,
                            "refusal_code": REFUSAL_CONNECTION_NO_NEGOTIATION,
                        },
                    )
                    return

                server_hello_payload = build_handshake_message(
                    message_kind="server_hello",
                    protocol_version="1.0.0",
                    payload_ref={"endpoint_descriptor": dict(self.descriptor_payload.get("descriptor") or {})},
                )
                self._send(writer, "negotiation", server_hello_payload)

                negotiation = negotiate_product_endpoints(
                    self.repo_root,
                    dict(client_descriptor),
                    dict(self.descriptor_payload.get("descriptor") or {}),
                    allow_read_only=True,
                    chosen_contract_bundle_hash=str(self.session_metadata.get("contract_bundle_hash", "")).strip(),
                )
                negotiation_record = dict(negotiation.get("negotiation_record") or {})
                negotiation_payload = build_handshake_message(
                    message_kind="negotiation_result",
                    protocol_version=str(negotiation_record.get("chosen_protocol_version", "1.0.0")).strip() or "1.0.0",
                    payload_ref={
                        "negotiation_record": negotiation_record,
                        "negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
                        "result": str(negotiation.get("result", "")).strip(),
                        "compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
                        "endpoint_a_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
                        "endpoint_b_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
                        "refusal": dict(negotiation.get("refusal") or {}),
                    },
                )
                self._send(writer, "negotiation", negotiation_payload)
                if str(negotiation.get("result", "")).strip() != "complete":
                    return

                ack_frame = recv_frame(reader)
                ack_payload = dict(dict(ack_frame).get("payload_ref") or {})
                ack_message = dict(ack_payload.get("payload_ref") or {})
                if not bool(ack_message.get("accepted", False)):
                    return
                if str(ack_message.get("negotiation_record_hash", "")).strip() != str(negotiation.get("negotiation_record_hash", "")).strip():
                    mismatch = {
                        "result": "refused",
                        "refusal_code": REFUSAL_CONNECTION_NEGOTIATION_MISMATCH,
                        "reason": "client acknowledgement negotiation hash did not match server record",
                        "remediation_hint": "Retry the attach so both sides negotiate against the same descriptors.",
                    }
                    self._send(writer, "negotiation", mismatch)
                    return

                self._record_attach(
                    negotiation_record,
                    {
                        "negotiation_record_hash": str(negotiation.get("negotiation_record_hash", "")).strip(),
                        "endpoint_a_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
                        "endpoint_b_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
                    },
                )
                log_emit(
                    category="ipc",
                    severity="info",
                    message_key="ipc.attach.accepted",
                    params={
                        "product_id": self.product_id,
                        "endpoint_id": self.endpoint_id,
                        "compatibility_mode_id": str(negotiation.get("compatibility_mode_id", "")).strip(),
                    },
                )
                if str(negotiation.get("compatibility_mode_id", "")).strip() == COMPAT_MODE_READ_ONLY:
                    log_emit(
                        category="compat",
                        severity="warn",
                        message_key="compat.negotiation.read_only",
                        params={"product_id": self.product_id, "endpoint_id": self.endpoint_id},
                    )

                connection_id = "ipc.{}.attach.{:04d}".format(self.endpoint_id, int(len(self._attach_records)))
                session_begin = build_handshake_message(
                    message_kind="session_begin",
                    protocol_version=str(negotiation_record.get("chosen_protocol_version", "1.0.0")).strip() or "1.0.0",
                    payload_ref=build_session_begin_payload(
                        connection_id=connection_id,
                        negotiation_record_hash=str(negotiation.get("negotiation_record_hash", "")).strip(),
                        contract_bundle_hash=str(self.session_metadata.get("contract_bundle_hash", "")).strip(),
                        pack_lock_hash=str(self.session_metadata.get("pack_lock_hash", "")).strip(),
                        semantic_contract_registry_hash=str(
                            dict(self.descriptor_payload.get("descriptor") or {}).get("extensions", {}).get(
                                "official.semantic_contract_registry_hash", ""
                            )
                        ).strip(),
                        compatibility_mode_id=str(negotiation.get("compatibility_mode_id", "")).strip(),
                        law_profile_id_override=str(
                            dict(negotiation_record.get("extensions") or {}).get("official.compat.read_only_law_profile_id", "")
                        ).strip(),
                        extensions={
                            "official.endpoint_id": self.endpoint_id,
                            "official.session_id": self.session_id,
                            "official.address": str(self.address_payload.get("address", "")).strip(),
                            "official.endpoint_a_hash": str(negotiation.get("endpoint_a_hash", "")).strip(),
                            "official.endpoint_b_hash": str(negotiation.get("endpoint_b_hash", "")).strip(),
                        },
                    ),
                )
                self._send(writer, "negotiation", session_begin)

                request_frame = recv_frame(reader)
                channel_id = str(dict(request_frame).get("channel_id", "")).strip()
                request_payload = dict(dict(request_frame).get("payload_ref") or {})
                if channel_id == "status":
                    self._send(writer, "status", self._status_payload())
                    return
                if channel_id == "log":
                    for row in self._log_events_payload(request_payload):
                        self._send(writer, "log", row)
                    return
                if channel_id == "console":
                    for row in self._dispatch_console(negotiation_record, request_payload):
                        self._send(
                            writer,
                            "console",
                            build_console_io_message(
                                kind=str(dict(row).get("kind", "")).strip(),
                                text=str(dict(row).get("text", "")),
                                extensions=dict(dict(row).get("extensions") or {}),
                            ),
                        )
            finally:
                writer.close()
                reader.close()

    def _serve_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                conn, _addr = self.listener.accept()
            except OSError:
                break
            try:
                self._handle_connection(conn)
            except Exception as exc:  # pragma: no cover
                log_emit(
                    category="ipc",
                    severity="error",
                    message_key="ipc.attach.refused",
                    params={"product_id": self.product_id, "error": str(exc)},
                )

    def start(self) -> dict:
        if self.listener is not None:
            return {"result": "complete", "endpoint_descriptor": dict(self.endpoint_descriptor)}
        self.listener = open_ipc_listener(self.address_payload)
        upsert_ipc_manifest_entry(
            self.repo_root,
            {
                **dict(self.endpoint_descriptor),
                "extensions": {
                    **dict(self.endpoint_descriptor.get("extensions") or {}),
                    "official.transport_id": str(self.address_payload.get("transport_id", "")).strip(),
                },
            },
            self.manifest_path,
        )
        self._thread = threading.Thread(target=self._serve_loop, name="appshell-ipc-{}".format(self.product_id), daemon=True)
        self._thread.start()
        set_current_ipc_endpoint_server(self)
        log_emit(
            category="ipc",
            severity="info",
            message_key="ipc.endpoint.started",
            params={"product_id": self.product_id, "endpoint_id": self.endpoint_id},
        )
        return {
            "result": "complete",
            "endpoint_id": self.endpoint_id,
            "endpoint_descriptor": dict(self.endpoint_descriptor),
            "address": str(self.address_payload.get("address", "")).strip(),
        }

    def stop(self) -> dict:
        if self.listener is None:
            return {"result": "complete", "endpoint_id": self.endpoint_id}
        self._stop_event.set()
        try:
            connector = connect_ipc_client(self.address_payload, max_attempts=1)
            connector.close()
        except OSError:
            pass
        try:
            self.listener.close()
        except OSError:
            pass
        if self._thread is not None:
            self._thread.join()
        if str(self.address_payload.get("family", "")).strip() == "unix":
            bind_target = str(self.address_payload.get("bind_target", "")).strip()
            if bind_target and os.path.exists(bind_target):
                os.remove(bind_target)
        remove_ipc_manifest_entry(self.repo_root, self.endpoint_id, self.manifest_path)
        if get_current_ipc_endpoint_server() is self:
            clear_current_ipc_endpoint_server()
        self.listener = None
        log_emit(
            category="ipc",
            severity="info",
            message_key="ipc.endpoint.stopped",
            params={"product_id": self.product_id, "endpoint_id": self.endpoint_id},
        )
        return {"result": "complete", "endpoint_id": self.endpoint_id}


__all__ = [
    "AppShellIPCEndpointServer",
    "clear_current_ipc_endpoint_server",
    "get_current_ipc_endpoint_server",
    "set_current_ipc_endpoint_server",
]
