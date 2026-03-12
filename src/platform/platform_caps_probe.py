"""Deterministic platform capability probing for AppShell UI selection."""

from __future__ import annotations

import ctypes
import importlib.util
import os
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from .platform_window import detect_platform_id


_WINDOWS_NATIVE_MARKERS = (
    "src/platform/native_win32_adapter.py",
    "src/client/ui/native_win32_adapter.py",
    "tools/launcher/ui/native_win32_adapter.py",
    "tools/setup/ui/native_win32_adapter.py",
)
_MACOS_NATIVE_MARKERS = (
    "src/platform/native_cocoa_adapter.py",
    "src/client/ui/native_cocoa_adapter.py",
    "tools/launcher/ui/native_cocoa_adapter.py",
    "tools/setup/ui/native_cocoa_adapter.py",
)
_LINUX_NATIVE_MARKERS = (
    "src/platform/native_gtk_adapter.py",
    "src/client/ui/native_gtk_adapter.py",
    "tools/launcher/ui/native_gtk_adapter.py",
    "tools/setup/ui/native_gtk_adapter.py",
)
_RENDERED_MARKERS = (
    "src/client/render/render_model_adapter.py",
    "src/client/render/renderers/software_renderer.py",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, bool):
        return value
    token = _token(value).lower()
    if token in {"1", "true", "yes", "on"}:
        return True
    if token in {"0", "false", "no", "off"}:
        return False
    return bool(default)


def _repo_has_any(repo_root: str, rel_paths: tuple[str, ...]) -> bool:
    root = os.path.normpath(os.path.abspath(_token(repo_root) or "."))
    for rel_path in rel_paths:
        if os.path.isfile(os.path.join(root, rel_path.replace("/", os.sep))):
            return True
    return False


def _isatty(handle: object) -> bool:
    try:
        return bool(handle.isatty())
    except Exception:
        return False


def _ncurses_available() -> bool:
    return importlib.util.find_spec("curses") is not None


def _windows_console_window_present() -> bool:
    if detect_platform_id() != "windows":
        return False
    try:
        kernel32 = getattr(ctypes, "windll").kernel32
        return bool(kernel32.GetConsoleWindow())
    except Exception:
        return False


def _macos_cocoa_available() -> bool:
    if detect_platform_id() != "macos":
        return False
    if importlib.util.find_spec("AppKit") is not None:
        return True
    env = os.environ
    return bool(_token(env.get("TERM_PROGRAM")) or _token(env.get("__CFBundleIdentifier")))


def _native_adapter_present(repo_root: str, platform_id: str) -> bool:
    token = _token(platform_id)
    if token == "windows":
        return _repo_has_any(repo_root, _WINDOWS_NATIVE_MARKERS)
    if token == "macos":
        return _repo_has_any(repo_root, _MACOS_NATIVE_MARKERS)
    return _repo_has_any(repo_root, _LINUX_NATIVE_MARKERS)


def _rendered_host_present(repo_root: str, product_id: str) -> bool:
    if _token(product_id) != "client":
        return False
    return _repo_has_any(repo_root, _RENDERED_MARKERS)


def probe_platform_caps(
    repo_root: str,
    *,
    product_id: str,
    platform_id: str = "",
    env: Mapping[str, object] | None = None,
    stdin_tty: object = None,
    stdout_tty: object = None,
    stderr_tty: object = None,
    gui_available: object = None,
    native_available: object = None,
    rendered_available: object = None,
    ncurses_available: object = None,
    console_window_present: object = None,
    cocoa_available: object = None,
) -> dict:
    """Probe presentation-only platform/UI capabilities.

    Optional overrides keep tests deterministic and avoid host dependence.
    """

    repo_root_abs = os.path.normpath(os.path.abspath(_token(repo_root) or "."))
    platform_token = detect_platform_id(platform_id)
    env_map = dict(env or os.environ)
    stdin_is_tty = _as_bool(stdin_tty, _isatty(sys.stdin)) if stdin_tty is not None else _isatty(sys.stdin)
    stdout_is_tty = _as_bool(stdout_tty, _isatty(sys.stdout)) if stdout_tty is not None else _isatty(sys.stdout)
    stderr_is_tty = _as_bool(stderr_tty, _isatty(sys.stderr)) if stderr_tty is not None else _isatty(sys.stderr)
    tty_present = bool(stdin_is_tty or stdout_is_tty or stderr_is_tty)

    display_present = bool(_token(env_map.get("DISPLAY")))
    wayland_present = bool(_token(env_map.get("WAYLAND_DISPLAY")))
    windows_console = (
        _as_bool(console_window_present, _windows_console_window_present())
        if console_window_present is not None
        else _windows_console_window_present()
    )
    cocoa_runtime = (
        _as_bool(cocoa_available, _macos_cocoa_available())
        if cocoa_available is not None
        else _macos_cocoa_available()
    )
    if gui_available is not None:
        gui_environment_available = _as_bool(gui_available)
    elif platform_token == "windows":
        gui_environment_available = not tty_present or not windows_console
    elif platform_token == "macos":
        gui_environment_available = bool(cocoa_runtime)
    else:
        gui_environment_available = bool(display_present or wayland_present)

    native_adapter_available = (
        _as_bool(native_available, _native_adapter_present(repo_root_abs, platform_token))
        if native_available is not None
        else _native_adapter_present(repo_root_abs, platform_token)
    )
    rendered_host_available = (
        _as_bool(rendered_available, _rendered_host_present(repo_root_abs, product_id))
        if rendered_available is not None
        else _rendered_host_present(repo_root_abs, product_id)
    )
    ncurses_present = (
        _as_bool(ncurses_available, _ncurses_available())
        if ncurses_available is not None
        else _ncurses_available()
    )

    os_native_available = bool(gui_environment_available and native_adapter_available)
    rendered_ui_available = bool(gui_environment_available and rendered_host_available)
    tui_available = bool(tty_present and ncurses_present)
    cli_available = True
    if tty_present:
        context_kind = "tty"
    elif gui_environment_available:
        context_kind = "gui"
    else:
        context_kind = "headless"

    payload = {
        "result": "complete",
        "platform_id": platform_token,
        "product_id": _token(product_id),
        "context_kind": context_kind,
        "stdin_tty": bool(stdin_is_tty),
        "stdout_tty": bool(stdout_is_tty),
        "stderr_tty": bool(stderr_is_tty),
        "tty_present": bool(tty_present),
        "gui_environment_available": bool(gui_environment_available),
        "display_present": bool(display_present),
        "wayland_present": bool(wayland_present),
        "windows_console_window_present": bool(windows_console),
        "cocoa_runtime_available": bool(cocoa_runtime),
        "ncurses_available": bool(ncurses_present),
        "native_adapter_available": bool(native_adapter_available),
        "rendered_host_available": bool(rendered_host_available),
        "available_modes": {
            "os_native": bool(os_native_available),
            "rendered": bool(rendered_ui_available),
            "tui": bool(tui_available),
            "cli": bool(cli_available),
        },
        "available_mode_ids": [
            mode_id
            for mode_id in ("os_native", "rendered", "tui", "cli")
            if {
                "os_native": os_native_available,
                "rendered": rendered_ui_available,
                "tui": tui_available,
                "cli": cli_available,
            }[mode_id]
        ],
        "detection_methods": {
            "tty": "sys.std*.isatty",
            "windows_gui": "GetConsoleWindow heuristic",
            "posix_gui": "DISPLAY or WAYLAND_DISPLAY",
            "macos_gui": "Cocoa import/env heuristic",
            "tui": "curses import plus tty",
            "rendered": "client render host markers plus GUI context",
            "os_native": "platform adapter markers plus GUI context",
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = ["probe_platform_caps"]
