"""Privilege model and entitlement enforcement checks."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple


REQUIRED_ROLE_IDS = ("role.observer", "role.creator", "role.mission_player")
REQUIRED_ENTITLEMENTS = {
    "role.observer": {"camera.mode.observer_truth", "ui.overlay.world_layers"},
    "role.creator": {"scenario.mutate"},
    "role.mission_player": {"ui.hud.basic"},
}


def load_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def validate_security_roles(path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    payload = load_json(path)
    if payload is None:
        return [], ["refuse.privilege_model.missing"]
    errors: List[str] = []
    if str(payload.get("schema_id", "")).strip() != "dominium.schema.governance.privilege_model":  # schema_version: 1.0.0
        errors.append("refuse.privilege_model.schema_id")
    if str(payload.get("schema_version", "")).strip() != "1.0.0":
        errors.append("refuse.privilege_model.schema_version")

    record = payload.get("record")
    if not isinstance(record, dict):
        return [], ["refuse.privilege_model.record"]
    roles = record.get("roles")
    if not isinstance(roles, list):
        return [], ["refuse.privilege_model.roles"]

    out: List[Dict[str, Any]] = []
    seen = set()
    for idx, role in enumerate(roles):
        if not isinstance(role, dict):
            errors.append("refuse.privilege_model.role_type.{}".format(idx))
            continue
        role_id = str(role.get("role_id", "")).strip()
        law_profile_id = str(role.get("law_profile_id", "")).strip()
        entitlements = role.get("entitlements")
        restrictions = role.get("restrictions")
        watermark = str(role.get("watermark_policy", "")).strip()
        if not role_id:
            errors.append("refuse.privilege_model.role_id.{}".format(idx))
            continue
        if role_id in seen:
            errors.append("refuse.privilege_model.duplicate_role.{}".format(role_id))
        seen.add(role_id)
        if not law_profile_id:
            errors.append("refuse.privilege_model.law_profile_id.{}".format(role_id))
        if not isinstance(entitlements, list):
            errors.append("refuse.privilege_model.entitlements.{}".format(role_id))
            entitlements = []
        if not isinstance(restrictions, list):
            errors.append("refuse.privilege_model.restrictions.{}".format(role_id))
        if watermark not in {"none", "observer", "dev"}:
            errors.append("refuse.privilege_model.watermark_policy.{}".format(role_id))
        required = REQUIRED_ENTITLEMENTS.get(role_id, set())
        missing = sorted(required.difference({str(item).strip() for item in entitlements if str(item).strip()}))
        for item in missing:
            errors.append("refuse.privilege_model.missing_entitlement.{}.{}".format(role_id, item))
        if watermark == "none" and role_id in {"role.observer", "role.creator"}:
            errors.append("refuse.privilege_model.watermark_required.{}".format(role_id))
        out.append(role)

    for role_id in REQUIRED_ROLE_IDS:
        if role_id not in seen:
            errors.append("refuse.privilege_model.required_role.{}".format(role_id))

    out.sort(key=lambda row: str(row.get("role_id", "")))
    return out, sorted(set(errors))


def scan_for_hardcoded_modes(repo_root: str) -> List[str]:
    source_roots = [os.path.join(repo_root, part) for part in ("client", "launcher", "setup", "server")]
    tokens = ("creative_mode_enabled", "spectator_mode_enabled", "observer_mode_enabled")
    issues: List[str] = []
    for root in source_roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in {".git", ".vs", "out", "dist", "__pycache__"}]
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in {".c", ".cc", ".cpp", ".h", ".hpp", ".py", ".json"}:
                    continue
                path = os.path.join(dirpath, filename)
                try:
                    text = open(path, "r", encoding="utf-8").read().lower()
                except OSError:
                    continue
                rel = path.replace("\\", "/")
                for token in tokens:
                    if token in text:
                        issues.append("refuse.privilege_model.hardcoded_mode.{}@{}".format(token, rel))
    return sorted(set(issues))
