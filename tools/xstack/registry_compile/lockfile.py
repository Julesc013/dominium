"""Lockfile hashing + validation for deterministic bundle composition."""

from __future__ import annotations

import re
from typing import Dict, List

from tools.xstack.compatx.canonical_json import canonical_sha256


HASH_RE = re.compile(r"^[A-Fa-f0-9]{64}$")


def compute_pack_lock_hash(resolved_packs: List[dict]) -> str:
    rows = []
    for row in sorted(
        resolved_packs or [],
        key=lambda item: (
            str(item.get("pack_id", "")),
            str(item.get("version", "")),
            str(item.get("canonical_hash", "")),
            str(item.get("signature_status", "")),
        ),
    ):
        rows.append(
            {
                "pack_id": str(row.get("pack_id", "")),
                "version": str(row.get("version", "")),
                "canonical_hash": str(row.get("canonical_hash", "")),
                "signature_status": str(row.get("signature_status", "")),
            }
        )
    return canonical_sha256(rows)


def validate_lockfile_payload(payload: Dict[str, object]) -> Dict[str, object]:
    errors = []
    if not isinstance(payload, dict):
        return {
            "result": "refused",
            "errors": [
                {
                    "code": "refuse.lockfile.invalid_root",
                    "message": "lockfile root must be an object",
                    "path": "$",
                }
            ],
        }

    required_fields = (
        "lockfile_version",
        "bundle_id",
        "resolved_packs",
        "registries",
        "compatibility_version",
        "pack_lock_hash",
    )
    for key in required_fields:
        if key not in payload:
            errors.append(
                {
                    "code": "refuse.lockfile.missing_required_field",
                    "message": "missing required field '{}'".format(key),
                    "path": "$.{}".format(key),
                }
            )

    lockfile_version = str(payload.get("lockfile_version", ""))
    if lockfile_version != "1.0.0":
        errors.append(
            {
                "code": "refuse.lockfile.invalid_lockfile_version",
                "message": "lockfile_version must equal '1.0.0'",
                "path": "$.lockfile_version",
            }
        )

    resolved = payload.get("resolved_packs")
    if not isinstance(resolved, list):
        errors.append(
            {
                "code": "refuse.lockfile.invalid_resolved_packs",
                "message": "resolved_packs must be a list",
                "path": "$.resolved_packs",
            }
        )
        resolved = []

    for idx, row in enumerate(resolved):
        if not isinstance(row, dict):
            errors.append(
                {
                    "code": "refuse.lockfile.invalid_resolved_pack_entry",
                    "message": "resolved_packs entry must be object",
                    "path": "$.resolved_packs[{}]".format(idx),
                }
            )
            continue
        for field in ("pack_id", "version", "canonical_hash", "signature_status"):
            if not str(row.get(field, "")).strip():
                errors.append(
                    {
                        "code": "refuse.lockfile.invalid_resolved_pack_field",
                        "message": "resolved_packs entry missing '{}'".format(field),
                        "path": "$.resolved_packs[{}].{}".format(idx, field),
                    }
                )

    registries = payload.get("registries")
    if not isinstance(registries, dict):
        errors.append(
            {
                "code": "refuse.lockfile.invalid_registries",
                "message": "registries must be an object",
                "path": "$.registries",
            }
        )
    else:
        expected_keys = (
            "domain_registry_hash",
            "law_registry_hash",
            "experience_registry_hash",
            "lens_registry_hash",
            "activation_policy_registry_hash",
            "budget_policy_registry_hash",
            "fidelity_policy_registry_hash",
            "astronomy_catalog_index_hash",
            "site_registry_index_hash",
            "ui_registry_hash",
        )
        for key in expected_keys:
            token = str(registries.get(key, "")).strip()
            if not HASH_RE.fullmatch(token):
                errors.append(
                    {
                        "code": "refuse.lockfile.invalid_registry_hash",
                        "message": "registries.{} must be sha256 hex".format(key),
                        "path": "$.registries.{}".format(key),
                    }
                )

    declared_hash = str(payload.get("pack_lock_hash", "")).strip()
    computed_hash = compute_pack_lock_hash(resolved)
    if declared_hash != computed_hash:
        errors.append(
            {
                "code": "refuse.lockfile.pack_lock_hash_mismatch",
                "message": "pack_lock_hash mismatch",
                "path": "$.pack_lock_hash",
            }
        )

    if errors:
        return {
            "result": "refused",
            "errors": sorted(errors, key=lambda row: (row["code"], row["path"], row["message"])),
            "computed_pack_lock_hash": computed_hash,
        }
    return {
        "result": "complete",
        "errors": [],
        "computed_pack_lock_hash": computed_hash,
    }
