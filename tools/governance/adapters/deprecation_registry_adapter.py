"""Adapter shim: legacy deprecation registry path -> governance deprecation registry."""

from __future__ import annotations

import json
import os
from typing import Dict, List


LEGACY_REGISTRY_REL = "data/registries/deprecation_registry.json"
GOVERNANCE_REGISTRY_REL = "data/governance/deprecations.json"


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _read_json(path: str) -> Dict[str, object]:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _legacy_entry_from_governance(row: Dict[str, object]) -> Dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "deprecated_id": str(row.get("deprecated_id", "")).strip(),
        "replacement_id": str(row.get("replacement_id", "")).strip(),
        "reason": str(row.get("reason", "")).strip(),
        "removal_target_version": str(row.get("removal_target_version", "")).strip(),
        "status": "removed" if str(row.get("status", "")).strip() == "removed" else "active",
        "extensions": dict(row.get("extensions") or {}),
    }


def read_legacy_compatible_registry(repo_root: str) -> Dict[str, object]:
    """Return a deterministic legacy-shape view backed by governance deprecations."""
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    governance_path = os.path.join(repo_root, GOVERNANCE_REGISTRY_REL.replace("/", os.sep))
    payload = _read_json(governance_path)
    rows: List[Dict[str, object]] = []
    for row in list(payload.get("entries") or []):
        if not isinstance(row, dict):
            continue
        rows.append(_legacy_entry_from_governance(row))
    rows = sorted(rows, key=lambda item: str(item.get("deprecated_id", "")))
    return {
        "schema_id": "dominium.registry.deprecation",
        "schema_version": "1.0.0",
        "record": {
            "deprecations": rows,
            "adapter_source": _norm(GOVERNANCE_REGISTRY_REL),
        },
    }


def read_governance_registry(repo_root: str) -> Dict[str, object]:
    repo_root = os.path.normpath(os.path.abspath(repo_root))
    governance_path = os.path.join(repo_root, GOVERNANCE_REGISTRY_REL.replace("/", os.sep))
    return _read_json(governance_path)

