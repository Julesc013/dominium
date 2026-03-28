"""Helpers for SCOPE-FREEZE-0 TestX coverage."""

from __future__ import annotations

import os

from meta.stability import validate_all_registries
from tools.release.scope_freeze_common import (
    FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH,
    PROVISIONAL_FEATURE_LIST_PATH,
    current_semantic_contract_ids,
    render_provisional_feature_list,
    semantic_contract_registry_hash,
    scope_freeze_violations,
)


def load_validation_report(repo_root: str) -> dict:
    return validate_all_registries(repo_root)


def missing_stability_errors(report: dict | None) -> list[dict]:
    rows: list[dict] = []
    for registry_report in list(dict(report or {}).get("reports") or []):
        rel_path = str(dict(registry_report or {}).get("file_path", "")).replace("\\", "/")
        for error in list(dict(registry_report or {}).get("errors") or []):
            error_row = dict(error or {})
            if str(error_row.get("code", "")).strip() != "missing_stability":
                continue
            rows.append(
                {
                    "file_path": rel_path,
                    "path": str(error_row.get("path", "")).strip(),
                    "message": str(error_row.get("message", "")).strip(),
                }
            )
    return sorted(rows, key=lambda row: (row["file_path"], row["path"], row["message"]))


def current_frozen_contract_hash(repo_root: str) -> str:
    return semantic_contract_registry_hash(repo_root)


def expected_frozen_contract_hash() -> str:
    return FROZEN_SEMANTIC_CONTRACT_REGISTRY_HASH


def frozen_contract_ids(repo_root: str) -> list[str]:
    return current_semantic_contract_ids(repo_root)


def provisional_feature_list_path(repo_root: str) -> str:
    return os.path.join(repo_root, PROVISIONAL_FEATURE_LIST_PATH.replace("/", os.sep))


def provisional_feature_list_mismatch(repo_root: str) -> str:
    path = provisional_feature_list_path(repo_root)
    try:
        current_text = open(path, "r", encoding="utf-8").read()
    except OSError:
        return "provisional feature list is missing"
    expected_text = render_provisional_feature_list(repo_root)
    if current_text != expected_text:
        return "provisional feature list is stale relative to current registry stability markers"
    return ""


def scope_freeze_findings(repo_root: str) -> list[dict]:
    return scope_freeze_violations(repo_root)
