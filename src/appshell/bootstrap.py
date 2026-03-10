"""Shared deterministic AppShell bootstrap."""

from __future__ import annotations

import json
from typing import Callable, Sequence

from .args_parser import parse_appshell_args
from .command_registry import build_root_command_descriptors, build_tui_panel_descriptors, format_help_text
from .commands import dispatch_registered_command
from .compat_adapter import build_version_payload, emit_descriptor_payload
from .config_loader import resolve_repo_root
from .logging import (
    build_default_log_file_path,
    clear_current_log_engine,
    create_log_engine,
    log_emit,
    set_current_log_engine,
)
from .mode_dispatcher import build_mode_stub, legacy_mode_args, normalize_mode, supported_modes_for_product
from .tui import run_tui_mode


EXIT_SUCCESS = 0
EXIT_USAGE = 10
EXIT_PACK = 20
EXIT_CONTRACT = 30
EXIT_TRANSPORT = 40
EXIT_REFUSAL = 50
EXIT_INTERNAL = 60


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _refusal(code: str, message: str, remediation_hint: str, **extra) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(code),
        "message": str(message),
        "remediation_hint": str(remediation_hint),
        "details": {}
    }
    for key, value in sorted(extra.items(), key=lambda item: str(item[0])):
        payload["details"][str(key)] = value
    return payload


def appshell_main(
    *,
    product_id: str,
    argv: Sequence[str] | None = None,
    repo_root_hint: str = ".",
    legacy_main: Callable[[Sequence[str]], int] | None = None,
    legacy_accepts_repo_root: bool = False,
) -> int:
    shell_args = parse_appshell_args(product_id=str(product_id).strip(), argv=argv)
    repo_root = resolve_repo_root(shell_args.repo_root, repo_root_hint=repo_root_hint)
    mode_id = normalize_mode(product_id=str(product_id).strip(), requested_mode=shell_args.mode)
    command_rows = build_root_command_descriptors(repo_root, str(product_id).strip())
    version_payload = build_version_payload(repo_root, product_id=str(product_id).strip())
    logger = create_log_engine(
        product_id=str(product_id).strip(),
        build_id=str(version_payload.get("build_id", "")).strip(),
        file_path=build_default_log_file_path(repo_root, str(product_id).strip()),
    )
    set_current_log_engine(logger)
    log_emit(
        category="appshell",
        severity="info",
        message_key="appshell.bootstrap.start",
        params={
            "mode_id": str(mode_id).strip(),
            "repo_root": str(repo_root).replace("\\", "/"),
        },
    )

    try:
        if shell_args.help_requested:
            topic_tokens = shell_args.command_args if str(shell_args.command or "").strip() == "help" else []
            log_emit(
                category="appshell",
                severity="info",
                message_key="appshell.mode.enter",
                params={"mode_id": "cli", "entry_surface": "help"},
            )
            print(format_help_text(str(product_id).strip(), command_rows, topic_tokens))
            return EXIT_SUCCESS

        if bool(shell_args.descriptor) or str(shell_args.descriptor_file).strip():
            _print_json(
                emit_descriptor_payload(
                    repo_root,
                    product_id=str(product_id).strip(),
                    descriptor_file=str(shell_args.descriptor_file),
                )
            )
            return EXIT_SUCCESS

        if bool(shell_args.version):
            _print_json(version_payload)
            return EXIT_SUCCESS

        if str(shell_args.command or "").strip():
            dispatch = dispatch_registered_command(
                repo_root,
                product_id=str(product_id).strip(),
                mode_id=str(mode_id),
                command_tokens=[str(shell_args.command)] + list(shell_args.command_args),
            )
            dispatch_kind = str(dict(dispatch or {}).get("dispatch_kind", "")).strip()
            if dispatch_kind == "text":
                print(str(dict(dispatch or {}).get("text", "")))
            else:
                _print_json(dict(dispatch or {}).get("payload") or {})
            exit_code = dict(dispatch or {}).get("exit_code", EXIT_INTERNAL)
            return int(EXIT_INTERNAL if exit_code is None else exit_code)

        supported_modes = supported_modes_for_product(str(product_id).strip())
        if bool(shell_args.mode_requested) and str(mode_id).strip() not in supported_modes:
            payload = _refusal(
                "refusal.debug.mode_unsupported",
                "requested shell mode is not supported by this product",
                "Choose one of the declared AppShell modes for the product.",
                product_id=str(product_id).strip(),
                mode_id=str(mode_id).strip(),
                supported_mode_ids=list(supported_modes),
            )
            log_emit(
                category="refusal",
                severity="error",
                message_key="appshell.refusal",
                params={"refusal_code": str(payload.get("refusal_code", "")).strip(), "mode_id": str(mode_id).strip()},
            )
            _print_json(payload)
            return EXIT_REFUSAL

        if bool(shell_args.mode_requested) and str(mode_id).strip() == "tui":
            panel_rows = build_tui_panel_descriptors(str(product_id).strip())
            log_emit(
                category="appshell",
                severity="info",
                message_key="appshell.mode.enter",
                params={
                    "mode_id": "tui",
                    "entry_surface": "tui_engine",
                    "panel_descriptor_count": int(len(list(panel_rows))),
                },
            )
            dispatch = run_tui_mode(
                repo_root,
                product_id=str(product_id).strip(),
                requested_layout_id=str(shell_args.tui_layout).strip(),
            )
            if str(dispatch.get("dispatch_kind", "")).strip() == "json":
                _print_json(dict(dispatch.get("payload") or {}))
            else:
                print(str(dispatch.get("text", "")), end="")
            exit_code = dict(dispatch or {}).get("exit_code", EXIT_INTERNAL)
            return int(EXIT_INTERNAL if exit_code is None else exit_code)

        if bool(shell_args.mode_requested) and str(mode_id).strip() == "rendered" and str(product_id).strip() != "client":
            payload = _refusal(
                "refusal.debug.rendered_client_only",
                "rendered mode is client-only",
                "Use --mode cli or --mode tui for this product.",
                product_id=str(product_id).strip(),
            )
            log_emit(
                category="refusal",
                severity="error",
                message_key="appshell.refusal",
                params={"refusal_code": str(payload.get("refusal_code", "")).strip(), "mode_id": "rendered"},
            )
            _print_json(payload)
            return EXIT_REFUSAL

        if legacy_main is None:
            log_emit(
                category="appshell",
                severity="info",
                message_key="appshell.mode.enter",
                params={"mode_id": str(mode_id).strip(), "entry_surface": "stub"},
            )
            _print_json(build_mode_stub(str(product_id).strip(), str(mode_id).strip(), command_rows, []))
            return EXIT_SUCCESS

        delegate_args = list(shell_args.remainder)
        mode_tokens = legacy_mode_args(str(product_id).strip(), str(mode_id).strip()) if bool(shell_args.mode_requested) else []
        if mode_tokens:
            delegate_args = list(mode_tokens) + delegate_args
        if legacy_accepts_repo_root:
            delegate_args = ["--repo-root", repo_root] + delegate_args
        log_emit(
            category="appshell",
            severity="info",
            message_key="appshell.mode.enter",
            params={"mode_id": str(mode_id).strip(), "entry_surface": "legacy_main"},
        )
        return int(legacy_main(delegate_args))
    finally:
        clear_current_log_engine()


__all__ = [
    "EXIT_CONTRACT",
    "EXIT_INTERNAL",
    "EXIT_PACK",
    "EXIT_REFUSAL",
    "EXIT_SUCCESS",
    "EXIT_TRANSPORT",
    "EXIT_USAGE",
    "appshell_main",
]
