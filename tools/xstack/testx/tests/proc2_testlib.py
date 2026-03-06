"""Shared PROC-2 quality modeling TestX fixtures."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _process_definition(*, yield_model_id: str, defect_model_id: str) -> dict:
    return {
        "process_id": "proc.test.proc2.quality",
        "version": "1.0.0",
        "description": "PROC-2 quality fixture definition",
        "step_graph": {
            "steps": [
                {
                    "step_id": "step.action",
                    "step_kind": "action",
                    "action_template_id": "action.elec.breaker.toggle",
                    "inputs": [],
                    "outputs": [{"ref_id": "artifact.process.action", "ref_type": "artifact"}],
                    "cost_units": 1,
                },
                {
                    "step_id": "step.transform",
                    "step_kind": "transform",
                    "domain_process_id": "process.test.proc2.transform",
                    "inputs": [],
                    "outputs": [{"ref_id": "batch.output.alpha", "ref_type": "batch"}],
                    "cost_units": 1,
                    "extensions": {
                        "moves_mass_energy": True,
                        "requires_energy_ledger": True,
                    },
                },
            ],
            "edges": [{"from_step_id": "step.action", "to_step_id": "step.transform"}],
        },
        "input_signature": [
            {"name": "input_a", "ref_id": "batch.input.alpha", "ref_type": "batch"},
            {"name": "input_b", "ref_id": "batch.input.beta", "ref_type": "batch"},
        ],
        "output_signature": [{"name": "output", "ref_id": "batch.output.alpha", "ref_type": "batch"}],
        "required_tools": ["tool.proc2.rig.alpha"],
        "required_environment": ["env.proc2.standard"],
        "tier_contract_id": "tier.proc.default",
        "coupling_budget_id": None,
        "yield_model_id": str(yield_model_id),
        "defect_model_id": str(defect_model_id),
    }


def run_proc2_quality_case(
    *,
    repo_root: str,
    run_id: str,
    yield_model_id: str,
    defect_model_id: str,
    quality_inputs: Mapping[str, object] | None = None,
    stochastic_quality_enabled: bool = False,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.process_run_engine import process_run_end, process_run_start, process_run_tick

    action_registry = _load_json(repo_root, "data/registries/action_template_registry.json")
    temporal_registry = _load_json(repo_root, "data/registries/temporal_domain_registry.json")
    yield_registry = _load_json(repo_root, "data/registries/yield_model_registry.json")
    defect_registry = _load_json(repo_root, "data/registries/defect_model_registry.json")
    model_registry = _load_json(repo_root, "data/registries/constitutive_model_registry.json")
    model_type_registry = _load_json(repo_root, "data/registries/model_type_registry.json")
    cache_policy_registry = _load_json(repo_root, "data/registries/model_cache_policy_registry.json")

    process_definition = _process_definition(yield_model_id=str(yield_model_id), defect_model_id=str(defect_model_id))
    started = process_run_start(
        current_tick=100,
        process_definition_row=process_definition,
        action_template_registry_payload=action_registry,
        temporal_domain_registry_payload=temporal_registry,
        input_refs=[
            {"name": "input_a", "ref_id": "batch.input.alpha", "ref_type": "batch"},
            {"name": "input_b", "ref_id": "batch.input.beta", "ref_type": "batch"},
        ],
        run_id=str(run_id),
    )
    if str(started.get("result", "")).strip() != "complete":
        return {"start": dict(started), "tick": {}, "end": {}, "state": {}}

    ticked = process_run_tick(
        current_tick=101,
        run_state=started.get("run_state"),
        process_definition_row=process_definition,
        budget_units=16,
        completed_action_step_ids=["step.action"],
        transform_step_results={
            "step.transform": {
                "output_refs": [{"name": "output", "ref_id": "batch.output.alpha", "ref_type": "batch"}],
                "energy_transform_refs": ["ledger.energy.proc2.test"],
                "emission_refs": ["emission.proc2.test"],
                "entropy_increment": 2,
            }
        },
    )
    if str(ticked.get("result", "")).strip() != "complete":
        return {"start": dict(started), "tick": dict(ticked), "end": {}, "state": {}}

    q_inputs = dict(
        {
            "temperature": 660,
            "pressure_head": 200,
            "entropy_index": 120,
            "tool_wear_permille": 140,
            "input_batch_quality_permille": 910,
            "spec_score_permille": 950,
            "calibration_state_permille": 980,
        },
        **dict(quality_inputs or {}),
    )
    end = process_run_end(
        current_tick=102,
        run_record_row=started.get("run_record_row"),
        run_state=ticked.get("run_state"),
        status="completed",
        quality_inputs=q_inputs,
        tool_ids=["tool.proc2.rig.alpha"],
        environment_snapshot_hash=canonical_sha256({"fixture": "proc2", "run_id": str(run_id)}),
        stochastic_quality_enabled=bool(stochastic_quality_enabled),
        yield_model_registry_payload=yield_registry,
        defect_model_registry_payload=defect_registry,
        constitutive_model_registry_payload=model_registry,
        model_type_registry_payload=model_type_registry,
        model_cache_policy_registry_payload=cache_policy_registry,
    )
    return {
        "start": dict(started),
        "tick": dict(ticked),
        "end": dict(end),
        "state": dict(end.get("run_state") or {}),
        "run_record": dict(end.get("run_record_row") or {}),
    }
