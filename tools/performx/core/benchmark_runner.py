"""Deterministic benchmark runner for PerformX envelopes."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, Iterable, List

from hardware_profile import normalize_value


DEFAULT_METRIC_UNITS = {
    "wall_time_ms": "ms",
    "allocations": "count",
    "peak_memory_mb": "MiB",
    "ops_count": "count",
}


def _metric_seed(envelope_id: str, workload_type: str, metric_id: str, seed: int) -> int:
    token = "{}|{}|{}|{}".format(envelope_id, workload_type, metric_id, int(seed))
    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _metric_value(metric_seed: int, metric_id: str) -> float:
    if metric_id == "wall_time_ms":
        return round(5.0 + float(metric_seed % 5000) / 100.0, 4)
    if metric_id == "allocations":
        return float(1000 + (metric_seed % 50000))
    if metric_id == "peak_memory_mb":
        return round(16.0 + float(metric_seed % 4096) / 16.0, 4)
    if metric_id == "ops_count":
        return float(10000 + (metric_seed % 500000))
    return round(float(metric_seed % 100000) / 100.0, 4)


def _metric_rows(
    envelope_id: str,
    workload_type: str,
    metrics: Iterable[Dict[str, Any]],
    normalization_factor: float,
    seed: int,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for metric in metrics:
        metric_id = str(metric.get("metric_id", "")).strip()
        if not metric_id:
            continue
        unit = str(metric.get("unit", "")).strip() or DEFAULT_METRIC_UNITS.get(metric_id, "unit")
        metric_seed = _metric_seed(envelope_id, workload_type, metric_id, seed)
        raw_value = _metric_value(metric_seed, metric_id)
        rows.append(
            {
                "metric_id": metric_id,
                "unit": unit,
                "raw_value": raw_value,
                "normalized_value": round(normalize_value(raw_value, normalization_factor), 6),
            }
        )
    rows.sort(key=lambda item: str(item.get("metric_id", "")))
    return rows


def run_envelopes(
    envelopes: Iterable[Dict[str, Any]],
    normalization_factor: float,
    seed: int = 0,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for envelope in sorted(envelopes, key=lambda item: str(item.get("envelope_id", ""))):
        envelope_id = str(envelope.get("envelope_id", "")).strip()
        if not envelope_id:
            continue
        workload_type = str(envelope.get("workload_type", "")).strip() or "worldgen"
        metrics = envelope.get("metrics")
        if not isinstance(metrics, list):
            metrics = []
        results.append(
            {
                "envelope_id": envelope_id,
                "subsystem": str(envelope.get("subsystem", "")).strip(),
                "workload_type": workload_type,
                "deterministic_required": bool(envelope.get("deterministic_required", True)),
                "regression_severity": str(envelope.get("regression_severity", "warn")).strip().lower(),
                "metrics": _metric_rows(
                    envelope_id=envelope_id,
                    workload_type=workload_type,
                    metrics=metrics,
                    normalization_factor=float(normalization_factor),
                    seed=int(seed),
                ),
            }
        )
    return results

