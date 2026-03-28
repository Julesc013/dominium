"""Deterministic reporting and enforcement helpers for REPO-LAYOUT-0."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from appshell.paths import load_virtual_root_registry, vpath_init  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


VIRTUAL_ROOT_REGISTRY_PATH = "data/registries/virtual_root_registry.json"
VIRTUAL_PATHS_ENGINE_PATH = "appshell/paths/virtual_paths.py"
VIRTUAL_PATHS_DOC_PATH = "docs/appshell/VIRTUAL_PATHS.md"
VIRTUAL_PATHS_BASELINE_PATH = "docs/audit/VIRTUAL_PATHS_BASELINE.md"
VIRTUAL_PATHS_REPORT_PATH = "data/audit/virtual_paths_report.json"

SCAN_ROOTS = (
    "src/appshell",
    "src/lib",
    "src/ui",
    "src/diag",
    "tools/setup",
    "tools/launcher",
)
TARGET_EXTENSIONS = {".py"}
ROOT_TOKENS = ("dist", "packs", "profiles", "locks", "instances", "saves", "exports", "runtime", "logs", "build")
BASE_TOKENS = ("repo_root", "repo_root_abs", "REPO_ROOT", "REPO_ROOT_HINT", "resolve_repo_root(", "install_root", "store_root", "data_root", "state_root")
ALLOWED_SCAN_PATHS = {
    "appshell/paths/virtual_paths.py",
    "tools/release/virtual_paths_common.py",
}
PACKAGING_LAYOUT_PATHS = {
    "tools/setup/setup_cli.py",
    "lib/import/import_engine.py",
    "lib/export/export_engine.py",
}
INTEGRATION_TARGETS = (
    {
        "file_path": "appshell/bootstrap.py",
        "markers": ("vpath_init(", "set_current_virtual_paths(", "clear_current_virtual_paths("),
        "surface": "bootstrap",
    },
    {
        "file_path": "appshell/commands/command_engine.py",
        "markers": ("VROOT_LOCKS", "VROOT_LOGS", "vpath_resolve(", "vpath_candidate_roots("),
        "surface": "command_engine",
    },
    {
        "file_path": "appshell/config_loader.py",
        "markers": ("vpath_candidate_roots(", "get_current_virtual_paths("),
        "surface": "config_loader",
    },
    {
        "file_path": "appshell/diag/diag_snapshot.py",
        "markers": ("VROOT_EXPORTS", "vpath_resolve(", "get_current_virtual_paths("),
        "surface": "diag_snapshot",
    },
    {
        "file_path": "appshell/ipc/ipc_transport.py",
        "markers": ("VROOT_IPC", "vpath_resolve(", "get_current_virtual_paths("),
        "surface": "ipc_transport",
    },
    {
        "file_path": "appshell/logging/log_engine.py",
        "markers": ("VROOT_LOGS", "vpath_resolve(", "get_current_virtual_paths("),
        "surface": "log_sink",
    },
    {
        "file_path": "appshell/pack_verifier_adapter.py",
        "markers": ("VROOT_STORE", "vpath_root(", "get_current_virtual_paths("),
        "surface": "pack_verifier",
    },
    {
        "file_path": "appshell/supervisor/supervisor_engine.py",
        "markers": ("VROOT_IPC", "VROOT_LOGS", "VROOT_EXPORTS", "vpath_resolve(", "get_current_virtual_paths("),
        "surface": "supervisor",
    },
    {
        "file_path": "diag/repro_bundle_builder.py",
        "markers": ("VROOT_EXPORTS", "vpath_resolve(", "get_current_virtual_paths("),
        "surface": "diag_bundle_writer",
    },
    {
        "file_path": "lib/export/export_engine.py",
        "markers": ("VROOT_STORE", "vpath_candidate_roots(", "vpath_init("),
        "surface": "export_engine",
    },
    {
        "file_path": "lib/import/import_engine.py",
        "markers": ("VROOT_INSTANCES", "VROOT_SAVES", "vpath_init(", "vpath_resolve("),
        "surface": "import_engine",
    },
    {
        "file_path": "lib/install/install_validator.py",
        "markers": ("VROOT_INSTALL", "vpath_resolve_existing(", "get_current_virtual_paths("),
        "surface": "install_validator",
    },
    {
        "file_path": "lib/save/save_validator.py",
        "markers": ("VROOT_SAVES", "vpath_candidate_roots(", "get_current_virtual_paths("),
        "surface": "save_validator",
    },
    {
        "file_path": "ui/ui_model.py",
        "markers": ("VROOT_INSTANCES", "VROOT_SAVES", "vpath_candidate_roots(", "get_current_virtual_paths("),
        "surface": "ui_model",
    },
    {
        "file_path": "tools/launcher/launch.py",
        "markers": ("VROOT_SAVES", "vpath_resolve_existing(", "get_current_virtual_paths("),
        "surface": "launcher_runtime",
    },
    {
        "file_path": "tools/launcher/launcher_cli.py",
        "markers": ("VROOT_LOGS", "VROOT_PACKS", "VROOT_PROFILES", "vpath_candidate_roots(", "vpath_resolve("),
        "surface": "launcher_cli",
    },
    {
        "file_path": "tools/setup/setup_cli.py",
        "markers": ("VROOT_INSTANCES", "VROOT_PACKS", "vpath_candidate_roots(", "vpath_init("),
        "surface": "setup_cli",
    },
)
RESOLUTION_ORDER = (
    "1. explicit CLI overrides: --root, --store-root, or per-vroot overrides",
    "2. install discovery explicit CLI: --install-root or --install-id",
    "3. install discovery portable mode: install.manifest.json adjacent to the product binary",
    "4. install discovery environment override: DOMINIUM_INSTALL_ROOT or DOMINIUM_INSTALL_ID",
    "5. install discovery installed registry mode: install_registry.json entry resolved by executable match or install_id",
    "6. refusal: refusal.install.not_found when no governed install root can be discovered",
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _normalize_repo_path(repo_root: str, abs_path: str) -> str:
    root = os.path.normpath(os.path.abspath(repo_root))
    target = os.path.normpath(os.path.abspath(str(abs_path or ".")))
    rel = os.path.relpath(target, root).replace("\\", "/")
    if rel == ".":
        return "<repo>"
    if not rel.startswith("../"):
        return "<repo>/{}".format(rel)
    return "<abs>"


def _collect_hardcoded_path_hits(repo_root: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    hits: list[dict] = []
    for scan_root in SCAN_ROOTS:
        abs_root = os.path.join(root, scan_root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for dirpath, _dirnames, filenames in os.walk(abs_root):
            for filename in sorted(filenames):
                rel_path = os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/")
                if rel_path in ALLOWED_SCAN_PATHS:
                    continue
                if os.path.splitext(filename)[1].lower() not in TARGET_EXTENSIONS:
                    continue
                text = _read_text(os.path.join(root, rel_path.replace("/", os.sep)))
                uses_vpath = "appshell.paths" in text or "vpath_" in text or "get_current_virtual_paths" in text
                for line_number, line in enumerate(text.splitlines(), start=1):
                    if "os.path.join(" not in line:
                        continue
                    if not any(anchor in line for anchor in BASE_TOKENS):
                        continue
                    if not any('"{}"'.format(token) in line for token in ROOT_TOKENS):
                        continue
                    classification = "remaining"
                    if rel_path in PACKAGING_LAYOUT_PATHS or any(token in line for token in ("tmp_root", "temp_root", "payload_root", "stage_root", "bundle_root")):
                        classification = "allowed_packaging_layout"
                    elif uses_vpath:
                        classification = "shim"
                    hits.append(
                        {
                            "file_path": rel_path,
                            "line_number": int(line_number),
                            "classification": classification,
                            "line": line.strip(),
                        }
                    )
    return sorted(hits, key=lambda row: (_token(row.get("classification")), _token(row.get("file_path")), int(row.get("line_number", 0) or 0)))


def _collect_separator_hits(repo_root: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    hits: list[dict] = []
    for scan_root in SCAN_ROOTS:
        abs_root = os.path.join(root, scan_root.replace("/", os.sep))
        if not os.path.isdir(abs_root):
            continue
        for dirpath, _dirnames, filenames in os.walk(abs_root):
            for filename in sorted(filenames):
                rel_path = os.path.relpath(os.path.join(dirpath, filename), root).replace("\\", "/")
                if rel_path in ALLOWED_SCAN_PATHS:
                    continue
                if os.path.splitext(filename)[1].lower() not in TARGET_EXTENSIONS:
                    continue
                text = _read_text(os.path.join(root, rel_path.replace("/", os.sep)))
                for line_number, line in enumerate(text.splitlines(), start=1):
                    if '\\"' not in line and "\\\\" not in line:
                        continue
                    if 'replace("\\\\", "/")' in line or "os.sep" in line:
                        continue
                    if not any(token in line for token in ROOT_TOKENS):
                        continue
                    hits.append(
                        {
                            "file_path": rel_path,
                            "line_number": int(line_number),
                            "line": line.strip(),
                        }
                    )
    return sorted(hits, key=lambda row: (_token(row.get("file_path")), int(row.get("line_number", 0) or 0)))


def _integration_rows(repo_root: str) -> list[dict]:
    root = os.path.normpath(os.path.abspath(repo_root))
    rows = []
    for target in INTEGRATION_TARGETS:
        rel_path = str(target["file_path"])
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        text = _read_text(abs_path)
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


def _repo_wrapper_projection(repo_root: str) -> dict:
    probe = vpath_init(
        {
            "repo_root": repo_root,
            "product_id": "launcher",
            "raw_args": [],
            "executable_path": os.path.join(repo_root, "dist", "bin", "dominium_launcher"),
        }
    )
    return {
        "result": _token(probe.get("result")),
        "resolution_source": _token(probe.get("resolution_source")),
        "refusal_code": _token(probe.get("refusal_code")),
        "warnings": list(probe.get("warnings") or []),
        "roots": {
            key: _normalize_repo_path(repo_root, value)
            for key, value in sorted(_as_map(probe.get("roots")).items(), key=lambda item: str(item[0]))
            if _token(value)
        },
    }


def virtual_paths_violations(repo_root: str) -> list[dict]:
    violations: list[dict] = []
    for row in _integration_rows(repo_root):
        if str(row.get("status", "")).strip() == "integrated":
            continue
        violations.append(
            {
                "code": "integration_target_not_using_vpath",
                "file_path": str(row.get("file_path", "")).strip(),
                "message": "integration target '{}' does not route its governed roots through the virtual path layer".format(str(row.get("surface", "")).strip()),
                "rule_id": "INV-VPATH-USED-FOR-STORE_ACCESS",
            }
        )
    for hit in _collect_hardcoded_path_hits(repo_root):
        if str(hit.get("classification", "")).strip() != "remaining":
            continue
        violations.append(
            {
                "code": "hardcoded_relative_root",
                "file_path": str(hit.get("file_path", "")).strip(),
                "message": "hardcoded repository-relative path root remains outside the governed virtual path layer",
                "rule_id": "INV-NO-HARDCODED-PATHS",
            }
        )
    for hit in _collect_separator_hits(repo_root):
        violations.append(
            {
                "code": "os_separator_literal",
                "file_path": str(hit.get("file_path", "")).strip(),
                "message": "OS-specific path separator literal leaked into a governed path surface",
                "rule_id": "INV-NO-HARDCODED-PATHS",
            }
        )
    unique = {
        (str(row.get("code", "")).strip(), str(row.get("file_path", "")).strip(), str(row.get("rule_id", "")).strip()): dict(row)
        for row in violations
    }
    return sorted(unique.values(), key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("rule_id"))))


def build_virtual_paths_report(repo_root: str) -> dict:
    registry_payload, registry_error = load_virtual_root_registry(repo_root)
    registry_rows = list(_as_map(registry_payload.get("record")).get("entries") or []) if not registry_error else []
    integration_rows = _integration_rows(repo_root)
    hardcoded_hits = _collect_hardcoded_path_hits(repo_root)
    separator_hits = _collect_separator_hits(repo_root)
    report = {
        "result": "complete" if not registry_error else "refused",
        "report_id": "repo.layout.virtual_paths.v1",
        "registry_rows": [dict(row) for row in registry_rows],
        "resolution_order": list(RESOLUTION_ORDER),
        "repo_wrapper_projection": _repo_wrapper_projection(repo_root),
        "integration_rows": integration_rows,
        "hardcoded_path_hits": hardcoded_hits,
        "os_separator_hits": separator_hits,
        "violations": virtual_paths_violations(repo_root),
        "metrics": {
            "registry_root_count": int(len(registry_rows)),
            "integration_target_count": int(len(integration_rows)),
            "integration_remaining_count": int(sum(1 for row in integration_rows if str(row.get("status", "")).strip() != "integrated")),
            "shim_hit_count": int(sum(1 for row in hardcoded_hits if str(row.get("classification", "")).strip() == "shim")),
            "allowed_packaging_hit_count": int(sum(1 for row in hardcoded_hits if str(row.get("classification", "")).strip() == "allowed_packaging_layout")),
            "remaining_hardcoded_hit_count": int(sum(1 for row in hardcoded_hits if str(row.get("classification", "")).strip() == "remaining")),
            "os_separator_hit_count": int(len(separator_hits)),
        },
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_virtual_paths_doc(report: Mapping[str, object]) -> str:
    rows = list(report.get("registry_rows") or [])
    lines = [
        "Status: CANONICAL",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: APPSHELL/LIB",
        "Replacement Target: release-pinned install discovery and virtual root contract",
        "",
        "# Virtual Paths",
        "",
        "AppShell owns deterministic logical-root resolution for packs, profiles, instances, saves, exports, logs, and IPC metadata.",
        "",
        "## Logical Roots",
        "",
        "| VROOT | Portable Default | Installed Pattern | Purpose |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` | {} |".format(
                _token(row_map.get("vroot_id")),
                _token(row_map.get("portable_default_rel")) or ".",
                _token(row_map.get("installed_default_pattern")),
                _token(row_map.get("description")),
            )
        )
    lines.extend(
        (
            "",
            "## Resolution Order",
            "",
            *RESOLUTION_ORDER,
            "",
            "## API",
            "",
            "- `vpath_init(context)` resolves and fingerprints the active root map.",
            "- `vpath_resolve(vroot_id, relative_path)` normalizes separators and joins under the resolved root.",
            "- `vpath_exists`, `vpath_list`, `vpath_open_read`, and `vpath_open_write` operate only through resolved virtual roots.",
            "",
            "## Refusal And Logging",
            "",
            "- AppShell refuses launch with `refusal.install.not_found` when no governed install root can be resolved.",
            "- Successful initialization emits `appshell.paths.initialized` before pack validation, negotiation, or UI startup.",
            "- Repo-wrapper runs remain available through the explicit `repo_wrapper_shim` resolution source and are logged as a warning-bearing development shim outside the authoritative install discovery order.",
        )
    )
    return "\n".join(lines) + "\n"


def render_virtual_paths_baseline(report: Mapping[str, object]) -> str:
    rows = list(report.get("registry_rows") or [])
    integration_rows = list(report.get("integration_rows") or [])
    hardcoded_hits = list(report.get("hardcoded_path_hits") or [])
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: release-pinned install discovery and virtual root contract",
        "",
        "# Virtual Paths Baseline",
        "",
        "Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "",
        "## Roots Table",
        "",
        "| VROOT | Portable Default | Installed Pattern |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` |".format(
                _token(row_map.get("vroot_id")),
                _token(row_map.get("portable_default_rel")) or ".",
                _token(row_map.get("installed_default_pattern")),
            )
        )
    lines.extend(
        (
            "",
            "## Resolution Order",
            "",
            *["- {}".format(step) for step in report.get("resolution_order") or []],
            "",
            "## Repo Wrapper Projection",
            "",
            "- result: `{}`".format(_token(_as_map(report.get("repo_wrapper_projection")).get("result"))),
            "- resolution_source: `{}`".format(_token(_as_map(report.get("repo_wrapper_projection")).get("resolution_source"))),
            "",
            "| Root | Repo-Normalized Path |",
            "| --- | --- |",
        )
    )
    for key, value in sorted(_as_map(_as_map(report.get("repo_wrapper_projection")).get("roots")).items(), key=lambda item: str(item[0])):
        lines.append("| `{}` | `{}` |".format(_token(key), _token(value)))
    lines.extend(
        (
            "",
            "## Integration Coverage",
            "",
            "| Surface | File | Status | Markers |",
            "| --- | --- | --- | --- |",
        )
    )
    for row in integration_rows:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}/{}` |".format(
                _token(row.get("surface")),
                _token(row.get("file_path")),
                _token(row.get("status")),
                int(row.get("matched_marker_count", 0) or 0),
                int(row.get("required_marker_count", 0) or 0),
            )
        )
    lines.extend(
        (
            "",
            "## Remaining Hardcoded Path Coverage",
            "",
            "- remaining hardcoded hits: `{}`".format(int(_as_map(report.get("metrics")).get("remaining_hardcoded_hit_count", 0) or 0)),
            "- shim hits: `{}`".format(int(_as_map(report.get("metrics")).get("shim_hit_count", 0) or 0)),
            "- allowed packaging-layout hits: `{}`".format(int(_as_map(report.get("metrics")).get("allowed_packaging_hit_count", 0) or 0)),
            "- OS separator hits: `{}`".format(int(_as_map(report.get("metrics")).get("os_separator_hit_count", 0) or 0)),
            "",
            "| Classification | File | Line |",
            "| --- | --- | --- |",
        )
    )
    if hardcoded_hits:
        for row in hardcoded_hits[:24]:
            lines.append(
                "| `{}` | `{}` | `{}` |".format(
                    _token(row.get("classification")),
                    _token(row.get("file_path")),
                    int(row.get("line_number", 0) or 0),
                )
            )
    else:
        lines.append("| `none` | `-` | `0` |")
    lines.extend(
        (
            "",
            "## Integration Coverage Report",
            "",
            "- Path resolution is centralized in `appshell/paths/virtual_paths.py` after install discovery is resolved by `lib/install/install_discovery_engine.py`.",
            "- AppShell now refuses launches that do not resolve a governed install root with `refusal.install.not_found`.",
            "- Remaining path literals are limited to explicit shims and packaging-layout builders, not authoritative runtime root discovery.",
        )
    )
    return "\n".join(lines) + "\n"


def render_virtual_paths_bundle(report: Mapping[str, object]) -> dict[str, str]:
    return {
        VIRTUAL_PATHS_DOC_PATH: render_virtual_paths_doc(report),
        VIRTUAL_PATHS_BASELINE_PATH: render_virtual_paths_baseline(report),
    }


def write_virtual_paths_outputs(repo_root: str, report: Mapping[str, object]) -> dict[str, str]:
    written: dict[str, str] = {}
    root = os.path.normpath(os.path.abspath(repo_root))
    for rel_path, text in render_virtual_paths_bundle(report).items():
        abs_path = os.path.join(root, rel_path.replace("/", os.sep))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        written[rel_path] = abs_path.replace("\\", "/")
    report_abs = os.path.join(root, VIRTUAL_PATHS_REPORT_PATH.replace("/", os.sep))
    os.makedirs(os.path.dirname(report_abs), exist_ok=True)
    with open(report_abs, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(report), handle, indent=2, sort_keys=True)
        handle.write("\n")
    written[VIRTUAL_PATHS_REPORT_PATH] = report_abs.replace("\\", "/")
    return dict(sorted(written.items()))


__all__ = [
    "VIRTUAL_PATHS_BASELINE_PATH",
    "VIRTUAL_PATHS_DOC_PATH",
    "VIRTUAL_PATHS_ENGINE_PATH",
    "VIRTUAL_PATHS_REPORT_PATH",
    "VIRTUAL_ROOT_REGISTRY_PATH",
    "build_virtual_paths_report",
    "virtual_paths_violations",
    "write_virtual_paths_outputs",
]
