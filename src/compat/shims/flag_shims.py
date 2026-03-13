"""Deterministic legacy CLI flag migration helpers."""

from __future__ import annotations

import os
from typing import Iterable

from src.appshell.mode_dispatcher import supported_modes_for_product

from .common import SHIM_SUNSET_TARGET, build_shim_stability, stable_rows


FLAG_WARNING_KEY = "warn.deprecated_flag_usage"
FLAG_SHIM_ROWS = stable_rows(
    (
        {
            "shim_id": "shim.flag.legacy_client_ui",
            "product_id": "client",
            "legacy_flag": "--ui gui|cli",
            "replacement_flag": "--mode rendered|cli",
            "replacement_value": "rendered|cli",
            "status": "supported_with_warning",
            "message_key": FLAG_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy client UI mode aliases remain supported during AppShell convergence.",
                replacement_target="Remove legacy client --ui aliases after AppShell convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
        {
            "shim_id": "shim.flag.legacy_server_ui",
            "product_id": "server",
            "legacy_flag": "--ui headless|cli",
            "replacement_flag": "--mode headless|cli",
            "replacement_value": "headless|cli",
            "status": "supported_with_warning",
            "message_key": FLAG_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy server UI mode aliases remain supported during AppShell convergence.",
                replacement_target="Remove legacy server --ui aliases after AppShell convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
        {
            "shim_id": "shim.flag.legacy_portable",
            "product_id": "*",
            "legacy_flag": "--portable",
            "replacement_flag": "--install-root",
            "replacement_value": "<portable adjacency root>",
            "status": "supported_with_warning",
            "message_key": FLAG_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy portable mode hints remain supported while install discovery converges.",
                replacement_target="Remove legacy --portable after install discovery convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
        {
            "shim_id": "shim.flag.legacy_no_gui",
            "product_id": "*",
            "legacy_flag": "--no-gui",
            "replacement_flag": "--mode",
            "replacement_value": "tui|cli",
            "status": "supported_with_warning",
            "message_key": FLAG_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy no-GUI toggles remain supported while deterministic UI mode selection converges.",
                replacement_target="Remove legacy --no-gui after UI mode convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
    )
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _has_flag(args: Iterable[object], flag: str) -> bool:
    target = _token(flag)
    return any(_token(token) == target for token in list(args or []))


def _remove_flag(args: Iterable[object], flag: str) -> list[str]:
    target = _token(flag)
    return [str(token) for token in list(args or []) if _token(token) != target]


def _has_flag_with_value(args: Iterable[object], *flags: str) -> bool:
    tokens = [_token(token) for token in list(args or [])]
    targets = {_token(flag) for flag in flags}
    for index, token in enumerate(tokens):
        if token in targets and index + 1 < len(tokens) and _token(tokens[index + 1]):
            return True
    return False


def _portable_warning_row(executable_path: str) -> dict:
    exe_dir = os.path.dirname(os.path.normpath(os.path.abspath(_token(executable_path) or "."))).replace("\\", "/")
    return {
        "shim_id": "shim.flag.legacy_portable",
        "legacy_flag": "--portable",
        "replacement_flag": "--install-root",
        "replacement_value": exe_dir or "<portable adjacency root>",
        "message_key": FLAG_WARNING_KEY,
        "message": "legacy --portable is deprecated; use --install-root <portable adjacency root>",
        "sunset_target": SHIM_SUNSET_TARGET,
    }


def _no_gui_mode(product_id: str, repo_root: str) -> str:
    supported = list(supported_modes_for_product(_token(product_id), repo_root=repo_root))
    if "tui" in supported:
        return "tui"
    if "cli" in supported:
        return "cli"
    return _token(supported[0] if supported else "cli") or "cli"


def legacy_flag_rows() -> list[dict]:
    return [dict(row) for row in FLAG_SHIM_ROWS]


def apply_flag_shims(
    *,
    product_id: str,
    raw_args: Iterable[object],
    repo_root: str,
    executable_path: str,
) -> dict:
    args = [str(token) for token in list(raw_args or [])]
    warnings: list[dict] = []

    if _has_flag(args, "--portable"):
        args = _remove_flag(args, "--portable")
        warning = _portable_warning_row(executable_path)
        manifest_path = os.path.join(os.path.dirname(os.path.normpath(os.path.abspath(_token(executable_path) or "."))), "install.manifest.json")
        if not _has_flag_with_value(args, "--install-root", "--install-id") and os.path.isfile(manifest_path):
            args = ["--install-root", os.path.dirname(os.path.normpath(os.path.abspath(manifest_path)))] + list(args)
        warnings.append(warning)

    if _has_flag(args, "--no-gui"):
        args = _remove_flag(args, "--no-gui")
        if not _has_flag_with_value(args, "--mode") and not _has_flag_with_value(args, "--ui"):
            mode_id = _no_gui_mode(_token(product_id), os.path.normpath(os.path.abspath(repo_root or ".")))
            args = ["--mode", mode_id] + list(args)
        else:
            mode_id = ""
        warnings.append(
            {
                "shim_id": "shim.flag.legacy_no_gui",
                "legacy_flag": "--no-gui",
                "replacement_flag": "--mode",
                "replacement_value": mode_id or "tui|cli",
                "message_key": FLAG_WARNING_KEY,
                "message": "legacy --no-gui is deprecated; use --mode tui or --mode cli",
                "sunset_target": SHIM_SUNSET_TARGET,
            }
        )

    return {
        "result": "complete",
        "raw_args": list(args),
        "warnings": [dict(row) for row in warnings],
        "deterministic_fingerprint": canonical_sha256(
            {
                "product_id": _token(product_id),
                "raw_args": list(args),
                "warnings": [dict(row) for row in warnings],
            }
        ),
    }


from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


__all__ = [
    "FLAG_SHIM_ROWS",
    "FLAG_WARNING_KEY",
    "apply_flag_shims",
    "legacy_flag_rows",
]
