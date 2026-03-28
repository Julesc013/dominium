"""Deterministic helpers for UI-RECONCILE-0 reporting and enforcement."""

from __future__ import annotations

import ast
import glob
import json
import os
import sys
from typing import Iterable, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from engine.platform.platform_probe import probe_platform_descriptor  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


UI_ADAPTER_CONTRACT_PATH = "docs/ui/UI_ADAPTER_CONTRACT.md"
UI_SURFACE_MAP_PATH = "docs/audit/UI_SURFACE_MAP.md"
UI_RECONCILE_FINAL_PATH = "docs/audit/UI_RECONCILE_FINAL.md"
UI_SURFACE_REPORT_PATH = "data/audit/ui_surface_report.json"

_GOVERNED_SURFACES = (
    {
        "path": "ui/ui_model.py",
        "surface_kind": "shared_ui_model",
        "status": "governed_active",
        "purpose": "Shared menu/navigation model over AppShell command descriptors and LIB manifests.",
        "product_scope": "client,launcher,setup,server,engine,game,tool.attach_console_stub",
    },
    {
        "path": "client/ui/main_menu_surface.py",
        "surface_kind": "rendered_menu_surface",
        "status": "governed_active",
        "purpose": "Derived rendered main-menu surface for client menu flows.",
        "product_scope": "client",
    },
    {
        "path": "client/ui/viewer_shell.py",
        "surface_kind": "rendered_view_surface",
        "status": "governed_active",
        "purpose": "Derived rendered viewer shell over map, inspection, sky, water, and orbit artifacts.",
        "product_scope": "client",
    },
    {
        "path": "client/ui/map_views.py",
        "surface_kind": "derived_view_surface",
        "status": "governed_active",
        "purpose": "Derived map view artifacts for client and TUI map surfaces.",
        "product_scope": "client",
    },
    {
        "path": "client/ui/inspect_panels.py",
        "surface_kind": "derived_view_surface",
        "status": "governed_active",
        "purpose": "Derived inspect panels over perceived/inspection artifacts.",
        "product_scope": "client",
    },
    {
        "path": "appshell/tui/tui_engine.py",
        "surface_kind": "tui_adapter",
        "status": "governed_active",
        "purpose": "AppShell TUI adapter over command engine, logs, and derived surfaces.",
        "product_scope": "client,engine,game,launcher,server,setup,tool.attach_console_stub",
    },
    {
        "path": "appshell/rendered_stub.py",
        "surface_kind": "rendered_adapter",
        "status": "governed_active",
        "purpose": "Rendered-mode adapter that exposes the shared client main-menu surface or a deterministic stub.",
        "product_scope": "client",
    },
)
_LEGACY_SURFACE_GLOBS = (
    "tools/launcher/ui/**/*.py",
    "tools/setup/ui/**/*.py",
    "tools/ui_shared/**/*",
    "tools/ui_preview_host/**/*",
    "tools/tool_editor/ui/**/*",
    "tools/editor_gui/**/*",
    "tools/gui/**/*",
    "tools/xstack/sessionx/ui_host.py",
)
_COMMAND_SIGNAL_TOKENS = (
    "dispatch_registered_command(",
    "build_root_command_descriptors(",
)
_VIEW_ARTIFACT_TOKENS = (
    "build_map_view_set(",
    "build_inspection_panel_set(",
    "build_sky_view_surface(",
    "build_lighting_view_surface(",
    "build_water_view_surface(",
    "build_orbit_view_surface(",
)
_BUSINESS_LOGIC_TOKENS = (
    "build_runtime_bootstrap(",
    "start_local_singleplayer(",
    "run_local_server_ticks(",
    "request_local_server_control(",
    "execute_single_intent_srz(",
    "emit_product_descriptor(",
    "negotiate_product_endpoints(",
    "pack_verification_pipeline",
)
_FORBIDDEN_TRUTH_NAMES = {"truth_model", "universe_state", "process_runtime"}
_GOVERNED_ADAPTER_PATHS = {
    "appshell/tui/tui_engine.py",
    "appshell/rendered_stub.py",
    "client/ui/main_menu_surface.py",
}
_SHARED_UI_MODEL_REQUIRED_PATHS = {
    "appshell/tui/tui_engine.py": "build_ui_model(",
    "appshell/rendered_stub.py": "build_client_main_menu_surface(",
    "client/ui/main_menu_surface.py": "build_ui_model(",
}
_NATIVE_ADAPTER_MARKERS = (
    "src/platform/native_win32_adapter.py",
    "src/platform/native_cocoa_adapter.py",
    "src/platform/native_gtk_adapter.py",
    "src/client/ui/native_win32_adapter.py",
    "src/client/ui/native_cocoa_adapter.py",
    "src/client/ui/native_gtk_adapter.py",
    "tools/launcher/ui/native_win32_adapter.py",
    "tools/launcher/ui/native_cocoa_adapter.py",
    "tools/launcher/ui/native_gtk_adapter.py",
    "tools/setup/ui/native_win32_adapter.py",
    "tools/setup/ui/native_cocoa_adapter.py",
    "tools/setup/ui/native_gtk_adapter.py",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return _token(path).replace("\\", "/")


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or REPO_ROOT_HINT))


def _repo_abs(repo_root: str, rel_path: str) -> str:
    return os.path.normpath(os.path.abspath(os.path.join(repo_root, rel_path.replace("/", os.sep))))


def _file_text(repo_root: str, rel_path: str) -> str:
    try:
        with open(_repo_abs(repo_root, rel_path), "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_ast_names(text: str) -> set[str]:
    names: set[str] = set()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(str(node.id))
        elif isinstance(node, ast.arg):
            names.add(str(node.arg))
        elif isinstance(node, ast.Attribute):
            names.add(str(node.attr))
    return names


def _platform_dependency(rel_path: str) -> str:
    token = _norm(rel_path).lower()
    if any(part in token for part in ("win32", ".rc", "windows")):
        return "windows"
    if any(part in token for part in ("gtk", "linux", "posix")):
        return "linux"
    if any(part in token for part in ("cocoa", "macos")):
        return "macos"
    return "cross_platform"


def _legacy_status(rel_path: str) -> str:
    token = _norm(rel_path)
    if token.startswith("tools/ui_shared/") or token.startswith("tools/ui_preview_host/"):
        return "legacy_reference_only"
    if token.startswith("tools/xstack/sessionx/"):
        return "contradictory_legacy_host"
    return "deferred_native_or_preview"


def _legacy_purpose(rel_path: str) -> str:
    token = _norm(rel_path)
    if token.startswith("tools/ui_shared/"):
        return "Legacy cross-platform UI support library and adapter scaffolding."
    if token.startswith("tools/ui_preview_host/"):
        return "Preview host scaffolding for platform UI experiments."
    if token.startswith("tools/xstack/sessionx/"):
        return "Legacy headless UI host outside the governed AppShell runtime surface."
    if token.startswith("tools/launcher/ui/"):
        return "Launcher native UI scaffold kept outside the governed MVP runtime surface."
    if token.startswith("tools/setup/ui/"):
        return "Setup native UI scaffold kept outside the governed MVP runtime surface."
    if token.startswith("tools/tool_editor/ui/") or token.startswith("tools/editor_gui/") or token.startswith("tools/gui/"):
        return "Editor or tooling UI scaffold kept outside the governed MVP runtime surface."
    return "Legacy or preview UI surface pending post-MVP formalization."


def _surface_row(repo_root: str, *, rel_path: str, surface_kind: str, status: str, purpose: str, product_scope: str) -> dict:
    text = _file_text(repo_root, rel_path)
    ast_names = _read_ast_names(text)
    business_logic_signals = sorted(token for token in _BUSINESS_LOGIC_TOKENS if token in text)
    command_signals = sorted(token for token in _COMMAND_SIGNAL_TOKENS if token in text)
    view_artifact_signals = sorted(token for token in _VIEW_ARTIFACT_TOKENS if token in text)
    truth_names = sorted(name for name in ast_names if name in _FORBIDDEN_TRUTH_NAMES)
    payload = {
        "path": _norm(rel_path),
        "surface_kind": _token(surface_kind),
        "status": _token(status),
        "purpose": _token(purpose),
        "product_scope": _token(product_scope),
        "platform_dependency": _platform_dependency(rel_path),
        "uses_appshell_commands": bool(command_signals),
        "uses_shared_ui_model": bool(
            "build_ui_model(" in text
            or "build_client_main_menu_surface(" in text
            or _norm(rel_path) == "ui/ui_model.py"
        ),
        "reads_truth_directly": bool(truth_names),
        "truth_name_hits": truth_names,
        "calls_internal_logic": bool(business_logic_signals),
        "business_logic_signals": business_logic_signals,
        "view_artifact_signals": view_artifact_signals,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _legacy_surface_paths(repo_root: str) -> list[str]:
    root = _repo_root(repo_root)
    discovered: set[str] = set()
    for pattern in _LEGACY_SURFACE_GLOBS:
        abs_pattern = _repo_abs(root, pattern)
        for abs_path in glob.glob(abs_pattern, recursive=True):
            if os.path.isdir(abs_path):
                continue
            discovered.add(_norm(os.path.relpath(abs_path, root)))
    return sorted(discovered)


def _platform_row(repo_root: str, platform_id: str) -> dict:
    client_gui_probe = probe_platform_descriptor(
        repo_root,
        product_id="client",
        platform_id=platform_id,
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=True,
        native_available=None,
        rendered_available=None,
        ncurses_available=True,
    )
    launcher_gui_probe = probe_platform_descriptor(
        repo_root,
        product_id="launcher",
        platform_id=platform_id,
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=True,
        native_available=None,
        rendered_available=False,
        ncurses_available=True,
    )
    setup_gui_probe = probe_platform_descriptor(
        repo_root,
        product_id="setup",
        platform_id=platform_id,
        stdin_tty=False,
        stdout_tty=False,
        stderr_tty=False,
        gui_available=True,
        native_available=None,
        rendered_available=False,
        ncurses_available=True,
    )
    server_tty_probe = probe_platform_descriptor(
        repo_root,
        product_id="server",
        platform_id=platform_id,
        stdin_tty=True,
        stdout_tty=True,
        stderr_tty=True,
        gui_available=False,
        native_available=False,
        rendered_available=False,
        ncurses_available=True,
    )
    payload = {
        "platform_id": _token(platform_id),
        "client_rendered_available": bool(dict(client_gui_probe.get("available_modes") or {}).get("rendered", False)),
        "launcher_os_native_available": bool(dict(launcher_gui_probe.get("available_modes") or {}).get("os_native", False)),
        "setup_os_native_available": bool(dict(setup_gui_probe.get("available_modes") or {}).get("os_native", False)),
        "tui_available": bool(dict(server_tty_probe.get("available_modes") or {}).get("tui", False)),
        "cli_available": bool(dict(server_tty_probe.get("available_modes") or {}).get("cli", False)),
        "native_runtime_enabled": bool(
            dict(launcher_gui_probe.get("available_modes") or {}).get("os_native", False)
            or dict(setup_gui_probe.get("available_modes") or {}).get("os_native", False)
        ),
        "fallback_summary": (
            "native disabled -> rendered/TUI/CLI fallback"
            if not (
                dict(launcher_gui_probe.get("available_modes") or {}).get("os_native", False)
                or dict(setup_gui_probe.get("available_modes") or {}).get("os_native", False)
            )
            else "native adapter available for governed setup/launcher path"
        ),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def ui_reconcile_violations(repo_root: str) -> list[dict]:
    root = _repo_root(repo_root)
    violations: list[dict] = []
    for rel_path, rule_id, message in (
        ("ui/ui_model.py", "INV-UI-SHARES-UI_MODEL", "shared UI model is required"),
        (UI_ADAPTER_CONTRACT_PATH, "INV-UI-ADAPTERS-COMMAND-ONLY", "UI adapter contract documentation is required"),
        (UI_SURFACE_MAP_PATH, "INV-UI-SHARES-UI_MODEL", "UI surface map is required"),
        (UI_RECONCILE_FINAL_PATH, "INV-UI-SHARES-UI_MODEL", "UI reconcile final report is required"),
        ("tools/release/tool_run_ui_reconcile.py", "INV-UI-SHARES-UI_MODEL", "UI reconcile report tool is required"),
        ("tools/release/ui_reconcile_common.py", "INV-UI-SHARES-UI_MODEL", "UI reconcile helper module is required"),
        ("tools/auditx/analyzers/e477_business_logic_in_ui_adapter_smell.py", "INV-UI-ADAPTERS-COMMAND-ONLY", "BusinessLogicInUIAdapterSmell analyzer is required"),
        ("tools/auditx/analyzers/e478_truth_leak_in_ui_smell.py", "INV-NO-TRUTH-READ-IN-UI", "TruthLeakInUISmell analyzer is required"),
        ("tools/xstack/testx/tests/ui_reconcile_testlib.py", "INV-UI-SHARES-UI_MODEL", "UI reconcile TestX helper is required"),
        ("tools/xstack/testx/tests/test_ui_model_drives_main_menu_flow_via_commands.py", "INV-UI-SHARES-UI_MODEL", "UI model TestX coverage is required"),
        ("tools/xstack/testx/tests/test_native_adapter_only_calls_command_engine.py", "INV-UI-ADAPTERS-COMMAND-ONLY", "native adapter TestX coverage is required"),
        ("tools/xstack/testx/tests/test_rendered_menu_uses_ui_model.py", "INV-UI-SHARES-UI_MODEL", "rendered menu TestX coverage is required"),
        ("tools/xstack/testx/tests/test_ui_fallback_order_respected.py", "INV-UI-SHARES-UI_MODEL", "UI fallback order TestX coverage is required"),
    ):
        if os.path.isfile(_repo_abs(root, rel_path)):
            continue
        violations.append(
            {
                "code": "missing_required_surface",
                "rule_id": rule_id,
                "file_path": rel_path,
                "message": message,
            }
        )

    for rel_path, required_token in sorted(_SHARED_UI_MODEL_REQUIRED_PATHS.items()):
        text = _file_text(root, rel_path)
        if required_token in text:
            continue
        violations.append(
            {
                "code": "ui_missing_shared_model",
                "rule_id": "INV-UI-SHARES-UI_MODEL",
                "file_path": rel_path,
                "message": "governed UI surface must bind through the shared UI model or rendered menu surface",
            }
        )

    governed_rows = [
        _surface_row(
            root,
            rel_path=row["path"],
            surface_kind=row["surface_kind"],
            status=row["status"],
            purpose=row["purpose"],
            product_scope=row["product_scope"],
        )
        for row in _GOVERNED_SURFACES
        if os.path.isfile(_repo_abs(root, row["path"]))
    ]
    for row in governed_rows:
        rel_path = _token(row.get("path"))
        if rel_path in _GOVERNED_ADAPTER_PATHS and bool(row.get("calls_internal_logic", False)):
            violations.append(
                {
                    "code": "ui_adapter_business_logic",
                    "rule_id": "INV-UI-ADAPTERS-COMMAND-ONLY",
                    "file_path": rel_path,
                    "message": "governed UI adapter contains business-logic signals outside the command/view layer",
                }
            )
        if bool(row.get("reads_truth_directly", False)):
            violations.append(
                {
                    "code": "ui_truth_leak",
                    "rule_id": "INV-NO-TRUTH-READ-IN-UI",
                    "file_path": rel_path,
                    "message": "governed UI surface references forbidden truth names directly",
                }
            )

    for rel_path in sorted(path for path in _NATIVE_ADAPTER_MARKERS if os.path.isfile(_repo_abs(root, path))):
        text = _file_text(root, rel_path)
        if any(token in text for token in ("dispatch_registered_command(", "build_ui_model(", "build_client_main_menu_surface(")):
            continue
        violations.append(
            {
                "code": "native_adapter_not_command_only",
                "rule_id": "INV-UI-ADAPTERS-COMMAND-ONLY",
                "file_path": rel_path,
                "message": "governed native adapter must bind through command or shared UI model surfaces only",
            }
        )

    return sorted(
        violations,
        key=lambda row: (_token(row.get("rule_id")), _token(row.get("file_path")), _token(row.get("code"))),
    )


def build_ui_reconcile_report(repo_root: str) -> dict:
    root = _repo_root(repo_root)
    governed_rows = [
        _surface_row(
            root,
            rel_path=row["path"],
            surface_kind=row["surface_kind"],
            status=row["status"],
            purpose=row["purpose"],
            product_scope=row["product_scope"],
        )
        for row in _GOVERNED_SURFACES
        if os.path.isfile(_repo_abs(root, row["path"]))
    ]
    legacy_rows = [
        _surface_row(
            root,
            rel_path=rel_path,
            surface_kind="legacy_or_preview",
            status=_legacy_status(rel_path),
            purpose=_legacy_purpose(rel_path),
            product_scope="legacy_or_tooling",
        )
        for rel_path in _legacy_surface_paths(root)
    ]
    payload = {
        "result": "complete",
        "report_id": "ui.reconcile.v1",
        "governed_surfaces": sorted(governed_rows, key=lambda row: _token(row.get("path"))),
        "legacy_surfaces": sorted(legacy_rows, key=lambda row: _token(row.get("path"))),
        "platform_rows": [_platform_row(root, platform_id) for platform_id in ("windows", "macos", "linux")],
        "violations": ui_reconcile_violations(root),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def render_ui_surface_map(report: Mapping[str, object]) -> str:
    governed_rows = list(report.get("governed_surfaces") or [])
    legacy_rows = list(report.get("legacy_surfaces") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: release-pinned UI architecture inventory for convergence and platform formalization",
        "",
        "# UI Surface Map",
        "",
        "## Summary",
        "",
        "- governed_surface_count: `{}`".format(len(governed_rows)),
        "- legacy_surface_count: `{}`".format(len(legacy_rows)),
        "- fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Governed Runtime UI Surfaces",
        "",
        "| Path | Surface | Purpose | Platform | AppShell Commands | Shared UI Model | Truth Direct | Internal Logic |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in governed_rows:
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | {} | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row_map.get("path")),
                _token(row_map.get("surface_kind")),
                _token(row_map.get("purpose")),
                _token(row_map.get("platform_dependency")),
                "yes" if bool(row_map.get("uses_appshell_commands", False)) else "no",
                "yes" if bool(row_map.get("uses_shared_ui_model", False)) else "no",
                "yes" if bool(row_map.get("reads_truth_directly", False)) else "no",
                "yes" if bool(row_map.get("calls_internal_logic", False)) else "no",
            )
        )
    lines.extend(
        (
            "",
            "## Legacy / Deferred UI Surfaces",
            "",
            "| Path | Status | Purpose | Platform | AppShell Commands | Truth Direct | Internal Logic |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        )
    )
    for row in legacy_rows:
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | {} | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row_map.get("path")),
                _token(row_map.get("status")),
                _token(row_map.get("purpose")),
                _token(row_map.get("platform_dependency")),
                "yes" if bool(row_map.get("uses_appshell_commands", False)) else "no",
                "yes" if bool(row_map.get("reads_truth_directly", False)) else "no",
                "yes" if bool(row_map.get("calls_internal_logic", False)) else "no",
            )
        )
    return "\n".join(lines) + "\n"


def render_ui_reconcile_final(report: Mapping[str, object]) -> str:
    governed_rows = list(report.get("governed_surfaces") or [])
    legacy_rows = list(report.get("legacy_surfaces") or [])
    platform_rows = list(report.get("platform_rows") or [])
    violations = list(report.get("violations") or [])
    deferred_rows = [dict(row) for row in legacy_rows if _token(dict(row).get("status")) != "legacy_reference_only"]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: release-pinned UI architecture inventory for platform formalization",
        "",
        "# UI Reconcile Final",
        "",
        "## Current UI Surfaces",
        "",
        "- governed_runtime_surfaces: `{}`".format(len(governed_rows)),
        "- legacy_or_preview_surfaces: `{}`".format(len(legacy_rows)),
        "- violations: `{}`".format(len(violations)),
        "- fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Enabled By Platform",
        "",
        "| Platform | Client Rendered | Launcher Native | Setup Native | TUI | CLI | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in platform_rows:
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                _token(row_map.get("platform_id")),
                "yes" if bool(row_map.get("client_rendered_available", False)) else "no",
                "yes" if bool(row_map.get("launcher_os_native_available", False)) else "no",
                "yes" if bool(row_map.get("setup_os_native_available", False)) else "no",
                "yes" if bool(row_map.get("tui_available", False)) else "no",
                "yes" if bool(row_map.get("cli_available", False)) else "no",
                _token(row_map.get("fallback_summary")),
            )
        )
    lines.extend(("", "## Deferred", ""))
    if not deferred_rows:
        lines.append("- No deferred native adapters remain inside the current source tree.")
    else:
        for row in deferred_rows[:12]:
            row_map = dict(row or {})
            lines.append("- `{}` `{}`: {}".format(_token(row_map.get("path")), _token(row_map.get("status")), _token(row_map.get("purpose"))))
    lines.extend(("", "## Enforcement", ""))
    if not violations:
        lines.append("- No governed UI adapter violations were detected.")
    else:
        for row in violations:
            row_map = dict(row or {})
            lines.append(
                "- `{}` `{}`: {}".format(
                    _token(row_map.get("file_path")),
                    _token(row_map.get("code")),
                    _token(row_map.get("message")),
                )
            )
    lines.extend(
        (
            "",
            "## Readiness",
            "",
            "- Shared menu/navigation state is centralized in `ui/ui_model.py`.",
            "- Rendered and TUI adapters now bind through the shared model without changing the locked viewer-shell truth/view contract.",
            "- Governed native adapters remain capability-disabled until PLATFORM-FORMALIZE-0 provides concrete platform bindings.",
        )
    )
    return "\n".join(lines) + "\n"


def render_ui_reconcile_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        UI_SURFACE_MAP_PATH: render_ui_surface_map(report),
        UI_RECONCILE_FINAL_PATH: render_ui_reconcile_final(report),
    }


def write_ui_reconcile_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    root = _repo_root(repo_root)
    written: dict[str, str] = {}
    for rel_path, text in render_ui_reconcile_bundle(report).items():
        abs_path = _repo_abs(root, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = _norm(abs_path)
    json_abs = _repo_abs(root, UI_SURFACE_REPORT_PATH)
    os.makedirs(os.path.dirname(json_abs), exist_ok=True)
    with open(json_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(report), handle, indent=2, sort_keys=True)
        handle.write("\n")
    written[UI_SURFACE_REPORT_PATH] = _norm(json_abs)
    return dict(sorted(written.items()))


__all__ = [
    "UI_ADAPTER_CONTRACT_PATH",
    "UI_RECONCILE_FINAL_PATH",
    "UI_SURFACE_MAP_PATH",
    "UI_SURFACE_REPORT_PATH",
    "build_ui_reconcile_report",
    "render_ui_reconcile_bundle",
    "render_ui_reconcile_final",
    "render_ui_surface_map",
    "ui_reconcile_violations",
    "write_ui_reconcile_outputs",
]
