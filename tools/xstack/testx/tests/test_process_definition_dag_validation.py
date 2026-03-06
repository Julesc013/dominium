"""FAST test: PROC-1 process definition DAG validation behaves deterministically."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_process_definition_dag_validation"
TEST_TAGS = ["fast", "proc", "validation"]


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

    from src.process.process_definition_validator import build_process_definition_row, validate_process_definition

    action_registry = _load_json(repo_root, "data/registries/action_template_registry.json")
    temporal_registry = _load_json(repo_root, "data/registries/temporal_domain_registry.json")

    valid_definition = build_process_definition_row(
        process_id="proc.test.dag_valid",
        version="1.0.0",
        description="valid dag",
        step_graph={
            "steps": [
                {"step_id": "step.action", "step_kind": "action", "action_template_id": "action.elec.breaker.toggle", "inputs": [], "outputs": [{"ref_id": "artifact.process.action", "ref_type": "artifact"}], "cost_units": 1},
                {"step_id": "step.verify", "step_kind": "verify", "inputs": [], "outputs": [{"ref_id": "artifact.process.verify", "ref_type": "report"}], "cost_units": 1},
            ],
            "edges": [{"from_step_id": "step.action", "to_step_id": "step.verify"}],
        },
        input_signature=[],
        output_signature=[],
        required_tools=[],
        required_environment=[],
        tier_contract_id="tier.proc.default",
        coupling_budget_id=None,
        deterministic_fingerprint="",
        extensions={},
    )
    valid = validate_process_definition(
        process_definition_row=valid_definition,
        action_template_registry_payload=action_registry,
        temporal_domain_registry_payload=temporal_registry,
    )
    if str(valid.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "valid process definition refused: {}".format(",".join(valid.get("violations") or []))}

    invalid_definition = dict(valid_definition)
    invalid_definition["step_graph"] = {
        "steps": list(valid_definition["step_graph"]["steps"]),
        "edges": [
            {"from_step_id": "step.action", "to_step_id": "step.verify"},
            {"from_step_id": "step.verify", "to_step_id": "step.action"},
        ],
    }
    invalid = validate_process_definition(
        process_definition_row=invalid_definition,
        action_template_registry_payload=action_registry,
        temporal_domain_registry_payload=temporal_registry,
    )
    if str(invalid.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "cyclic process definition unexpectedly accepted"}
    if str(invalid.get("reason_code", "")).strip() != "refusal.process.invalid_definition":
        return {"status": "fail", "message": "unexpected reason code for cyclic definition"}

    return {"status": "pass", "message": "PROC-1 DAG validation deterministic and cycle-safe"}
