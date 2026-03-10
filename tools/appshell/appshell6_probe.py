"""Deterministic APPSHELL-6 supervisor probe helpers."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from src.appshell.supervisor import (  # noqa: E402
    SUPERVISOR_AGGREGATED_LOG_REL,
    SUPERVISOR_RUN_MANIFEST_REL,
    attach_supervisor_children,
    discover_active_supervisor_endpoint,
    invoke_supervisor_service_command,
    launch_supervisor_service,
    load_supervisor_runtime_state,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value or []) if isinstance(value, list) else []


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, dict) else {}


def _read_jsonl(path: str) -> list[dict]:
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw_line in handle:
                token = str(raw_line or "").strip()
                if not token:
                    continue
                try:
                    payload = json.loads(token)
                except ValueError:
                    continue
                if isinstance(payload, Mapping):
                    rows.append(dict(payload))
    except OSError:
        return []
    return rows


def _cleanup_supervisor(repo_root: str) -> None:
    for _ in range(4):
        endpoint = discover_active_supervisor_endpoint(repo_root)
        state = load_supervisor_runtime_state(repo_root)
        process_rows = [_as_map(row) for row in _as_list(_as_map(state).get("processes"))]
        any_running = any(str(row.get("status", "")).strip() == "running" for row in process_rows)
        if not endpoint and not any_running:
            return
        if endpoint:
            invoke_supervisor_service_command(repo_root, "launcher stop")
        for _drain in range(2):
            endpoint = discover_active_supervisor_endpoint(repo_root)
            state = load_supervisor_runtime_state(repo_root)
            process_rows = [_as_map(row) for row in _as_list(_as_map(state).get("processes"))]
            any_running = any(str(row.get("status", "")).strip() == "running" for row in process_rows)
            if not endpoint and not any_running:
                return


def run_supervisor_probe(
    repo_root: str,
    *,
    suffix: str = "default",
    topology: str = "singleplayer",
    supervisor_policy_id: str = "supervisor.policy.lab",
) -> dict:
    repo_root_abs = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    _cleanup_supervisor(repo_root_abs)
    seed = "seed.appshell6.{}".format(str(suffix or "default").strip() or "default")
    started = launch_supervisor_service(
        repo_root=repo_root_abs,
        seed=seed,
        supervisor_policy_id=str(supervisor_policy_id).strip() or "supervisor.policy.lab",
        topology=str(topology or "singleplayer").strip() or "singleplayer",
    )
    if str(started.get("result", "")).strip() != "complete":
        return dict(started)
    try:
        status = invoke_supervisor_service_command(repo_root_abs, "launcher status")
        state = load_supervisor_runtime_state(repo_root_abs)
        manifest = _read_json(os.path.join(repo_root_abs, SUPERVISOR_RUN_MANIFEST_REL.replace("/", os.sep)))
        aggregated_logs = _read_jsonl(os.path.join(repo_root_abs, SUPERVISOR_AGGREGATED_LOG_REL.replace("/", os.sep)))
        attachments = attach_supervisor_children(repo_root_abs, attach_all=True)
        stop = invoke_supervisor_service_command(repo_root_abs, "launcher stop")
        process_rows = sorted(
            _as_list(_as_map(state).get("processes")),
            key=lambda row: (str(_as_map(row).get("product_id", "")), str(_as_map(row).get("pid_stub", ""))),
        )
        endpoint_to_product = {
            str(_as_map(row).get("endpoint_id", "")).strip(): str(_as_map(row).get("product_id", "")).strip()
            for row in process_rows
            if str(_as_map(row).get("endpoint_id", "")).strip()
        }
        summary = {
            "process_statuses": [
                {
                    "product_id": str(_as_map(row).get("product_id", "")).strip(),
                    "status": str(_as_map(row).get("status", "")).strip(),
                    "attach_status": str(_as_map(row).get("attach_status", "")).strip(),
                    "restart_count": int(_as_map(row).get("restart_count", 0) or 0),
                    "compatibility_mode_id": str(_as_map(row).get("compatibility_mode_id", "")).strip(),
                    "read_only_mode": bool(_as_map(row).get("read_only_mode", False)),
                }
                for row in process_rows
            ],
            "attachment_results": [
                {
                    "product_id": endpoint_to_product.get(str(_as_map(row).get("endpoint_id", "")).strip(), ""),
                    "result": str(_as_map(row).get("result", "")).strip(),
                    "compatibility_mode_id": str(_as_map(row).get("compatibility_mode_id", "")).strip(),
                }
                for row in sorted(_as_list(_as_map(attachments).get("attachments")), key=lambda row: str(_as_map(row).get("endpoint_id", "")))
            ],
            "aggregated_log_event_ids": [
                str(_as_map(row).get("event_id", "")).strip()
                for row in aggregated_logs[-16:]
            ],
            "aggregated_log_rows": [
                {
                    "source_product_id": str(_as_map(row).get("source_product_id", "")).strip(),
                    "event_id": str(_as_map(row).get("event_id", "")).strip(),
                    "message_key": str(_as_map(row).get("message_key", "")).strip(),
                    "severity": str(_as_map(row).get("severity", "")).strip(),
                }
                for row in aggregated_logs[-16:]
            ],
            "processes": [
                {
                    "product_id": str(_as_map(row).get("product_id", "")).strip(),
                    "binary_hash": str(_as_map(row).get("binary_hash", "")).strip(),
                    "pid_stub": str(_as_map(row).get("pid_stub", "")).strip(),
                }
                for row in sorted(_as_list(_as_map(manifest).get("processes")), key=lambda row: (str(_as_map(row).get("product_id", "")), str(_as_map(row).get("pid_stub", ""))))
            ],
            "topology": str(_as_map(_as_map(manifest).get("extensions")).get("official.topology", "")).strip(),
            "supervisor_policy_id": str(_as_map(_as_map(manifest).get("extensions")).get("official.supervisor_policy_id", "")).strip(),
            "stop_result": str(_as_map(stop).get("result", "")).strip(),
        }
        return {
            "result": "complete",
            "start": dict(started),
            "status": dict(status),
            "attachments": dict(attachments),
            "state": dict(state),
            "run_manifest": dict(manifest),
            "aggregated_logs": aggregated_logs,
            "stop": dict(stop),
            "cross_platform_supervisor_hash": canonical_sha256(summary),
            "deterministic_fingerprint": canonical_sha256(
                {
                    "start": str(_as_map(started).get("service_endpoint_id", "")).strip(),
                    "status": str(_as_map(status).get("result", "")).strip(),
                    "attachments": len(_as_list(_as_map(attachments).get("attachments"))),
                    "hash": canonical_sha256(summary),
                }
            ),
        }
    finally:
        _cleanup_supervisor(repo_root_abs)


def verify_supervisor_replay(repo_root: str, *, suffix: str = "replay") -> dict:
    token = str(suffix).strip() or "replay"
    first = run_supervisor_probe(repo_root, suffix="{}.one".format(token))
    second = run_supervisor_probe(repo_root, suffix="{}.two".format(token))
    mismatches = []
    for key in ("cross_platform_supervisor_hash",):
        if first.get(key) != second.get(key):
            mismatches.append(key)
    return {
        "result": "complete" if not mismatches else "refused",
        "first": first,
        "second": second,
        "mismatches": mismatches,
        "replay_fingerprint": canonical_sha256(
            {
                "first_hash": str(_as_map(first).get("cross_platform_supervisor_hash", "")).strip(),
                "second_hash": str(_as_map(second).get("cross_platform_supervisor_hash", "")).strip(),
                "mismatches": mismatches,
            }
        ),
    }


__all__ = ["run_supervisor_probe", "verify_supervisor_replay"]
