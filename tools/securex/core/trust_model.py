"""Trust policy loading and validation helpers."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple


REQUIRED_SUBSYSTEMS = (
    "engine_core",
    "game_logic",
    "client_renderer",
    "server_authority",
    "tools",
    "packs",
    "controlx",
)


def load_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _as_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _validate_entry_shape(entry: Dict[str, Any], idx: int, errors: List[str]) -> None:
    subsystem = str(entry.get("subsystem", "")).strip()
    trust_level = str(entry.get("trust_level", "")).strip()
    allowed = _as_string_list(entry.get("allowed_actions"))
    forbidden = _as_string_list(entry.get("forbidden_actions"))
    notes = _as_string_list(entry.get("notes"))
    escalation = entry.get("escalation_required")

    if not subsystem:
        errors.append("refuse.trust_policy.subsystem_missing.{}".format(idx))
    if trust_level not in {"root", "authoritative", "bounded", "untrusted"}:
        errors.append("refuse.trust_policy.trust_level.{}".format(idx))
    if not allowed:
        errors.append("refuse.trust_policy.allowed_actions.{}".format(idx))
    if not forbidden:
        errors.append("refuse.trust_policy.forbidden_actions.{}".format(idx))
    if not isinstance(escalation, bool):
        errors.append("refuse.trust_policy.escalation_required.{}".format(idx))
    if not isinstance(entry.get("extensions"), dict):
        errors.append("refuse.trust_policy.extensions.{}".format(idx))
    if not notes:
        errors.append("refuse.trust_policy.notes.{}".format(idx))


def validate_trust_policy_payload(payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    errors: List[str] = []
    if str(payload.get("schema_id", "")).strip() != "dominium.schema.governance.trust_policy":  # schema_version: 1.0.0
        errors.append("refuse.trust_policy.schema_id")
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        errors.append("refuse.trust_policy.schema_version")

    record = payload.get("record")
    if not isinstance(record, dict):
        return [], ["refuse.trust_policy.record"]

    entries = record.get("entries")
    if not isinstance(entries, list):
        return [], ["refuse.trust_policy.entries"]

    out: List[Dict[str, Any]] = []
    seen_subsystems = set()
    for idx, raw in enumerate(entries):
        if not isinstance(raw, dict):
            errors.append("refuse.trust_policy.entry_type.{}".format(idx))
            continue
        _validate_entry_shape(raw, idx, errors)
        subsystem = str(raw.get("subsystem", "")).strip()
        if subsystem:
            if subsystem in seen_subsystems:
                errors.append("refuse.trust_policy.duplicate_subsystem.{}".format(subsystem))
            seen_subsystems.add(subsystem)
        out.append(raw)

    for subsystem in REQUIRED_SUBSYSTEMS:
        if subsystem not in seen_subsystems:
            errors.append("refuse.trust_policy.required_subsystem.{}".format(subsystem))

    out.sort(key=lambda row: str(row.get("subsystem", "")))
    return out, sorted(set(errors))


def load_and_validate(path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    if not os.path.isfile(path):
        return [], ["refuse.trust_policy.missing"]
    payload = load_json(path)
    if payload is None:
        return [], ["refuse.trust_policy.invalid_json"]
    return validate_trust_policy_payload(payload)
