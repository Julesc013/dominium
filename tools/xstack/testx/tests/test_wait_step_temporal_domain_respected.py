"""FAST test: PROC-1 wait steps respect temporal-domain readiness signals."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_wait_step_temporal_domain_respected"
TEST_TAGS = ["fast", "proc", "temporal"]


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.process_run_engine import process_run_start, process_run_tick

    action_registry = _load_json(repo_root, "data/registries/action_template_registry.json")
    temporal_registry = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    process_definition = {
        "process_id": "proc.test.wait",
        "version": "1.0.0",
        "description": "wait gate fixture",
        "step_graph": {
            "steps": [
                {"step_id": "step.wait", "step_kind": "wait", "temporal_domain_id": "time.canonical_tick", "inputs": [], "outputs": [{"ref_id": "artifact.process.wait", "ref_type": "artifact"}], "cost_units": 1}
            ],
            "edges": [],
        },
        "input_signature": [],
        "output_signature": [],
        "required_tools": [],
        "required_environment": [],
        "tier_contract_id": "tier.proc.default",
    }

    started = process_run_start(
        current_tick=200,
        process_definition_row=process_definition,
        action_template_registry_payload=action_registry,
        temporal_domain_registry_payload=temporal_registry,
        input_refs=[],
        run_id="",
    )
    if str(started.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_start refused"}

    tick_pending = process_run_tick(
        current_tick=201,
        run_state=started.get("run_state"),
        process_definition_row=process_definition,
        budget_units=10,
        wait_ready_step_ids=[],
    )
    if str(tick_pending.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "pending tick refused"}
    pending_state = dict((tick_pending.get("run_state") or {}).get("step_status") or {})
    if str(pending_state.get("step.wait", "")).strip() != "waiting_time":
        return {"status": "fail", "message": "wait step completed without temporal readiness"}

    tick_ready = process_run_tick(
        current_tick=202,
        run_state=tick_pending.get("run_state"),
        process_definition_row=process_definition,
        budget_units=10,
        wait_ready_step_ids=["step.wait"],
    )
    if str(tick_ready.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "ready tick refused"}
    ready_state = dict((tick_ready.get("run_state") or {}).get("step_status") or {})
    if str(ready_state.get("step.wait", "")).strip() != "completed":
        return {"status": "fail", "message": "wait step did not complete with temporal readiness"}

    return {"status": "pass", "message": "wait step respects temporal-domain readiness"}
