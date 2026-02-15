"""CompatX schema version resolution and migration stub routing."""

from __future__ import annotations

import re
from typing import Dict, Tuple


SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse_semver(value: str) -> Tuple[int, int, int] | None:
    token = str(value or "").strip()
    match = SEMVER_RE.match(token)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def migration_stub(schema_name: str, payload_version: str, current_version: str) -> Dict[str, object]:
    return {
        "ok": False,
        "action": "migrate_stub",
        "refusal_code": "refuse.compatx.migration_not_implemented",
        "message": "migration stub invoked for schema '{}' from {} to {}".format(
            str(schema_name),
            str(payload_version),
            str(current_version),
        ),
    }


def resolve_payload_version(
    schema_name: str,
    payload_version: str,
    current_version: str,
    supported_versions: list,
    version_field: str = "schema_version",
) -> Dict[str, object]:
    payload_token = str(payload_version or "").strip()
    current_token = str(current_version or "").strip()
    supported = sorted(set(str(item).strip() for item in (supported_versions or []) if str(item).strip()))
    field_name = str(version_field or "").strip() or "schema_version"

    if not payload_token:
        return {
            "ok": False,
            "action": "refuse",
            "refusal_code": "refuse.compatx.missing_payload_version",
            "message": "payload is missing required field '{}'".format(field_name),
        }

    if payload_token == current_token:
        return {
            "ok": True,
            "action": "pass",
            "refusal_code": "",
            "message": "payload schema_version matches current version",
        }

    payload_semver = parse_semver(payload_token)
    current_semver = parse_semver(current_token)
    if payload_token in supported and payload_semver and current_semver and payload_semver < current_semver:
        return migration_stub(schema_name=schema_name, payload_version=payload_token, current_version=current_token)

    if payload_token in supported and payload_token != current_token:
        return {
            "ok": False,
            "action": "refuse",
            "refusal_code": "refuse.compatx.unsupported_supported_version_state",
            "message": "supported version '{}' does not map to current '{}'".format(payload_token, current_token),
        }

    return {
        "ok": False,
        "action": "refuse",
        "refusal_code": "refuse.compatx.unsupported_schema_version",
        "message": "unsupported schema_version '{}' for schema '{}' (supported: {})".format(
            payload_token,
            str(schema_name),
            ",".join(supported) if supported else "none",
        ),
    }
