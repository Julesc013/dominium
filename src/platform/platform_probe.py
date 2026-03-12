"""Deterministic platform capability probing and descriptor emission."""

from __future__ import annotations

import importlib.util
import json
import os
import socket
import sys
from typing import Iterable, Mapping

from ._canonical import canonical_sha256
from .platform_window import detect_platform_id


PLATFORM_CAPABILITY_REGISTRY_REL = os.path.join("data", "registries", "platform_capability_registry.json")
PLATFORM_ID_WIN9X = "platform.win9x"
PLATFORM_ID_WINNT = "platform.winnt"
PLATFORM_ID_MACOS_CLASSIC = "platform.macos_classic"
PLATFORM_ID_MACOS_COCOA = "platform.macos_cocoa"
PLATFORM_ID_LINUX_GTK = "platform.linux_gtk"
PLATFORM_ID_POSIX_MIN = "platform.posix_min"
PLATFORM_ID_SDL_STUB = "platform.sdl_stub"
PLATFORM_ID_ORDER = (
    PLATFORM_ID_WIN9X,
    PLATFORM_ID_WINNT,
    PLATFORM_ID_MACOS_CLASSIC,
    PLATFORM_ID_MACOS_COCOA,
    PLATFORM_ID_LINUX_GTK,
    PLATFORM_ID_POSIX_MIN,
    PLATFORM_ID_SDL_STUB,
)
PLATFORM_CAPABILITY_KEYS = (
    "cap.ui.os_native",
    "cap.ui.rendered",
    "cap.ui.tui",
    "cap.ui.cli",
    "cap.ipc.local_socket",
    "cap.ipc.named_pipe",
    "cap.fs.symlink",
    "cap.renderer.null",
    "cap.renderer.software",
    "cap.renderer.opengl",
    "cap.renderer.directx",
    "cap.renderer.vulkan",
    "cap.renderer.metal",
)
UI_CAPABILITY_KEYS = (
    "cap.ui.os_native",
    "cap.ui.rendered",
    "cap.ui.tui",
    "cap.ui.cli",
)
MODE_TO_CAPABILITY_ID = {
    "os_native": "cap.ui.os_native",
    "rendered": "cap.ui.rendered",
    "tui": "cap.ui.tui",
    "cli": "cap.ui.cli",
}
PLATFORM_ALIASES = {
    "classic": PLATFORM_ID_MACOS_CLASSIC,
    "cocoa": PLATFORM_ID_MACOS_COCOA,
    "darwin": PLATFORM_ID_MACOS_COCOA,
    "gtk": PLATFORM_ID_LINUX_GTK,
    "linux": PLATFORM_ID_LINUX_GTK,
    "mac": PLATFORM_ID_MACOS_COCOA,
    "macos": PLATFORM_ID_MACOS_COCOA,
    "macos_classic": PLATFORM_ID_MACOS_CLASSIC,
    "macos_cocoa": PLATFORM_ID_MACOS_COCOA,
    "osx": PLATFORM_ID_MACOS_COCOA,
    "platform.linux_gtk": PLATFORM_ID_LINUX_GTK,
    "platform.macos_classic": PLATFORM_ID_MACOS_CLASSIC,
    "platform.macos_cocoa": PLATFORM_ID_MACOS_COCOA,
    "platform.posix_min": PLATFORM_ID_POSIX_MIN,
    "platform.sdl_stub": PLATFORM_ID_SDL_STUB,
    "platform.win9x": PLATFORM_ID_WIN9X,
    "platform.winnt": PLATFORM_ID_WINNT,
    "posix": PLATFORM_ID_POSIX_MIN,
    "sdl": PLATFORM_ID_SDL_STUB,
    "win": PLATFORM_ID_WINNT,
    "win9x": PLATFORM_ID_WIN9X,
    "windows": PLATFORM_ID_WINNT,
    "windows9x": PLATFORM_ID_WIN9X,
    "winnt": PLATFORM_ID_WINNT,
}
_WINDOWS_NATIVE_MARKERS = {
    "*": ("src/platform/native_win32_adapter.py",),
    "client": ("src/client/ui/native_win32_adapter.py",),
    "launcher": ("tools/launcher/ui/native_win32_adapter.py",),
    "setup": ("tools/setup/ui/native_win32_adapter.py",),
}
_MACOS_NATIVE_MARKERS = {
    "*": ("src/platform/native_cocoa_adapter.py",),
    "client": ("src/client/ui/native_cocoa_adapter.py",),
    "launcher": ("tools/launcher/ui/native_cocoa_adapter.py",),
    "setup": ("tools/setup/ui/native_cocoa_adapter.py",),
}
_LINUX_NATIVE_MARKERS = {
    "*": ("src/platform/native_gtk_adapter.py",),
    "client": ("src/client/ui/native_gtk_adapter.py",),
    "launcher": ("tools/launcher/ui/native_gtk_adapter.py",),
    "setup": ("tools/setup/ui/native_gtk_adapter.py",),
}
_RENDERED_MARKERS = (
    "src/client/render/render_model_adapter.py",
    "src/client/render/renderers/software_renderer.py",
)
_SOFTWARE_RENDERER_MARKERS = (
    "src/client/render/renderers/software_renderer.py",
    "src/client/render/render_model_adapter.py",
)
_OPENGL_RENDERER_MARKERS = (
    "src/client/render/renderers/hw_renderer_gl.py",
    "src/platform/platform_gfx.py",
)
_DIRECTX_RENDERER_MARKERS = (
    "src/client/render/renderers/hw_renderer_dx.py",
    "src/platform/renderers/hw_renderer_dx.py",
)
_VULKAN_RENDERER_MARKERS = (
    "src/client/render/renderers/hw_renderer_vk.py",
    "src/platform/renderers/hw_renderer_vk.py",
)
_METAL_RENDERER_MARKERS = (
    "src/client/render/renderers/hw_renderer_metal.py",
    "src/platform/renderers/hw_renderer_metal.py",
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


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _ordered_tokens(values: Iterable[object]) -> list[str]:
    out: list[str] = []
    for item in list(values or []):
        token = _token(item)
        if token and token not in out:
            out.append(token)
    return out


def _platform_sort_key(platform_id: str) -> tuple[int, int | str]:
    token = canonical_platform_id(platform_id)
    if token in PLATFORM_ID_ORDER:
        return (0, PLATFORM_ID_ORDER.index(token))
    return (1, _token(platform_id))


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, path.replace("\\", "/")
    if not isinstance(payload, dict):
        return {}, path.replace("\\", "/")
    return dict(payload), ""


def _repo_root(repo_root: str) -> str:
    return os.path.normpath(os.path.abspath(_token(repo_root) or "."))


def _repo_has_any(repo_root: str, rel_paths: Iterable[str]) -> bool:
    root = _repo_root(repo_root)
    for rel_path in list(rel_paths or []):
        abs_path = os.path.join(root, str(rel_path).replace("/", os.sep))
        if os.path.isfile(abs_path):
            return True
    return False


def _normalize_platform_row(row: Mapping[str, object] | None) -> dict:
    payload = _as_map(row)
    normalized = {
        "platform_id": _token(payload.get("platform_id")),
        "display_name": _token(payload.get("display_name")),
        "os_family_id": _token(payload.get("os_family_id")),
        "support_tier": _token(payload.get("support_tier")),
        "extensions": _as_map(payload.get("extensions")),
        "stability": _as_map(payload.get("stability")),
        "deterministic_fingerprint": _token(payload.get("deterministic_fingerprint")),
    }
    for capability_id in PLATFORM_CAPABILITY_KEYS:
        normalized[capability_id] = bool(payload.get(capability_id, False))
    if not normalized["deterministic_fingerprint"]:
        normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def load_platform_capability_registry(repo_root: str) -> tuple[dict, str]:
    payload, error = _read_json(os.path.join(_repo_root(repo_root), PLATFORM_CAPABILITY_REGISTRY_REL))
    if error:
        return {}, error
    record = _as_map(payload.get("record"))
    entries = []
    for row in sorted(_as_list(record.get("entries")), key=lambda item: _platform_sort_key(_token(_as_map(item).get("platform_id")))):
        if not isinstance(row, Mapping):
            continue
        entries.append(_normalize_platform_row(row))
    record["entries"] = entries
    record_fingerprint = _token(record.get("deterministic_fingerprint"))
    if not record_fingerprint:
        record["deterministic_fingerprint"] = canonical_sha256(dict(record, deterministic_fingerprint=""))
    return {
        "schema_id": _token(payload.get("schema_id")),
        "schema_version": _token(payload.get("schema_version")) or "1.0.0",
        "record": record,
    }, ""


def platform_capability_rows_by_id(repo_root: str) -> tuple[dict[str, dict], str]:
    payload, error = load_platform_capability_registry(repo_root)
    if error:
        return {}, error
    out: dict[str, dict] = {}
    for row in _as_list(_as_map(payload.get("record")).get("entries")):
        row_map = _as_map(row)
        platform_id = _token(row_map.get("platform_id"))
        if platform_id:
            out[platform_id] = row_map
    return dict((key, out[key]) for key in sorted(out.keys())), ""


def canonical_platform_id(platform_id: str = "") -> str:
    token = _token(platform_id).lower()
    if token in PLATFORM_ALIASES:
        return PLATFORM_ALIASES[token]
    if token in PLATFORM_ID_ORDER:
        return token
    coarse = detect_platform_id(token)
    if coarse == "windows":
        return PLATFORM_ID_WINNT
    if coarse == "macos":
        return PLATFORM_ID_MACOS_COCOA
    if coarse == "linux":
        return PLATFORM_ID_LINUX_GTK
    if os.name == "posix":
        return PLATFORM_ID_POSIX_MIN
    return PLATFORM_ID_POSIX_MIN


def platform_family_id(platform_id: str) -> str:
    token = canonical_platform_id(platform_id)
    if token in (PLATFORM_ID_WIN9X, PLATFORM_ID_WINNT):
        return "windows"
    if token in (PLATFORM_ID_MACOS_CLASSIC, PLATFORM_ID_MACOS_COCOA):
        return "macos"
    if token == PLATFORM_ID_LINUX_GTK:
        return "linux"
    if token == PLATFORM_ID_SDL_STUB:
        return "sdl"
    return "posix"


def _product_native_markers(platform_id: str, product_id: str) -> tuple[str, ...]:
    family = platform_family_id(platform_id)
    product_token = _token(product_id)
    if family == "windows":
        rows = _WINDOWS_NATIVE_MARKERS
    elif family == "macos":
        rows = _MACOS_NATIVE_MARKERS
    elif family == "linux":
        rows = _LINUX_NATIVE_MARKERS
    else:
        rows = {}
    return tuple(list(rows.get("*", ())) + list(rows.get(product_token, ())))


def _isatty(handle: object) -> bool:
    try:
        return bool(handle.isatty())
    except Exception:
        return False


def _ncurses_runtime_available() -> bool:
    return importlib.util.find_spec("curses") is not None


def _windows_console_window_present(platform_id: str) -> bool:
    if platform_family_id(platform_id) != "windows":
        return False
    try:
        import ctypes

        kernel32 = getattr(ctypes, "windll").kernel32
        return bool(kernel32.GetConsoleWindow())
    except Exception:
        return False


def _macos_cocoa_runtime_available(platform_id: str) -> bool:
    if canonical_platform_id(platform_id) != PLATFORM_ID_MACOS_COCOA:
        return False
    if importlib.util.find_spec("AppKit") is not None:
        return True
    env = os.environ
    return bool(_token(env.get("TERM_PROGRAM")) or _token(env.get("__CFBundleIdentifier")))


def _local_socket_runtime_available(platform_id: str) -> bool:
    if canonical_platform_id(platform_id) in (PLATFORM_ID_WIN9X, PLATFORM_ID_WINNT, PLATFORM_ID_MACOS_CLASSIC):
        return False
    return hasattr(socket, "AF_UNIX")


def _named_pipe_runtime_available(platform_id: str) -> bool:
    return canonical_platform_id(platform_id) == PLATFORM_ID_WINNT


def _symlink_runtime_available() -> bool:
    return hasattr(os, "symlink")


def _native_adapter_supported(repo_root: str, platform_id: str, product_id: str) -> bool:
    return _repo_has_any(repo_root, _product_native_markers(platform_id, product_id))


def _rendered_host_supported(repo_root: str, product_id: str) -> bool:
    if _token(product_id) != "client":
        return False
    return _repo_has_any(repo_root, _RENDERED_MARKERS)


def _renderer_flag(
    repo_root: str,
    *,
    marker_paths: Iterable[str],
    override: object,
    default: bool,
) -> bool:
    if override is not None:
        return _as_bool(override)
    if default is False:
        return False
    return _repo_has_any(repo_root, marker_paths)


def _supported_capability_flags(
    repo_root: str,
    *,
    platform_row: Mapping[str, object],
    platform_id: str,
    product_id: str,
    native_available: object,
    rendered_available: object,
    local_socket_available: object,
    named_pipe_available: object,
    symlink_available: object,
    renderer_overrides: Mapping[str, object] | None,
) -> dict[str, bool]:
    row = _as_map(platform_row)
    renderer_map = _as_map(renderer_overrides)
    return {
        "cap.ui.os_native": bool(row.get("cap.ui.os_native", False))
        and (
            _as_bool(native_available)
            if native_available is not None
            else _native_adapter_supported(repo_root, platform_id, product_id)
        ),
        "cap.ui.rendered": bool(row.get("cap.ui.rendered", False))
        and (
            _as_bool(rendered_available)
            if rendered_available is not None
            else _rendered_host_supported(repo_root, product_id)
        ),
        "cap.ui.tui": bool(row.get("cap.ui.tui", False)),
        "cap.ui.cli": bool(row.get("cap.ui.cli", False)),
        "cap.ipc.local_socket": bool(row.get("cap.ipc.local_socket", False))
        and (
            _as_bool(local_socket_available)
            if local_socket_available is not None
            else _local_socket_runtime_available(platform_id)
        ),
        "cap.ipc.named_pipe": bool(row.get("cap.ipc.named_pipe", False))
        and (
            _as_bool(named_pipe_available)
            if named_pipe_available is not None
            else _named_pipe_runtime_available(platform_id)
        ),
        "cap.fs.symlink": bool(row.get("cap.fs.symlink", False))
        and (
            _as_bool(symlink_available)
            if symlink_available is not None
            else _symlink_runtime_available()
        ),
        "cap.renderer.null": bool(row.get("cap.renderer.null", False)),
        "cap.renderer.software": bool(row.get("cap.renderer.software", False))
        and _renderer_flag(
            repo_root,
            marker_paths=_SOFTWARE_RENDERER_MARKERS,
            override=renderer_map.get("software"),
            default=True,
        ),
        "cap.renderer.opengl": bool(row.get("cap.renderer.opengl", False))
        and _renderer_flag(
            repo_root,
            marker_paths=_OPENGL_RENDERER_MARKERS,
            override=renderer_map.get("opengl"),
            default=True,
        ),
        "cap.renderer.directx": bool(row.get("cap.renderer.directx", False))
        and _renderer_flag(
            repo_root,
            marker_paths=_DIRECTX_RENDERER_MARKERS,
            override=renderer_map.get("directx"),
            default=False,
        ),
        "cap.renderer.vulkan": bool(row.get("cap.renderer.vulkan", False))
        and _renderer_flag(
            repo_root,
            marker_paths=_VULKAN_RENDERER_MARKERS,
            override=renderer_map.get("vulkan"),
            default=False,
        ),
        "cap.renderer.metal": bool(row.get("cap.renderer.metal", False))
        and _renderer_flag(
            repo_root,
            marker_paths=_METAL_RENDERER_MARKERS,
            override=renderer_map.get("metal"),
            default=False,
        ),
    }


def _gui_environment_available(
    *,
    platform_id: str,
    tty_present: bool,
    gui_available: object,
    console_window_present: object,
    cocoa_available: object,
    env_map: Mapping[str, object],
) -> tuple[bool, bool, bool, bool, bool]:
    platform_token = canonical_platform_id(platform_id)
    display_present = bool(_token(env_map.get("DISPLAY")))
    wayland_present = bool(_token(env_map.get("WAYLAND_DISPLAY")))
    windows_console = (
        _as_bool(console_window_present)
        if console_window_present is not None
        else _windows_console_window_present(platform_token)
    )
    cocoa_runtime = (
        _as_bool(cocoa_available)
        if cocoa_available is not None
        else _macos_cocoa_runtime_available(platform_token)
    )
    if gui_available is not None:
        gui_environment = _as_bool(gui_available)
    elif platform_token in (PLATFORM_ID_WIN9X, PLATFORM_ID_WINNT):
        gui_environment = not tty_present or not windows_console
    elif platform_token == PLATFORM_ID_MACOS_COCOA:
        gui_environment = bool(cocoa_runtime)
    elif platform_token == PLATFORM_ID_LINUX_GTK:
        gui_environment = bool(display_present or wayland_present)
    elif platform_token == PLATFORM_ID_SDL_STUB:
        gui_environment = not tty_present
    else:
        gui_environment = False
    return gui_environment, display_present, wayland_present, windows_console, cocoa_runtime


def _available_mode_flags(
    *,
    supported_flags: Mapping[str, object],
    tty_present: bool,
    gui_environment_available: bool,
    ncurses_available: object,
) -> tuple[dict[str, bool], bool]:
    curses_present = _as_bool(ncurses_available) if ncurses_available is not None else _ncurses_runtime_available()
    flags = {
        "os_native": bool(supported_flags.get("cap.ui.os_native", False) and gui_environment_available),
        "rendered": bool(supported_flags.get("cap.ui.rendered", False) and gui_environment_available),
        "tui": bool(supported_flags.get("cap.ui.tui", False) and tty_present and curses_present),
        "cli": bool(supported_flags.get("cap.ui.cli", False)),
    }
    return flags, bool(curses_present)


def probe_platform_descriptor(
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
    local_socket_available: object = None,
    named_pipe_available: object = None,
    symlink_available: object = None,
    renderer_overrides: Mapping[str, object] | None = None,
) -> dict:
    repo_root_abs = _repo_root(repo_root)
    platform_token = canonical_platform_id(platform_id)
    rows_by_id, _error = platform_capability_rows_by_id(repo_root_abs)
    platform_row = _as_map(rows_by_id.get(platform_token))
    env_map = dict(env or os.environ)
    stdin_is_tty = _as_bool(stdin_tty, _isatty(sys.stdin)) if stdin_tty is not None else _isatty(sys.stdin)
    stdout_is_tty = _as_bool(stdout_tty, _isatty(sys.stdout)) if stdout_tty is not None else _isatty(sys.stdout)
    stderr_is_tty = _as_bool(stderr_tty, _isatty(sys.stderr)) if stderr_tty is not None else _isatty(sys.stderr)
    tty_present = bool(stdin_is_tty or stdout_is_tty or stderr_is_tty)
    gui_environment, display_present, wayland_present, windows_console, cocoa_runtime = _gui_environment_available(
        platform_id=platform_token,
        tty_present=tty_present,
        gui_available=gui_available,
        console_window_present=console_window_present,
        cocoa_available=cocoa_available,
        env_map=env_map,
    )
    supported_flags = _supported_capability_flags(
        repo_root_abs,
        platform_row=platform_row,
        platform_id=platform_token,
        product_id=_token(product_id),
        native_available=native_available,
        rendered_available=rendered_available,
        local_socket_available=local_socket_available,
        named_pipe_available=named_pipe_available,
        symlink_available=symlink_available,
        renderer_overrides=renderer_overrides,
    )
    available_mode_flags, curses_present = _available_mode_flags(
        supported_flags=supported_flags,
        tty_present=tty_present,
        gui_environment_available=gui_environment,
        ncurses_available=ncurses_available,
    )
    if tty_present:
        context_kind = "tty"
    elif gui_environment:
        context_kind = "gui"
    else:
        context_kind = "headless"
    supported_mode_ids = [
        mode_id
        for mode_id in ("os_native", "rendered", "tui", "cli")
        if bool(supported_flags.get(MODE_TO_CAPABILITY_ID[mode_id], False))
    ]
    available_mode_ids = [
        mode_id
        for mode_id in ("os_native", "rendered", "tui", "cli")
        if bool(available_mode_flags.get(mode_id, False))
    ]
    renderer_backend_ids = [
        backend_id
        for backend_id, capability_id in (
            ("null", "cap.renderer.null"),
            ("software", "cap.renderer.software"),
            ("opengl", "cap.renderer.opengl"),
            ("directx", "cap.renderer.directx"),
            ("vulkan", "cap.renderer.vulkan"),
            ("metal", "cap.renderer.metal"),
        )
        if bool(supported_flags.get(capability_id, False))
    ]
    payload = {
        "result": "complete",
        "schema_version": "1.0.0",
        "platform_id": platform_token,
        "platform_family_id": platform_family_id(platform_token),
        "product_id": _token(product_id),
        "display_name": _token(platform_row.get("display_name")),
        "support_tier": _token(platform_row.get("support_tier")),
        "context_kind": context_kind,
        "stdin_tty": bool(stdin_is_tty),
        "stdout_tty": bool(stdout_is_tty),
        "stderr_tty": bool(stderr_is_tty),
        "tty_present": bool(tty_present),
        "gui_environment_available": bool(gui_environment),
        "display_present": bool(display_present),
        "wayland_present": bool(wayland_present),
        "windows_console_window_present": bool(windows_console),
        "cocoa_runtime_available": bool(cocoa_runtime),
        "ncurses_runtime_available": bool(curses_present),
        "supported_capability_flags": dict((key, bool(supported_flags.get(key, False))) for key in PLATFORM_CAPABILITY_KEYS),
        "supported_capability_ids": _ordered_tokens(
            capability_id for capability_id in PLATFORM_CAPABILITY_KEYS if bool(supported_flags.get(capability_id, False))
        ),
        "supported_mode_ids": list(supported_mode_ids),
        "available_modes": dict((key, bool(available_mode_flags.get(key, False))) for key in ("os_native", "rendered", "tui", "cli")),
        "available_mode_ids": list(available_mode_ids),
        "ipc_transport_ids": _ordered_tokens(
            transport_id
            for transport_id, capability_id in (
                ("local_socket", "cap.ipc.local_socket"),
                ("named_pipe", "cap.ipc.named_pipe"),
            )
            if bool(supported_flags.get(capability_id, False))
        ),
        "renderer_backend_ids": list(renderer_backend_ids),
        "platform_registry_row_hash": canonical_sha256(platform_row) if platform_row else "",
        "detection_methods": {
            "platform_family": "sys.platform alias resolution",
            "tty": "sys.std*.isatty",
            "windows_gui": "GetConsoleWindow heuristic",
            "posix_gui": "DISPLAY or WAYLAND_DISPLAY",
            "macos_gui": "Cocoa import/env heuristic",
            "native_adapter": "repo marker lookup",
            "rendered_host": "render host marker lookup",
            "tui_runtime": "curses import",
            "ipc_local_socket": "socket.AF_UNIX availability",
            "ipc_named_pipe": "Windows NT family mapping",
            "fs_symlink": "os.symlink availability",
            "renderer_backends": "renderer marker lookup",
        },
        "extensions": {
            "registry_rel": PLATFORM_CAPABILITY_REGISTRY_REL.replace("\\", "/"),
            "registry_row": dict(platform_row),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def project_feature_capabilities_for_platform(
    feature_capabilities: Iterable[object] | None,
    *,
    platform_descriptor: Mapping[str, object] | None,
) -> list[str]:
    descriptor = _as_map(platform_descriptor)
    supported = set(_ordered_tokens(_as_list(descriptor.get("supported_capability_ids"))))
    out: list[str] = []
    for capability_id in _ordered_tokens(feature_capabilities):
        if capability_id in UI_CAPABILITY_KEYS and capability_id not in supported:
            continue
        out.append(capability_id)
    return out


__all__ = [
    "MODE_TO_CAPABILITY_ID",
    "PLATFORM_CAPABILITY_KEYS",
    "PLATFORM_CAPABILITY_REGISTRY_REL",
    "PLATFORM_ID_LINUX_GTK",
    "PLATFORM_ID_MACOS_CLASSIC",
    "PLATFORM_ID_MACOS_COCOA",
    "PLATFORM_ID_ORDER",
    "PLATFORM_ID_POSIX_MIN",
    "PLATFORM_ID_SDL_STUB",
    "PLATFORM_ID_WIN9X",
    "PLATFORM_ID_WINNT",
    "UI_CAPABILITY_KEYS",
    "canonical_platform_id",
    "load_platform_capability_registry",
    "platform_capability_rows_by_id",
    "platform_family_id",
    "probe_platform_descriptor",
    "project_feature_capabilities_for_platform",
]
