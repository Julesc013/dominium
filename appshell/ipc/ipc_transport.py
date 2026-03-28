"""Deterministic local AppShell IPC transport helpers."""

from __future__ import annotations

import hashlib
import json
import os
import socket
from typing import Mapping

from appshell.paths import VROOT_IPC, get_current_virtual_paths, vpath_resolve


IPC_ENDPOINT_MANIFEST_REL = "ipc_endpoints.json"
IPC_ENDPOINT_DESCRIPTOR_DIR_REL = "endpoints"
IPC_SOCKET_ROOT_REL = "ipc"
IPC_CHANNEL_IDS = ("console", "log", "negotiation", "status")
CONSOLE_IO_KINDS = ("cmd_request", "cmd_response", "stderr", "stdout")


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in value]
    if value is None or isinstance(value, (bool, int)):
        return value
    return str(value)


def _canonical_text(payload: Mapping[str, object]) -> str:
    return json.dumps(dict(_normalize_tree(dict(payload or {}))), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _fingerprint(payload: Mapping[str, object]) -> str:
    body = dict(_normalize_tree(dict(payload or {})))
    body["deterministic_fingerprint"] = ""
    return hashlib.sha256(_canonical_text(body).encode("utf-8")).hexdigest()


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    out_path = os.path.normpath(os.path.abspath(str(path)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(_normalize_tree(dict(payload or {}))), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")
    return out_path


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _stable_hash(*parts: object) -> str:
    return hashlib.sha256("|".join(str(part).strip() for part in parts).encode("utf-8")).hexdigest()


def resolve_ipc_session_id(product_id: str, session_id: str = "") -> str:
    token = str(session_id or "").strip()
    if token:
        return token
    return "session.{}.default".format(str(product_id or "product").strip() or "product")


def build_ipc_local_address(repo_root: str, product_id: str, session_id: str = "") -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    session_token = resolve_ipc_session_id(product_id, session_id)
    hash_token = _stable_hash(str(product_id).strip(), session_token)[:16]
    context = get_current_virtual_paths()
    ipc_root = vpath_resolve(VROOT_IPC, IPC_SOCKET_ROOT_REL, context) if context is not None and str(context.get("result", "")).strip() == "complete" else os.path.join(repo_root_abs, "build", "appshell", "ipc")
    if os.name != "nt" and hasattr(socket, "AF_UNIX"):
        bind_target = os.path.join(ipc_root, "{}.sock".format(hash_token))
        return {
            "transport_id": "ipc.unix_socket",
            "family": "unix",
            "bind_target": os.path.normpath(bind_target),
            "address": os.path.normpath(bind_target).replace("\\", "/"),
            "deterministic_fingerprint": _stable_hash("ipc.unix_socket", hash_token),
            "extensions": {},
        }
    port = 43000 + (int(hash_token[:8], 16) % 10000)
    return {
        "transport_id": "ipc.localhost_tcp",
        "family": "tcp",
        "host": "127.0.0.1",
        "port": int(port),
        "bind_target": ("127.0.0.1", int(port)),
        "address": "tcp://127.0.0.1:{}".format(int(port)),
        "deterministic_fingerprint": _stable_hash("ipc.localhost_tcp", hash_token, int(port)),
        "extensions": {},
    }


def build_ipc_endpoint_descriptor(
    *,
    endpoint_id: str,
    product_id: str,
    session_id: str,
    address: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "endpoint_id": str(endpoint_id).strip(),
        "product_id": str(product_id).strip(),
        "session_id": str(session_id).strip(),
        "address": str(address).strip(),
        "deterministic_fingerprint": "",
        "extensions": dict(_normalize_tree(dict(extensions or {}))),
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def build_ipc_frame(
    *,
    channel_id: str,
    seq_no: int,
    payload_ref: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "channel_id": str(channel_id).strip(),
        "seq_no": int(max(1, int(seq_no or 1))),
        "payload_ref": dict(_normalize_tree(dict(payload_ref or {}))),
        "deterministic_fingerprint": "",
        "extensions": dict(_normalize_tree(dict(extensions or {}))),
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def build_console_io_message(
    *,
    kind: str,
    text: str,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "kind": str(kind).strip(),
        "text": str(text or ""),
        "deterministic_fingerprint": "",
        "extensions": dict(_normalize_tree(dict(extensions or {}))),
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    return payload


def ipc_manifest_path(repo_root: str, manifest_path: str = "") -> str:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or ".")))
    token = str(manifest_path or "").strip()
    if token:
        if os.path.isabs(token):
            return os.path.normpath(token)
        return os.path.normpath(os.path.join(repo_root_abs, token.replace("/", os.sep)))
    context = get_current_virtual_paths()
    if context is not None and str(context.get("result", "")).strip() == "complete":
        return vpath_resolve(VROOT_IPC, IPC_ENDPOINT_MANIFEST_REL, context)
    return os.path.normpath(os.path.join(repo_root_abs, "dist", "runtime", IPC_ENDPOINT_MANIFEST_REL))


def _safe_endpoint_filename(endpoint_id: str) -> str:
    token = str(endpoint_id or "").strip()
    return "{}.json".format("".join(ch if ch.isalnum() or ch in (".", "-", "_") else "_" for ch in token) or "endpoint")


def _descriptor_rel_path_for_endpoint(endpoint_id: str) -> str:
    return "{}/{}".format(IPC_ENDPOINT_DESCRIPTOR_DIR_REL, _safe_endpoint_filename(endpoint_id))


def ipc_endpoint_descriptor_path(repo_root: str, endpoint_id: str, manifest_path: str = "") -> str:
    manifest_abs = ipc_manifest_path(repo_root, manifest_path)
    return os.path.normpath(os.path.join(os.path.dirname(manifest_abs), _descriptor_rel_path_for_endpoint(endpoint_id)))


def write_ipc_endpoint_descriptor(repo_root: str, endpoint_row: Mapping[str, object], manifest_path: str = "") -> dict:
    endpoint_payload = dict(_normalize_tree(dict(endpoint_row or {})))
    descriptor_path = ipc_endpoint_descriptor_path(repo_root, str(endpoint_payload.get("endpoint_id", "")).strip(), manifest_path)
    payload = {
        "schema_id": "dominium.artifact.appshell.ipc_endpoint_descriptor",
        "schema_version": "1.0.0",
        "record": endpoint_payload,
        "deterministic_fingerprint": "",
        "extensions": {
            "official.descriptor_rel_path": _descriptor_rel_path_for_endpoint(str(endpoint_payload.get("endpoint_id", "")).strip()),
        },
    }
    payload["deterministic_fingerprint"] = _fingerprint(payload)
    _write_json(descriptor_path, payload)
    return payload


def discover_ipc_endpoint_descriptor(repo_root: str, endpoint_id: str, manifest_path: str = "") -> dict:
    return _read_json(ipc_endpoint_descriptor_path(repo_root, endpoint_id, manifest_path))


def discover_ipc_manifest(repo_root: str, manifest_path: str = "") -> dict:
    path = ipc_manifest_path(repo_root, manifest_path)
    payload = _read_json(path)
    record = dict(payload.get("record") or {})
    endpoints = []
    for row in list(record.get("endpoints") or []):
        if not isinstance(row, Mapping):
            continue
        row_map = dict(_normalize_tree(dict(row)))
        if str(row_map.get("endpoint_id", "")).strip():
            endpoints.append(row_map)
    endpoints = sorted(
        endpoints,
        key=lambda row: (
            str(row.get("endpoint_id", "")).strip(),
            str(row.get("product_id", "")).strip(),
            str(row.get("session_id", "")).strip(),
        ),
    )
    return {
        "schema_id": "dominium.registry.appshell.ipc_endpoints",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.appshell.ipc_endpoints",
            "endpoints": endpoints,
            "deterministic_fingerprint": _fingerprint({"endpoints": endpoints}),
            "extensions": {},
        },
    }


def _write_manifest(repo_root: str, manifest_path: str, endpoints: list[dict]) -> dict:
    payload = {
        "schema_id": "dominium.registry.appshell.ipc_endpoints",
        "schema_version": "1.0.0",
        "record": {
            "registry_id": "dominium.registry.appshell.ipc_endpoints",
            "endpoints": sorted(
                [dict(_normalize_tree(dict(row))) for row in list(endpoints or [])],
                key=lambda row: (
                    str(row.get("endpoint_id", "")).strip(),
                    str(row.get("product_id", "")).strip(),
                    str(row.get("session_id", "")).strip(),
                ),
            ),
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    }
    payload["record"]["deterministic_fingerprint"] = _fingerprint(payload["record"])
    _write_json(ipc_manifest_path(repo_root, manifest_path), payload)
    return payload


def upsert_ipc_manifest_entry(repo_root: str, endpoint_row: Mapping[str, object], manifest_path: str = "") -> dict:
    manifest = discover_ipc_manifest(repo_root, manifest_path)
    endpoints = [dict(row) for row in list(dict(manifest.get("record") or {}).get("endpoints") or [])]
    normalized_row = dict(_normalize_tree(dict(endpoint_row or {})))
    endpoint_id = str(normalized_row.get("endpoint_id", "")).strip()
    descriptor_payload = write_ipc_endpoint_descriptor(repo_root, normalized_row, manifest_path)
    extensions = dict(normalized_row.get("extensions") or {})
    extensions["official.descriptor_hash"] = str(descriptor_payload.get("deterministic_fingerprint", "")).strip()
    extensions["official.descriptor_rel_path"] = _descriptor_rel_path_for_endpoint(endpoint_id)
    normalized_row["extensions"] = dict(_normalize_tree(extensions))
    endpoints = [row for row in endpoints if str(row.get("endpoint_id", "")).strip() != endpoint_id]
    endpoints.append(normalized_row)
    return _write_manifest(repo_root, manifest_path, endpoints)


def remove_ipc_manifest_entry(repo_root: str, endpoint_id: str, manifest_path: str = "") -> dict:
    descriptor_path = ipc_endpoint_descriptor_path(repo_root, endpoint_id, manifest_path)
    if os.path.isfile(descriptor_path):
        os.remove(descriptor_path)
    manifest = discover_ipc_manifest(repo_root, manifest_path)
    endpoints = [
        dict(row)
        for row in list(dict(manifest.get("record") or {}).get("endpoints") or [])
        if str(dict(row).get("endpoint_id", "")).strip() != str(endpoint_id).strip()
    ]
    return _write_manifest(repo_root, manifest_path, endpoints)


def open_ipc_listener(address_payload: Mapping[str, object]) -> socket.socket:
    family = str(dict(address_payload or {}).get("family", "")).strip()
    if family == "unix":
        bind_target = os.path.normpath(str(dict(address_payload or {}).get("bind_target", "")).strip())
        os.makedirs(os.path.dirname(bind_target), exist_ok=True)
        if os.path.exists(bind_target):
            os.remove(bind_target)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(bind_target)
    else:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(tuple(dict(address_payload or {}).get("bind_target") or ("127.0.0.1", 0)))
    listener.listen(4)
    return listener


def connect_ipc_client(
    address_payload: Mapping[str, object],
    *,
    max_attempts: int = 4,
    timeout_sec: float | None = None,
) -> socket.socket:
    family = str(dict(address_payload or {}).get("family", "")).strip()
    last_error = None
    for _attempt in range(max(1, int(max_attempts or 1))):
        sock = socket.socket(socket.AF_UNIX if family == "unix" else socket.AF_INET, socket.SOCK_STREAM)
        if timeout_sec is not None:
            sock.settimeout(float(timeout_sec))
        try:
            if family == "unix":
                sock.connect(str(dict(address_payload or {}).get("bind_target", "")).strip())
            else:
                sock.connect(tuple(dict(address_payload or {}).get("bind_target") or ("127.0.0.1", 0)))
            return sock
        except OSError as exc:
            last_error = exc
            sock.close()
    raise OSError(str(last_error or "ipc connect failed"))


def send_frame(handle, frame_payload: Mapping[str, object]) -> None:
    handle.write(_canonical_text(dict(frame_payload or {})))
    handle.write("\n")
    handle.flush()


def recv_frame(handle) -> dict:
    line = handle.readline()
    if not line:
        return {}
    try:
        payload = json.loads(str(line))
    except ValueError:
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


__all__ = [
    "CONSOLE_IO_KINDS",
    "IPC_CHANNEL_IDS",
    "IPC_ENDPOINT_DESCRIPTOR_DIR_REL",
    "IPC_ENDPOINT_MANIFEST_REL",
    "build_console_io_message",
    "build_ipc_endpoint_descriptor",
    "build_ipc_frame",
    "build_ipc_local_address",
    "connect_ipc_client",
    "discover_ipc_endpoint_descriptor",
    "discover_ipc_manifest",
    "ipc_manifest_path",
    "ipc_endpoint_descriptor_path",
    "open_ipc_listener",
    "recv_frame",
    "remove_ipc_manifest_entry",
    "resolve_ipc_session_id",
    "send_frame",
    "upsert_ipc_manifest_entry",
    "write_ipc_endpoint_descriptor",
]
