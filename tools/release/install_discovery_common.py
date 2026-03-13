"""Deterministic reporting and enforcement helpers for INSTALL-DISCOVERY-0."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.lib.install import discover_install, load_runtime_install_registry  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


INSTALL_DISCOVERY_ENGINE_PATH = "src/lib/install/install_discovery_engine.py"
INSTALL_DISCOVERY_SCHEMA_PATH = "schema/lib/install_registry.schema"
INSTALL_DISCOVERY_TOOL_PATH = "tools/release/tool_run_install_discovery.py"
INSTALL_DISCOVERY_COMMON_PATH = "tools/release/install_discovery_common.py"
INSTALL_DISCOVERY_BASELINE_PATH = "docs/audit/INSTALL_DISCOVERY_BASELINE.md"
INSTALL_DISCOVERY_REPORT_PATH = "data/audit/install_discovery_report.json"

DISCOVERY_ORDER = (
    "1. explicit CLI: --install-root or --install-id",
    "2. portable adjacency: <exe_dir>/install.manifest.json",
    "3. environment override: DOMINIUM_INSTALL_ROOT or DOMINIUM_INSTALL_ID",
    "4. installed registry: install_registry.json from user config or platform default location",
    "5. refusal: refusal.install.not_found",
)

INTEGRATION_TARGETS = (
    {
        "file_path": "src/lib/install/install_discovery_engine.py",
        "surface": "install_discovery_engine",
        "markers": ("discover_install(", "REFUSAL_INSTALL_NOT_FOUND", "portable_manifest"),
    },
    {
        "file_path": "src/appshell/paths/virtual_paths.py",
        "surface": "virtual_paths",
        "markers": ("discover_install(", "\"install_discovery\": {", "REFUSAL_INSTALL_NOT_FOUND"),
    },
    {
        "file_path": "src/appshell/bootstrap.py",
        "surface": "appshell_bootstrap",
        "markers": ("compat.install_selected", "refusal.install.not_found", "_allow_install_refusal_cli"),
    },
    {
        "file_path": "src/appshell/commands/command_engine.py",
        "surface": "compat_status",
        "markers": ("status_payload[\"install_discovery\"]",),
    },
    {
        "file_path": "tools/setup/setup_cli.py",
        "surface": "setup_install_commands",
        "markers": ("cmd == \"status\"", "discover_install(", "\"register\", \"unregister\", \"status\""),
    },
    {
        "file_path": "tools/launcher/launch.py",
        "surface": "launcher_install_commands",
        "markers": ("cmd_install_status(", "install_sub = install_cmd.add_subparsers", "discover_install("),
    },
)

MANIFEST_SCAN_EXCLUDED_PREFIXES = (
    "build/",
    "dist/",
    ".git/",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _read_json(path: str) -> tuple[dict, str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}, "invalid json"
    if not isinstance(payload, dict):
        return {}, "invalid root object"
    return dict(payload), ""


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _integration_rows(repo_root: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    rows = []
    for target in INTEGRATION_TARGETS:
        rel_path = str(target.get("file_path", "")).strip()
        text = _read_text(os.path.join(root, rel_path.replace("/", os.sep)))
        markers = list(target.get("markers") or [])
        matched = [marker for marker in markers if marker in text]
        rows.append(
            {
                "file_path": rel_path,
                "surface": str(target.get("surface", "")).strip(),
                "status": "integrated" if len(matched) == len(markers) else "remaining",
                "matched_marker_count": int(len(matched)),
                "required_marker_count": int(len(markers)),
                "markers": markers,
            }
        )
    return rows


def _manifest_absolute_path_violations(repo_root: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    violations: list[dict] = []
    registry_path = os.path.join(root, "data", "registries", "install_registry.json")
    registry_payload = load_runtime_install_registry(registry_path)
    for row in list(dict(registry_payload.get("record") or {}).get("installs") or []):
        entry = dict(row or {})
        path_token = _token(entry.get("path"))
        if path_token and os.path.isabs(path_token):
            violations.append(
                {
                    "code": "absolute_install_registry_path",
                    "file_path": "data/registries/install_registry.json",
                    "message": "install registry entry path must remain relative or logical",
                    "rule_id": "INV-NO-ABSOLUTE-PATHS-IN-MANIFESTS",
                }
            )
    for dirpath, _dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace("\\", "/")
        if any(rel_dir == prefix.rstrip("/") or rel_dir.startswith(prefix) for prefix in MANIFEST_SCAN_EXCLUDED_PREFIXES):
            continue
        if "install.manifest.json" not in filenames:
            continue
        rel_path = os.path.join(rel_dir, "install.manifest.json").replace("\\", "/")
        payload, error = _read_json(os.path.join(dirpath, "install.manifest.json"))
        if error:
            continue
        root_ref = dict(payload.get("store_root_ref") or {})
        for field in ("root_path", "manifest_ref"):
            token = _token(root_ref.get(field))
            if token and os.path.isabs(token):
                violations.append(
                    {
                        "code": "absolute_manifest_path_ref",
                        "file_path": rel_path,
                        "message": "install manifest field store_root_ref.{} must remain relative or logical".format(field),
                        "rule_id": "INV-NO-ABSOLUTE-PATHS-IN-MANIFESTS",
                    }
                )
        install_root = _token(payload.get("install_root"))
        if install_root and os.path.isabs(install_root):
            violations.append(
                {
                    "code": "absolute_install_root_field",
                    "file_path": rel_path,
                    "message": "install manifest field install_root must remain relative or logical",
                    "rule_id": "INV-NO-ABSOLUTE-PATHS-IN-MANIFESTS",
                }
            )
    unique = {
        (str(row.get("code", "")), str(row.get("file_path", "")), str(row.get("rule_id", ""))): dict(row)
        for row in violations
    }
    return sorted(unique.values(), key=lambda row: (_token(row.get("file_path")), _token(row.get("code"))))


def install_discovery_violations(repo_root: str) -> list[dict]:
    violations = []
    for row in _integration_rows(repo_root):
        if str(row.get("status", "")).strip() == "integrated":
            continue
        violations.append(
            {
                "code": "install_discovery_integration_missing",
                "file_path": str(row.get("file_path", "")).strip(),
                "message": "install discovery integration surface '{}' is not fully wired".format(str(row.get("surface", "")).strip()),
                "rule_id": "INV-INSTALL-DISCOVERY-REQUIRED",
            }
        )
    violations.extend(_manifest_absolute_path_violations(repo_root))
    unique = {
        (str(row.get("code", "")), str(row.get("file_path", "")), str(row.get("rule_id", ""))): dict(row)
        for row in violations
    }
    return sorted(unique.values(), key=lambda row: (_token(row.get("file_path")), _token(row.get("code"))))


def _fixture_manifest_payload(install_id: str, root_path: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "install_id": install_id,
        "install_version": "0.0.0",
        "store_root_ref": {"root_path": root_path},
        "semantic_contract_registry_hash": "0" * 64,
    }


def _sample_discovery_rows() -> dict[str, dict]:
    with tempfile.TemporaryDirectory(prefix="install_discovery_") as temp_root:
        explicit_root = os.path.join(temp_root, "explicit_install")
        portable_root = os.path.join(temp_root, "portable_install")
        registry_install_root = os.path.join(temp_root, "installs", "primary")
        config_root = os.path.join(temp_root, "config")
        os.makedirs(explicit_root, exist_ok=True)
        os.makedirs(portable_root, exist_ok=True)
        os.makedirs(registry_install_root, exist_ok=True)
        os.makedirs(os.path.join(config_root, "dominium"), exist_ok=True)
        _write_json(os.path.join(explicit_root, "install.manifest.json"), _fixture_manifest_payload("install.explicit", "."))
        _write_json(os.path.join(portable_root, "install.manifest.json"), _fixture_manifest_payload("install.portable", "."))
        _write_json(os.path.join(registry_install_root, "install.manifest.json"), _fixture_manifest_payload("install.registered", "../store"))
        _write_json(
            os.path.join(config_root, "dominium", "install_registry.json"),
            {
                "schema_id": "dominium.registry.install_registry",
                "schema_version": "1.0.0",
                "record": {
                    "registry_id": "dominium.registry.install_registry",
                    "registry_version": "1.0.0",
                    "installs": [
                        {
                            "install_id": "install.registered",
                            "path": "../../installs/primary",
                            "version": "0.0.0",
                            "contract_registry_hash": "0" * 64,
                        }
                    ],
                },
            },
        )
        explicit = discover_install(
            raw_args=["--install-root", explicit_root],
            executable_path=os.path.join(temp_root, "bin", "dominium_setup"),
            cwd=temp_root,
            env={},
            platform_id="platform.posix_min",
        )
        portable = discover_install(
            raw_args=[],
            executable_path=os.path.join(portable_root, "dominium_client"),
            cwd=temp_root,
            env={},
            platform_id="platform.posix_min",
        )
        installed = discover_install(
            raw_args=[],
            executable_path=os.path.join(temp_root, "bin", "dominium_launcher"),
            cwd=temp_root,
            env={"XDG_CONFIG_HOME": config_root, "HOME": temp_root},
            platform_id="platform.posix_min",
        )
        refused = discover_install(
            raw_args=[],
            executable_path=os.path.join(temp_root, "bin", "dominium_server"),
            cwd=temp_root,
            env={"XDG_CONFIG_HOME": os.path.join(temp_root, "empty_config"), "HOME": temp_root},
            platform_id="platform.posix_min",
        )
    return {
        "explicit": explicit,
        "portable": portable,
        "installed": installed,
        "refused": refused,
    }


def build_install_discovery_report(repo_root: str) -> dict:
    samples = _sample_discovery_rows()
    integration_rows = _integration_rows(repo_root)
    violations = install_discovery_violations(repo_root)
    report = {
        "result": "complete" if not violations else "refused",
        "report_id": "install.discovery.v1",
        "discovery_order": list(DISCOVERY_ORDER),
        "refusal_codes": ["refusal.install.not_found"],
        "integration_rows": integration_rows,
        "sample_rows": {
            key: {
                "result": _token(dict(value).get("result")),
                "mode": _token(dict(value).get("mode")),
                "resolution_source": _token(dict(value).get("resolution_source")),
                "resolved_install_id": _token(dict(value).get("resolved_install_id")),
                "refusal_code": _token(dict(value).get("refusal_code")),
            }
            for key, value in sorted(samples.items(), key=lambda item: str(item[0]))
        },
        "manifest_absolute_path_violations": _manifest_absolute_path_violations(repo_root),
        "violations": violations,
        "metrics": {
            "integration_target_count": int(len(integration_rows)),
            "integration_remaining_count": int(sum(1 for row in integration_rows if str(row.get("status", "")).strip() != "integrated")),
            "manifest_violation_count": int(len(_manifest_absolute_path_violations(repo_root))),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_install_discovery_baseline(report: Mapping[str, object]) -> str:
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: LIB/APPSHELL",
        "Replacement Target: release-pinned install discovery and installation governance contract",
        "",
        "# Install Discovery Baseline",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Discovery Order",
        "",
        *["- {}".format(step) for step in list(report.get("discovery_order") or [])],
        "",
        "## Refusal Codes",
        "",
        *["- `{}`".format(_token(code)) for code in list(report.get("refusal_codes") or [])],
        "",
        "## Sample Outcomes",
        "",
        "| Case | Result | Mode | Resolution Source | Install Id | Refusal Code |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for key, row in sorted(dict(report.get("sample_rows") or {}).items(), key=lambda item: str(item[0])):
        item = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                _token(key),
                _token(item.get("result")),
                _token(item.get("mode")),
                _token(item.get("resolution_source")),
                _token(item.get("resolved_install_id")),
                _token(item.get("refusal_code")),
            )
        )
    lines.extend(
        (
            "",
            "## Integration Coverage",
            "",
            "| Surface | File | Status | Markers |",
            "| --- | --- | --- | --- |",
        )
    )
    for row in list(report.get("integration_rows") or []):
        item = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}/{}` |".format(
                _token(item.get("surface")),
                _token(item.get("file_path")),
                _token(item.get("status")),
                int(item.get("matched_marker_count", 0) or 0),
                int(item.get("required_marker_count", 0) or 0),
            )
        )
    lines.extend(
        (
            "",
            "## Manifest Discipline",
            "",
            "- manifest absolute-path violations: `{}`".format(int(len(list(report.get("manifest_absolute_path_violations") or [])))),
            "- integration remaining count: `{}`".format(int(dict(report.get("metrics") or {}).get("integration_remaining_count", 0) or 0)),
            "",
            "## Integration Coverage Report",
            "",
            "- AppShell boot now resolves install selection through the LIB discovery engine before virtual roots are derived.",
            "- `compat-status`, `setup install status`, and `launcher install status` expose the resolved install decision or refusal details.",
            "- Repo wrapper fallback remains outside the authoritative discovery order and is tracked in the virtual-path shim surface, not the runtime install discovery contract.",
        )
    )
    return "\n".join(lines) + "\n"


def write_install_discovery_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    root = os.path.normpath(os.path.abspath(repo_root))
    written: dict[str, str] = {}
    baseline_abs = os.path.join(root, INSTALL_DISCOVERY_BASELINE_PATH.replace("/", os.sep))
    os.makedirs(os.path.dirname(baseline_abs), exist_ok=True)
    with open(baseline_abs, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_install_discovery_baseline(report))
    written[INSTALL_DISCOVERY_BASELINE_PATH] = baseline_abs.replace("\\", "/")
    report_abs = os.path.join(root, INSTALL_DISCOVERY_REPORT_PATH.replace("/", os.sep))
    os.makedirs(os.path.dirname(report_abs), exist_ok=True)
    with open(report_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(report), handle, indent=2, sort_keys=True)
        handle.write("\n")
    written[INSTALL_DISCOVERY_REPORT_PATH] = report_abs.replace("\\", "/")
    return dict(sorted(written.items()))


__all__ = [
    "INSTALL_DISCOVERY_BASELINE_PATH",
    "INSTALL_DISCOVERY_COMMON_PATH",
    "INSTALL_DISCOVERY_ENGINE_PATH",
    "INSTALL_DISCOVERY_REPORT_PATH",
    "INSTALL_DISCOVERY_SCHEMA_PATH",
    "INSTALL_DISCOVERY_TOOL_PATH",
    "build_install_discovery_report",
    "install_discovery_violations",
    "render_install_discovery_baseline",
    "write_install_discovery_outputs",
]
