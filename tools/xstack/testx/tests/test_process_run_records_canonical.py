"""FAST test: PROC-1 process run emits canonical run and step records."""

from __future__ import annotations

import json
import os
import re
import sys


TEST_ID = "test_process_run_records_canonical"
TEST_TAGS = ["fast", "proc", "canonical"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


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

    from process.process_run_engine import process_run_end, process_run_start, process_run_tick

    action_registry = _load_json(repo_root, "data/registries/action_template_registry.json")
    temporal_registry = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    process_definition = {
        "process_id": "proc.test.canonical",
        "version": "1.0.0",
        "description": "canonical run fixture",
        "step_graph": {
            "steps": [
                {"step_id": "step.action", "step_kind": "action", "action_template_id": "action.elec.breaker.toggle", "inputs": [], "outputs": [{"ref_id": "artifact.process.action", "ref_type": "artifact"}], "cost_units": 1},
                {"step_id": "step.transform", "step_kind": "transform", "domain_process_id": "process.test.transform", "inputs": [], "outputs": [{"ref_id": "artifact.process.output", "ref_type": "artifact"}], "cost_units": 1},
            ],
            "edges": [{"from_step_id": "step.action", "to_step_id": "step.transform"}],
        },
        "input_signature": [],
        "output_signature": [],
        "required_tools": [],
        "required_environment": [],
        "tier_contract_id": "tier.proc.default",
    }
    started = process_run_start(
        current_tick=100,
        process_definition_row=process_definition,
        action_template_registry_payload=action_registry,
        temporal_domain_registry_payload=temporal_registry,
        input_refs=[{"ref_id": "batch.input.1", "name": "input", "ref_type": "batch"}],
        run_id="",
    )
    if str(started.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_start refused"}

    ticked = process_run_tick(
        current_tick=101,
        run_state=started.get("run_state"),
        process_definition_row=process_definition,
        budget_units=20,
        completed_action_step_ids=["step.action"],
        transform_step_results={
            "step.transform": {
                "output_refs": [{"ref_id": "batch.output.1", "name": "output", "ref_type": "batch"}],
                "energy_transform_refs": ["ledger.energy.proc.test"],
                "entropy_increment": 2,
            }
        },
    )
    if str(ticked.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_tick refused"}

    ended = process_run_end(current_tick=102, run_record_row=started.get("run_record_row"), run_state=ticked.get("run_state"))
    if str(ended.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process_run_end refused"}

    run_record = dict(ended.get("run_record_row") or {})
    if str(run_record.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "run record missing schema_version"}
    if str(run_record.get("status", "")).strip() != "completed":
        return {"status": "fail", "message": "run record status not completed"}
    if not _HASH64.fullmatch(str(run_record.get("deterministic_fingerprint", "")).strip().lower()):
        return {"status": "fail", "message": "run record fingerprint invalid"}

    step_records = list((dict(ended.get("run_state") or {}).get("step_records") or []))
    if len(step_records) < 3:
        return {"status": "fail", "message": "expected canonical step records not emitted"}
    for row in step_records:
        if str(row.get("schema_version", "")).strip() != "1.0.0":
            return {"status": "fail", "message": "step record missing schema_version"}
        if not _HASH64.fullmatch(str(row.get("deterministic_fingerprint", "")).strip().lower()):
            return {"status": "fail", "message": "step record fingerprint invalid"}

    return {"status": "pass", "message": "process run and step records are canonical"}
