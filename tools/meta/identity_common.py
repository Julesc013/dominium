"""Shared UNIVERSAL-ID reporting helpers."""

from __future__ import annotations

import os
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in os.sys.path:
    os.sys.path.insert(0, REPO_ROOT_HINT)


from src.meta.identity import (  # noqa: E402
    IDENTITY_KINDS,
    UNIVERSAL_IDENTITY_FIELD,
    validate_identity_repo,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256  # noqa: E402


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "UNIVERSAL_IDENTITY0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "meta", "UNIVERSAL_IDENTITY_MODEL.md")
INTEGRATION_MAP_DOC_REL = os.path.join("docs", "meta", "IDENTITY_INTEGRATION_MAP.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "UNIVERSAL_IDENTITY_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "universal_identity_report.json")
RULE_WARN = "INV-ARTIFACTS-MUST-HAVE-UNIVERSAL-IDENTITY"
RULE_NAMESPACED = "INV-IDENTITY-NAMESPACED"
RULE_CANONICAL = "INV-IDENTITY-CANONICAL-SERIALIZED"
LAST_REVIEWED = "2026-03-14"
STRICT_MISSING_POLICY_ACTIVE = False


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def build_identity_report(repo_root: str, *, strict_missing: bool = False) -> dict:
    root = _norm(repo_root)
    validation = validate_identity_repo(root, strict_missing=strict_missing)
    reports = list(validation.get("reports") or [])
    integration_rows = []
    for row in reports:
        item = dict(row or {})
        integration_rows.append(
            {
                "path": _token(item.get("path")),
                "result": _token(item.get("result")) or "complete",
                "error_count": len(list(item.get("errors") or [])),
                "warning_count": len(list(item.get("warnings") or [])),
                "identity_kind_id": _token(dict(item.get("expected") or {}).get("identity_kind_id")),
                "identity_present": bool(item.get("identity_block")),
            }
        )
    integration_rows = sorted(
        integration_rows,
        key=lambda row: (_token(row.get("path")), _token(row.get("identity_kind_id"))),
    )
    report = {
        "report_id": "universal_identity.report.v1",
        "result": _token(validation.get("result")) or "complete",
        "strict_missing": bool(strict_missing),
        "identity_kind_ids": list(IDENTITY_KINDS),
        "artifact_count": len(reports),
        "error_count": int(validation.get("error_count") or 0),
        "warning_count": int(validation.get("warning_count") or 0),
        "integration_rows": integration_rows,
        "reports": reports,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_identity_baseline(report: Mapping[str, object]) -> str:
    rows = list(report.get("integration_rows") or [])
    present_count = sum(1 for row in rows if bool(dict(row or {}).get("identity_present")))
    warning_count = int(report.get("warning_count") or 0)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: UNIVERSAL-ID",
        "Replacement Target: contract-pinned universal identity enforcement after v0.0.0-mock",
        "",
        "# Universal Identity Baseline",
        "",
        "## Identity Kinds",
        "",
    ]
    for identity_kind in IDENTITY_KINDS:
        lines.append("- `{}`".format(identity_kind))
    lines += [
        "",
        "## Required Fields Per Kind",
        "",
        "- `identity.pack`: `content_hash`, `semver`",
        "- `identity.product_binary`: `content_hash`, `build_id`",
        "- `identity.save`: `contract_bundle_hash`, `format_version`",
        "- `identity.protocol`: `protocol_range`",
        "- `identity.schema`: `content_hash`, `schema_version`",
        "",
        "## Integration Status",
        "",
        "- Artifacts scanned: `{}`".format(int(report.get("artifact_count") or 0)),
        "- Embedded identity blocks present: `{}`".format(int(present_count)),
        "- Missing-block warnings: `{}`".format(warning_count),
        "- Current policy: missing blocks warn in `v0.0.0-mock`; malformed blocks refuse",
        "",
        "## Readiness",
        "",
        "- Universal identity validator is ready for `validate.identity`",
        "- Major distribution/update/trust manifests can embed `universal_identity_block` additively",
        "- DIST-7 packaging can carry identity blocks in shipped manifests without changing runtime semantics",
        "",
    ]
    return "\n".join(lines)


def write_identity_artifacts(repo_root: str, *, strict_missing: bool = False) -> dict:
    root = _norm(repo_root)
    report = build_identity_report(root, strict_missing=strict_missing)
    _write_json(os.path.join(root, REPORT_JSON_REL), report)
    _write_text(os.path.join(root, BASELINE_DOC_REL), render_identity_baseline(report))
    return report


def identity_violations(repo_root: str, *, strict_missing: bool = False) -> list[dict]:
    root = _norm(repo_root)
    findings: list[dict] = []
    required_files = (
        (RETRO_AUDIT_DOC_REL, "UNIVERSAL-ID retro audit is required", RULE_WARN),
        (DOCTRINE_DOC_REL, "universal identity doctrine is required", RULE_WARN),
        (INTEGRATION_MAP_DOC_REL, "identity integration map is required", RULE_WARN),
        (os.path.join("schema", "meta", "universal_identity_block.schema"), "universal identity schema is required", RULE_CANONICAL),
        (os.path.join("schemas", "universal_identity_block.schema.json"), "compiled universal identity schema is required", RULE_CANONICAL),
        (os.path.join("data", "registries", "identity_kind_registry.json"), "identity kind registry is required", RULE_NAMESPACED),
        (os.path.join("src", "meta", "identity", "identity_validator.py"), "identity validator is required", RULE_CANONICAL),
        (os.path.join("tools", "meta", "identity_common.py"), "identity helper is required", RULE_CANONICAL),
        (os.path.join("tools", "meta", "tool_print_identity.py"), "identity print tool is required", RULE_WARN),
        (os.path.join("tools", "meta", "tool_diff_identity.py"), "identity diff tool is required", RULE_WARN),
        (BASELINE_DOC_REL, "universal identity baseline is required", RULE_WARN),
        (REPORT_JSON_REL, "universal identity machine report is required", RULE_WARN),
    )
    for rel_path, message, rule_id in required_files:
        if os.path.isfile(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        findings.append(
            {
                "file_path": rel_path,
                "code": "identity_required_file_missing",
                "message": message,
                "rule_id": rule_id,
            }
        )
    validation = validate_identity_repo(root, strict_missing=strict_missing)
    for row in list(validation.get("reports") or []):
        item = dict(row or {})
        rel_path = _token(item.get("path"))
        for error in list(item.get("errors") or []):
            error_row = dict(error or {})
            findings.append(
                {
                    "file_path": rel_path or _token(error_row.get("path")),
                    "code": _token(error_row.get("code")) or "identity_validation_error",
                    "message": _token(error_row.get("message")) or "universal identity validation failed",
                    "rule_id": RULE_CANONICAL if "fingerprint" in _token(error_row.get("code")) else RULE_NAMESPACED,
                }
            )
        for warning in list(item.get("warnings") or []):
            warning_row = dict(warning or {})
            findings.append(
                {
                    "file_path": rel_path or _token(warning_row.get("path")),
                    "code": _token(warning_row.get("code")) or "identity_validation_warning",
                    "message": _token(warning_row.get("message")) or "universal identity warning",
                    "rule_id": RULE_WARN,
                }
            )
    return sorted(
        findings,
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
    )


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "INTEGRATION_MAP_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_CANONICAL",
    "RULE_NAMESPACED",
    "RULE_WARN",
    "STRICT_MISSING_POLICY_ACTIVE",
    "build_identity_report",
    "identity_violations",
    "render_identity_baseline",
    "write_identity_artifacts",
]
