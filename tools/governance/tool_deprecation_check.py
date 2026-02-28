#!/usr/bin/env python3
"""Deterministic ARCH-REF-4 deprecation registry validator."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Iterable, List, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


DEFAULT_DEPRECATIONS_REL = "data/governance/deprecations.json"
DEFAULT_TOPOLOGY_MAP_REL = "docs/audit/TOPOLOGY_MAP.json"
ALLOWED_STATUS = ("active", "deprecated", "quarantined", "removed")


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _read_json(path: str) -> Dict[str, object]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _error(code: str, message: str, path: str = "$") -> Dict[str, str]:
    return {
        "code": str(code),
        "message": str(message),
        "path": str(path),
    }


def _validate_entry_shape(row: Dict[str, object], index: int, repo_root: str) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []
    required = (
        "deprecated_id",
        "deprecated_kind",
        "replacement_id",
        "reason",
        "introduced_version",
        "deprecated_version",
        "removal_target_version",
        "status",
        "adapter_path",
        "notes",
        "extensions",
    )
    for key in required:
        if key in row:
            continue
        errors.append(_error("refuse.deprecation.missing_field", "entry missing '{}'".format(key), "$.entries[{}]".format(index)))
    if errors:
        return errors

    deprecated_id = str(row.get("deprecated_id", "")).strip()
    deprecated_kind = str(row.get("deprecated_kind", "")).strip()
    replacement_id = str(row.get("replacement_id", "")).strip()
    status = str(row.get("status", "")).strip()
    removal_target_version = str(row.get("removal_target_version", "")).strip()
    adapter_path = _norm(str(row.get("adapter_path", "")).strip())
    notes = str(row.get("notes", ""))
    extensions = row.get("extensions")

    if not deprecated_id:
        errors.append(_error("refuse.deprecation.invalid_deprecated_id", "deprecated_id must be non-empty", "$.entries[{}].deprecated_id".format(index)))
    if deprecated_kind not in {"schema", "api", "process", "registry", "module"}:
        errors.append(
            _error(
                "refuse.deprecation.invalid_deprecated_kind",
                "deprecated_kind '{}' is invalid".format(deprecated_kind),
                "$.entries[{}].deprecated_kind".format(index),
            )
        )
    if status not in ALLOWED_STATUS:
        errors.append(_error("refuse.deprecation.invalid_status", "status '{}' is invalid".format(status), "$.entries[{}].status".format(index)))
    if status in {"deprecated", "quarantined"}:
        if not replacement_id:
            errors.append(
                _error(
                    "refuse.deprecation.missing_replacement",
                    "deprecated/quarantined entries require replacement_id",
                    "$.entries[{}].replacement_id".format(index),
                )
            )
        if not removal_target_version:
            errors.append(
                _error(
                    "refuse.deprecation.missing_removal_target",
                    "deprecated/quarantined entries require removal_target_version",
                    "$.entries[{}].removal_target_version".format(index),
                )
            )
    if not isinstance(notes, str):
        errors.append(_error("refuse.deprecation.invalid_notes", "notes must be string", "$.entries[{}].notes".format(index)))
    if not isinstance(extensions, dict):
        errors.append(_error("refuse.deprecation.invalid_extensions", "extensions must be object", "$.entries[{}].extensions".format(index)))
    if adapter_path:
        abs_adapter = os.path.join(repo_root, adapter_path.replace("/", os.sep))
        if not os.path.isfile(abs_adapter):
            errors.append(
                _error(
                    "refuse.deprecation.adapter_missing",
                    "adapter_path '{}' does not exist".format(adapter_path),
                    "$.entries[{}].adapter_path".format(index),
                )
            )
    return errors


def _removed_reference_errors(
    removed_ids: Iterable[str],
    topology_payload: Dict[str, object],
) -> List[Dict[str, str]]:
    errors: List[Dict[str, str]] = []
    if not removed_ids:
        return errors
    if not topology_payload:
        return errors
    topology_text = json.dumps(topology_payload, sort_keys=True)
    for deprecated_id in sorted(set(str(token).strip() for token in removed_ids if str(token).strip())):
        if deprecated_id not in topology_text:
            continue
        errors.append(
            _error(
                "refuse.deprecation.removed_still_referenced",
                "removed deprecated_id '{}' still appears in topology map".format(deprecated_id),
                "$.entries",
            )
        )
    return errors


def validate_deprecation_registry(
    *,
    repo_root: str,
    deprecations_rel: str = DEFAULT_DEPRECATIONS_REL,
    topology_map_rel: str = DEFAULT_TOPOLOGY_MAP_REL,
) -> Dict[str, object]:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    deprecations_rel = _norm(deprecations_rel) or DEFAULT_DEPRECATIONS_REL
    topology_map_rel = _norm(topology_map_rel) or DEFAULT_TOPOLOGY_MAP_REL
    deprecations_abs = os.path.join(repo_root, deprecations_rel.replace("/", os.sep))
    topology_abs = os.path.join(repo_root, topology_map_rel.replace("/", os.sep))

    payload = _read_json(deprecations_abs)
    topology_payload = _read_json(topology_abs)
    errors: List[Dict[str, str]] = []

    if not payload:
        errors.append(
            _error(
                "refuse.deprecation.registry_missing",
                "deprecation registry missing or invalid JSON: '{}'".format(deprecations_rel),
                "$",
            )
        )
        return {
            "result": "refused",
            "errors": errors,
            "checked_entries": 0,
            "deterministic_fingerprint_expected": "",
        }

    if str(payload.get("registry_id", "")).strip() != "dominium.governance.deprecations":
        errors.append(_error("refuse.deprecation.registry_id_invalid", "registry_id must be 'dominium.governance.deprecations'"))

    rows = payload.get("entries")
    if not isinstance(rows, list):
        rows = []
        errors.append(_error("refuse.deprecation.entries_invalid", "entries must be an ordered list", "$.entries"))

    deprecated_ids: List[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(_error("refuse.deprecation.entry_invalid", "entry must be object", "$.entries[{}]".format(index)))
            continue
        deprecated_id = str(row.get("deprecated_id", "")).strip()
        if deprecated_id:
            deprecated_ids.append(deprecated_id)
        errors.extend(_validate_entry_shape(row, index, repo_root))

    if deprecated_ids:
        sorted_ids = sorted(deprecated_ids)
        if deprecated_ids != sorted_ids:
            errors.append(
                _error(
                    "refuse.deprecation.ordering_invalid",
                    "entries must be sorted by deprecated_id",
                    "$.entries",
                )
            )
        if len(sorted_ids) != len(set(sorted_ids)):
            errors.append(_error("refuse.deprecation.duplicate_id", "duplicate deprecated_id entries detected", "$.entries"))

    removed_ids = [
        str(row.get("deprecated_id", "")).strip()
        for row in rows
        if isinstance(row, dict) and str(row.get("status", "")).strip() == "removed"
    ]
    errors.extend(_removed_reference_errors(removed_ids, topology_payload))

    expected_payload = dict(payload)
    expected_payload["deterministic_fingerprint"] = ""
    expected_fingerprint = canonical_sha256(expected_payload)
    actual_fingerprint = str(payload.get("deterministic_fingerprint", "")).strip()
    if actual_fingerprint != expected_fingerprint:
        errors.append(
            _error(
                "refuse.deprecation.fingerprint_mismatch",
                "deterministic_fingerprint mismatch",
                "$.deterministic_fingerprint",
            )
        )

    return {
        "result": "pass" if not errors else "refused",
        "errors": errors,
        "checked_entries": len(rows),
        "deterministic_fingerprint_expected": expected_fingerprint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate governance deprecation registry and adapter policy.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--deprecations", default=DEFAULT_DEPRECATIONS_REL)
    parser.add_argument("--topology-map", default=DEFAULT_TOPOLOGY_MAP_REL)
    args = parser.parse_args()

    repo_root = os.path.normpath(os.path.abspath(args.repo_root)) if str(args.repo_root).strip() else REPO_ROOT_HINT
    result = validate_deprecation_registry(
        repo_root=repo_root,
        deprecations_rel=str(args.deprecations or DEFAULT_DEPRECATIONS_REL),
        topology_map_rel=str(args.topology_map or DEFAULT_TOPOLOGY_MAP_REL),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())

