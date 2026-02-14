"""Structural work estimator for bounded FULL planning."""

from __future__ import annotations

from typing import Dict, List


DEFAULT_NODE_WEIGHTS = {
    "repox_runner": 1,
    "testx_runner": 2,
    "auditx_runner": 1,
    "performx_runner": 2,
    "compatx_runner": 2,
    "securex_runner": 2,
    "testx.group": 1,
    "auditx.group": 1,
}


def _weight_for_runner(runner_id: str) -> int:
    token = str(runner_id).strip()
    if token in DEFAULT_NODE_WEIGHTS:
        return DEFAULT_NODE_WEIGHTS[token]
    for prefix, weight in DEFAULT_NODE_WEIGHTS.items():
        if token.startswith(prefix):
            return weight
    return 1


def estimate_plan(plan_payload: Dict[str, object]) -> Dict[str, object]:
    nodes = plan_payload.get("nodes") or []
    total_units = 0
    max_parallel_bucket = 0
    buckets: Dict[int, int] = {}

    for row in nodes:
        if not isinstance(row, dict):
            continue
        weight = _weight_for_runner(str(row.get("runner_id", "")))
        total_units += weight
        level = int(row.get("level", 0))
        buckets[level] = buckets.get(level, 0) + weight
        if buckets[level] > max_parallel_bucket:
            max_parallel_bucket = buckets[level]

    estimated_seconds = total_units * 8
    summary = {
        "total_nodes": len(nodes),
        "total_work_units": total_units,
        "max_parallel_bucket_units": max_parallel_bucket,
        "estimated_seconds": estimated_seconds,
        "warn_full_plan_too_large": bool(
            str(plan_payload.get("profile", "")).strip().upper() in {"FULL", "FULL_ALL"}
            and total_units > 240
        ),
    }
    return summary
