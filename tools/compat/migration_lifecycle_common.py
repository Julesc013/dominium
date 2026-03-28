"""Deterministic MIGRATION-LIFECYCLE-0 helpers."""

from __future__ import annotations

import json
import os
from typing import Mapping

from compat.migration_lifecycle import (
    ARTIFACT_KIND_BLUEPRINT,
    ARTIFACT_KIND_COMPONENT_GRAPH,
    ARTIFACT_KIND_IDS,
    ARTIFACT_KIND_INSTALL_MANIFEST,
    ARTIFACT_KIND_INSTALL_PLAN,
    ARTIFACT_KIND_INSTANCE_MANIFEST,
    ARTIFACT_KIND_NEGOTIATION_RECORD,
    ARTIFACT_KIND_PACK_LOCK,
    ARTIFACT_KIND_PROFILE_BUNDLE,
    ARTIFACT_KIND_RELEASE_INDEX,
    ARTIFACT_KIND_RELEASE_MANIFEST,
    ARTIFACT_KIND_SAVE,
    ARTIFACT_KIND_SESSION_TEMPLATE,
    DECISION_MIGRATE,
    DECISION_READ_ONLY,
    DECISION_REFUSE,
    REFUSAL_MIGRATION_NO_PATH,
    determine_migration_decision,
    load_migration_policy_registry,
    load_migration_rows,
    plan_migration_path,
)
from lib.install import validate_install_manifest, write_json as write_install_json
from lib.instance import validate_instance_manifest, write_json as write_instance_json
from lib.save import migrate_save_manifest, validate_save_manifest, write_json as write_save_json
from tools.import_bridge import resolve_repo_path_equivalent
from tools.xstack.compatx.canonical_json import canonical_json_text, canonical_sha256


RETRO_AUDIT_DOC_REL = os.path.join("docs", "audit", "MIGRATION_LIFECYCLE0_RETRO_AUDIT.md")
DOCTRINE_DOC_REL = os.path.join("docs", "compat", "MIGRATION_LIFECYCLE_MODEL.md")
BASELINE_DOC_REL = os.path.join("docs", "audit", "MIGRATION_LIFECYCLE_BASELINE.md")
REPORT_JSON_REL = os.path.join("data", "audit", "migration_lifecycle_report.json")
RULE_POLICY = "INV-MIGRATION-POLICY-DECLARED-FOR-ALL-ARTIFACTS"
RULE_SILENT = "INV-NO-SILENT-MIGRATION"
RULE_READ_ONLY = "INV-READONLY-LOGGED"
LAST_REVIEWED = "2026-03-14"

_PACK_COMPAT_KIND_MAP = {
    ARTIFACT_KIND_BLUEPRINT: "blueprint_file",
    ARTIFACT_KIND_PACK_LOCK: "pack_lock",
    ARTIFACT_KIND_PROFILE_BUNDLE: "profile_bundle",
    ARTIFACT_KIND_SESSION_TEMPLATE: "session_template",
}


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


def _read_json(path: str) -> dict:
    try:
        with open(_norm(path), "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


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


def _decision_stub(artifact_kind_id: str, payload: Mapping[str, object], *, allow_read_only: bool = False, expected_contract_bundle_hash: str = "") -> dict:
    return determine_migration_decision(
        repo_root=".",
        artifact_kind_id=artifact_kind_id,
        payload=payload,
        allow_read_only=allow_read_only,
        expected_contract_bundle_hash=expected_contract_bundle_hash,
    )


def plan_artifact_migration(
    repo_root: str,
    *,
    artifact_kind_id: str,
    artifact_path: str,
    allow_read_only: bool = False,
    expected_contract_bundle_hash: str = "",
) -> dict:
    return plan_migration_path(
        repo_root,
        artifact_kind_id=artifact_kind_id,
        artifact_path=artifact_path,
        allow_read_only=allow_read_only,
        expected_contract_bundle_hash=expected_contract_bundle_hash,
    )


def apply_artifact_migration(
    repo_root: str,
    *,
    artifact_kind_id: str,
    artifact_path: str,
    output_path: str = "",
    allow_read_only: bool = False,
    expected_contract_bundle_hash: str = "",
    migration_id: str = "",
    tick_applied: int = 0,
) -> dict:
    root = _norm(repo_root)
    source_path = _norm(artifact_path)
    decision = plan_artifact_migration(
        root,
        artifact_kind_id=artifact_kind_id,
        artifact_path=source_path,
        allow_read_only=allow_read_only,
        expected_contract_bundle_hash=expected_contract_bundle_hash,
    )
    action = _token(decision.get("decision_action_id"))
    target_path = _norm(output_path) if _token(output_path) else source_path
    read_only_applied = action == DECISION_READ_ONLY
    migration_events: list[dict] = []
    wrote_output = False

    if action == DECISION_REFUSE:
        payload = {
            "result": "refused",
            "artifact_kind_id": _token(artifact_kind_id),
            "artifact_path": _norm_rel(source_path),
            "output_path": _norm_rel(target_path) if _token(output_path) else "",
            "migration_decision_record": decision,
            "refusal_code": _token(decision.get("refusal_code")) or REFUSAL_MIGRATION_NO_PATH,
            "migration_events": [],
            "read_only_applied": False,
            "wrote_output": False,
            "deterministic_fingerprint": "",
        }
        payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
        return payload

    output_payload: dict
    if _token(artifact_kind_id) in _PACK_COMPAT_KIND_MAP:
        from compat.data_format_loader import load_versioned_artifact

        migrated, meta, error = load_versioned_artifact(
            repo_root=root,
            artifact_kind=_PACK_COMPAT_KIND_MAP[_token(artifact_kind_id)],
            path=source_path,
            semantic_contract_bundle_hash=_token(expected_contract_bundle_hash),
            allow_read_only=allow_read_only,
            strip_loaded_metadata=False,
        )
        if error:
            payload = {
                "result": "refused",
                "artifact_kind_id": _token(artifact_kind_id),
                "artifact_path": _norm_rel(source_path),
                "output_path": _norm_rel(target_path) if _token(output_path) else "",
                "migration_decision_record": decision,
                "refusal_code": _token(_as_map(error.get("refusal")).get("reason_code")),
                "migration_events": [],
                "read_only_applied": False,
                "wrote_output": False,
                "deterministic_fingerprint": "",
            }
            payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
            return payload
        output_payload = dict(migrated or {})
        migration_events = [dict(row or {}) for row in _as_list(meta.get("migration_events"))]
        read_only_applied = bool(meta.get("read_only_applied", False))
        if migration_events or _token(output_path):
            _write_json(target_path, output_payload)
            wrote_output = True
    elif _token(artifact_kind_id) == ARTIFACT_KIND_SAVE:
        validation = validate_save_manifest(repo_root=root, save_manifest_path=source_path)
        output_payload = dict(validation.get("save_manifest") or {})
        if action == DECISION_MIGRATE:
            migration = migrate_save_manifest(
                repo_root=root,
                manifest_payload=output_payload,
                to_version=_token(decision.get("target_version")),
                migration_id=_token(migration_id) or _token(_as_map((_as_list(decision.get("migration_chain")) or [{}])[0]).get("migration_id")),
                tick_applied=int(tick_applied or 0),
            )
            if _token(migration.get("result")) != "complete":
                payload = {
                    "result": "refused",
                    "artifact_kind_id": _token(artifact_kind_id),
                    "artifact_path": _norm_rel(source_path),
                    "output_path": _norm_rel(target_path) if _token(output_path) else "",
                    "migration_decision_record": decision,
                    "refusal_code": _token(migration.get("refusal_code")),
                    "migration_events": [],
                    "read_only_applied": False,
                    "wrote_output": False,
                    "deterministic_fingerprint": "",
                }
                payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
                return payload
            output_payload = dict(migration.get("save_manifest") or output_payload)
            migration_event = dict(migration.get("migration_event") or {})
            migration_events = [migration_event] if migration_event else []
        if action == DECISION_MIGRATE or _token(output_path):
            write_save_json(target_path, output_payload)
            wrote_output = True
    elif _token(artifact_kind_id) == ARTIFACT_KIND_INSTALL_MANIFEST:
        validation = validate_install_manifest(repo_root=root, install_manifest_path=source_path)
        output_payload = dict(validation.get("install_manifest") or {})
        if _token(output_path):
            write_install_json(target_path, output_payload)
            wrote_output = True
    elif _token(artifact_kind_id) == ARTIFACT_KIND_INSTANCE_MANIFEST:
        validation = validate_instance_manifest(repo_root=root, instance_manifest_path=source_path)
        output_payload = dict(validation.get("instance_manifest") or {})
        if _token(output_path):
            write_instance_json(target_path, output_payload)
            wrote_output = True
    else:
        output_payload = _read_json(source_path)
        if _token(output_path):
            _write_json(target_path, output_payload)
            wrote_output = True

    payload = {
        "result": "complete",
        "artifact_kind_id": _token(artifact_kind_id),
        "artifact_path": _norm_rel(source_path),
        "output_path": _norm_rel(target_path) if wrote_output else "",
        "migration_decision_record": decision,
        "migration_events": migration_events,
        "read_only_applied": bool(read_only_applied),
        "wrote_output": bool(wrote_output),
        "output_hash": canonical_sha256(output_payload) if output_payload else "",
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def build_migration_lifecycle_report(repo_root: str) -> dict:
    root = _norm(repo_root)
    policy_registry = load_migration_policy_registry(root)
    policy_rows = list(_as_map(policy_registry.get("record")).get("migration_policies") or [])
    migration_rows = load_migration_rows(root)
    policy_ids = sorted(_token(_as_map(row).get("artifact_kind_id")) for row in policy_rows if _token(_as_map(row).get("artifact_kind_id")))
    sample_blueprint_migrate = determine_migration_decision(
        root,
        artifact_kind_id=ARTIFACT_KIND_BLUEPRINT,
        payload={"format_version": "1.0.0"},
        allow_read_only=False,
    )
    sample_save_read_only = determine_migration_decision(
        root,
        artifact_kind_id=ARTIFACT_KIND_SAVE,
        payload={"save_format_version": "1.0.1", "universe_contract_bundle_hash": "bundle.hash.sample"},
        allow_read_only=True,
        expected_contract_bundle_hash="bundle.hash.sample",
    )
    sample_no_policy = determine_migration_decision(
        root,
        artifact_kind_id="artifact.unknown",
        payload={"format_version": "1.0.0"},
        allow_read_only=False,
    )
    violations = []
    for artifact_kind_id in ARTIFACT_KIND_IDS:
        if artifact_kind_id in policy_ids:
            continue
        violations.append(
            {
                "rule_id": RULE_POLICY,
                "code": "missing_policy",
                "message": "missing migration policy for '{}'".format(artifact_kind_id),
                "file_path": os.path.join("data", "registries", "migration_policy_registry.json"),
            }
        )
    for rel_path, token, rule_id, code, message in (
        ("compat/data_format_loader.py", "migration_decision_record", RULE_POLICY, "loader_policy_missing", "PACK-COMPAT loader must emit migration_decision_record"),
        ("lib/save/save_validator.py", "migration_decision_record", RULE_POLICY, "save_policy_missing", "save loader/validator must emit migration_decision_record"),
        ("lib/install/install_validator.py", "migration_decision_record", RULE_POLICY, "install_policy_missing", "install loader/validator must emit migration_decision_record"),
        ("lib/instance/instance_validator.py", "migration_decision_record", RULE_POLICY, "instance_policy_missing", "instance loader/validator must emit migration_decision_record"),
        ("tools/compat/tool_plan_migration.py", "plan_artifact_migration(", RULE_SILENT, "plan_tool_missing_hook", "migration planning tool must route through canonical planning helper"),
        ("tools/compat/tool_apply_migration.py", "apply_artifact_migration(", RULE_SILENT, "apply_tool_missing_hook", "migration apply tool must route through canonical apply helper"),
        ("tools/setup/setup_cli.py", "migrate-save", RULE_SILENT, "setup_migrate_save_missing", "setup CLI must expose migrate-save"),
        ("tools/setup/setup_cli.py", "migrate-instance", RULE_SILENT, "setup_migrate_instance_missing", "setup CLI must expose migrate-instance"),
    ):
        text = ""
        effective_rel = resolve_repo_path_equivalent(root, rel_path)
        try:
            with open(os.path.join(root, effective_rel.replace("/", os.sep)), "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            pass
        if token in text:
            continue
        violations.append(
            {
                "rule_id": rule_id,
                "code": code,
                "message": message,
                "file_path": rel_path,
            }
        )
    if _token(sample_blueprint_migrate.get("decision_action_id")) != DECISION_MIGRATE:
        violations.append(
            {
                "rule_id": RULE_SILENT,
                "code": "blueprint_migrate_expected",
                "message": "legacy blueprint versions must resolve to deterministic migration chains",
                "file_path": "compat/migration_lifecycle.py",
            }
        )
    if _token(sample_save_read_only.get("decision_action_id")) != DECISION_READ_ONLY:
        violations.append(
            {
                "rule_id": RULE_READ_ONLY,
                "code": "future_save_read_only_expected",
                "message": "future save manifests must resolve to explicit read-only mode when policy allows it",
                "file_path": "lib/save/save_validator.py",
            }
        )
    if _token(sample_no_policy.get("refusal_code")) != REFUSAL_MIGRATION_NO_PATH:
        violations.append(
            {
                "rule_id": RULE_POLICY,
                "code": "missing_policy_not_refused",
                "message": "artifacts without a declared migration policy must refuse deterministically",
                "file_path": "compat/migration_lifecycle.py",
            }
        )
    report = {
        "report_id": "compat.migration_lifecycle.v1",
        "result": "complete" if not violations else "refused",
        "artifact_kind_ids": list(ARTIFACT_KIND_IDS),
        "policy_ids": policy_ids,
        "migration_row_count": len(migration_rows),
        "sample_decisions": {
            "blueprint_legacy": sample_blueprint_migrate,
            "save_future_read_only": sample_save_read_only,
            "unknown_policy": sample_no_policy,
        },
        "violations": sorted(
            [dict(row or {}) for row in violations],
            key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
        ),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def render_migration_lifecycle_baseline(report: Mapping[str, object]) -> str:
    rows = _as_map(report)
    lines = [
        "Status: DERIVED",
        "Last Reviewed: {}".format(LAST_REVIEWED),
        "Supersedes: none",
        "Superseded By: none",
        "Stability: provisional",
        "Future Series: COMPAT/MIGRATION",
        "Replacement Target: release-pinned migration bundles and stricter lifecycle enforcement after v0.0.0-mock",
        "",
        "# Migration Lifecycle Baseline",
        "",
        "## Policy Table",
        "",
    ]
    for artifact_kind_id in list(rows.get("policy_ids") or []):
        lines.append("- `{}`".format(_token(artifact_kind_id)))
    lines.extend(
        [
            "",
            "## Decision Examples",
            "",
            "- legacy blueprint: `{}`".format(_token(_as_map(_as_map(rows.get("sample_decisions")).get("blueprint_legacy")).get("decision_action_id"))),
            "- future save: `{}`".format(_token(_as_map(_as_map(rows.get("sample_decisions")).get("save_future_read_only")).get("decision_action_id"))),
            "- unknown policy: `{}` / `{}`".format(
                _token(_as_map(_as_map(rows.get("sample_decisions")).get("unknown_policy")).get("decision_action_id")),
                _token(_as_map(_as_map(rows.get("sample_decisions")).get("unknown_policy")).get("refusal_code")),
            ),
            "",
            "## Readiness",
            "",
            "- migrate vs read-only vs refuse decisions are centralized in `compat/migration_lifecycle.py`",
            "- save/install/instance validators emit `migration_decision_record`",
            "- setup migration commands and standalone tools can route through the same deterministic planner/apply helpers",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_migration_lifecycle_outputs(repo_root: str) -> dict:
    root = _norm(repo_root)
    report = build_migration_lifecycle_report(root)
    baseline_doc_path = _write_text(os.path.join(root, BASELINE_DOC_REL), render_migration_lifecycle_baseline(report))
    report_json_path = _write_json(os.path.join(root, REPORT_JSON_REL), report)
    return {
        "report": report,
        "baseline_doc_path": _norm_rel(os.path.relpath(baseline_doc_path, root)),
        "report_json_path": _norm_rel(os.path.relpath(report_json_path, root)),
    }


def migration_lifecycle_violations(repo_root: str) -> list[dict]:
    root = _norm(repo_root)
    violations = []
    required_paths = (
        (RETRO_AUDIT_DOC_REL, "migration lifecycle retro audit is required", RULE_POLICY),
        (DOCTRINE_DOC_REL, "migration lifecycle doctrine is required", RULE_POLICY),
        ("schema/compat/migration_policy.schema", "migration policy schema is required", RULE_POLICY),
        ("schema/compat/migration_chain.schema", "migration chain schema is required", RULE_POLICY),
        ("schema/compat/migration_decision_record.schema", "migration decision record schema is required", RULE_POLICY),
        ("schemas/migration_policy.schema.json", "compiled migration policy schema is required", RULE_POLICY),
        ("schemas/migration_chain.schema.json", "compiled migration chain schema is required", RULE_POLICY),
        ("schemas/migration_decision_record.schema.json", "compiled migration decision record schema is required", RULE_POLICY),
        ("data/registries/migration_policy_registry.json", "migration policy registry is required", RULE_POLICY),
        ("compat/migration_lifecycle.py", "migration lifecycle helper is required", RULE_POLICY),
        ("tools/compat/migration_lifecycle_common.py", "migration lifecycle common helper is required", RULE_POLICY),
        ("tools/compat/tool_plan_migration.py", "migration planning tool is required", RULE_SILENT),
        ("tools/compat/tool_apply_migration.py", "migration apply tool is required", RULE_SILENT),
        (BASELINE_DOC_REL, "migration lifecycle baseline is required", RULE_POLICY),
        (REPORT_JSON_REL, "migration lifecycle machine report is required", RULE_POLICY),
    )
    for rel_path, message, rule_id in required_paths:
        if os.path.exists(os.path.join(root, rel_path.replace("/", os.sep))):
            continue
        violations.append({"rule_id": rule_id, "code": "missing_required_file", "message": message, "file_path": rel_path})
    report = build_migration_lifecycle_report(root)
    violations.extend(list(report.get("violations") or []))
    return sorted(
        [dict(row or {}) for row in violations],
        key=lambda row: (_token(row.get("file_path")), _token(row.get("code")), _token(row.get("message"))),
    )


__all__ = [
    "BASELINE_DOC_REL",
    "DOCTRINE_DOC_REL",
    "REPORT_JSON_REL",
    "RETRO_AUDIT_DOC_REL",
    "RULE_POLICY",
    "RULE_READ_ONLY",
    "RULE_SILENT",
    "apply_artifact_migration",
    "build_migration_lifecycle_report",
    "migration_lifecycle_violations",
    "plan_artifact_migration",
    "render_migration_lifecycle_baseline",
    "write_migration_lifecycle_outputs",
]
