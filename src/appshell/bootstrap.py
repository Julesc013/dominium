"""Shared deterministic AppShell bootstrap."""

from __future__ import annotations

import json
from typing import Callable, Sequence

from .args_parser import parse_appshell_args
from .command_registry import build_root_command_descriptors, build_tui_panel_descriptors, format_help_text
from .commands import dispatch_registered_command
from .compat_adapter import build_version_payload, emit_descriptor_payload
from .config_loader import resolve_repo_root
from .ipc import AppShellIPCEndpointServer
from .logging import (
    build_default_log_file_path,
    clear_current_log_engine,
    create_log_engine,
    log_emit,
    set_current_log_engine,
)
from .mode_dispatcher import build_mode_stub, normalize_mode, supported_modes_for_product
from .product_bootstrap import build_product_bootstrap_context, resolve_mode_request
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
    product_bootstrap: Callable[[dict], int] | None = None,
    legacy_main: Callable[[Sequence[str]], int] | None = None,
    legacy_accepts_repo_root: bool = False,
) -> int:
    shell_args = parse_appshell_args(product_id=str(product_id).strip(), argv=argv)
    repo_root = resolve_repo_root(shell_args.repo_root, repo_root_hint=repo_root_hint)
    mode_resolution = resolve_mode_request(
        product_id=str(product_id).strip(),
        explicit_mode=shell_args.mode,
        raw_args=shell_args.raw_args,
    )
    mode_id = normalize_mode(
        product_id=str(product_id).strip(),
        requested_mode=str(mode_resolution.get("requested_mode_id", "")).strip(),
    )
    mode_requested = bool(mode_resolution.get("mode_requested", False))
    command_rows = build_root_command_descriptors(repo_root, str(product_id).strip())
    version_payload = build_version_payload(repo_root, product_id=str(product_id).strip())
    logger = create_log_engine(
        product_id=str(product_id).strip(),
        build_id=str(version_payload.get("build_id", "")).strip(),
        file_path=build_default_log_file_path(repo_root, str(product_id).strip()),
    )
    set_current_log_engine(logger)
    ipc_server = None
    log_emit(
        category="appshell",
        severity="info",
        message_key="appshell.bootstrap.start",
        params={
            "mode_id": str(mode_id).strip(),
            "mode_source": str(mode_resolution.get("mode_source", "default")).strip() or "default",
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
            payload = dict(dispatch or {}).get("payload") or {}
            if (
                (legacy_main is not None or product_bootstrap is not None)
                and str(dict(payload or {}).get("refusal_code", "")).strip() == "refusal.debug.command_unknown"
            ):
                bootstrap_context = build_product_bootstrap_context(
                    product_id=str(product_id).strip(),
                    repo_root=repo_root,
                    shell_args=shell_args,
                    resolved_mode_id=str(mode_id).strip(),
                    mode_resolution=mode_resolution,
                    version_payload=version_payload,
                )
                if bool(shell_args.ipc_enabled) and ipc_server is None:
                    ipc_server = AppShellIPCEndpointServer(
                        repo_root=repo_root,
                        product_id=str(product_id).strip(),
                        session_id=str(shell_args.session_id).strip(),
                        mode_id=str(mode_id).strip() or "cli",
                        manifest_path=str(shell_args.ipc_manifest_path).strip(),
                    )
                    ipc_server.start()
                log_emit(
                    category="appshell",
                    severity="info",
                    message_key="appshell.mode.enter",
                    params={
                        "mode_id": str(mode_id).strip(),
                        "entry_surface": "product_bootstrap_fallback" if product_bootstrap is not None else "legacy_main_fallback",
                    },
                )
                if product_bootstrap is not None:
                    return int(product_bootstrap(bootstrap_context))
                delegate_args = list(bootstrap_context.get("delegate_argv") or [])
                if legacy_accepts_repo_root:
                    delegate_args = ["--repo-root", repo_root] + delegate_args
                return int(legacy_main(delegate_args))
            dispatch_kind = str(dict(dispatch or {}).get("dispatch_kind", "")).strip()
            if dispatch_kind == "text":
                print(str(dict(dispatch or {}).get("text", "")))
            else:
                _print_json(payload)
            exit_code = dict(dispatch or {}).get("exit_code", EXIT_INTERNAL)
            return int(EXIT_INTERNAL if exit_code is None else exit_code)

        supported_modes = supported_modes_for_product(str(product_id).strip())
        if bool(mode_requested) and str(mode_id).strip() not in supported_modes:
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

        if bool(mode_requested) and str(mode_id).strip() == "tui":
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

        if bool(mode_requested) and str(mode_id).strip() == "rendered" and str(product_id).strip() != "client":
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

        bootstrap_context = build_product_bootstrap_context(
            product_id=str(product_id).strip(),
            repo_root=repo_root,
            shell_args=shell_args,
            resolved_mode_id=str(mode_id).strip(),
            mode_resolution=mode_resolution,
            version_payload=version_payload,
        )
        for row in list((dict(bootstrap_context.get("mode") or {})).get("deprecated_flags") or []):
            warning = dict(row or {})
            log_emit(
                category="appshell",
                severity="warn",
                message_key="appshell.flag.deprecated",
                params={
                    "legacy_flag": str(warning.get("legacy_flag", "")).strip(),
                    "replacement_flag": str(warning.get("replacement_flag", "")).strip(),
                    "replacement_value": str(warning.get("replacement_value", "")).strip(),
                },
            )
        log_emit(
            category="appshell",
            severity="info",
            message_key="appshell.bootstrap.context",
            params={
                "compatibility_mode_id": str((dict(bootstrap_context.get("negotiation") or {})).get("compatibility_mode_id", "")).strip(),
                "entrypoint_label": str(bootstrap_context.get("entrypoint_label", "")).strip(),
                "mode_id": str((dict(bootstrap_context.get("mode") or {})).get("effective_mode_id", "")).strip(),
                "step_count": int(len(list(bootstrap_context.get("bootstrap_steps") or []))),
            },
        )
        if bool(shell_args.ipc_enabled):
            ipc_server = AppShellIPCEndpointServer(
                repo_root=repo_root,
                product_id=str(product_id).strip(),
                session_id=str(shell_args.session_id).strip(),
                mode_id=str(mode_id).strip() or "cli",
                manifest_path=str(shell_args.ipc_manifest_path).strip(),
            )
            ipc_server.start()

        if legacy_main is None and product_bootstrap is None:
            log_emit(
                category="appshell",
                severity="info",
                message_key="appshell.mode.enter",
                params={"mode_id": str(mode_id).strip(), "entry_surface": "stub"},
            )
            _print_json(build_mode_stub(str(product_id).strip(), str(mode_id).strip(), command_rows, []))
            return EXIT_SUCCESS

        log_emit(
            category="appshell",
            severity="info",
            message_key="appshell.mode.enter",
            params={
                "mode_id": str(mode_id).strip(),
                "entry_surface": "product_bootstrap" if product_bootstrap is not None else "legacy_main",
            },
        )
        if product_bootstrap is not None:
            return int(product_bootstrap(bootstrap_context))
        delegate_args = list(bootstrap_context.get("delegate_argv") or [])
        if legacy_accepts_repo_root:
            delegate_args = ["--repo-root", repo_root] + delegate_args
        return int(legacy_main(delegate_args))
    finally:
        if ipc_server is not None:
            ipc_server.stop()
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
