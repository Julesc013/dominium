"""Deterministic reporting and enforcement helpers for REPO-LAYOUT-1."""

from __future__ import annotations

import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.compat.shims import legacy_flag_rows, path_shim_rows, tool_shim_rows, validation_shim_rows  # noqa: E402
from src.validation import validation_surface_rows  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


SHIM_POLICY_DOC_PATH = "docs/restructure/SHIM_POLICY.md"
FLAG_MIGRATION_DOC_PATH = "docs/appshell/FLAG_MIGRATION.md"
SHIM_COVERAGE_REPORT_PATH = "docs/audit/SHIM_COVERAGE_REPORT.md"
SHIM_TOOL_PATH = "tools/release/tool_run_shim_coverage.py"
PATH_SHIMS_PATH = "src/compat/shims/path_shims.py"
FLAG_SHIMS_PATH = "src/compat/shims/flag_shims.py"
TOOL_SHIMS_PATH = "src/compat/shims/tool_shims.py"
VALIDATION_SHIMS_PATH = "src/compat/shims/validation_shims.py"

_INTEGRATION_TARGETS = (
    {
        "integration_id": "bootstrap_flag_shims",
        "file_path": "src/appshell/bootstrap.py",
        "required_tokens": ("apply_flag_shims(",),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "AppShell bootstrap must apply centralized legacy flag shims before shell argument resolution.",
    },
    {
        "integration_id": "entrypoint_report_flag_shims",
        "file_path": "tools/release/entrypoint_unify_common.py",
        "required_tokens": ("apply_flag_shims(",),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "Entrypoint unify reporting must reflect centralized legacy flag shims.",
    },
    {
        "integration_id": "distribution_path_shims",
        "file_path": "tools/distribution/distribution_lib.py",
        "required_tokens": ("redirect_legacy_path(",),
        "rule_id": "INV-SHIMS-MUST-NOT-BYPASS-VALIDATION",
        "message": "Legacy pack discovery roots must redirect through the governed path shim layer.",
    },
    {
        "integration_id": "pack_validate_tool_shim",
        "file_path": "tools/pack/pack_validate.py",
        "required_tokens": ("emit_legacy_tool_warning(", "redirect_legacy_path("),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "Legacy pack_validate entrypoint must emit a deprecation warning and redirect legacy paths through vpath shims.",
    },
    {
        "integration_id": "pack_migrate_tool_shim",
        "file_path": "tools/pack/migrate_capability_gating.py",
        "required_tokens": ("emit_legacy_tool_warning(", "redirect_legacy_path("),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "Legacy capability-gating migration entrypoint must emit a deprecation warning and redirect legacy paths through vpath shims.",
    },
    {
        "integration_id": "legacy_validate_all_shim",
        "file_path": "tools/ci/validate_all.py",
        "required_tokens": ("run_legacy_validate_all(",),
        "rule_id": "INV-SHIMS-MUST-NOT-BYPASS-VALIDATION",
        "message": "Legacy validate_all wrapper must route into the unified validation pipeline.",
    },
)
_WARNING_TOKEN_CHECKS = (
    {
        "file_path": PATH_SHIMS_PATH,
        "tokens": ("warn.deprecated_path_usage", "emit_deprecation_warning(", "vpath_resolve("),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "path shims must emit deterministic deprecation warnings and resolve through vpath.",
    },
    {
        "file_path": FLAG_SHIMS_PATH,
        "tokens": ("warn.deprecated_flag_usage", "build_shim_stability(",),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "flag shims must declare provisional stability and deterministic deprecation warnings.",
    },
    {
        "file_path": TOOL_SHIMS_PATH,
        "tokens": ("warn.deprecated_tool_usage", "emit_deprecation_warning("),
        "rule_id": "INV-SHIMS-MUST-LOG-DEPRECATION",
        "message": "tool shims must emit deterministic deprecation warnings.",
    },
    {
        "file_path": VALIDATION_SHIMS_PATH,
        "tokens": ("warn.deprecated_validator_usage", "build_validation_report(", "write_validation_outputs("),
        "rule_id": "INV-SHIMS-MUST-NOT-BYPASS-VALIDATION",
        "message": "validation shims must emit deterministic deprecation warnings and route through the unified validation pipeline.",
    },
)


def _token(value: object) -> str:
    return str(value or "").strip()


def _read_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def _integration_rows(repo_root: str) -> list[dict]:
    rows: list[dict] = []
    for target in _INTEGRATION_TARGETS:
        text = _read_text(repo_root, str(target.get("file_path")))
        tokens = list(target.get("required_tokens") or [])
        matched = [token for token in tokens if token in text]
        rows.append(
            {
                "integration_id": _token(target.get("integration_id")),
                "file_path": _token(target.get("file_path")),
                "required_tokens": tokens,
                "matched_tokens": matched,
                "status": "integrated" if len(matched) == len(tokens) else "missing",
                "message": _token(target.get("message")),
                "rule_id": _token(target.get("rule_id")),
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("status")), _token(row.get("file_path")), _token(row.get("integration_id"))))


def _warning_rows(repo_root: str) -> list[dict]:
    rows: list[dict] = []
    for target in _WARNING_TOKEN_CHECKS:
        text = _read_text(repo_root, str(target.get("file_path")))
        tokens = list(target.get("tokens") or [])
        matched = [token for token in tokens if token in text]
        rows.append(
            {
                "file_path": _token(target.get("file_path")),
                "required_tokens": tokens,
                "matched_tokens": matched,
                "status": "complete" if len(matched) == len(tokens) else "missing",
                "message": _token(target.get("message")),
                "rule_id": _token(target.get("rule_id")),
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("status")), _token(row.get("file_path"))))


def shim_coverage_violations(repo_root: str) -> list[dict]:
    violations: list[dict] = []
    for row in _integration_rows(repo_root):
        if _token(row.get("status")) == "integrated":
            continue
        violations.append(
            {
                "code": "shim_integration_missing",
                "file_path": _token(row.get("file_path")),
                "message": _token(row.get("message")) or "shim integration is missing",
                "rule_id": _token(row.get("rule_id")) or "INV-SHIMS-MUST-LOG-DEPRECATION",
            }
        )
    for row in _warning_rows(repo_root):
        if _token(row.get("status")) == "complete":
            continue
        violations.append(
            {
                "code": "shim_warning_missing",
                "file_path": _token(row.get("file_path")),
                "message": _token(row.get("message")) or "shim deprecation warning surface is incomplete",
                "rule_id": _token(row.get("rule_id")) or "INV-SHIMS-MUST-LOG-DEPRECATION",
            }
        )
    return sorted(violations, key=lambda row: (_token(row.get("rule_id")), _token(row.get("file_path")), _token(row.get("code"))))


def _legacy_validation_remainders(repo_root: str) -> list[dict]:
    rows = []
    for row in validation_surface_rows(repo_root):
        row_map = dict(row or {})
        path = _token(row_map.get("path"))
        if path in {"tools/ci/validate_all.py"}:
            continue
        rows.append(
            {
                "path": path,
                "surface_id": _token(row_map.get("surface_id")),
                "status": _token(row_map.get("status")),
                "replacement_target": _token(row_map.get("replacement_target")),
            }
        )
    return sorted(rows, key=lambda row: (_token(row.get("status")), _token(row.get("path")), _token(row.get("surface_id"))))


def build_shim_coverage_report(repo_root: str) -> dict:
    root = os.path.normpath(os.path.abspath(repo_root))
    report = {
        "result": "complete",
        "report_id": "repo.layout.shims.v1",
        "shim_rows": {
            "path": path_shim_rows(),
            "flag": legacy_flag_rows(),
            "tool": tool_shim_rows(),
            "validation": validation_shim_rows(),
        },
        "integration_rows": _integration_rows(root),
        "warning_rows": _warning_rows(root),
        "remaining_legacy_assumptions": _legacy_validation_remainders(root),
        "violations": shim_coverage_violations(root),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_shim_coverage_report(report: Mapping[str, object]) -> str:
    shim_rows = dict(report.get("shim_rows") or {})
    lines = [
        "Status: DERIVED",
        "Last Reviewed: 2026-03-13",
        "Stability: provisional",
        "Future Series: DOC-CONVERGENCE",
        "Replacement Target: regenerated shim coverage report after convergence cleanup",
        "",
        "# Shim Coverage Report",
        "",
        "- Fingerprint: `{}`".format(_token(report.get("deterministic_fingerprint"))),
        "- Violations: `{}`".format(int(len(list(report.get("violations") or [])))),
        "",
        "## Shim Surfaces",
        "",
        "| Category | Legacy Surface | Replacement | Shim ID |",
        "| --- | --- | --- | --- |",
    ]
    for category in ("path", "flag", "tool", "validation"):
        for row in list(shim_rows.get(category) or []):
            row_map = dict(row or {})
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` |".format(
                    category,
                    _token(row_map.get("legacy_surface")) or _token(row_map.get("legacy_flag")),
                    _token(row_map.get("replacement_surface")) or "{} {}".format(_token(row_map.get("replacement_flag")), _token(row_map.get("replacement_value"))).strip(),
                    _token(row_map.get("shim_id")),
                )
            )
    lines.extend(
        (
            "",
            "## Integration Coverage",
            "",
            "| File | Status | Required Tokens |",
            "| --- | --- | --- |",
        )
    )
    for row in list(report.get("integration_rows") or []):
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` |".format(
                _token(row_map.get("file_path")),
                _token(row_map.get("status")),
                "`, `".join(_token(token) for token in list(row_map.get("required_tokens") or [])),
            )
        )
    lines.extend(
        (
            "",
            "## Warning Coverage",
            "",
            "| File | Status | Required Tokens |",
            "| --- | --- | --- |",
        )
    )
    for row in list(report.get("warning_rows") or []):
        row_map = dict(row or {})
        lines.append(
            "| `{}` | `{}` | `{}` |".format(
                _token(row_map.get("file_path")),
                _token(row_map.get("status")),
                "`, `".join(_token(token) for token in list(row_map.get("required_tokens") or [])),
            )
        )
    lines.extend(("", "## Known Remaining Legacy Assumptions", ""))
    remaining = list(report.get("remaining_legacy_assumptions") or [])
    if not remaining:
        lines.append("- No remaining legacy validation surfaces were detected outside the governed shim layer.")
    else:
        for row in remaining[:20]:
            row_map = dict(row or {})
            lines.append(
                "- surface_id=`{}` path=`{}` status=`{}` replacement_target=`{}`".format(
                    _token(row_map.get("surface_id")),
                    _token(row_map.get("path")),
                    _token(row_map.get("status")),
                    _token(row_map.get("replacement_target")),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def write_shim_coverage_report(repo_root: str) -> dict:
    report = build_shim_coverage_report(repo_root)
    target = os.path.join(repo_root, SHIM_COVERAGE_REPORT_PATH.replace("/", os.sep))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_shim_coverage_report(report))
    return report


__all__ = [
    "FLAG_MIGRATION_DOC_PATH",
    "FLAG_SHIMS_PATH",
    "PATH_SHIMS_PATH",
    "SHIM_COVERAGE_REPORT_PATH",
    "SHIM_POLICY_DOC_PATH",
    "SHIM_TOOL_PATH",
    "TOOL_SHIMS_PATH",
    "VALIDATION_SHIMS_PATH",
    "build_shim_coverage_report",
    "render_shim_coverage_report",
    "shim_coverage_violations",
    "write_shim_coverage_report",
]
