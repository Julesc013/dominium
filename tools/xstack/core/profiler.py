"""Deterministic structured profiler for XStack execution."""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime
from typing import Dict, List


class _ProfilerState:
    def __init__(self):
        self.lock = threading.Lock()
        self.trace = False
        self.reset()

    def reset(self):
        self.run_started_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.run_started_perf = time.perf_counter()
        self.next_id = 1
        self.tokens: Dict[int, dict] = {}
        self.stacks: Dict[int, List[int]] = {}
        self.events: List[dict] = []
        self.cumulative: Dict[str, dict] = {}


_STATE = _ProfilerState()


def configure(trace: bool = False):
    with _STATE.lock:
        _STATE.trace = bool(trace)


def reset(trace: bool = False):
    with _STATE.lock:
        _STATE.trace = bool(trace)
        _STATE.reset()


def _emit(line: str):
    if _STATE.trace:
        print(line, flush=True)


def start_phase(name: str, meta: dict | None = None) -> int:
    phase_name = str(name).strip() or "unnamed_phase"
    with _STATE.lock:
        token_id = _STATE.next_id
        _STATE.next_id += 1
        now = time.perf_counter()
        tid = threading.get_ident()
        stack = _STATE.stacks.setdefault(tid, [])
        parent_id = stack[-1] if stack else 0
        depth = len(stack)
        token = {
            "id": token_id,
            "name": phase_name,
            "started_perf": now,
            "thread_id": tid,
            "parent_id": parent_id,
            "depth": depth,
            "meta": dict(meta or {}),
        }
        _STATE.tokens[token_id] = token
        stack.append(token_id)
        _STATE.events.append(
            {
                "event": "start",
                "phase_id": token_id,
                "name": phase_name,
                "thread_id": tid,
                "parent_id": parent_id,
                "depth": depth,
                "t_rel_s": max(0.0, now - _STATE.run_started_perf),
                "meta": dict(meta or {}),
            }
        )
    _emit("[xstack-profile] start {} id={}".format(phase_name, token_id))
    return token_id


def end_phase(name: str, meta: dict | None = None) -> float:
    phase_name = str(name).strip() or "unnamed_phase"
    now = time.perf_counter()
    with _STATE.lock:
        tid = threading.get_ident()
        stack = _STATE.stacks.get(tid, [])
        token_id = 0
        if stack:
            if _STATE.tokens.get(stack[-1], {}).get("name", "") == phase_name:
                token_id = stack.pop()
            else:
                for idx in range(len(stack) - 1, -1, -1):
                    probe_id = stack[idx]
                    if _STATE.tokens.get(probe_id, {}).get("name", "") == phase_name:
                        token_id = probe_id
                        del stack[idx]
                        break
        token = _STATE.tokens.pop(token_id, {}) if token_id else {}
        started = float(token.get("started_perf", now))
        duration = max(0.0, now - started)
        cumulative = _STATE.cumulative.setdefault(
            phase_name,
            {
                "phase_name": phase_name,
                "count": 0,
                "total_s": 0.0,
                "min_s": 0.0,
                "max_s": 0.0,
            },
        )
        cumulative["count"] = int(cumulative["count"]) + 1
        cumulative["total_s"] = float(cumulative["total_s"]) + duration
        if int(cumulative["count"]) == 1:
            cumulative["min_s"] = duration
            cumulative["max_s"] = duration
        else:
            cumulative["min_s"] = min(float(cumulative["min_s"]), duration)
            cumulative["max_s"] = max(float(cumulative["max_s"]), duration)
        _STATE.events.append(
            {
                "event": "end",
                "phase_id": int(token.get("id", 0)),
                "name": phase_name,
                "thread_id": tid,
                "parent_id": int(token.get("parent_id", 0)),
                "depth": int(token.get("depth", 0)),
                "duration_s": duration,
                "t_rel_s": max(0.0, now - _STATE.run_started_perf),
                "meta": dict(meta or {}),
            }
        )
    _emit("[xstack-profile] end {} duration_s={:.3f}".format(phase_name, duration))
    return duration


def snapshot(extra: dict | None = None) -> dict:
    with _STATE.lock:
        total_s = max(0.0, time.perf_counter() - _STATE.run_started_perf)
        cumulative_rows = sorted(
            (dict(row) for row in _STATE.cumulative.values()),
            key=lambda row: (-float(row.get("total_s", 0.0)), str(row.get("phase_name", ""))),
        )
        payload = {
            "schema_version": "1.0.0",
            "run_started_utc": _STATE.run_started_utc,
            "total_runtime_s": total_s,
            "cumulative": cumulative_rows,
            "events": list(_STATE.events),
        }
    if extra:
        payload["extra"] = dict(extra)
    return payload


def export_json(path: str, extra: dict | None = None) -> str:
    payload = snapshot(extra=extra)
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
