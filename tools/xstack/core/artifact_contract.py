"""Derived artifact contract helpers for gate runner expectations."""

from __future__ import annotations

import json
import os
from typing import Dict, List


DERIVED_ARTIFACTS_REL = os.path.join("data", "registries", "derived_artifacts.json")


def load_artifact_contract(repo_root: str, contract_rel: str = DERIVED_ARTIFACTS_REL) -> Dict[str, dict]:
    path = os.path.join(repo_root, contract_rel)
    if not os.path.isfile(path):
        return {}
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    rows = ((payload.get("record") or {}).get("artifacts") or [])
    out: Dict[str, dict] = {}
    for row in rows:
        if isinstance(row, dict):
            artifact_id = str(row.get("artifact_id", "")).strip()
            if artifact_id:
                out[artifact_id] = row
    return out


def classify_paths(repo_root: str, paths: List[str]) -> Dict[str, List[str]]:
    contract = load_artifact_contract(repo_root)
    by_path = {}
    for row in contract.values():
        path = str(row.get("path", "")).replace("\\", "/").strip("/")
        if path:
            by_path[path] = str(row.get("artifact_class", "")).strip() or "UNKNOWN"

    out = {"CANONICAL": [], "DERIVED_VIEW": [], "RUN_META": [], "UNKNOWN": []}
    for rel in paths:
        token = str(rel).replace("\\", "/").strip("/")
        klass = by_path.get(token, "UNKNOWN")
        if klass not in out:
            klass = "UNKNOWN"
        out[klass].append(token)
    for key in out:
        out[key] = sorted(set(out[key]))
    return out
