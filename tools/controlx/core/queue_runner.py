"""Queue runner for ControlX."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, List, Tuple

from escalation import detect_semantic_ambiguity, format_semantic_escalation
from execution_router import route_execution
from controlx_logging import compute_run_id, write_json, write_runlog
from prompt_parser import parse_prompt
from prompt_sanitizer import sanitize_prompt, write_sanitization_report
from remediation_bridge import write_remediation_links
from workspace_manager import prepare_workspace


def _norm(path: str) -> str:
    return os.path.normpath(path)


def _repo_rel(repo_root: str, path: str) -> str:
    return os.path.relpath(path, repo_root).replace("\\", "/")


def _read_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def load_policy(repo_root: str, policy_rel: str) -> Dict[str, Any]:
    path = _norm(os.path.join(repo_root, policy_rel))
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise RuntimeError("refuse.controlx_policy_invalid")
    return payload


def _resolve_prompt_text(item: Dict[str, Any], queue_dir: str) -> str:
    text = str(item.get("prompt_text", "")).strip()
    if text:
        return text
    prompt_file = str(item.get("prompt_file", "")).strip()
    if not prompt_file:
        return ""
    path = prompt_file
    if not os.path.isabs(path):
        path = _norm(os.path.join(queue_dir, prompt_file))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return ""


def _normalize_items(raw_items: Iterable[Any], queue_dir: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for idx, row in enumerate(raw_items, start=1):
        if isinstance(row, str):
            out.append({"item_id": "queue-item-{:04d}".format(idx), "prompt_text": row})
            continue
        if not isinstance(row, dict):
            continue
        item_id = str(row.get("item_id", "")).strip() or "queue-item-{:04d}".format(idx)
        prompt_text = _resolve_prompt_text(row, queue_dir)
        out.append(
            {
                "item_id": item_id,
                "prompt_text": prompt_text,
                "metadata": row.get("metadata", {}) if isinstance(row.get("metadata"), dict) else {},
            }
        )
    return out


def load_queue_file(queue_file: str) -> Tuple[str, List[Dict[str, Any]], bool]:
    queue_path = _norm(os.path.abspath(queue_file))
    queue_dir = os.path.dirname(queue_path)
    payload = _read_json(queue_path)
    if isinstance(payload, list):
        return "controlx.queue.list", _normalize_items(payload, queue_dir), True
    if not isinstance(payload, dict):
        raise RuntimeError("refuse.queue_invalid")

    if isinstance(payload.get("record"), dict):
        record = payload.get("record", {})
        queue_id = str(record.get("queue_id", "")).strip() or "controlx.queue.record"
        rows = record.get("items", [])
        continue_on_mechanical = bool(record.get("continue_on_mechanical_failure", True))
        return queue_id, _normalize_items(rows if isinstance(rows, list) else [], queue_dir), continue_on_mechanical

    queue_id = str(payload.get("queue_id", "")).strip() or "controlx.queue.object"
    rows = payload.get("items", [])
    continue_on_mechanical = bool(payload.get("continue_on_mechanical_failure", True))
    return queue_id, _normalize_items(rows if isinstance(rows, list) else [], queue_dir), continue_on_mechanical


def _audit_root_path(repo_root: str, audit_root: str) -> str:
    if os.path.isabs(audit_root):
        return _norm(audit_root)
    return _norm(os.path.join(repo_root, audit_root))


def _run_dir(audit_root_abs: str, run_id: str) -> str:
    path = _norm(os.path.join(audit_root_abs, run_id))
    os.makedirs(path, exist_ok=True)
    return path


def _queue_summary_payload(queue_id: str, run_results: List[Dict[str, Any]], overall_status: str) -> Dict[str, Any]:
    return {
        "artifact_class": "CANONICAL",
        "queue_id": queue_id,
        "overall_status": overall_status,
        "run_count": len(run_results),
        "runs": run_results,
    }


def run_items(
    repo_root: str,
    items: List[Dict[str, Any]],
    policy: Dict[str, Any],
    workspace_seed: str = "",
    dry_run: bool = False,
    audit_root: str = os.path.join("docs", "audit", "controlx"),
    simulate_mechanical_failure_index: int = 0,
    queue_id: str = "controlx.queue.runtime",
    continue_on_mechanical_failure: bool = True,
) -> Dict[str, Any]:
    audit_root_abs = _audit_root_path(repo_root, audit_root)
    os.makedirs(audit_root_abs, exist_ok=True)

    run_summaries: List[Dict[str, Any]] = []
    overall_code = 0
    escalation_text = ""
    for idx, item in enumerate(items, start=1):
        prompt_text = str(item.get("prompt_text", ""))
        parsed = parse_prompt(prompt_text, policy)
        sanitized = sanitize_prompt(parsed, policy)

        workspace = prepare_workspace(repo_root, parsed.get("prompt_hash", ""), idx, workspace_seed=workspace_seed)
        ws_id = workspace["workspace_id"]
        run_id = compute_run_id(parsed.get("prompt_hash", ""), idx)
        run_dir = _run_dir(audit_root_abs, run_id)

        write_sanitization_report(os.path.join(run_dir, "SANITIZATION.md"), parsed, sanitized)
        route_result = route_execution(
            repo_root=repo_root,
            ws_id=ws_id,
            env=workspace["env"],
            dry_run=dry_run,
            simulate_mechanical_failure=(simulate_mechanical_failure_index == idx),
        )
        links = write_remediation_links(repo_root, run_dir, ws_id, route_result)

        semantic_markers = detect_semantic_ambiguity(route_result.get("steps", [])[-1].get("output", "") if route_result.get("steps") else "", policy)
        semantic_failure = bool(route_result.get("semantic_failure", False)) and bool(semantic_markers)

        status = "pass" if int(route_result.get("returncode", 1)) == 0 else "fail"
        if route_result.get("mechanical_failure", False):
            status = "pass" if int(route_result.get("returncode", 1)) == 0 else "mechanical_failed"
        if semantic_failure:
            status = "semantic_escalation_required"

        run_payload = {
            "artifact_class": "CANONICAL",
            "item_id": item.get("item_id", "queue-item-{:04d}".format(idx)),
            "prompt_hash": parsed.get("prompt_hash", ""),
            "requested_subsystems": parsed.get("requested_subsystems", []),
            "sanitization_action_count": len(sanitized.get("actions", [])),
            "workspace_id": ws_id,
            "gate_steps": [
                {
                    "command": " ".join(step.get("command", [])),
                    "returncode": int(step.get("returncode", 1)),
                }
                for step in route_result.get("steps", [])
            ],
            "remediation_artifact_count": len(links.get("remediation_artifacts", [])),
            "status": status,
        }
        write_runlog(run_dir, run_payload)
        run_summaries.append(
            {
                "run_id": run_id,
                "workspace_id": ws_id,
                "status": status,
                "runlog": _repo_rel(repo_root, os.path.join(run_dir, "RUNLOG.json")),
            }
        )

        if semantic_failure:
            escalation_text = format_semantic_escalation(
                blocker_type="SEMANTIC_AMBIGUITY",
                failed_gate="gate.py exitcheck",
                root_cause="semantic markers detected: {}".format(", ".join(semantic_markers)),
                attempted_fixes=["prompt_sanitization", "gate_remediation"],
                remaining_options=["interpretation_a", "interpretation_b"],
                recommended_option="interpretation_a",
                rationale="Policy requires semantic decision for conflicting governance meaning.",
            )
            overall_code = 2
            break

        if int(route_result.get("returncode", 1)) != 0:
            overall_code = 1
            if not route_result.get("mechanical_failure", False):
                break
            if not continue_on_mechanical_failure:
                break

    overall_status = "queue_complete"
    if overall_code == 1:
        overall_status = "queue_complete_with_failures"
    if overall_code == 2:
        overall_status = "queue_semantic_escalation"

    summary = _queue_summary_payload(queue_id, run_summaries, overall_status)
    summary_path = os.path.join(audit_root_abs, "{}.QUEUE_RUNLOG.json".format(queue_id.replace("/", "_")))
    write_json(summary_path, summary)
    payload: Dict[str, Any] = {
        "result": overall_status,
        "queue_id": queue_id,
        "run_count": len(run_summaries),
        "runs": run_summaries,
        "queue_runlog": _repo_rel(repo_root, summary_path),
    }
    if escalation_text:
        payload["semantic_escalation"] = escalation_text
    return {"returncode": overall_code, "payload": payload}


def run_queue_file(
    repo_root: str,
    queue_file: str,
    policy: Dict[str, Any],
    workspace_seed: str = "",
    dry_run: bool = False,
    audit_root: str = os.path.join("docs", "audit", "controlx"),
    simulate_mechanical_failure_index: int = 0,
) -> Dict[str, Any]:
    queue_id, items, continue_on_mechanical = load_queue_file(queue_file)
    if not items:
        raise RuntimeError("refuse.queue_empty")
    return run_items(
        repo_root=repo_root,
        items=items,
        policy=policy,
        workspace_seed=workspace_seed,
        dry_run=dry_run,
        audit_root=audit_root,
        simulate_mechanical_failure_index=simulate_mechanical_failure_index,
        queue_id=queue_id,
        continue_on_mechanical_failure=continue_on_mechanical,
    )
