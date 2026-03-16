"""Minimal deterministic CLI/GUI/server bootstrap for MVP runtime bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Sequence

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.appshell import appshell_main
from src.compat import descriptor_json_text, emit_product_descriptor
from tools.mvp.runtime_bundle import (
    MVP_PACK_LOCK_REL,
    MVP_PROFILE_BUNDLE_REL,
    build_runtime_bootstrap,
)


_LEGACY_UI_TO_MODE = {
    "cli": "cli",
    "gui": "rendered",
    "headless": "cli",
}
_MODE_TO_LEGACY_UI = {
    "cli": "cli",
    "tui": "cli",
    "rendered": "gui",
    "os_native": "gui",
}


def build_parser(entrypoint: str = "") -> argparse.ArgumentParser:
    entrypoint_token = str(entrypoint).strip()
    description = "Bootstrap Dominium MVP runtime entrypoint."
    if entrypoint_token:
        description = "Bootstrap Dominium MVP runtime entrypoint for {}.".format(entrypoint_token)
    parser = argparse.ArgumentParser(
        description=description
    )
    parser.add_argument("entrypoint", nargs="?", default=entrypoint_token or "client", choices=("client", "server"))
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


def _has_mode_flag(argv: Sequence[str] | None) -> bool:
    for token in list(argv or []):
        value = str(token).strip()
        if value == "--mode" or value.startswith("--mode="):
            return True
    return False


def _normalize_appshel_args(argv: Sequence[str] | None) -> list[str]:
    raw_args = [str(token) for token in list(argv or [])]
    explicit_mode = _has_mode_flag(raw_args)
    normalized: list[str] = []
    index = 0
    while index < len(raw_args):
        token = str(raw_args[index]).strip()
        if token == "--ui":
            legacy_value = str(raw_args[index + 1]).strip() if index + 1 < len(raw_args) else ""
            if not explicit_mode:
                mapped = _LEGACY_UI_TO_MODE.get(legacy_value, "")
                if mapped:
                    normalized.extend(["--mode", mapped])
            index += 2 if index + 1 < len(raw_args) else 1
            continue
        if token.startswith("--ui="):
            if not explicit_mode:
                mapped = _LEGACY_UI_TO_MODE.get(token.split("=", 1)[1].strip(), "")
                if mapped:
                    normalized.extend(["--mode", mapped])
            index += 1
            continue
        normalized.append(str(raw_args[index]))
        index += 1
    return normalized


def _legacy_ui_for_mode(mode_id: str) -> str:
    return _MODE_TO_LEGACY_UI.get(str(mode_id).strip(), "")


def _delegate_args_for_legacy(context: dict) -> list[str]:
    delegate_argv = [str(token) for token in list(context.get("delegate_argv") or [])]
    converted: list[str] = []
    index = 0
    saw_ui = False
    while index < len(delegate_argv):
        token = str(delegate_argv[index]).strip()
        if token == "--mode":
            mode_value = str(delegate_argv[index + 1]).strip() if index + 1 < len(delegate_argv) else ""
            legacy_ui = _legacy_ui_for_mode(mode_value)
            if legacy_ui:
                converted.extend(["--ui", legacy_ui])
                saw_ui = True
            index += 2 if index + 1 < len(delegate_argv) else 1
            continue
        if token.startswith("--mode="):
            legacy_ui = _legacy_ui_for_mode(token.split("=", 1)[1].strip())
            if legacy_ui:
                converted.extend(["--ui", legacy_ui])
                saw_ui = True
            index += 1
            continue
        if token == "--ui" or token.startswith("--ui="):
            saw_ui = True
        converted.append(str(delegate_argv[index]))
        index += 1
    if not saw_ui:
        selected_mode_id = str(context.get("selected_mode_id", "")).strip() or str(context.get("mode_id", "")).strip()
        legacy_ui = _legacy_ui_for_mode(selected_mode_id)
        if legacy_ui:
            converted = ["--ui", legacy_ui] + converted
    return converted


def _legacy_main(entrypoint: str, argv: Sequence[str] | None = None) -> int:
    args = build_parser(entrypoint).parse_args(argv)
    resolved_entrypoint = str(args.entrypoint or entrypoint).strip() or str(entrypoint).strip()
    repo_root = os.path.abspath(str(args.repo_root))
    if bool(args.descriptor) or str(args.descriptor_file or "").strip():
        emitted = emit_product_descriptor(
            repo_root,
            product_id=resolved_entrypoint,
            descriptor_file=str(args.descriptor_file or "").strip(),
        )
        print(descriptor_json_text(dict(emitted.get("descriptor") or {})))
        return 0
    if resolved_entrypoint == "client" and bool(args.local_singleplayer):
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
            entrypoint=resolved_entrypoint,
            ui=_default_ui(entrypoint=resolved_entrypoint, ui=str(args.ui)),
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


def appshell_product_bootstrap(context: dict) -> int:
    product_id = str(context.get("product_id", "")).strip() or "client"
    delegate_argv = ["--repo-root", str(context.get("repo_root", ".")).replace("/", "\\")]
    delegate_argv.extend(_delegate_args_for_legacy(context))
    return _legacy_main(product_id, delegate_argv)


def client_main(argv: Sequence[str] | None = None) -> int:
    return appshell_main(
        product_id="client",
        argv=argv,
        repo_root_hint=REPO_ROOT_HINT,
        product_bootstrap=appshell_product_bootstrap,
        legacy_main=lambda delegate_argv: _legacy_main("client", delegate_argv),
    )


def server_main(argv: Sequence[str] | None = None) -> int:
    return appshell_main(
        product_id="server",
        argv=argv,
        repo_root_hint=REPO_ROOT_HINT,
        product_bootstrap=appshell_product_bootstrap,
        legacy_main=lambda delegate_argv: _legacy_main("server", delegate_argv),
    )


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = _normalize_appshel_args(list(argv or sys.argv[1:]))
    if raw_args and str(raw_args[0]).strip() in {"client", "server"}:
        if str(raw_args[0]).strip() == "server":
            return server_main(raw_args[1:])
        return client_main(raw_args[1:])
    script_name = os.path.basename(sys.argv[0]).lower()
    if "server" in script_name:
        return server_main(raw_args)
    return client_main(raw_args)


if __name__ == "__main__":
    raise SystemExit(main())
