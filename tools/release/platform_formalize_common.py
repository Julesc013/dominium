"""Deterministic reporting and enforcement helpers for PLATFORM-FORMALIZE-0."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from compat import build_default_endpoint_descriptor  # noqa: E402
from engine.platform import (  # noqa: E402
    PLATFORM_ID_ORDER,
    load_platform_capability_registry,
    probe_platform_descriptor,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


PLATFORM_RENDERER_MATRIX_PATH = "docs/audit/PLATFORM_RENDERER_MATRIX.md"
PLATFORM_FORMALIZE_FINAL_PATH = "docs/audit/PLATFORM_FORMALIZE_FINAL.md"
PLATFORM_FORMALIZE_REPORT_PATH = "data/audit/platform_formalize_report.json"
PLATFORM_CAPABILITY_REGISTRY_PATH = "data/registries/platform_capability_registry.json"
PLATFORM_PROBE_PATH = "engine/platform/platform_probe.py"
PLATFORM_CAPS_PROBE_PATH = "engine/platform/platform_caps_probe.py"


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _bool_symbol(value: object) -> str:
    return "yes" if bool(value) else "no"


def _platform_matrix_row(repo_root: str, platform_id: str) -> dict:
    client_probe = probe_platform_descriptor(
        repo_root,
        product_id="client",
        platform_id=platform_id,
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=True,
        ncurses_available=True,
    )
    launcher_probe = probe_platform_descriptor(
        repo_root,
        product_id="launcher",
        platform_id=platform_id,
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=True,
        ncurses_available=True,
    )
    server_probe = probe_platform_descriptor(
        repo_root,
        product_id="server",
        platform_id=platform_id,
        stdin_tty=True,
        stdout_tty=True,
        stderr_tty=True,
        gui_available=False,
        ncurses_available=True,
    )
    row = _as_map(_as_map(client_probe.get("extensions")).get("registry_row"))
    return {
        "platform_id": _token(platform_id),
        "display_name": _token(row.get("display_name")),
        "support_tier": _token(row.get("support_tier")),
        "declared_ui": {
            "os_native": bool(row.get("cap.ui.os_native", False)),
            "rendered": bool(row.get("cap.ui.rendered", False)),
            "tui": bool(row.get("cap.ui.tui", False)),
            "cli": bool(row.get("cap.ui.cli", False)),
        },
        "declared_ipc": {
            "local_socket": bool(row.get("cap.ipc.local_socket", False)),
            "named_pipe": bool(row.get("cap.ipc.named_pipe", False)),
        },
        "declared_renderers": {
            "null": bool(row.get("cap.renderer.null", False)),
            "software": bool(row.get("cap.renderer.software", False)),
            "opengl": bool(row.get("cap.renderer.opengl", False)),
            "directx": bool(row.get("cap.renderer.directx", False)),
            "vulkan": bool(row.get("cap.renderer.vulkan", False)),
            "metal": bool(row.get("cap.renderer.metal", False)),
        },
        "client_supported_mode_ids": list(client_probe.get("supported_mode_ids") or []),
        "client_available_mode_ids": list(client_probe.get("available_mode_ids") or []),
        "client_renderer_backend_ids": list(client_probe.get("renderer_backend_ids") or []),
        "launcher_supported_mode_ids": list(launcher_probe.get("supported_mode_ids") or []),
        "launcher_available_mode_ids": list(launcher_probe.get("available_mode_ids") or []),
        "server_tty_available_mode_ids": list(server_probe.get("available_mode_ids") or []),
        "ipc_transport_ids": list(client_probe.get("ipc_transport_ids") or []),
        "platform_probe_fingerprint": _token(client_probe.get("deterministic_fingerprint")),
        "platform_registry_row_hash": _token(client_probe.get("platform_registry_row_hash")),
    }


def _host_probe_row(repo_root: str, product_id: str) -> dict:
    probe = probe_platform_descriptor(repo_root, product_id=product_id)
    return {
        "product_id": _token(product_id),
        "platform_id": _token(probe.get("platform_id")),
        "context_kind": _token(probe.get("context_kind")),
        "supported_mode_ids": list(probe.get("supported_mode_ids") or []),
        "available_mode_ids": list(probe.get("available_mode_ids") or []),
        "renderer_backend_ids": list(probe.get("renderer_backend_ids") or []),
        "ipc_transport_ids": list(probe.get("ipc_transport_ids") or []),
        "probe_fingerprint": _token(probe.get("deterministic_fingerprint")),
    }


def platform_formalize_violations(repo_root: str) -> list[dict]:
    violations: list[dict] = []
    selector_text = _file_text(repo_root, "appshell/ui_mode_selector.py")
    if "probe_platform_descriptor" not in selector_text:
        violations.append(
            {
                "code": "selector_not_using_platform_probe",
                "file_path": "appshell/ui_mode_selector.py",
                "message": "UI mode selector must resolve host capabilities through engine.platform.platform_probe.probe_platform_descriptor",
                "rule_id": "INV-UI-MODE-SELECTION-USES-PROBE",
            }
        )
    if "platform_caps_probe" in selector_text:
        violations.append(
            {
                "code": "legacy_probe_import_left_in_selector",
                "file_path": "appshell/ui_mode_selector.py",
                "message": "UI mode selector must not import the legacy platform_caps_probe wrapper directly",
                "rule_id": "INV-UI-MODE-SELECTION-USES-PROBE",
            }
        )
    if not os.path.isfile(os.path.join(repo_root, PLATFORM_CAPABILITY_REGISTRY_PATH.replace("/", os.sep))):
        violations.append(
            {
                "code": "platform_registry_missing",
                "file_path": PLATFORM_CAPABILITY_REGISTRY_PATH,
                "message": "Platform capability registry must exist",
                "rule_id": "INV-PLATFORM-CAPS-DECLARED",
            }
        )
        return violations

    payload, error = load_platform_capability_registry(repo_root)
    if error:
        violations.append(
            {
                "code": "platform_registry_unreadable",
                "file_path": PLATFORM_CAPABILITY_REGISTRY_PATH,
                "message": "Platform capability registry could not be read",
                "rule_id": "INV-PLATFORM-CAPS-DECLARED",
            }
        )
        return violations
    rows = list(_as_map(payload.get("record")).get("entries") or [])
    seen_ids = set()
    for row in rows:
        row_map = _as_map(row)
        platform_id = _token(row_map.get("platform_id"))
        if not platform_id:
            violations.append(
                {
                    "code": "platform_id_missing",
                    "file_path": PLATFORM_CAPABILITY_REGISTRY_PATH,
                    "message": "Each platform capability row must declare platform_id",
                    "rule_id": "INV-PLATFORM-CAPS-DECLARED",
                }
            )
            continue
        if platform_id in seen_ids:
            violations.append(
                {
                    "code": "platform_id_duplicate",
                    "file_path": PLATFORM_CAPABILITY_REGISTRY_PATH,
                    "message": "Platform capability registry must not contain duplicate platform ids",
                    "rule_id": "INV-PLATFORM-CAPS-DECLARED",
                }
            )
        seen_ids.add(platform_id)
        for capability_id in (
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
        ):
            if capability_id in row_map:
                continue
            violations.append(
                {
                    "code": "platform_capability_missing",
                    "file_path": PLATFORM_CAPABILITY_REGISTRY_PATH,
                    "message": "Platform capability row '{}' must declare '{}'".format(platform_id, capability_id),
                    "rule_id": "INV-PLATFORM-CAPS-DECLARED",
                }
            )

    descriptor = build_default_endpoint_descriptor(
        repo_root,
        product_id="client",
        product_version="0.0.0+platform_probe",
    )
    descriptor_extensions = _as_map(descriptor.get("extensions"))
    for key in ("official.platform_id", "official.platform_descriptor_hash", "official.platform_capability_ids", "official.platform_descriptor"):
        if key in descriptor_extensions:
            continue
        violations.append(
            {
                "code": "endpoint_descriptor_missing_platform_metadata",
                "file_path": "compat/capability_negotiation.py",
                "message": "Endpoint descriptors must include '{}'".format(key),
                "rule_id": "INV-PLATFORM-CAPS-DECLARED",
            }
        )
    return sorted(
        [dict(row) for row in violations],
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
    )


def build_platform_formalize_report(repo_root: str) -> dict:
    payload, error = load_platform_capability_registry(repo_root)
    registry_rows = list(_as_map(payload.get("record")).get("entries") or []) if not error else []
    matrix_rows = [_platform_matrix_row(repo_root, platform_id) for platform_id in PLATFORM_ID_ORDER]
    host_probe_rows = [_host_probe_row(repo_root, product_id) for product_id in ("client", "launcher", "setup", "server")]
    report = {
        "result": "complete" if not error else "refused",
        "report_id": "platform.formalize.v1",
        "registry_rows": [dict(row) for row in registry_rows],
        "matrix_rows": matrix_rows,
        "host_probe_rows": host_probe_rows,
        "violations": platform_formalize_violations(repo_root),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_platform_renderer_matrix(report: Mapping[str, object]) -> str:
    rows = list(report.get("matrix_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: APPSHELL",
        "Replacement Target: release-pinned platform adapter contracts and install discovery guarantees",
        "",
        "# Platform Renderer Matrix",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Declared vs Repo-Supported Matrix",
        "",
        "| Platform | Tier | Declared UI | Client Supported Modes | Client Available Modes (GUI) | Launcher Available Modes (GUI) | Server Available Modes (TTY) | Renderer Backends | IPC |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `native={}` `rendered={}` `tui={}` `cli={}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("platform_id")),
                _token(row.get("support_tier")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("os_native")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("rendered")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("tui")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("cli")),
                "`, `".join(_token(item) for item in list(row.get("client_supported_mode_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("client_available_mode_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("launcher_available_mode_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("server_tty_available_mode_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("client_renderer_backend_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("ipc_transport_ids") or [])) or "none",
            )
        )
    return "\n".join(lines) + "\n"


def render_platform_formalize_final(report: Mapping[str, object]) -> str:
    host_rows = list(report.get("host_probe_rows") or [])
    rows = list(report.get("matrix_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: APPSHELL",
        "Replacement Target: release-pinned platform adapter contracts and install discovery guarantees",
        "",
        "# Platform Formalize Final",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Supported Platforms",
        "",
        "| Platform | Tier | Declared Native | Declared Rendered | Declared TUI | Declared CLI |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("platform_id")),
                _token(row.get("support_tier")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("os_native")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("rendered")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("tui")),
                _bool_symbol(_as_map(row.get("declared_ui")).get("cli")),
            )
        )
    lines.extend(
        (
            "",
            "## Current Host Probe",
            "",
            "| Product | Platform | Context | Supported Modes | Available Modes | Renderers | IPC |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        )
    )
    for row in host_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("product_id")),
                _token(row.get("platform_id")),
                _token(row.get("context_kind")),
                "`, `".join(_token(item) for item in list(row.get("supported_mode_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("available_mode_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("renderer_backend_ids") or [])) or "none",
                "`, `".join(_token(item) for item in list(row.get("ipc_transport_ids") or [])) or "none",
            )
        )
    lines.extend(
        (
            "",
            "## Deferred Platforms",
            "",
            "- `platform.win9x` and `platform.macos_classic` remain subset targets with conservative capability declarations only.",
            "- `platform.sdl_stub` is declared for future portable windowing but does not claim an active adapter in the repo today.",
            "- DirectX, Vulkan, and Metal renderer capabilities remain declared `no` until concrete backends land.",
            "",
            "## Readiness",
            "",
            "- UI mode selection now depends on the canonical platform probe.",
            "- CAP-NEG endpoint descriptors include platform id, platform descriptor hash, and computed capability ids.",
            "- The platform matrix is ready for REPO-LAYOUT-0 virtual paths and INSTALL-DISCOVERY-0.",
        )
    )
    return "\n".join(lines) + "\n"


def render_platform_formalize_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        PLATFORM_RENDERER_MATRIX_PATH: render_platform_renderer_matrix(report),
        PLATFORM_FORMALIZE_FINAL_PATH: render_platform_formalize_final(report),
    }


def write_platform_formalize_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    written: dict[str, str] = {}
    root = os.path.normpath(os.path.abspath(repo_root))
    bundle = render_platform_formalize_bundle(report)
    for rel_path, text in bundle.items():
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = abs_path.replace("\\", "/")
    report_abs = os.path.join(root, PLATFORM_FORMALIZE_REPORT_PATH.replace("/", os.sep))
    os.makedirs(os.path.dirname(report_abs), exist_ok=True)
    with open(report_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(report), handle, indent=2, sort_keys=True)
        handle.write("\n")
    written[PLATFORM_FORMALIZE_REPORT_PATH] = report_abs.replace("\\", "/")
    return dict(sorted(written.items()))


__all__ = [
    "PLATFORM_CAPABILITY_REGISTRY_PATH",
    "PLATFORM_CAPS_PROBE_PATH",
    "PLATFORM_FORMALIZE_FINAL_PATH",
    "PLATFORM_FORMALIZE_REPORT_PATH",
    "PLATFORM_PROBE_PATH",
    "PLATFORM_RENDERER_MATRIX_PATH",
    "build_platform_formalize_report",
    "platform_formalize_violations",
    "write_platform_formalize_outputs",
]
