"""Shared SERVER-MVP console command helpers."""

from __future__ import annotations

import os
from typing import Mapping

from src.compat import build_compat_status_payload
from src.compat.data_format_loader import stamp_artifact_metadata
from src.compat import emit_product_descriptor
from src.diag import write_repro_bundle
from src.appshell.logging import get_current_log_engine
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, write_canonical_json


def _runtime(server_boot_payload: Mapping[str, object] | None) -> dict:
    runtime = (dict(server_boot_payload or {})).get("runtime")
    if isinstance(runtime, dict):
        return runtime
    return {}


def server_status(server_boot_payload: Mapping[str, object]) -> dict:
    runtime = _runtime(server_boot_payload)
    server = dict(runtime.get("server") or {})
    connections = dict(runtime.get("server_mvp_connections") or {})
    return {
        "result": "complete",
        "tick": int(server.get("network_tick", 0) or 0),
        "client_count": len(connections),
        "queued_intents": len(list(server.get("intent_queue") or [])),
        "proof_anchor_count": len(list(runtime.get("server_mvp_proof_anchors") or [])),
        "save_id": str((dict(server_boot_payload or {}).get("session_spec") or {}).get("save_id", "")).strip(),
    }


def list_clients(server_boot_payload: Mapping[str, object]) -> dict:
    runtime = _runtime(server_boot_payload)
    connections = dict(runtime.get("server_mvp_connections") or {})
    rows = [
        {
            "connection_id": str(connection_id),
            "peer_id": str((dict(row or {})).get("peer_id", "")).strip(),
            "account_id": str((dict(row or {})).get("account_id", "")).strip(),
        }
        for connection_id, row in sorted(connections.items(), key=lambda item: str(item[0]))
    ]
    return {"result": "complete", "clients": rows}


def compat_status(server_boot_payload: Mapping[str, object], connection_id: str = "") -> dict:
    runtime = _runtime(server_boot_payload)
    connections = dict(runtime.get("server_mvp_connections") or {})
    requested_connection_id = str(connection_id or "").strip()
    rows = []
    for current_connection_id, row in sorted(connections.items(), key=lambda item: str(item[0])):
        if requested_connection_id and str(current_connection_id) != requested_connection_id:
            continue
        status_payload = build_compat_status_payload(
            dict((dict(row or {})).get("negotiation_record") or {}),
            product_id="server",
            connection_id=str(current_connection_id),
        )
        status_payload["peer_id"] = str((dict(row or {})).get("peer_id", "")).strip()
        rows.append(status_payload)
    return {"result": "complete", "compat_rows": rows}


def kick_client_stub(server_boot_payload: Mapping[str, object], connection_id: str) -> dict:
    runtime = _runtime(server_boot_payload)
    connections = dict(runtime.get("server_mvp_connections") or {})
    token = str(connection_id or "").strip()
    row = dict(connections.get(token) or {})
    if not row:
        return {
            "result": "refused",
            "refusal": {
                "reason_code": "refusal.client.unauthorized",
                "message": "connection_id is not active",
            },
        }
    peer_id = str(row.get("peer_id", "")).strip()
    connections.pop(token, None)
    runtime["server_mvp_connections"] = dict((key, connections[key]) for key in sorted(connections.keys()))
    live = dict(runtime.get("_server_mvp_live_transports") or {})
    transport = live.pop(token, None)
    if transport is not None:
        try:
            transport.close()
        except Exception:
            pass
    runtime["_server_mvp_live_transports"] = dict((key, live[key]) for key in sorted(live.keys()))
    clients = dict(runtime.get("clients") or {})
    clients.pop(peer_id, None)
    runtime["clients"] = dict((key, clients[key]) for key in sorted(clients.keys()))
    return {"result": "complete", "connection_id": token, "peer_id": peer_id}


def save_snapshot(server_boot_payload: Mapping[str, object], output_path: str = "") -> dict:
    repo_root = str((dict(server_boot_payload or {})).get("repo_root", "")).strip()
    runtime = _runtime(server_boot_payload)
    server = dict(runtime.get("server") or {})
    tick = int(server.get("network_tick", 0) or 0)
    if str(output_path or "").strip():
        out_abs = os.path.normpath(os.path.abspath(str(output_path)))
    else:
        out_abs = os.path.join(
            repo_root,
            "build",
            "server",
            str(runtime.get("save_id", "save.server.mvp")),
            "snapshots",
            "manual.tick.{}.json".format(int(tick)),
        )
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    payload = stamp_artifact_metadata(
        repo_root=repo_root,
        artifact_kind="save_file",
        payload=dict(server.get("universe_state") or {}),
        semantic_contract_bundle_hash=str((dict(runtime.get("server_mvp") or {})).get("contract_bundle_hash", "")).strip(),
    )
    write_canonical_json(out_abs, payload)
    return {
        "result": "complete",
        "snapshot_path": norm(os.path.relpath(out_abs, repo_root)),
        "snapshot_hash": canonical_sha256(payload),
        "tick": int(tick),
    }


def emit_diag_bundle_stub(server_boot_payload: Mapping[str, object], output_path: str = "") -> dict:
    repo_root = str((dict(server_boot_payload or {})).get("repo_root", "")).strip()
    runtime = _runtime(server_boot_payload)
    server = dict(runtime.get("server") or {})
    if str(output_path or "").strip():
        out_abs = os.path.normpath(os.path.abspath(str(output_path)))
        out_dir = os.path.splitext(out_abs)[0] if os.path.splitext(out_abs)[1] else out_abs
    else:
        out_dir = os.path.join(
            repo_root,
            "build",
            "server",
            str(runtime.get("save_id", "save.server.mvp")),
            "diag",
        )
    logger = get_current_log_engine()
    descriptor = emit_product_descriptor(repo_root, product_id="server")
    materialized_paths = dict((dict(server_boot_payload or {})).get("materialized_paths") or {})
    save_id = str(runtime.get("save_id", "")).strip() or str((dict(server_boot_payload or {}).get("session_spec") or {}).get("save_id", "")).strip()
    contract_bundle_path = str(materialized_paths.get("universe_contract_bundle_path", "")).strip()
    if not contract_bundle_path and save_id:
        candidate = os.path.join(repo_root, "saves", save_id, "universe_contract_bundle.json")
        if os.path.isfile(candidate):
            contract_bundle_path = candidate
    pack_lock_payload = dict((dict(server_boot_payload or {})).get("effective_lock_payload") or {})
    proof_rows = [dict(row) for row in list(runtime.get("server_mvp_proof_anchors") or []) if isinstance(row, dict)]
    canonical_rows = [dict(row) for row in list(server.get("hash_anchor_frames") or []) if isinstance(row, dict)]
    canonical_rows.extend([dict(row) for row in list(server.get("control_proof_bundles") or []) if isinstance(row, dict)])
    bundle = write_repro_bundle(
        repo_root=repo_root,
        created_by_product_id="server",
        build_id=str(dict(descriptor.get("version") or {}).get("build_id", "")).strip(),
        out_dir=out_dir,
        descriptor_payloads=[descriptor],
        session_spec_payload=dict((dict(server_boot_payload or {}).get("session_spec") or {})),
        contract_bundle_path=contract_bundle_path,
        pack_lock_payload=pack_lock_payload,
        semantic_contract_registry_hash=str((dict(runtime.get("server_mvp") or {})).get("semantic_contract_registry_hash", "")).strip(),
        contract_bundle_hash=str((dict(runtime.get("server_mvp") or {})).get("contract_bundle_hash", "")).strip(),
        overlay_manifest_hash=str((dict(runtime.get("server_mvp") or {})).get("overlay_manifest_hash", "")).strip(),
        seed=str((dict(server_boot_payload or {}).get("session_spec") or {}).get("selected_seed", "")).strip(),
        session_id=save_id,
        session_template_id=str((dict(server_boot_payload or {}).get("session_spec") or {}).get("template_id", "")).strip(),
        proof_anchor_rows=proof_rows,
        canonical_event_rows=canonical_rows,
        log_events=list(logger.ring_events() if logger is not None else []),
    )
    return {
        "result": "complete",
        "diag_bundle_path": norm(os.path.relpath(str(bundle.get("manifest_path", "")).replace("/", os.sep), repo_root)),
        "bundle_dir": str(bundle.get("bundle_dir", "")).replace("\\", "/"),
        "bundle_hash": str(bundle.get("bundle_hash", "")).strip(),
    }


def dispatch_server_console_command(
    server_boot_payload: Mapping[str, object],
    *,
    command: str,
    payload: Mapping[str, object] | None = None,
) -> dict:
    token = str(command or "").strip().lower().replace("-", "_").replace(" ", "_")
    if token == "status":
        return server_status(server_boot_payload)
    if token == "list_clients":
        return list_clients(server_boot_payload)
    if token == "compat_status":
        return compat_status(server_boot_payload, str((dict(payload or {})).get("connection_id", "")).strip())
    if token == "save_snapshot":
        return save_snapshot(server_boot_payload, str((dict(payload or {})).get("output_path", "")).strip())
    if token == "emit_diag":
        return emit_diag_bundle_stub(server_boot_payload, str((dict(payload or {})).get("output_path", "")).strip())
    if token == "kick":
        return kick_client_stub(server_boot_payload, str((dict(payload or {})).get("connection_id", "")).strip())
    return {
        "result": "refused",
        "refusal": {
            "reason_code": "refusal.server.command_unknown",
            "message": "command is not declared in SERVER-MVP command surface",
        },
    }
