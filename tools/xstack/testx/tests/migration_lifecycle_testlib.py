"""Shared MIGRATION-LIFECYCLE-0 TestX helpers."""

from __future__ import annotations

import json

from src.compat.migration_lifecycle import (
    ARTIFACT_KIND_BLUEPRINT,
    ARTIFACT_KIND_IDS,
    ARTIFACT_KIND_SAVE,
    DECISION_MIGRATE,
    DECISION_READ_ONLY,
    REFUSAL_MIGRATION_NO_PATH,
    determine_migration_decision,
    load_migration_policy_registry,
)
import os

from tools.compat.migration_lifecycle_common import BASELINE_DOC_REL, REPORT_JSON_REL, build_migration_lifecycle_report, write_migration_lifecycle_outputs


def ensure_assets(repo_root: str) -> dict:
    root = os.path.abspath(repo_root)
    report_path = os.path.join(root, REPORT_JSON_REL.replace("/", os.sep))
    baseline_path = os.path.join(root, BASELINE_DOC_REL.replace("/", os.sep))
    if os.path.isfile(report_path) and os.path.isfile(baseline_path):
        return build_migration_lifecycle_report(repo_root)
    return write_migration_lifecycle_outputs(repo_root)


def policy_registry(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return load_migration_policy_registry(repo_root)


def policy_ids(repo_root: str) -> list[str]:
    rows = list(dict(policy_registry(repo_root).get("record") or {}).get("migration_policies") or [])
    return sorted(str(dict(row or {}).get("artifact_kind_id", "")).strip() for row in rows if str(dict(row or {}).get("artifact_kind_id", "")).strip())


def build_report(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return build_migration_lifecycle_report(repo_root)


def blueprint_migrate_decision(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return determine_migration_decision(
        repo_root,
        artifact_kind_id=ARTIFACT_KIND_BLUEPRINT,
        payload={"format_version": "1.0.0"},
        allow_read_only=False,
    )


def blueprint_migrate_decision_for_path(repo_root: str, artifact_path: str) -> dict:
    ensure_assets(repo_root)
    return determine_migration_decision(
        repo_root,
        artifact_kind_id=ARTIFACT_KIND_BLUEPRINT,
        payload={"format_version": "1.0.0"},
        allow_read_only=False,
        artifact_path=artifact_path,
    )


def future_save_read_only_decision(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return determine_migration_decision(
        repo_root,
        artifact_kind_id=ARTIFACT_KIND_SAVE,
        payload={
            "save_format_version": "1.0.1",
            "universe_contract_bundle_hash": "bundle.hash.sample",
        },
        allow_read_only=True,
        expected_contract_bundle_hash="bundle.hash.sample",
    )


def no_policy_decision(repo_root: str) -> dict:
    ensure_assets(repo_root)
    return determine_migration_decision(
        repo_root,
        artifact_kind_id="artifact.unknown",
        payload={"format_version": "1.0.0"},
        allow_read_only=False,
    )


def repeated_blueprint_decisions_match(repo_root: str) -> bool:
    left = blueprint_migrate_decision(repo_root)
    right = blueprint_migrate_decision(repo_root)
    return json.dumps(left, sort_keys=True) == json.dumps(right, sort_keys=True)


def path_variant_blueprint_decisions_stable(repo_root: str) -> bool:
    left = blueprint_migrate_decision_for_path(repo_root, "build/tmp/a/blueprint.json")
    right = blueprint_migrate_decision_for_path(repo_root, "build/tmp/b/blueprint.json")
    comparable_left = dict(left)
    comparable_right = dict(right)
    comparable_left.setdefault("extensions", {}).pop("artifact_path", None)
    comparable_right.setdefault("extensions", {}).pop("artifact_path", None)
    return json.dumps(comparable_left, sort_keys=True) == json.dumps(comparable_right, sort_keys=True)


__all__ = [
    "ARTIFACT_KIND_IDS",
    "DECISION_MIGRATE",
    "DECISION_READ_ONLY",
    "REFUSAL_MIGRATION_NO_PATH",
    "blueprint_migrate_decision",
    "blueprint_migrate_decision_for_path",
    "build_report",
    "ensure_assets",
    "future_save_read_only_decision",
    "no_policy_decision",
    "path_variant_blueprint_decisions_stable",
    "policy_ids",
    "repeated_blueprint_decisions_match",
]
