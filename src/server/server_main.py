"""SERVER-MVP-0 CLI entrypoint."""

from __future__ import annotations

import argparse
import json
import os

from src.server.net.loopback_transport import accept_loopback_connection, create_loopback_listener
from src.server.runtime.tick_loop import run_server_ticks
from src.server.server_boot import boot_server_runtime
from src.server.server_console import (
    emit_diag_bundle_stub,
    kick_client_stub,
    list_clients,
    save_snapshot,
    server_status,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SERVER-MVP-0 deterministic headless server baseline.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--session-spec-path", default="")
    parser.add_argument("--server-config-id", default="server.mvp_default")
    parser.add_argument("--seed", default="0")
    parser.add_argument("--profile-bundle", default="")
    parser.add_argument("--pack-lock", default="")
    parser.add_argument("--contract-bundle-hash", default="")
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
        expected_contract_bundle_hash=str(args.contract_bundle_hash),
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
        command_result = server_status(boot)
    elif str(args.command or "").strip() == "list-clients":
        command_result = list_clients(boot)
    elif str(args.command or "").strip() == "kick":
        command_result = kick_client_stub(boot, str(args.client_id))
    elif str(args.command or "").strip() == "save-snapshot":
        command_result = save_snapshot(boot, str(args.output_path))
    elif str(args.command or "").strip() == "emit-diag":
        command_result = emit_diag_bundle_stub(boot, str(args.output_path))

    summary = {
        "result": "complete",
        "save_id": str((dict(boot.get("session_spec") or {})).get("save_id", "")).strip(),
        "listener": listener_result,
        "accept": accept_result,
        "ticks": ticks_result,
        "command": command_result,
        "status": server_status(boot),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
