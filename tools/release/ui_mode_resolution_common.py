"""Deterministic reporting and enforcement helpers for APPSHELL-PLATFORM-1."""

from __future__ import annotations

import os
from typing import Mapping

from appshell.ui_mode_selector import load_ui_mode_policy_registry, select_ui_mode
from engine.platform.platform_probe import probe_platform_descriptor
from tools.xstack.compatx.canonical_json import canonical_sha256


UI_MODE_RESOLUTION_DOC_PATH = "docs/appshell/UI_MODE_RESOLUTION.md"
UI_MODE_RESOLUTION_BASELINE_PATH = "docs/audit/UI_MODE_RESOLUTION_BASELINE.md"
UI_MODE_RESOLUTION_TOOL_PATH = "tools/release/tool_run_ui_mode_resolution.py"


def _token(value: object) -> str:
    return str(value or "").strip()


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def build_test_probe(
    repo_root: str,
    *,
    product_id: str,
    platform_id: str = "linux",
    tty: bool,
    gui: bool,
    native: bool,
    rendered: bool,
    tui: bool,
) -> dict:
    return probe_platform_descriptor(
        repo_root,
        product_id=product_id,
        platform_id=platform_id,
        stdin_tty=tty,
        stdout_tty=tty,
        stderr_tty=tty,
        gui_available=gui,
        native_available=native,
        rendered_available=rendered,
        ncurses_available=tui,
    )


def selection_for_product(
    repo_root: str,
    *,
    product_id: str,
    requested_mode_id: str = "",
    mode_source: str = "default",
    mode_requested: bool | None = None,
    probe: Mapping[str, object],
) -> dict:
    resolution = {
        "requested_mode_id": _token(requested_mode_id),
        "mode_source": _token(mode_source) or "default",
        "mode_requested": bool(mode_requested if mode_requested is not None else bool(_token(requested_mode_id))),
        "deprecated_flags": [],
    }
    return select_ui_mode(
        repo_root,
        product_id=product_id,
        mode_resolution=resolution,
        probe_override=dict(probe),
    )


def ui_mode_resolution_violations(repo_root: str) -> list[dict]:
    violations: list[dict] = []
    bootstrap_text = _file_text(repo_root, "appshell/bootstrap.py")
    if "select_ui_mode(" not in bootstrap_text:
        violations.append(
            {
                "code": "ad_hoc_mode_selection",
                "file_path": "appshell/bootstrap.py",
                "message": "AppShell bootstrap must resolve UI mode through appshell.ui_mode_selector.select_ui_mode",
                "rule_id": "INV-UI-MODE-SELECTOR-SINGLE",
            }
        )
    if "appshell.mode.selected" not in bootstrap_text:
        violations.append(
            {
                "code": "mode_not_logged",
                "file_path": "appshell/bootstrap.py",
                "message": "selected UI mode must be logged explicitly",
                "rule_id": "INV-UI-MODE-LOGGED",
            }
        )
    if "appshell.mode.degraded" not in bootstrap_text:
        violations.append(
            {
                "code": "degrade_not_logged",
                "file_path": "appshell/bootstrap.py",
                "message": "mode degrade chains must be logged explicitly",
                "rule_id": "INV-FALLBACK-DETERMINISTIC",
            }
        )
    command_engine_text = _file_text(repo_root, "appshell/commands/command_engine.py")
    if "\"mode_selection\"" not in command_engine_text:
        violations.append(
            {
                "code": "silent_mode_fallback",
                "file_path": "appshell/commands/command_engine.py",
                "message": "compat-status must expose current mode selection and degrade details",
                "rule_id": "INV-UI-MODE-LOGGED",
            }
        )
    mode_dispatcher_text = _file_text(repo_root, "appshell/mode_dispatcher.py")
    if "return [\"cli\", \"tui\"" in mode_dispatcher_text or "token == \"client\"" in mode_dispatcher_text:
        violations.append(
            {
                "code": "ad_hoc_mode_selection",
                "file_path": "appshell/mode_dispatcher.py",
                "message": "mode dispatcher must not keep product-specific hardcoded selection ladders",
                "rule_id": "INV-UI-MODE-SELECTOR-SINGLE",
            }
        )
    return sorted(
        [dict(row) for row in violations],
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code"))),
    )


def build_ui_mode_resolution_report(repo_root: str) -> dict:
    registry_payload, _error = load_ui_mode_policy_registry(repo_root)
    policy_rows = list(dict(registry_payload.get("record") or {}).get("policies") or [])
    scenarios = (
        {
            "scenario_id": "client_tty",
            "product_id": "client",
            "requested_mode_id": "",
            "probe": build_test_probe(repo_root, product_id="client", tty=True, gui=True, native=False, rendered=True, tui=True),
        },
        {
            "scenario_id": "client_gui",
            "product_id": "client",
            "requested_mode_id": "",
            "probe": build_test_probe(repo_root, product_id="client", tty=False, gui=True, native=False, rendered=True, tui=True),
        },
        {
            "scenario_id": "launcher_gui_no_native",
            "product_id": "launcher",
            "requested_mode_id": "",
            "probe": build_test_probe(repo_root, product_id="launcher", tty=False, gui=True, native=False, rendered=False, tui=True),
        },
        {
            "scenario_id": "setup_gui_native",
            "product_id": "setup",
            "requested_mode_id": "",
            "probe": build_test_probe(repo_root, product_id="setup", tty=False, gui=True, native=True, rendered=False, tui=True),
        },
        {
            "scenario_id": "server_tty",
            "product_id": "server",
            "requested_mode_id": "",
            "probe": build_test_probe(repo_root, product_id="server", tty=True, gui=False, native=False, rendered=False, tui=True),
        },
        {
            "scenario_id": "server_headless_explicit",
            "product_id": "server",
            "requested_mode_id": "headless",
            "mode_source": "explicit",
            "mode_requested": True,
            "probe": build_test_probe(repo_root, product_id="server", tty=False, gui=False, native=False, rendered=False, tui=False),
        },
    )
    selections = []
    for scenario in scenarios:
        selection = selection_for_product(
            repo_root,
            product_id=_token(scenario.get("product_id")),
            requested_mode_id=_token(scenario.get("requested_mode_id")),
            mode_source=_token(scenario.get("mode_source")) or "default",
            mode_requested=scenario.get("mode_requested"),
            probe=dict(scenario.get("probe") or {}),
        )
        selections.append(
            {
                "scenario_id": _token(scenario.get("scenario_id")),
                "product_id": _token(scenario.get("product_id")),
                "requested_mode_id": _token(scenario.get("requested_mode_id")),
                "selected_mode_id": _token(selection.get("selected_mode_id")),
                "context_kind": _token(selection.get("context_kind")),
                "compatibility_mode_id": _token(selection.get("compatibility_mode_id")),
                "degrade_chain": list(selection.get("degrade_chain") or []),
                "selection_fingerprint": _token(selection.get("deterministic_fingerprint")),
            }
        )
    report = {
        "result": "complete",
        "report_id": "appshell.ui_mode_resolution.v1",
        "policy_rows": [dict(row) for row in policy_rows],
        "selection_rows": sorted(
            selections,
            key=lambda row: (_token(row.get("scenario_id")), _token(row.get("product_id"))),
        ),
        "violations": ui_mode_resolution_violations(repo_root),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_ui_mode_resolution_doc(report: Mapping[str, object]) -> str:
    policy_rows = list(report.get("policy_rows") or [])
    lines = [
        "Status: CANONICAL",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: APPSHELL",
        "Replacement Target: release-pinned standalone shell and product UI bootstrap contract",
        "",
        "# UI Mode Resolution",
        "",
        "AppShell owns deterministic product UI selection before product bootstrap, pack validation handoff, or IPC startup.",
        "",
        "## Decision Tree",
        "",
        "1. Parse explicit `--mode` or supported legacy `--ui` migration.",
        "2. Probe presentation-only host capabilities through `engine/platform/platform_probe.py`.",
        "3. If an explicit mode was requested, honor it when available; otherwise degrade through the CAP-NEG fallback map.",
        "4. Without an explicit mode, use the product policy order for the detected context:",
        "   - `tty`: prefer interactive console surfaces.",
        "   - `gui`: prefer GUI surfaces when no TTY is attached.",
        "   - `headless`: prefer deterministic CLI/non-interactive fallback.",
        "5. Emit structured `appshell.mode.selected` and `appshell.mode.degraded` events when applicable.",
        "",
        "## Detection Methods",
        "",
        "- TTY: `sys.std*.isatty()`",
        "- Windows GUI heuristic: console-window presence via `GetConsoleWindow`",
        "- POSIX GUI heuristic: `DISPLAY` / `WAYLAND_DISPLAY`",
        "- macOS GUI heuristic: Cocoa import or bundle env hint",
        "- TUI availability: `curses` import plus TTY context",
        "- Rendered availability: client render host markers plus GUI context",
        "- OS-native availability: platform adapter markers plus GUI context",
        "",
        "## Product Policies",
        "",
        "| Product | GUI Order | TTY Order | Headless Order | Legacy Explicit Modes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in policy_rows:
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row_map.get("product_id")),
                " -> ".join(_token(item) for item in list(row_map.get("gui_mode_order") or [])) or "n/a",
                " -> ".join(_token(item) for item in list(row_map.get("tty_mode_order") or [])) or "n/a",
                " -> ".join(_token(item) for item in list(row_map.get("headless_mode_order") or [])) or "n/a",
                "`, `".join(_token(item) for item in list(row_map.get("legacy_mode_ids") or [])) or "none",
            )
        )
    lines.extend(
        (
            "",
            "## Notes",
            "",
            "- `client` prefers `rendered` in GUI contexts, but TTY contexts prefer `tui` first.",
            "- `setup` and `launcher` prefer `os_native` only when a platform adapter exists; otherwise they degrade to `tui` or `cli`.",
            "- `server` and `engine` keep `headless` only as an explicit legacy/non-interactive mode.",
            "- UI mode selection is presentation-only and must not affect authoritative truth or simulation semantics.",
        )
    )
    return "\n".join(lines) + "\n"


def render_ui_mode_resolution_baseline(report: Mapping[str, object]) -> str:
    selection_rows = list(report.get("selection_rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: release-pinned standalone shell and product UI bootstrap contract",
        "",
        "# UI Mode Resolution Baseline",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Decision Tree Lock",
        "",
        "- explicit override -> explicit mode or deterministic fallback",
        "- attached TTY -> product TTY policy order",
        "- GUI without TTY -> product GUI policy order",
        "- no TTY and no GUI -> product headless policy order",
        "",
        "## Sample Outcomes",
        "",
        "| Scenario | Product | Requested | Context | Selected | Compat | Degrade Steps |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in selection_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("scenario_id")),
                _token(row.get("product_id")),
                _token(row.get("requested_mode_id")) or "default",
                _token(row.get("context_kind")),
                _token(row.get("selected_mode_id")),
                _token(row.get("compatibility_mode_id")),
                int(len(list(row.get("degrade_chain") or []))),
            )
        )
    violations = list(report.get("violations") or [])
    lines.extend(("", "## Enforcement Status", ""))
    if not violations:
        lines.append("- No selector-surface violations were detected.")
    else:
        for row in violations:
            lines.append(
                "- `{}` `{}`: {}".format(
                    _token(row.get("file_path")),
                    _token(row.get("code")),
                    _token(row.get("message")),
                )
            )
    lines.extend(
        (
            "",
            "## Readiness",
            "",
            "- The governed selector is centralized in `appshell/ui_mode_selector.py`.",
            "- The presentation-only probe is isolated in `engine/platform/platform_probe.py`.",
            "- The selector is ready for UI-RECONCILE-0 and PLATFORM-FORMALIZE-0 without changing simulation truth.",
        )
    )
    return "\n".join(lines) + "\n"


def render_ui_mode_resolution_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        UI_MODE_RESOLUTION_DOC_PATH: render_ui_mode_resolution_doc(report),
        UI_MODE_RESOLUTION_BASELINE_PATH: render_ui_mode_resolution_baseline(report),
    }


def write_ui_mode_resolution_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    written: dict[str, str] = {}
    root = os.path.normpath(os.path.abspath(repo_root))
    for rel_path, text in render_ui_mode_resolution_bundle(report).items():
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = abs_path.replace("\\", "/")
    return dict(sorted(written.items()))


__all__ = [
    "UI_MODE_RESOLUTION_BASELINE_PATH",
    "UI_MODE_RESOLUTION_DOC_PATH",
    "UI_MODE_RESOLUTION_TOOL_PATH",
    "build_test_probe",
    "build_ui_mode_resolution_report",
    "render_ui_mode_resolution_baseline",
    "render_ui_mode_resolution_bundle",
    "render_ui_mode_resolution_doc",
    "selection_for_product",
    "ui_mode_resolution_violations",
    "write_ui_mode_resolution_outputs",
]
