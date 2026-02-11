"""Regression detection for PerformX envelopes."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple


def _tolerance_object(tolerances: Dict[str, Any], metric_id: str) -> Dict[str, float]:
    raw = tolerances.get(metric_id, {})
    if not isinstance(raw, dict):
        raw = {}
    percent = raw.get("percent")
    absolute = raw.get("absolute")
    try:
        percent_value = float(percent) if percent is not None else 10.0
    except (TypeError, ValueError):
        percent_value = 10.0
    try:
        absolute_value = float(absolute) if absolute is not None else 0.0
    except (TypeError, ValueError):
        absolute_value = 0.0
    return {
        "percent": max(percent_value, 0.0),
        "absolute": max(absolute_value, 0.0),
    }


def _baseline_index(payload: Dict[str, Any]) -> Dict[Tuple[str, str], float]:
    rows = payload.get("results", [])
    if isinstance(payload.get("record"), dict):
        rows = payload.get("record", {}).get("results", rows)
    out: Dict[Tuple[str, str], float] = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        envelope_id = str(row.get("envelope_id", "")).strip()
        metrics = row.get("metrics")
        if not envelope_id or not isinstance(metrics, list):
            continue
        for metric in metrics:
            if not isinstance(metric, dict):
                continue
            metric_id = str(metric.get("metric_id", "")).strip()
            if not metric_id:
                continue
            value = metric.get("normalized_value", metric.get("raw_value"))
            try:
                out[(envelope_id, metric_id)] = float(value)
            except (TypeError, ValueError):
                continue
    return out


def detect_regressions(
    current_results: Iterable[Dict[str, Any]],
    envelope_index: Dict[str, Dict[str, Any]],
    baseline_payload: Dict[str, Any] | None,
) -> Dict[str, Any]:
    baseline_map = _baseline_index(baseline_payload or {})
    regressions: List[Dict[str, Any]] = []
    summary = {
        "critical_failures": 0,
        "regression_count": 0,
        "warnings": 0,
    }

    for row in current_results:
        envelope_id = str(row.get("envelope_id", "")).strip()
        envelope_meta = envelope_index.get(envelope_id, {})
        tolerances = envelope_meta.get("tolerances", {}) if isinstance(envelope_meta.get("tolerances"), dict) else {}
        severity = str(envelope_meta.get("regression_severity", row.get("regression_severity", "warn"))).strip().lower()
        metrics = row.get("metrics")
        if not isinstance(metrics, list):
            continue
        for metric in metrics:
            metric_id = str(metric.get("metric_id", "")).strip()
            if not metric_id:
                continue
            baseline_value = baseline_map.get((envelope_id, metric_id))
            if baseline_value is None:
                continue
            try:
                current_value = float(metric.get("normalized_value", metric.get("raw_value")))
            except (TypeError, ValueError):
                continue
            tolerance = _tolerance_object(tolerances, metric_id)
            delta = current_value - baseline_value
            absolute_delta = abs(delta)
            if baseline_value == 0.0:
                percent_delta = 0.0 if absolute_delta == 0.0 else 100.0
            else:
                percent_delta = abs((delta / baseline_value) * 100.0)
            exceeds = absolute_delta > tolerance["absolute"] and percent_delta > tolerance["percent"]
            if not exceeds:
                continue
            regression_id = "regression.{}.{}".format(envelope_id, metric_id)
            regressions.append(
                {
                    "regression_id": regression_id,
                    "envelope_id": envelope_id,
                    "metric_id": metric_id,
                    "severity": severity if severity in ("warn", "fail") else "warn",
                    "baseline_value": round(baseline_value, 6),
                    "current_value": round(current_value, 6),
                    "absolute_delta": round(absolute_delta, 6),
                    "percent_delta": round(percent_delta, 6),
                    "tolerance": tolerance,
                }
            )
            summary["regression_count"] += 1
            if severity == "fail":
                summary["critical_failures"] += 1
            else:
                summary["warnings"] += 1

    regressions.sort(key=lambda item: (str(item.get("envelope_id", "")), str(item.get("metric_id", ""))))
    return {
        "artifact_class": "CANONICAL",
        "schema_id": "dominium.schema.governance.performance_result",
        "schema_version": "1.0.0",
        "record": {
            "result_set_id": "performx.regressions",
            "regressions": regressions,
            "summary": summary,
            "extensions": {},
        },
    }

