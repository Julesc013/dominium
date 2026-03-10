"""SERVER-MVP-0 CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import os

from src.server.net.loopback_transport import accept_loopback_connection, create_loopback_listener
from src.server.runtime.tick_loop import run_server_ticks
from src.server.server_boot import boot_server_runtime
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.sessionx.common import norm, write_canonical_json


def _server_status(server_boot_payload: dict) -> dict:
    runtime = server_boot_payload.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
    server = dict(runtime.get("server") or {})
    connections = dict(runtime.get("server_mvp_connections") or {})
    return {
        "result": "complete",
        "tick": int(server.get("network_tick", 0) or 0),
        "client_count": len(connections),
        "queued_intents": len(list(server.get("intent_queue") or [])),
        "proof_anchor_count": len(list(runtime.get("server_mvp_proof_anchors") or [])),
        "save_id": str(server_boot_payload.get("session_spec", {}).get("save_id", "")).strip(),
    }


def _list_clients(server_boot_payload: dict) -> dict:
    runtime = server_boot_payload.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
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


def _kick_client_stub(server_boot_payload: dict, connection_id: str) -> dict:
    runtime = server_boot_payload.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
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


def _save_snapshot(server_boot_payload: dict, output_path: str = "") -> dict:
    repo_root = str(server_boot_payload.get("repo_root", "")).strip()
    runtime = server_boot_payload.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
    server = dict(runtime.get("server") or {})
    tick = int(server.get("network_tick", 0) or 0)
    if str(output_path or "").strip():
        out_abs = os.path.normpath(os.path.abspath(str(output_path)))
    else:
        out_abs = os.path.join(repo_root, "build", "server", str(runtime.get("save_id", "save.server.mvp")), "snapshots", "manual.tick.{}.json".format(int(tick)))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    payload = dict(server.get("universe_state") or {})
    write_canonical_json(out_abs, payload)
    return {
        "result": "complete",
        "snapshot_path": norm(os.path.relpath(out_abs, repo_root)),
        "snapshot_hash": canonical_sha256(payload),
        "tick": int(tick),
    }


def _emit_diag_bundle_stub(server_boot_payload: dict, output_path: str = "") -> dict:
    repo_root = str(server_boot_payload.get("repo_root", "")).strip()
    runtime = server_boot_payload.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
    server = dict(runtime.get("server") or {})
    payload = {
        "schema_version": "1.0.0",
        "tick": int(server.get("network_tick", 0) or 0),
        "save_id": str(runtime.get("save_id", "")).strip(),
        "client_count": len(dict(runtime.get("server_mvp_connections") or {})),
        "proof_anchor_count": len(list(runtime.get("server_mvp_proof_anchors") or [])),
        "extensions": {},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(payload)
    if str(output_path or "").strip():
        out_abs = os.path.normpath(os.path.abspath(str(output_path)))
    else:
        out_abs = os.path.join(repo_root, "build", "server", str(runtime.get("save_id", "save.server.mvp")), "diag", "diag_bundle.stub.json")
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    write_canonical_json(out_abs, payload)
    return {"result": "complete", "diag_bundle_path": norm(os.path.relpath(out_abs, repo_root))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SERVER-MVP-0 deterministic headless server baseline.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--session-spec-path", default="")
    parser.add_argument("--server-config-id", default="server.mvp_default")
    parser.add_argument("--seed", default="0")
    parser.add_argument("--profile-bundle", default="")
    parser.add_argument("--pack-lock", default="")
    parser.add_argument("--save-id", default="")
    parser.add_argument("--authority", default="dev")
    parser.add_argument("--ticks", type=int, default=0)
    parser.add_argument("--listen-loopback", action="store_true")
    parser.add_argument("--accept-once", action="store_true")
    parser.add_argument(
        "--command",
        choices=("status", "list-clients", "kick", "save-snapshot", "emit-diag"),
        default="",
    )
    parser.add_argument("--client-id", default="")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args(argv)

    repo_root = os.path.normpath(os.path.abspath(str(args.repo_root)))
    boot = boot_server_runtime(
        repo_root=repo_root,
        session_spec_path=str(args.session_spec_path),
        seed=str(args.seed),
        profile_bundle_path=str(args.profile_bundle),
        pack_lock_path=str(args.pack_lock),
        server_config_id=str(args.server_config_id),
        authority_mode=str(args.authority),
        save_id=str(args.save_id),
    )
    if str(boot.get("result", "")) != "complete":
        print(json.dumps(boot, indent=2, sort_keys=True))
        return 2
    boot["repo_root"] = repo_root

    listener_result = {}
    if bool(args.listen_loopback):
        listener_result = create_loopback_listener(boot)
        if str(listener_result.get("result", "")) != "complete":
            print(json.dumps(listener_result, indent=2, sort_keys=True))
            return 2

    accept_result = {}
    if bool(args.accept_once):
        accept_result = accept_loopback_connection(boot)
        if str(accept_result.get("result", "")) not in {"complete", "empty"}:
            print(json.dumps(accept_result, indent=2, sort_keys=True))
            return 2

    ticks_result = {}
    if int(args.ticks or 0) > 0:
        ticks_result = run_server_ticks(boot, int(args.ticks))
        if str(ticks_result.get("result", "")) != "complete":
            print(json.dumps(ticks_result, indent=2, sort_keys=True))
            return 2

    command_result = {}
    if str(args.command or "").strip() == "status":
        command_result = _server_status(boot)
    elif str(args.command or "").strip() == "list-clients":
        command_result = _list_clients(boot)
    elif str(args.command or "").strip() == "kick":
        command_result = _kick_client_stub(boot, str(args.client_id))
    elif str(args.command or "").strip() == "save-snapshot":
        command_result = _save_snapshot(boot, str(args.output_path))
    elif str(args.command or "").strip() == "emit-diag":
        command_result = _emit_diag_bundle_stub(boot, str(args.output_path))

    summary = {
        "result": "complete",
        "save_id": str((dict(boot.get("session_spec") or {})).get("save_id", "")).strip(),
        "listener": listener_result,
        "accept": accept_result,
        "ticks": ticks_result,
        "command": command_result,
        "status": _server_status(boot),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
