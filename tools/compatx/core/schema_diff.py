"""Schema diff classification engine for CompatX."""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any, Dict, List, Tuple


SCHEMA_ID_RE = re.compile(r"^\s*schema_id\s*:\s*([A-Za-z0-9_.-]+)\s*$", re.MULTILINE)
SCHEMA_VERSION_RE = re.compile(r"^\s*schema_version\s*:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*-\s*([A-Za-z0-9_.-]+)\s*:\s*([A-Za-z0-9_.\[\]-]+)", re.MULTILINE)


def _parse_semver(value: str) -> Tuple[int, int, int] | None:
    parts = str(value or "").strip().split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def schema_signature(path: str) -> Dict[str, Any]:
    text = _read_text(path)
    schema_id_match = SCHEMA_ID_RE.search(text)
    schema_version_match = SCHEMA_VERSION_RE.search(text)

    fields: Dict[str, str] = {}
    for name, type_id in FIELD_RE.findall(text):
        fields[str(name).strip()] = str(type_id).strip()

    return {
        "path": os.path.normpath(path).replace("\\", "/"),
        "schema_id": schema_id_match.group(1).strip() if schema_id_match else "",
        "schema_version": schema_version_match.group(1).strip() if schema_version_match else "",
        "fields": dict(sorted(fields.items())),
        "signature_sha256": hashlib.sha256(
            json.dumps(fields, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        ).hexdigest(),
    }


def classify_schema_change(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    before_fields = before.get("fields", {}) if isinstance(before.get("fields"), dict) else {}
    after_fields = after.get("fields", {}) if isinstance(after.get("fields"), dict) else {}

    removed_fields = sorted(set(before_fields.keys()) - set(after_fields.keys()))
    added_fields = sorted(set(after_fields.keys()) - set(before_fields.keys()))
    type_changes = sorted(
        key for key in set(before_fields.keys()) & set(after_fields.keys()) if before_fields.get(key) != after_fields.get(key)
    )

    breaking_reasons: List[str] = []
    if str(before.get("schema_id", "")).strip() != str(after.get("schema_id", "")).strip():
        breaking_reasons.append("schema_id_changed")
    if removed_fields:
        breaking_reasons.append("field_removed")
    if type_changes:
        breaking_reasons.append("field_type_changed")

    before_ver = _parse_semver(str(before.get("schema_version", "")).strip())
    after_ver = _parse_semver(str(after.get("schema_version", "")).strip())
    version_change = ""
    if before_ver and after_ver:
        if after_ver < before_ver:
            breaking_reasons.append("version_decreased")
            version_change = "decrease"
        elif after_ver[0] > before_ver[0]:
            version_change = "major"
        elif after_ver[1] > before_ver[1]:
            version_change = "minor"
        elif after_ver[2] > before_ver[2]:
            version_change = "patch"
        elif after_ver == before_ver:
            version_change = "unchanged"
        else:
            version_change = "mixed"

    if breaking_reasons:
        compatibility = "breaking"
    elif added_fields:
        compatibility = "backward_compatible"
    else:
        compatibility = "no_semantic_change"

    return {
        "artifact_class": "CANONICAL",
        "change_id": "{}:{}->{}".format(
            str(after.get("schema_id", "")).strip() or "<unknown>",
            str(before.get("schema_version", "")).strip() or "<unknown>",
            str(after.get("schema_version", "")).strip() or "<unknown>",
        ),
        "schema_id": str(after.get("schema_id", "")).strip() or str(before.get("schema_id", "")).strip(),
        "before_version": str(before.get("schema_version", "")).strip(),
        "after_version": str(after.get("schema_version", "")).strip(),
        "version_change": version_change,
        "compatibility": compatibility,
        "added_fields": added_fields,
        "removed_fields": removed_fields,
        "type_changes": type_changes,
        "breaking_reasons": sorted(set(breaking_reasons)),
    }


def diff_schema_files(before_path: str, after_path: str) -> Dict[str, Any]:
    before = schema_signature(before_path)
    after = schema_signature(after_path)
    diff = classify_schema_change(before, after)
    diff["before_path"] = before.get("path", "")
    diff["after_path"] = after.get("path", "")
    return diff

