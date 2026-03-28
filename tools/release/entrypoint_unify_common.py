"""Deterministic helpers for ENTRYPOINT-UNIFY-0 reporting and enforcement."""

from __future__ import annotations

import os
from typing import Iterable, Mapping

from appshell.args_parser import parse_appshell_args
from appshell.compat_adapter import build_version_payload
from appshell.paths import clear_current_virtual_paths, set_current_virtual_paths, vpath_init
from appshell.product_bootstrap import build_product_bootstrap_context, resolve_mode_request
from appshell.product_bootstrap import flag_migration_rows
from appshell.ui_mode_selector import select_ui_mode
from compat.shims import apply_flag_shims
from engine.platform.platform_probe import probe_platform_descriptor
from tools.xstack.compatx.canonical_json import canonical_sha256


ENTRYPOINT_UNIFY_MAP_PATH = "docs/audit/ENTRYPOINT_UNIFY_MAP.md"
FLAG_MIGRATION_PATH = "docs/appshell/FLAG_MIGRATION.md"
ENTRYPOINT_UNIFY_FINAL_PATH = "docs/audit/ENTRYPOINT_UNIFY_FINAL.md"
ENTRYPOINT_UNIFY_TOOL_PATH = "tools/release/tool_run_entrypoint_unify.py"
STUB_ONLY_PRODUCTS = {"engine", "game", "tool.attach_console_stub"}
SAMPLE_ARGS = {
    "client": ["--seed", "123", "--ui", "gui", "--local-singleplayer"],
    "engine": [],
    "game": [],
    "launcher": ["run", "--dist", "dist", "--session", "saves/mvp_default/session_spec.json"],
    "server": ["--seed", "123", "--listen-loopback"],
    "setup": ["verify", "--root", "dist"],
    "tool.attach_console_stub": [],
}

PRODUCT_ROWS = (
    {
        "product_id": "client",
        "executable_names": ["client", "dominium_client"],
        "source_file": "tools/mvp/runtime_entry.py",
        "main_symbol": "client_main",
        "ui_init_location": "AppShell mode handoff -> tools/mvp/runtime_entry.py::_legacy_main",
        "pack_loading_location": "tools/mvp/runtime_bundle.py::build_runtime_bootstrap",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer",
        "supervisor_involvement": "no",
    },
    {
        "product_id": "engine",
        "executable_names": ["engine"],
        "source_file": "tools/appshell/product_stub_cli.py",
        "main_symbol": "main",
        "ui_init_location": "AppShell stub mode only",
        "pack_loading_location": "none",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer",
        "supervisor_involvement": "no",
    },
    {
        "product_id": "game",
        "executable_names": ["game"],
        "source_file": "tools/appshell/product_stub_cli.py",
        "main_symbol": "main",
        "ui_init_location": "AppShell stub mode only",
        "pack_loading_location": "none",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer",
        "supervisor_involvement": "no",
    },
    {
        "product_id": "launcher",
        "executable_names": ["launcher"],
        "source_file": "tools/launcher/launch.py",
        "main_symbol": "main",
        "ui_init_location": "AppShell mode handoff -> tools/launcher/launch.py::_legacy_main",
        "pack_loading_location": "appshell.pack_verifier_adapter.verify_pack_root",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer",
        "supervisor_involvement": "yes",
    },
    {
        "product_id": "server",
        "executable_names": ["server", "dominium_server"],
        "source_file": "server/server_main.py",
        "main_symbol": "main",
        "ui_init_location": "AppShell mode handoff -> server/server_main.py::_legacy_main",
        "pack_loading_location": "server/server_boot.py::boot_server_runtime",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer; server/net/loopback_transport.py",
        "supervisor_involvement": "no",
    },
    {
        "product_id": "setup",
        "executable_names": ["setup"],
        "source_file": "tools/setup/setup_cli.py",
        "main_symbol": "main",
        "ui_init_location": "AppShell mode handoff -> tools/setup/setup_cli.py::_legacy_main",
        "pack_loading_location": "appshell.pack_verifier_adapter.verify_pack_root",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer",
        "supervisor_involvement": "no",
    },
    {
        "product_id": "tool.attach_console_stub",
        "executable_names": ["tool_attach_console_stub"],
        "source_file": "tools/appshell/product_stub_cli.py",
        "main_symbol": "main",
        "ui_init_location": "AppShell stub mode only",
        "pack_loading_location": "none",
        "ipc_start_location": "appshell/bootstrap.py::AppShellIPCEndpointServer",
        "supervisor_involvement": "no",
    },
)
MAIN_TOKENS = ("def main(", "def client_main(", "def server_main(")
DIRECT_SIMULATION_TOKENS = (
    "build_runtime_bootstrap(",
    "boot_server_runtime(",
    "start_local_singleplayer(",
    "create_loopback_listener(",
    "accept_loopback_connection(",
    "run_server_ticks(",
)


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _token(value: object) -> str:
    return str(value or "").strip()


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return open(abs_path, "r", encoding="utf-8", errors="ignore").read()
    except OSError:
        return ""


def _snippet(text: str, marker: str) -> str:
    for line in text.splitlines():
        if marker in line:
            return line.strip()
    return ""


def _has_legacy_main_fallback(text: str) -> bool:
    return "legacy_main=" in text and "legacy_main=None" not in text


def _function_block(text: str, function_name: str) -> str:
    lines = text.splitlines()
    target = "def {}(".format(function_name)
    start = -1
    for index, line in enumerate(lines):
        if line.startswith(target):
            start = index
            break
    if start < 0:
        return ""
    out = []
    for index in range(start, len(lines)):
        line = lines[index]
        if index > start and line.startswith("def "):
            break
        out.append(line)
    return "\n".join(out)


def _compliance_status(product_id: str, text: str) -> str:
    token = _token(product_id)
    if token in STUB_ONLY_PRODUCTS and "appshell_main(" in text:
        return "compliant"
    if "product_bootstrap=" in text and "appshell_product_bootstrap" in text:
        return "compliant"
    if "appshell_main(" in text:
        return "partially_compliant"
    return "non_compliant"


def _boot_flow(text: str) -> str:
    if "product_bootstrap=" in text and "appshell_product_bootstrap" in text:
        return "AppShell -> bootstrap context -> appshell_product_bootstrap"
    if _has_legacy_main_fallback(text):
        return "AppShell -> legacy_main fallback"
    if "appshell_main(" in text:
        return "AppShell -> stub dispatch"
    return "ad hoc main"


def _violations_for_row(repo_root: str, row: Mapping[str, object]) -> list[dict]:
    rel_path = _token(row.get("source_file"))
    product_id = _token(row.get("product_id"))
    text = _read_text(repo_root, rel_path)
    violations: list[dict] = []
    if not text:
        return [
            {
                "code": "missing_entrypoint",
                "file_path": rel_path,
                "message": "product entrypoint source is missing",
                "rule_id": "INV-ALL-PRODUCTS-USE-APPSHELL",
            }
        ]
    if _compliance_status(product_id, text) != "compliant":
        violations.append(
            {
                "code": "product_not_unified",
                "file_path": rel_path,
                "message": "product entrypoint is not fully unified under AppShell bootstrap",
                "rule_id": "INV-ALL-PRODUCTS-USE-APPSHELL",
            }
        )
    if _has_legacy_main_fallback(text):
        violations.append(
            {
                "code": "ad_hoc_main",
                "file_path": rel_path,
                "message": "entrypoint still delegates through legacy_main instead of appshell_product_bootstrap",
                "rule_id": "INV-NO-ADHOC-MAIN",
            }
        )
    for function_name in ("main", "client_main", "server_main"):
        block = _function_block(text, function_name)
        if not block:
            continue
        for token in DIRECT_SIMULATION_TOKENS:
            if token in block:
                violations.append(
                    {
                        "code": "direct_simulation_start",
                        "file_path": rel_path,
                        "message": "entrypoint {} still starts simulation or transport directly".format(function_name),
                        "rule_id": "INV-NO-DIRECT-UI-INIT-IN-MAIN",
                    }
                )
                break
        if "verify_pack_set(" in block:
            violations.append(
                {
                    "code": "direct_pack_load",
                    "file_path": rel_path,
                    "message": "entrypoint {} still performs pack verification directly".format(function_name),
                    "rule_id": "INV-NO-ADHOC-MAIN",
                }
            )
    if product_id in {"launcher", "setup"} and "verify_pack_set(" in text:
        violations.append(
            {
                "code": "direct_pack_load",
                "file_path": rel_path,
                "message": "product source still uses verify_pack_set directly instead of AppShell pack adapter",
                "rule_id": "INV-NO-ADHOC-MAIN",
            }
        )
    if rel_path == "tools/mvp/runtime_entry.py" and "return _legacy_main(str(raw_args[0]).strip(), raw_args[1:])" in text:
        violations.append(
            {
                "code": "multiplexer_bypass",
                "file_path": rel_path,
                "message": "runtime_entry multiplexer still bypasses AppShell for client/server dispatch",
                "rule_id": "INV-ALL-PRODUCTS-USE-APPSHELL",
            }
        )
    return violations


def build_entrypoint_unify_report(repo_root: str) -> dict:
    rows: list[dict] = []
    violations: list[dict] = []
    for base_row in PRODUCT_ROWS:
        row = dict(base_row)
        product_id = _token(row.get("product_id"))
        text = _read_text(repo_root, _token(row.get("source_file")))
        row["current_main_implementation"] = _snippet(text, "return appshell_main(") or _snippet(text, "def main(")
        row["current_boot_flow"] = _boot_flow(text)
        row["compliance_status"] = _compliance_status(product_id, text)
        row["calls_appshell_main"] = "appshell_main(" in text
        row["uses_product_bootstrap"] = "product_bootstrap=appshell_product_bootstrap" in text
        try:
            row["bootstrap_steps"] = bootstrap_steps_for_product(repo_root, product_id)
        except ValueError as exc:
            row["bootstrap_steps"] = []
            row["bootstrap_error"] = _token(exc)
        rows.append(row)
        violations.extend(_violations_for_row(repo_root, row))
    report = {
        "result": "complete",
        "inventory_id": "entrypoint.unify.v1",
        "rows": sorted(rows, key=lambda item: _token(item.get("product_id"))),
        "deprecated_flags": flag_migration_rows(),
        "violations": sorted(
            [dict(row) for row in violations],
            key=lambda item: (_token(item.get("file_path")), _token(item.get("code"))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def entrypoint_unify_violations(repo_root: str) -> list[dict]:
    return list(build_entrypoint_unify_report(repo_root).get("violations") or [])


def bootstrap_context_for_product(
    repo_root: str,
    product_id: str,
    raw_args: Iterable[str] | None = None,
    *,
    executable_path: str = "",
) -> dict:
    product_token = _token(product_id)
    argv = list(raw_args or SAMPLE_ARGS.get(product_token, []))
    initial_shell_args = parse_appshell_args(product_token, argv=argv)
    shimmed = apply_flag_shims(
        product_id=product_token,
        raw_args=initial_shell_args.raw_args,
        repo_root=repo_root,
        executable_path=executable_path or os.path.join(repo_root, "dist", "bin", product_token.replace(".", "_")),
    )
    shell_args = parse_appshell_args(product_token, argv=list(shimmed.get("raw_args") or []))
    mode_resolution = resolve_mode_request(
        product_id=product_token,
        explicit_mode=shell_args.mode,
        raw_args=shell_args.raw_args,
    )
    if list(shimmed.get("warnings") or []):
        mode_resolution = dict(mode_resolution)
        mode_resolution["deprecated_flags"] = list(mode_resolution.get("deprecated_flags") or []) + list(shimmed.get("warnings") or [])
    mode_selection = select_ui_mode(
        repo_root,
        product_id=product_token,
        mode_resolution=mode_resolution,
        probe_override=probe_platform_descriptor(
            repo_root,
            product_id=product_token,
            stdin_tty=False,
            stdout_tty=False,
            stderr_tty=False,
            gui_available=True,
            native_available=False,
            rendered_available=True,
            ncurses_available=True,
        ),
    )
    vpath_context = vpath_init(
        {
            "repo_root": os.path.normpath(os.path.abspath(repo_root)),
            "product_id": product_token,
            "raw_args": shell_args.raw_args,
            "executable_path": executable_path or os.path.join(repo_root, "dist", "bin", product_token.replace(".", "_")),
        }
    )
    set_current_virtual_paths(vpath_context)
    try:
        return build_product_bootstrap_context(
            product_id=product_token,
            repo_root=os.path.normpath(os.path.abspath(repo_root)),
            shell_args=shell_args,
            mode_resolution=mode_resolution,
            mode_selection=mode_selection,
            version_payload=build_version_payload(repo_root, product_id=product_token),
        )
    finally:
        clear_current_virtual_paths()


def bootstrap_steps_for_product(repo_root: str, product_id: str, raw_args: Iterable[str] | None = None) -> list[str]:
    return list(bootstrap_context_for_product(repo_root, product_id, raw_args).get("bootstrap_steps") or [])


def render_entrypoint_unify_map(report: Mapping[str, object]) -> str:
    rows = list(report.get("rows") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: canon-aligned documentation set for convergence and release preparation",
        "",
        "# Entrypoint Unify Map",
        "",
        "Status source: `tools/release/entrypoint_unify_common.py`",
        "",
        "| Product | Executables | Source | Main Implementation | Boot Flow | UI Init | Pack Gate | IPC Start | Steps | Compliance |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("product_id")),
                "`, `".join(_token(item) for item in list(row.get("executable_names") or [])),
                _token(row.get("source_file")),
                _token(row.get("current_main_implementation")) or "missing",
                _token(row.get("current_boot_flow")),
                _token(row.get("ui_init_location")),
                _token(row.get("pack_loading_location")),
                _token(row.get("ipc_start_location")),
                " -> ".join(_token(item) for item in list(row.get("bootstrap_steps") or [])) or "n/a",
                _token(row.get("compliance_status")),
            )
        )
    violations = list(report.get("violations") or [])
    lines.extend(("", "## Compliance Summary", ""))
    if not violations:
        lines.append("- All governed product entrypoints are unified under AppShell bootstrap.")
    else:
        for row in violations:
            lines.append(
                "- `{}` `{}`: {}".format(
                    _token(row.get("file_path")),
                    _token(row.get("code")),
                    _token(row.get("message")),
                )
            )
    return "\n".join(lines) + "\n"


def render_flag_migration(report: Mapping[str, object]) -> str:
    rows = list(report.get("deprecated_flags") or [])
    lines = [
        "Status: CANONICAL",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: APPSHELL",
        "Replacement Target: release-pinned standalone product command reference after convergence",
        "",
        "# Flag Migration",
        "",
        "Legacy boot flags remain supported, but AppShell owns the canonical entry surface.",
        "",
        "| Product | Legacy Flag | Canonical AppShell Flag | Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                _token(row.get("product_id")),
                _token(row.get("legacy_flag")),
                _token(row.get("replacement_flag")),
                _token(row.get("status")),
            )
        )
    lines.extend(
        (
            "",
            "## Notes",
            "",
            "- `client` and `server` continue to accept legacy `--ui` values, but AppShell resolves them as `--mode` before product bootstrap.",
            "- Default mode selection is now centralized in `appshell/ui_mode_selector.py` and follows the product policy registry plus deterministic platform probing.",
            "- `headless` remains an explicit legacy/non-interactive mode for governed server and engine surfaces; it is not part of the default interactive ladder.",
            "- Existing product-domain flags such as setup `--ui-mode` remain product arguments and are not AppShell shell-mode aliases.",
            "- Deprecated legacy flags emit a structured AppShell warning event before product bootstrap.",
        )
    )
    return "\n".join(lines) + "\n"


def render_entrypoint_unify_final(report: Mapping[str, object]) -> str:
    rows = list(report.get("rows") or [])
    deprecated = list(report.get("deprecated_flags") or [])
    compliant = [row for row in rows if _token(row.get("compliance_status")) == "compliant"]
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: canon-aligned documentation set for convergence and release preparation",
        "",
        "# Entrypoint Unify Final",
        "",
        "## Before",
        "",
        "```text",
        "product main -> appshell_main -> legacy_main fallback -> product-local validation/startup",
        "runtime multiplexer -> direct _legacy_main bypass (client/server script path)",
        "```",
        "",
        "## After",
        "",
        "```text",
        "product main -> appshell_main -> bootstrap context -> appshell_product_bootstrap -> product-local runtime logic",
        "AppShell owns mode resolution, negotiation preflight, legacy flag migration, logging, and IPC endpoint startup.",
        "```",
        "",
        "## Unified Products",
        "",
        "- `{}` governed product surfaces are compliant.".format(len(compliant)),
    ]
    for row in compliant:
        lines.append("- `{}` via `{}`".format(_token(row.get("product_id")), _token(row.get("source_file"))))
    lines.extend(("", "## Deprecated Flags", ""))
    if not deprecated:
        lines.append("- none")
    else:
        for row in deprecated:
            lines.append(
                "- `{}` `{}` -> `{}`".format(
                    _token(row.get("product_id")),
                    _token(row.get("legacy_flag")),
                    _token(row.get("replacement_flag")),
                )
            )
    lines.extend(
        (
            "",
        "## Validation Unification Readiness",
        "",
        "- Product mains no longer delegate through `legacy_main=` directly.",
        "- Launcher and setup pack verification flow through `appshell.pack_verifier_adapter.verify_pack_root`.",
        "- Runtime multiplexer dispatch now re-enters AppShell for `client` and `server` instead of bypassing it.",
        "- AppShell now emits bootstrap context and only starts IPC after negotiation preflight context construction.",
        )
    )
    return "\n".join(lines) + "\n"


def render_entrypoint_unify_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        ENTRYPOINT_UNIFY_MAP_PATH: render_entrypoint_unify_map(report),
        FLAG_MIGRATION_PATH: render_flag_migration(report),
        ENTRYPOINT_UNIFY_FINAL_PATH: render_entrypoint_unify_final(report),
    }


def write_entrypoint_unify_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    written: dict[str, str] = {}
    root = os.path.normpath(os.path.abspath(repo_root))
    for rel_path, text in render_entrypoint_unify_bundle(report).items():
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = abs_path.replace("\\", "/")
    return dict(sorted(written.items()))


__all__ = [
    "ENTRYPOINT_UNIFY_FINAL_PATH",
    "ENTRYPOINT_UNIFY_MAP_PATH",
    "ENTRYPOINT_UNIFY_TOOL_PATH",
    "FLAG_MIGRATION_PATH",
    "SAMPLE_ARGS",
    "bootstrap_context_for_product",
    "bootstrap_steps_for_product",
    "build_entrypoint_unify_report",
    "entrypoint_unify_violations",
    "render_entrypoint_unify_final",
    "render_entrypoint_unify_bundle",
    "render_entrypoint_unify_map",
    "render_flag_migration",
    "write_entrypoint_unify_outputs",
]
