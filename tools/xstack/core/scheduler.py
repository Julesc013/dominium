"""Parallel deterministic scheduler for XStack execution plans."""

from __future__ import annotations

import hashlib
import json
import os
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from typing import Dict, List

from . import log as xlog
from .cache_store import load_entry, store_entry
from .profiler import end_phase, start_phase
from .runners import resolve_adapter, result_to_dict
from .runners_base import RunnerContext


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _node_input_hash(node: dict, plan_payload: dict, completed: Dict[str, dict]) -> str:
    dep_hashes = []
    for dep_id in sorted(str(item) for item in (node.get("depends_on") or []) if str(item).strip()):
        dep = completed.get(dep_id, {})
        dep_hashes.append("{}:{}".format(dep_id, str(dep.get("output_hash", ""))))
    payload = {
        "repo_state_hash": str(plan_payload.get("repo_state_hash", "")),
        "plan_profile": str(plan_payload.get("profile", "")),
        "strict_variant": str(plan_payload.get("strict_variant", "")),
        "runner_id": str(node.get("runner_id", "")),
        "group_id": str(node.get("group_id", "")),
        "command": node.get("command") or [],
        "deps": dep_hashes,
    }
    return _hash_text(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def _run_node(node: dict, repo_root: str, workspace_id: str, plan_payload: dict) -> dict:
    adapter = resolve_adapter(str(node.get("runner_id", "")))
    context = RunnerContext(
        repo_root=repo_root,
        workspace_id=workspace_id,
        node=node,
        plan_profile=str(plan_payload.get("profile", "")).strip(),
        repo_state_hash=str(plan_payload.get("repo_state_hash", "")).strip(),
    )
    return result_to_dict(adapter.run(context))


def _cache_profile_id(runner_id: str, profile_id: str) -> str:
    token = str(runner_id).strip()
    if token == "repox_runner":
        return "SHARED_REPOX"
    if token == "auditx.group.core.policy":
        return "SHARED_AUDITX_CORE"
    if token == "testx.group.core.invariants":
        return "SHARED_TESTX_CORE"
    if token == "testx.group.runtime.verify":
        return "SHARED_TESTX_RUNTIME"
    return str(profile_id).strip()


def execute_plan(
    repo_root: str,
    plan_payload: Dict[str, object],
    trace: bool = False,
    profile_report: bool = False,
    cache_root: str = "",
) -> Dict[str, object]:
    start_phase("scheduler.execute_plan", {"profile": str(plan_payload.get("profile", ""))})
    fail_fast = str(plan_payload.get("profile", "")).strip().upper() not in {"FULL", "FULL_ALL"}
    nodes = [row for row in (plan_payload.get("nodes") or []) if isinstance(row, dict)]
    node_by_id = {str(row.get("node_id", "")): row for row in nodes}
    pending = sorted(node_by_id.keys())
    completed: Dict[str, dict] = {}
    running = {}
    results: List[dict] = []

    cache_hits = 0
    cache_misses = 0
    started = time.time()
    max_workers = max(1, min(int(os.environ.get("DOM_GATE_MAX_WORKERS", "0") or 0) or (os.cpu_count() or 4), 16))

    xlog.plan_summary(plan_payload, trace=trace)
    xlog.explain_plan(plan_payload, trace=trace)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            while pending or running:
                ready: List[str] = []
                for node_id in list(pending):
                    node = node_by_id[node_id]
                    deps = [str(item) for item in (node.get("depends_on") or []) if str(item).strip()]
                    if all(dep in completed for dep in deps):
                        ready.append(node_id)

                ready.sort(
                    key=lambda node_id: (
                        int((node_by_id[node_id]).get("level", 0)),
                        str((node_by_id[node_id]).get("runner_id", "")),
                        node_id,
                    )
                )

                for node_id in ready:
                    node = node_by_id[node_id]
                    pending.remove(node_id)
                    runner_id = str(node.get("runner_id", "")).strip()
                    input_hash = _node_input_hash(node, plan_payload, completed)
                    cache_profile = _cache_profile_id(runner_id, str(plan_payload.get("profile", "")).strip())
                    cache_entry = load_entry(
                        repo_root,
                        runner_id=runner_id,
                        input_hash=input_hash,
                        profile_id=cache_profile,
                        cache_root=cache_root,
                    )
                    if cache_entry:
                        cache_hits += 1
                        xlog.cache_event(runner_id, True, trace=trace)
                        result = {
                            "node_id": node_id,
                            "runner_id": runner_id,
                            "exit_code": int(cache_entry.get("exit_code", 1)),
                            "output_hash": str(cache_entry.get("output_hash", "")),
                            "artifacts_produced": cache_entry.get("artifacts_produced") or [],
                            "output": "cache_hit",
                            "cache_hit": True,
                        }
                        completed[node_id] = result
                        results.append(result)
                        continue

                    cache_misses += 1
                    xlog.cache_event(runner_id, False, trace=trace)
                    node_start = xlog.phase_start(runner_id, trace=trace)
                    start_phase("runner.{}".format(runner_id))
                    future = pool.submit(_run_node, node, repo_root, str(plan_payload.get("workspace_id", "")), plan_payload)
                    running[future] = (node_id, input_hash, node_start, "runner.{}".format(runner_id), cache_profile)

                if not running:
                    continue

                done, _pending = wait(list(running.keys()), return_when=FIRST_COMPLETED)
                for future in done:
                    node_id, input_hash, node_start, phase_name, cache_profile = running.pop(future)
                    node = node_by_id[node_id]
                    runner_id = str(node.get("runner_id", "")).strip()
                    raw = future.result()
                    result = {
                        "node_id": node_id,
                        "runner_id": runner_id,
                        "exit_code": int(raw.get("exit_code", 1)),
                        "output_hash": str(raw.get("output_hash", "")),
                        "artifacts_produced": raw.get("artifacts_produced") or [],
                        "output": str(raw.get("output", "")),
                        "cache_hit": False,
                    }
                    xlog.phase_end(runner_id, node_start, False, trace=trace)
                    end_phase(phase_name, {"exit_code": int(result["exit_code"])})
                    completed[node_id] = result
                    results.append(result)

                    store_entry(
                        repo_root,
                        runner_id=runner_id,
                        input_hash=input_hash,
                        profile_id=cache_profile,
                        exit_code=result["exit_code"],
                        output_hash=result["output_hash"],
                        artifacts_produced=result["artifacts_produced"],
                        timestamp_utc=str(raw.get("timestamp_utc", "")),
                        output=result["output"],
                        cache_root=cache_root,
                    )

                    if result["exit_code"] != 0 and fail_fast:
                        # FAST/STRICT lanes fail fast; FULL continues to surface full-shard diagnostics.
                        pending = []
                        running.clear()
                        break

        ordered = sorted(
            results,
            key=lambda row: (
                int((node_by_id.get(str(row.get("node_id", "")), {})).get("level", 0)),
                str(row.get("runner_id", "")),
                str(row.get("node_id", "")),
            ),
        )
        total_s = max(0.0, time.time() - started)
        xlog.profile_summary(str(plan_payload.get("profile", "")).strip(), total_s, cache_hits, cache_misses, trace=trace)

        payload = {
            "plan_hash": str(plan_payload.get("plan_hash", "")),
            "profile": str(plan_payload.get("profile", "")),
            "total_seconds": total_s,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "results": ordered,
            "exit_code": 0 if all(int(item.get("exit_code", 1)) == 0 for item in ordered) else 1,
        }
        if profile_report:
            payload["profile_report"] = {
                "max_workers": max_workers,
                "node_count": len(nodes),
                "cache_hit_ratio": float(cache_hits) / float(max(1, cache_hits + cache_misses)),
            }
        return payload
    finally:
        end_phase("scheduler.execute_plan")
