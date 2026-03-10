"""Minimal deterministic CLI/GUI/server bootstrap for MVP runtime bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.compat import descriptor_json_text, emit_product_descriptor
from tools.mvp.runtime_bundle import (
    MVP_PACK_LOCK_REL,
    MVP_PROFILE_BUNDLE_REL,
    build_runtime_bootstrap,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap Dominium MVP runtime entrypoints.")
    parser.add_argument("entrypoint", choices=("client", "server"))
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--descriptor", action="store_true")
    parser.add_argument("--descriptor-file", default="")
    parser.add_argument("--seed", default="")
    parser.add_argument("--profile_bundle", default=MVP_PROFILE_BUNDLE_REL)
    parser.add_argument("--pack_lock", default=MVP_PACK_LOCK_REL)
    parser.add_argument("--teleport", default="")
    parser.add_argument("--authority", default="dev", choices=("dev", "release"))
    parser.add_argument("--ui", default="", choices=("", "cli", "gui", "headless"))
    parser.add_argument("--local-singleplayer", action="store_true")
    parser.add_argument("--server-config-id", default="server.mvp_default")
    parser.add_argument("--ticks", type=int, default=0)
    parser.add_argument("--server-command", default="", choices=("", "status", "save_snapshot"))
    parser.add_argument("--output-path", default="")
    return parser


def _default_ui(entrypoint: str, ui: str) -> str:
    token = str(ui).strip().lower()
    if token:
        return token
    if str(entrypoint) == "server":
        return "headless"
    return "gui"


def main() -> int:
    args = build_parser().parse_args()
    repo_root = os.path.abspath(str(args.repo_root))
    if bool(args.descriptor) or str(args.descriptor_file or "").strip():
        emitted = emit_product_descriptor(
            repo_root,
            product_id=str(args.entrypoint),
            descriptor_file=str(args.descriptor_file or "").strip(),
        )
        print(descriptor_json_text(dict(emitted.get("descriptor") or {})))
        return 0
    if str(args.entrypoint) == "client" and bool(args.local_singleplayer):
        from src.client.local_server import request_local_server_control, run_local_server_ticks, start_local_singleplayer

        started = start_local_singleplayer(
            repo_root=repo_root,
            seed=str(args.seed),
            profile_bundle_path=str(args.profile_bundle),
            pack_lock_path=str(args.pack_lock),
            server_config_id=str(args.server_config_id),
            authority_mode=str(args.authority),
        )
        if str(started.get("result", "")) != "complete":
            print(json.dumps(started, indent=2, sort_keys=True))
            return 2
        controller = dict(started.get("controller") or {})
        command_result = {}
        if str(args.server_command or "").strip():
            command_request = request_local_server_control(
                controller,
                request_kind=str(args.server_command),
                payload={"output_path": str(args.output_path or "").strip()},
            )
            tick_report = run_local_server_ticks(controller, ticks=1)
            command_result = {
                "request": dict(command_request),
                "responses": list(tick_report.get("control_responses") or []),
                "log_events": list(tick_report.get("log_events") or []),
            }
        tick_report = run_local_server_ticks(controller, ticks=int(max(0, int(args.ticks or 0))))
        payload = {
            "result": "complete",
            "local_singleplayer": dict(started),
            "server_command": command_result,
            "ticks": dict(tick_report),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    try:
        payload = build_runtime_bootstrap(
            repo_root=repo_root,
            entrypoint=str(args.entrypoint),
            ui=_default_ui(entrypoint=str(args.entrypoint), ui=str(args.ui)),
            seed=str(args.seed),
            profile_bundle_path=str(args.profile_bundle),
            pack_lock_path=str(args.pack_lock),
            teleport=str(args.teleport),
            authority_mode=str(args.authority),
        )
    except ValueError as exc:
        print(json.dumps({"reason": str(exc), "result": "refused"}, indent=2, sort_keys=True))
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
