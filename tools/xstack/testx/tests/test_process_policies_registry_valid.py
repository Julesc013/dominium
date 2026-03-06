"""FAST test: PROC policy registries exist and declare required baseline policy ids."""

from __future__ import annotations

import json
import os


TEST_ID = "test_process_policies_registry_valid"
TEST_TAGS = ["fast", "proc", "registry"]


def _load(repo_root: str, rel_path: str):
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        return json.load(open(abs_path, "r", encoding="utf-8")), ""
    except (OSError, ValueError):
        return {}, "invalid json"


def _collect_ids(rows, key: str):
    out = set()
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        token = str(row.get(key, "")).strip()
        if token:
            out.add(token)
    return out


def run(repo_root: str):
    lifecycle_payload, lifecycle_err = _load(repo_root, "data/registries/process_lifecycle_policy_registry.json")
    stabilization_payload, stabilization_err = _load(repo_root, "data/registries/process_stabilization_policy_registry.json")
    drift_payload, drift_err = _load(repo_root, "data/registries/process_drift_policy_registry.json")

    if lifecycle_err:
        return {"status": "fail", "message": "process_lifecycle_policy_registry missing or invalid"}
    if stabilization_err:
        return {"status": "fail", "message": "process_stabilization_policy_registry missing or invalid"}
    if drift_err:
        return {"status": "fail", "message": "process_drift_policy_registry missing or invalid"}

    lifecycle_rows = list((dict(lifecycle_payload.get("record") or {})).get("process_lifecycle_policies") or [])
    stabilization_rows = list((dict(stabilization_payload.get("record") or {})).get("process_stabilization_policies") or [])
    drift_rows = list((dict(drift_payload.get("record") or {})).get("process_drift_policies") or [])

    lifecycle_ids = _collect_ids(lifecycle_rows, "process_lifecycle_policy_id")
    stabilization_ids = _collect_ids(stabilization_rows, "process_stabilization_policy_id")
    drift_ids = _collect_ids(drift_rows, "process_drift_policy_id")

    missing = []
    for token in ("proc.lifecycle.default", "proc.lifecycle.rank_strict", "proc.lifecycle.lab_experimental"):
        if token not in lifecycle_ids:
            missing.append(token)
    for token in ("stab.default", "stab.strict", "stab.fast_dev"):
        if token not in stabilization_ids:
            missing.append(token)
    for token in ("drift.default", "drift.strict"):
        if token not in drift_ids:
            missing.append(token)
    if missing:
        return {"status": "fail", "message": "missing required PROC policy ids: {}".format(",".join(sorted(missing)))}

    return {"status": "pass", "message": "PROC lifecycle/stabilization/drift policy registries valid"}
