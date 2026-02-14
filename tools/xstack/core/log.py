"""Structured live logging for XStack gate execution."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List


def _utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _emit(payload: Dict[str, Any], trace: bool = False) -> None:
    record = dict(payload)
    record["ts_utc"] = _utc_now()
    if trace:
        sys.stdout.write(json.dumps(record, sort_keys=True) + "\n")
    else:
        event = str(record.get("event", "")).strip()
        runner_id = str(record.get("runner_id", "")).strip()
        summary = str(record.get("summary", "")).strip()
        duration = record.get("duration_s")
        cache_hit = record.get("cache_hit")
        parts: List[str] = [event] if event else ["gate"]
        if runner_id:
            parts.append("runner={}".format(runner_id))
        if duration is not None:
            parts.append("duration_s={:.3f}".format(float(duration)))
        if cache_hit is not None:
            parts.append("cache_hit={}".format("true" if cache_hit else "false"))
        if summary:
            parts.append(summary)
        sys.stdout.write("[xstack] {}\n".format(" ".join(parts)))
    sys.stdout.flush()


def phase_start(runner_id: str, trace: bool = False) -> float:
    start = time.time()
    _emit({"event": "phase_start", "runner_id": runner_id}, trace=trace)
    return start


def phase_end(runner_id: str, start_time: float, cache_hit: bool, trace: bool = False) -> None:
    duration = max(0.0, time.time() - float(start_time))
    _emit(
        {
            "event": "phase_end",
            "runner_id": runner_id,
            "duration_s": duration,
            "cache_hit": bool(cache_hit),
        },
        trace=trace,
    )


def plan_summary(plan_payload: Dict[str, Any], trace: bool = False) -> None:
    nodes = plan_payload.get("nodes", [])
    profile = str(plan_payload.get("profile", "")).strip()
    summary = "profile={} nodes={}".format(profile or "unknown", len(nodes))
    _emit({"event": "plan_summary", "summary": summary}, trace=trace)


def explain_plan(plan_payload: Dict[str, Any], trace: bool = False) -> None:
    node_ids = [str(item.get("runner_id", "")).strip() for item in (plan_payload.get("nodes") or []) if isinstance(item, dict)]
    _emit(
        {
            "event": "plan_explain",
            "summary": " -> ".join([item for item in node_ids if item]) or "empty_plan",
        },
        trace=trace,
    )


def profile_summary(profile_id: str, total_time_s: float, cache_hits: int, cache_misses: int, trace: bool = False) -> None:
    _emit(
        {
            "event": "profile_summary",
            "summary": "profile={} total_s={:.3f} cache_hits={} cache_misses={}".format(
                profile_id,
                max(0.0, float(total_time_s)),
                int(cache_hits),
                int(cache_misses),
            ),
        },
        trace=trace,
    )


def failure_summary(primary_failure_class: str, rows: Iterable[Dict[str, Any]], trace: bool = False) -> None:
    summary_rows = [row for row in rows if isinstance(row, dict)]
    parts = []
    for row in summary_rows:
        klass = str(row.get("failure_class", "")).strip()
        count = int(row.get("count", 0))
        if not klass:
            continue
        parts.append("{}={}".format(klass, count))
    if not parts:
        return
    _emit(
        {
            "event": "failure_summary",
            "summary": "primary={} classes={}".format(str(primary_failure_class or "none"), ",".join(parts)),
        },
        trace=trace,
    )


def escalation_trigger(reason: str, trace: bool = False) -> None:
    _emit({"event": "escalation_trigger", "summary": reason}, trace=trace)


def cache_event(runner_id: str, cache_hit: bool, trace: bool = False) -> None:
    _emit(
        {
            "event": "cache_hit" if cache_hit else "cache_miss",
            "runner_id": runner_id,
            "cache_hit": bool(cache_hit),
        },
        trace=trace,
    )
