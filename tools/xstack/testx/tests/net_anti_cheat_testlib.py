"""Shared helpers for deterministic anti-cheat TestX suites."""

from __future__ import annotations

from typing import Dict, Tuple

from src.net.anti_cheat import ensure_runtime_channels


def _registry_rows(payload: dict, record_key: str) -> list:
    if not isinstance(payload, dict):
        return []
    rows = payload.get(record_key)
    if isinstance(rows, list):
        return list(rows)
    record = payload.get("record")
    if isinstance(record, dict):
        rows = record.get(record_key)
        if isinstance(rows, list):
            return list(rows)
    return []


def _module_registry_map(payloads: Dict[str, dict]) -> Dict[str, dict]:
    rows = _registry_rows(dict(payloads.get("anti_cheat_module_registry_hash") or {}), "modules")
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("module_id", ""))):
        module_id = str(row.get("module_id", "")).strip()
        if module_id:
            out[module_id] = dict(row)
    return out


def anti_cheat_policy_map(payloads: Dict[str, dict]) -> Dict[str, dict]:
    rows = _registry_rows(dict(payloads.get("anti_cheat_policy_registry_hash") or {}), "policies")
    out: Dict[str, dict] = {}
    for row in sorted((item for item in rows if isinstance(item, dict)), key=lambda item: str(item.get("policy_id", ""))):
        policy_id = str(row.get("policy_id", "")).strip()
        if policy_id:
            out[policy_id] = dict(row)
    return out


def apply_anti_cheat_policy(runtime: dict, payloads: Dict[str, dict], policy_id: str) -> Tuple[bool, str]:
    policies = anti_cheat_policy_map(payloads)
    selected = dict(policies.get(str(policy_id), {}))
    if not selected:
        return False, "policy '{}' missing in anti-cheat registry".format(str(policy_id))

    modules_enabled = sorted(
        set(str(item).strip() for item in (selected.get("modules_enabled") or []) if str(item).strip())
    )
    default_actions = dict(selected.get("default_actions") or {})
    cleaned_actions = {}
    for key in sorted(default_actions.keys()):
        token = str(key).strip()
        if token:
            cleaned_actions[token] = str(default_actions.get(key, "")).strip()

    runtime["anti_cheat"] = {
        "policy_id": str(policy_id),
        "modules_enabled": modules_enabled,
        "default_actions": cleaned_actions,
        "extensions": dict(selected.get("extensions") or {}),
        "module_registry_map": _module_registry_map(payloads),
    }
    ensure_runtime_channels(runtime)
    return True, ""

