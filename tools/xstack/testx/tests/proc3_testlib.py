"""Shared PROC-3 QC sampling TestX fixtures."""

from __future__ import annotations

import json
import os
import sys
from typing import Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    try:
        payload = json.load(open(abs_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _process_definition(
    *,
    qc_policy_id: str,
    yield_model_id: str,
    defect_model_id: str,
    drift_policy_id: str,
) -> dict:
    return {
        "process_id": "proc.test.proc3.qc",
        "version": "1.0.0",
        "description": "PROC-3 QC fixture definition",
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
                    "domain_process_id": "process.test.proc3.transform",
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
        "required_tools": ["tool.proc3.qc.rig.alpha"],
        "required_environment": ["env.proc3.standard"],
        "tier_contract_id": "tier.proc.default",
        "coupling_budget_id": None,
        "qc_policy_id": str(qc_policy_id),
        "drift_policy_id": str(drift_policy_id),
        "yield_model_id": str(yield_model_id),
        "defect_model_id": str(defect_model_id),
    }


def run_proc3_qc_case(
    *,
    repo_root: str,
    run_id: str,
    qc_policy_id: str = "qc.basic_sampling",
    output_batch_ids: Sequence[str] | None = None,
    yield_model_id: str = "yield.default_deterministic",
    defect_model_id: str = "defect.default_deterministic",
    drift_policy_id: str = "drift.default",
    quality_inputs: Mapping[str, object] | None = None,
    stochastic_quality_enabled: bool = False,
    qc_policy_registry_payload: Mapping[str, object] | None = None,
    sampling_strategy_registry_payload: Mapping[str, object] | None = None,
    test_procedure_registry_payload: Mapping[str, object] | None = None,
    tolerance_policy_registry_payload: Mapping[str, object] | None = None,
    drift_policy_registry_payload: Mapping[str, object] | None = None,
    drift_update_stride: int = 1,
    force_drift_update: bool = True,
    reliability_failure_count: int = 0,
    run_state_overrides: Mapping[str, object] | None = None,
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
    qc_registry = (
        dict(qc_policy_registry_payload)
        if isinstance(qc_policy_registry_payload, Mapping)
        else _load_json(repo_root, "data/registries/qc_policy_registry.json")
    )
    sampling_registry = (
        dict(sampling_strategy_registry_payload)
        if isinstance(sampling_strategy_registry_payload, Mapping)
        else _load_json(repo_root, "data/registries/sampling_strategy_registry.json")
    )
    test_registry = (
        dict(test_procedure_registry_payload)
        if isinstance(test_procedure_registry_payload, Mapping)
        else _load_json(repo_root, "data/registries/test_procedure_registry.json")
    )
    tolerance_registry = (
        dict(tolerance_policy_registry_payload)
        if isinstance(tolerance_policy_registry_payload, Mapping)
        else _load_json(repo_root, "data/registries/tolerance_policy_registry.json")
    )
    drift_registry = (
        dict(drift_policy_registry_payload)
        if isinstance(drift_policy_registry_payload, Mapping)
        else _load_json(repo_root, "data/registries/process_drift_policy_registry.json")
    )

    process_definition = _process_definition(
        qc_policy_id=str(qc_policy_id),
        yield_model_id=str(yield_model_id),
        defect_model_id=str(defect_model_id),
        drift_policy_id=str(drift_policy_id),
    )
    started = process_run_start(
        current_tick=200,
        process_definition_row=process_definition,
        action_template_registry_payload=action_registry,
        temporal_domain_registry_payload=temporal_registry,
        input_refs=[
            {"name": "input_a", "ref_id": "batch.input.alpha", "ref_type": "batch"},
            {"name": "input_b", "ref_id": "batch.input.beta", "ref_type": "batch"},
        ],
        run_id=str(run_id),
        qc_policy_registry_payload=qc_registry,
        drift_policy_registry_payload=drift_registry,
    )
    if str(started.get("result", "")).strip() != "complete":
        return {"start": dict(started), "tick": {}, "end": {}, "state": {}}

    batch_ids = [str(item).strip() for item in list(output_batch_ids or []) if str(item).strip()]
    if not batch_ids:
        batch_ids = ["batch.output.alpha", "batch.output.beta", "batch.output.gamma"]
    output_refs = [
        {"name": "output_{}".format(index), "ref_id": batch_id, "ref_type": "batch"}
        for index, batch_id in enumerate(batch_ids, start=1)
    ]

    ticked = process_run_tick(
        current_tick=201,
        run_state=started.get("run_state"),
        process_definition_row=process_definition,
        budget_units=24,
        completed_action_step_ids=["step.action"],
        transform_step_results={
            "step.transform": {
                "output_refs": list(output_refs),
                "energy_transform_refs": ["ledger.energy.proc3.test"],
                "emission_refs": ["emission.proc3.test"],
                "entropy_increment": 2,
            }
        },
    )
    if str(ticked.get("result", "")).strip() != "complete":
        return {"start": dict(started), "tick": dict(ticked), "end": {}, "state": {}}
    if isinstance(run_state_overrides, Mapping):
        patched_state = dict(ticked.get("run_state") or {})
        for key, value in sorted(dict(run_state_overrides).items(), key=lambda item: str(item[0])):
            patched_state[str(key)] = value
        ticked["run_state"] = patched_state

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
        current_tick=202,
        run_record_row=started.get("run_record_row"),
        run_state=ticked.get("run_state"),
        status="completed",
        quality_inputs=q_inputs,
        tool_ids=["tool.proc3.qc.rig.alpha"],
        environment_snapshot_hash=canonical_sha256({"fixture": "proc3", "run_id": str(run_id)}),
        stochastic_quality_enabled=bool(stochastic_quality_enabled),
        yield_model_registry_payload=yield_registry,
        defect_model_registry_payload=defect_registry,
        constitutive_model_registry_payload=model_registry,
        model_type_registry_payload=model_type_registry,
        model_cache_policy_registry_payload=cache_policy_registry,
        qc_policy_registry_payload=qc_registry,
        sampling_strategy_registry_payload=sampling_registry,
        test_procedure_registry_payload=test_registry,
        tolerance_policy_registry_payload=tolerance_registry,
        instrument_id="instrument.proc3.qc.basic",
        calibration_cert_id="cert.instrument.proc3.qc.basic",
        requester_subject_id="subject.proc3.inspector",
        drift_policy_registry_payload=drift_registry,
        drift_update_stride=int(max(1, int(drift_update_stride))),
        force_drift_update=bool(force_drift_update),
        reliability_failure_count=int(max(0, int(reliability_failure_count))),
    )
    return {
        "start": dict(started),
        "tick": dict(ticked),
        "end": dict(end),
        "state": dict(end.get("run_state") or {}),
        "run_record": dict(end.get("run_record_row") or {}),
        "batch_ids": list(batch_ids),
    }
