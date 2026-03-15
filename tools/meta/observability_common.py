"""Deterministic OBSERVABILITY-0 helpers."""

from __future__ import annotations

import json
import os
import re
from typing import Mapping

from src.meta.stability import build_stability_marker
from src.meta.observability import (
    load_log_category_registry,
    load_log_message_key_registry,
    load_observability_guarantee_registry,
)
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "OBSERVABILITY0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "meta", "OBSERVABILITY_CONTRACT.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "OBSERVABILITY_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "observability_report.json")
GUARANTEE_SCHEMA_REL = os.path.join("schema", "meta", "observability_guarantee.schema")
GUARANTEE_SCHEMA_JSON_REL = os.path.join("schemas", "observability_guarantee.schema.json")
GUARANTEE_REGISTRY_REL = os.path.join("data", "registries", "observability_guarantee_registry.json")
RULE_GUARANTEES = "INV-GUARANTEED-CATEGORIES-LOGGED"
RULE_SECRETS = "INV-NO-SECRETS-IN-LOGS"
LAST_REVIEWED = "2026-03-14"

DIAG_MINIMUM_REL_PATHS = [
    "events/canonical_events.json",
    "events/negotiation_records.json",
    "logs/log_events.jsonl",
    "packs/pack_verification_report.json",
    "plans/install_plan.json",
    "plans/update_plan.json",
    "proofs/proof_anchors.json",
]
REQUIRED_MESSAGE_KEYS = {
    "compat": [
        "compat.install.refused",
        "compat.install_selected",
        "compat.negotiation.read_only",
        "compat.negotiation.refused",
        "compat.negotiation.result",
    ],
    "packs": [
        "packs.lock.generated",
        "packs.verify.result",
    ],
    "lib": [
        "lib.install.apply",
        "lib.install.plan",
        "lib.install.status",
        "lib.instance.migrated",
        "lib.save.migrated",
    ],
    "update": [
        "update.apply.completed",
        "update.check.result",
        "update.plan.generated",
        "update.rollback.completed",
    ],
    "supervisor": [
        "explain.supervisor_restart",
        "explain.supervisor_stop",
        "supervisor.child.crash_requested",
        "supervisor.child.ready",
        "supervisor.child.stdin_ignored",
        "supervisor.child.stop_requested",
        "supervisor.command.attach",
        "supervisor.command.start",
        "supervisor.command.stop",
        "supervisor.process.spawned",
        "supervisor.restart.applied",
        "supervisor.service.ready",
        "supervisor.start.complete",
    ],
    "server": [
        "server.log.event",
        "server.proof_anchor.emitted",
    ],
    "diag": [
        "diag.capture.written",
        "diag.snapshot.written",
    ],
    "refusal": [
        "appshell.refusal",
    ],
}
PRINTF_SCAN_FILES = (
    "src/appshell/logging/log_engine.py",
    "src/diag/repro_bundle_builder.py",
    "src/server/net/loopback_transport.py",
    "src/server/runtime/tick_loop.py",
    "src/appshell/diag/diag_snapshot.py",
)
INTEGRATION_TOKENS = (
    ("src/appshell/logging/log_engine.py", "validate_observability_event(", "runtime log engine must validate guaranteed-category events", RULE_GUARANTEES),
    ("src/appshell/logging/log_engine.py", "redact_observability_mapping(", "runtime log engine must redact secret-like fields", RULE_SECRETS),
    ("src/diag/repro_bundle_builder.py", "pack_verification_report.json", "repro bundle must include the pack verification report surface", RULE_GUARANTEES),
    ("src/diag/repro_bundle_builder.py", "install_plan.json", "repro bundle must include the install-plan surface", RULE_GUARANTEES),
    ("src/diag/repro_bundle_builder.py", "update_plan.json", "repro bundle must include the update-plan surface", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "update.check.result", "setup update check must emit the guaranteed update category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "update.plan.generated", "setup update plan must emit the guaranteed update category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "update.apply.completed", "setup update apply must emit the guaranteed update category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "update.rollback.completed", "setup rollback must emit the guaranteed update category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "lib.install.status", "setup install status must emit the guaranteed lib category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "lib.install.plan", "setup install planning must emit the guaranteed lib category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "lib.install.apply", "setup install apply must emit the guaranteed lib category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "lib.save.migrated", "setup save migration must emit the guaranteed lib category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "lib.instance.migrated", "setup instance migration must emit the guaranteed lib category", RULE_GUARANTEES),
    ("src/appshell/supervisor/supervisor_engine.py", "category=\"supervisor\"", "supervisor runtime events must emit under the supervisor category", RULE_GUARANTEES),
    ("tools/appshell/supervisor_service.py", "category=\"supervisor\"", "supervisor service readiness must emit under the supervisor category", RULE_GUARANTEES),
    ("tools/appshell/supervised_product_host.py", "category=\"supervisor\"", "supervised child lifecycle events must emit under the supervisor category", RULE_GUARANTEES),
    ("tools/setup/setup_cli.py", "appshell.refusal", "setup refusal paths must emit the refusal category", RULE_GUARANTEES),
)
PRINT_RE = re.compile(r"\bprint\s*\(")


def _token(value: object) -> str:
    return str(value or "").strip()


def _norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(_token(path) or "."))


def _norm_rel(path: str) -> str:
    return _token(path).replace("\\", "/")


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list[object]:
    return list(value or []) if isinstance(value, list) else []


def _normalize_tree(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _normalize_tree(item)
            for key, item in sorted(dict(value).items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, list):
        return [_normalize_tree(item) for item in list(value)]
    if isinstance(value, tuple):
        return [_normalize_tree(item) for item in list(value)]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


def _sorted_unique_strings(values: object) -> list[str]:
    return sorted({_token(value) for value in _as_list(values) if _token(value)})


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(canonical_json_text(dict(payload or {})))
        handle.write("\n")
    return target


def _write_text(path: str, text: str) -> str:
    target = _norm(path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(str(text or "").replace("\r\n", "\n"))
    return target


def _file_text(repo_root: str, rel_path: str) -> str:
    abs_path = os.path.join(_norm(repo_root), rel_path.replace("/", os.sep))
    try:
        with open(abs_path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _default_guarantee_stability(category_id: str) -> dict:
    token = _token(category_id)
    return build_stability_marker(
        stability_class_id="provisional",
        rationale="Guaranteed observability category '{}' is frozen for v0.0.0-mock while message expansion remains additive.".format(token),
        future_series="OBSERVABILITY/DIAG",
        replacement_target="Release-pinned observability guarantee bundles and per-channel message governance.",
        extensions={"category_id": token, "id_stability": "stable"},
    )


def _canonicalize_guarantee_row(payload: Mapping[str, object] | None) -> dict:
    row = _as_map(payload)
    category_id = _token(row.get("category_id"))
    normalized = {
        "category_id": category_id,
        "guaranteed": bool(row.get("guaranteed", False)),
        "minimum_fields": _sorted_unique_strings(row.get("minimum_fields")),
        "redaction_policy_id": _token(row.get("redaction_policy_id")),
        "deterministic_fingerprint": _token(row.get("deterministic_fingerprint")),
        "extensions": dict(_normalize_tree(_as_map(row.get("extensions")))),
        "stability": dict(_normalize_tree(_as_map(row.get("stability")) or _default_guarantee_stability(category_id))),
    }
    normalized["deterministic_fingerprint"] = canonical_sha256(dict(normalized, deterministic_fingerprint=""))
    return normalized


def canonicalize_observability_guarantee_registry(payload: Mapping[str, object] | None) -> dict:
    item = _as_map(payload)
    record = _as_map(item.get("record"))
    rows = sorted(
        (
            _canonicalize_guarantee_row(row)
            for row in _as_list(record.get("guarantees"))
            if isinstance(row, Mapping)
        ),
        key=lambda row: _token(row.get("category_id")),
    )
    normalized_record = {
        "registry_id": _token(record.get("registry_id")) or "dominium.registry.meta.observability_guarantee_registry",
        "guarantees": rows,
        "deterministic_fingerprint": "",
        "extensions": dict(_normalize_tree(_as_map(record.get("extensions")))),
    }
    normalized_record["deterministic_fingerprint"] = canonical_sha256(dict(normalized_record, deterministic_fingerprint=""))
    return {
        "schema_id": _token(item.get("schema_id")) or "dominium.registry.meta.observability_guarantee_registry",
        "schema_version": _token(item.get("schema_version")) or "1.0.0",
        "record": normalized_record,
    }


def write_observability_registry(repo_root: str) -> str:
    root = _norm(repo_root)
    payload = load_observability_guarantee_registry(root)
    target = _write_json(
        os.path.join(root, GUARANTEE_REGISTRY_REL),
        canonicalize_observability_guarantee_registry(payload),
    )
    load_observability_guarantee_registry.cache_clear()
    return target


def _guarantee_rows(repo_root: str) -> list[dict]:
    rows = list(_as_map(load_observability_guarantee_registry(repo_root).get("record")).get("guarantees") or [])
    return sorted((dict(row) for row in rows if isinstance(row, Mapping)), key=lambda row: _token(row.get("category_id")))


def _category_ids(repo_root: str) -> set[str]:
    rows = list(_as_map(load_log_category_registry(repo_root).get("record")).get("categories") or [])
    return {_token(dict(row).get("category_id")) for row in rows if isinstance(row, Mapping) and _token(dict(row).get("category_id"))}


def _message_rows(repo_root: str) -> list[dict]:
    rows = list(_as_map(load_log_message_key_registry(repo_root).get("record")).get("messages") or [])
    return sorted((dict(row) for row in rows if isinstance(row, Mapping)), key=lambda row: _token(row.get("message_key")))


def _message_rows_by_category(repo_root: str) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in _message_rows(repo_root):
        grouped.setdefault(_token(row.get("category_id")), []).append(row)
    return grouped


def _printf_findings(repo_root: str) -> list[dict]:
    rows = []
    for rel_path in PRINTF_SCAN_FILES:
        text = _file_text(repo_root, rel_path)
        if not text:
            continue
        if PRINT_RE.search(text):
            rows.append(
                {
                    "code": "printf_logging_present",
                    "message": "governed logging surface still contains print-style logging",
                    "file_path": rel_path,
                    "rule_id": RULE_GUARANTEES,
                }
            )
    return rows


def observability_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    for rel_path, message, rule_id in (
        (RETRO_AUDIT_DOC_REL, "OBSERVABILITY-0 retro audit is required", RULE_GUARANTEES),
        (DOCTRINE_DOC_REL, "observability contract doc is required", RULE_GUARANTEES),
        (GUARANTEE_SCHEMA_REL, "observability guarantee schema is required", RULE_GUARANTEES),
        (GUARANTEE_SCHEMA_JSON_REL, "compiled observability guarantee schema is required", RULE_GUARANTEES),
        (GUARANTEE_REGISTRY_REL, "observability guarantee registry is required", RULE_GUARANTEES),
        (os.path.join("tools", "meta", "observability_common.py"), "observability helper is required", RULE_GUARANTEES),
        (os.path.join("tools", "meta", "tool_run_observability.py"), "observability runner is required", RULE_GUARANTEES),
    ):
        if os.path.isfile(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"code": "missing_required_file", "message": message, "file_path": rel_path, "rule_id": rule_id})

    guarantee_rows = _guarantee_rows(root)
    guarantee_ids = [_token(row.get("category_id")) for row in guarantee_rows if bool(row.get("guaranteed", False))]
    category_ids = _category_ids(root)
    message_rows_by_category = _message_rows_by_category(root)
    for category_id in guarantee_ids:
        if category_id not in category_ids:
            violations.append(
                {
                    "code": "category_not_declared",
                    "message": "guaranteed category '{}' must exist in log_category_registry".format(category_id),
                    "file_path": "data/registries/log_category_registry.json",
                    "rule_id": RULE_GUARANTEES,
                }
            )
        if not message_rows_by_category.get(category_id):
            violations.append(
                {
                    "code": "category_has_no_message_keys",
                    "message": "guaranteed category '{}' must declare stable message keys".format(category_id),
                    "file_path": "data/registries/log_message_key_registry.json",
                    "rule_id": RULE_GUARANTEES,
                }
            )
        declared_keys = {_token(row.get("message_key")) for row in message_rows_by_category.get(category_id, [])}
        for message_key in REQUIRED_MESSAGE_KEYS.get(category_id, []):
            if message_key in declared_keys:
                continue
            violations.append(
                {
                    "code": "required_message_key_missing",
                    "message": "guaranteed category '{}' is missing message key '{}'".format(category_id, message_key),
                    "file_path": "data/registries/log_message_key_registry.json",
                    "rule_id": RULE_GUARANTEES,
                }
            )

    for rel_path, token, message, rule_id in INTEGRATION_TOKENS:
        if token in _file_text(root, rel_path):
            continue
        violations.append({"code": "missing_integration_hook", "message": message, "file_path": rel_path, "rule_id": rule_id})

    violations.extend(_printf_findings(root))
    return violations


def build_observability_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    guarantee_registry = load_observability_guarantee_registry(root)
    category_registry = load_log_category_registry(root)
    message_registry = load_log_message_key_registry(root)
    guarantee_rows = _guarantee_rows(root)
    message_rows = _message_rows(root)
    violations = observability_violations(root)
    message_rows_by_category = _message_rows_by_category(root)
    guaranteed_rows = [dict(row) for row in guarantee_rows if bool(row.get("guaranteed", False))]
    report = {
        "report_id": "meta.observability.v1",
        "result": "complete" if not violations else "refused",
        "last_reviewed": LAST_REVIEWED,
        "guaranteed_categories": [
            {
                "category_id": _token(row.get("category_id")),
                "minimum_fields": list(row.get("minimum_fields") or []),
                "redaction_policy_id": _token(row.get("redaction_policy_id")),
                "declared_message_keys": [
                    _token(item.get("message_key"))
                    for item in list(message_rows_by_category.get(_token(row.get("category_id")), []))
                    if _token(item.get("message_key"))
                ],
            }
            for row in guaranteed_rows
        ],
        "diag_minimum_rel_paths": list(DIAG_MINIMUM_REL_PATHS),
        "registry_hashes": {
            "observability_guarantee_registry_hash": canonical_sha256(guarantee_registry) if guarantee_registry else "",
            "log_category_registry_hash": canonical_sha256(category_registry) if category_registry else "",
            "log_message_key_registry_hash": canonical_sha256(message_registry) if message_registry else "",
        },
        "guaranteed_category_count": int(len(guaranteed_rows)),
        "message_key_count": int(len(message_rows)),
        "violations": violations,
        "ready_for_store_gc_0": not violations,
        "ready_for_dist7": not violations,
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_observability_baseline(report: Mapping[str, object]) -> str:
    payload = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Stability: provisional",
        "Future Series: OBSERVABILITY/DIAG",
        "Replacement Target: release-pinned observability policies and repro-bundle minimum-set governance",
        "",
        "# Observability Baseline",
        "",
        "- result: `{}`".format(_token(payload.get("result"))),
        "- guaranteed_category_count: `{}`".format(int(payload.get("guaranteed_category_count", 0) or 0)),
        "- message_key_count: `{}`".format(int(payload.get("message_key_count", 0) or 0)),
        "- deterministic_fingerprint: `{}`".format(_token(payload.get("deterministic_fingerprint"))),
        "",
        "## Guaranteed Categories",
        "",
    ]
    for row in list(payload.get("guaranteed_categories") or []):
        row_map = dict(row or {})
        lines.append("- `{}`: minimum_fields=`{}` redaction_policy_id=`{}`".format(
            _token(row_map.get("category_id")),
            ",".join(str(item) for item in list(row_map.get("minimum_fields") or [])),
            _token(row_map.get("redaction_policy_id")),
        ))
    lines.extend(["", "## Minimum Fields", ""])
    for row in list(payload.get("guaranteed_categories") or []):
        row_map = dict(row or {})
        lines.append("- `{}` -> `{}`".format(_token(row_map.get("category_id")), ",".join(str(item) for item in list(row_map.get("minimum_fields") or []))))
    lines.extend(["", "## DIAG Bundle Mapping", ""])
    for rel_path in list(payload.get("diag_minimum_rel_paths") or []):
        lines.append("- `{}`".format(_token(rel_path)))
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "- STORE-GC-0: `{}`".format("ready" if bool(payload.get("ready_for_store_gc_0", False)) else "blocked"),
            "- DIST-7 final packaging: `{}`".format("ready" if bool(payload.get("ready_for_dist7", False)) else "blocked"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_observability_outputs(repo_root: str) -> dict:
    root = _norm(repo_root)
    write_observability_registry(root)
    report = build_observability_report(root)
    return {
        "report": report,
        "retro_audit_doc_path": _norm_rel(os.path.join(root, RETRO_AUDIT_DOC_REL)),
        "doctrine_doc_path": _norm_rel(os.path.join(root, DOCTRINE_DOC_REL)),
        "baseline_doc_path": _norm_rel(_write_text(os.path.join(root, BASELINE_DOC_REL), render_observability_baseline(report))),
        "report_json_path": _norm_rel(_write_json(os.path.join(root, REPORT_JSON_REL), report)),
    }


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "GUARANTEE_REGISTRY_REL",
    "GUARANTEE_SCHEMA_JSON_REL",
    "GUARANTEE_SCHEMA_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_GUARANTEES",
    "RULE_SECRETS",
    "build_observability_report",
    "canonicalize_observability_guarantee_registry",
    "observability_violations",
    "render_observability_baseline",
    "write_observability_registry",
    "write_observability_outputs",
]
