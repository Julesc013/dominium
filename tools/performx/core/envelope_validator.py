"""Registry validators for PerformX envelopes and hardware profiles."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple


VALID_WORKLOADS = {
    "worldgen",
    "simulation_step",
    "ensemble_run",
    "ui_render",
}

VALID_SEVERITY = {"warn", "fail"}


def _read_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def load_registry(path: str, refusal_code: str) -> Tuple[Dict[str, Any] | None, List[str]]:
    payload = _read_json(path)
    if payload is None:
        return None, [refusal_code]
    record = payload.get("record")
    if not isinstance(record, dict):
        return None, [refusal_code + ".record"]
    return payload, []


def _validate_metric(metric: Dict[str, Any], prefix: str) -> List[str]:
    violations: List[str] = []
    metric_id = str(metric.get("metric_id", "")).strip()
    unit = str(metric.get("unit", "")).strip()
    if not metric_id:
        violations.append(prefix + ".metric_id_missing")
    if not unit:
        violations.append(prefix + ".metric_unit_missing")
    return violations


def validate_envelope_registry(payload: Dict[str, Any]) -> List[str]:
    record = payload.get("record", {})
    rows = record.get("envelopes")
    if not isinstance(rows, list):
        return ["refuse.invalid_performance_envelopes.envelopes_missing"]

    violations: List[str] = []
    seen_ids = set()
    for idx, row in enumerate(rows):
        prefix = "envelope[{}]".format(idx)
        if not isinstance(row, dict):
            violations.append(prefix + ".not_object")
            continue
        envelope_id = str(row.get("envelope_id", "")).strip()
        subsystem = str(row.get("subsystem", "")).strip()
        workload_type = str(row.get("workload_type", "")).strip()
        metrics = row.get("metrics")
        tolerances = row.get("tolerances")
        severity = str(row.get("regression_severity", "warn")).strip().lower()
        if not envelope_id:
            violations.append(prefix + ".envelope_id_missing")
            continue
        if envelope_id in seen_ids:
            violations.append(prefix + ".duplicate_id")
        seen_ids.add(envelope_id)
        if not subsystem:
            violations.append(prefix + ".subsystem_missing")
        if workload_type not in VALID_WORKLOADS:
            violations.append(prefix + ".invalid_workload_type")
        if severity not in VALID_SEVERITY:
            violations.append(prefix + ".invalid_regression_severity")
        if not isinstance(metrics, list) or not metrics:
            violations.append(prefix + ".metrics_missing")
        else:
            for metric_idx, metric in enumerate(metrics):
                if not isinstance(metric, dict):
                    violations.append(prefix + ".metric_{}_not_object".format(metric_idx))
                    continue
                violations.extend(_validate_metric(metric, prefix + ".metric_{}".format(metric_idx)))
        if not isinstance(tolerances, dict):
            violations.append(prefix + ".tolerances_missing")
    return sorted(set(violations))


def validate_profile_registry(payload: Dict[str, Any]) -> List[str]:
    record = payload.get("record", {})
    rows = record.get("profiles")
    if not isinstance(rows, list):
        return ["refuse.invalid_performance_profiles.profiles_missing"]

    violations: List[str] = []
    seen = set()
    for idx, row in enumerate(rows):
        prefix = "profile[{}]".format(idx)
        if not isinstance(row, dict):
            violations.append(prefix + ".not_object")
            continue
        profile_id = str(row.get("profile_id", "")).strip()
        cpu_class = str(row.get("cpu_class", "")).strip()
        factor = row.get("normalization_factor")
        if not profile_id:
            violations.append(prefix + ".profile_id_missing")
            continue
        if profile_id in seen:
            violations.append(prefix + ".duplicate_id")
        seen.add(profile_id)
        if not cpu_class:
            violations.append(prefix + ".cpu_class_missing")
        if not isinstance(factor, (int, float)) or float(factor) <= 0.0:
            violations.append(prefix + ".normalization_factor_invalid")
    return sorted(set(violations))


def envelope_index(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = payload.get("record", {}).get("envelopes", [])
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        envelope_id = str(row.get("envelope_id", "")).strip()
        if envelope_id:
            out[envelope_id] = row
    return out


def profile_index(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows = payload.get("record", {}).get("profiles", [])
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        profile_id = str(row.get("profile_id", "")).strip()
        if profile_id:
            out[profile_id] = row
    return out


def select_envelopes(payload: Dict[str, Any], selected_ids: List[str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    index = envelope_index(payload)
    if not selected_ids:
        return [index[key] for key in sorted(index.keys())], []
    selected: List[Dict[str, Any]] = []
    missing: List[str] = []
    for envelope_id in selected_ids:
        row = index.get(envelope_id)
        if row is None:
            missing.append(envelope_id)
            continue
        selected.append(row)
    selected = sorted(selected, key=lambda item: str(item.get("envelope_id", "")))
    return selected, missing


def absolute_path(repo_root: str, relative_path: str) -> str:
    if os.path.isabs(relative_path):
        return os.path.normpath(relative_path)
    return os.path.normpath(os.path.join(repo_root, relative_path))

