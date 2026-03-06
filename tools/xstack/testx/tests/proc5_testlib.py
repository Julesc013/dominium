"""Shared PROC-5 process capsule TestX fixtures."""

from __future__ import annotations

import copy
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


def _process_definition(process_id: str, version: str) -> dict:
    return {
        "process_id": str(process_id),
        "version": str(version),
        "description": "PROC-5 capsule fixture definition",
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
                    "domain_process_id": "process.test.proc5.transform",
                    "inputs": [],
                    "outputs": [{"ref_id": "batch.output.capsule", "ref_type": "batch"}],
                    "cost_units": 1,
                },
            ],
            "edges": [{"from_step_id": "step.action", "to_step_id": "step.transform"}],
        },
        "input_signature": [
            {"name": "input_1", "ref_id": "batch.input.proc5.a", "ref_type": "batch"},
            {"name": "input_2", "ref_id": "batch.input.proc5.b", "ref_type": "batch"},
        ],
        "output_signature": [
            {"name": "output_1", "ref_id": "batch.output.proc5.a", "ref_type": "batch"}
        ],
        "required_tools": ["tool.proc5.rig.alpha"],
        "required_environment": ["env.proc5.standard"],
        "tier_contract_id": "tier.proc.default",
        "coupling_budget_id": "budget.coupling.process.default",
    }


def run_proc5_capsule_case(
    *,
    repo_root: str,
    process_id: str = "proc.test.proc5",
    version: str = "1.0.0",
    maturity_state: str = "capsule_eligible",
    compile_with_compiled_model: bool = False,
    out_of_domain: bool = False,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.capsules import execute_process_capsule, generate_process_capsule
    from src.process.maturity import build_process_maturity_record_row, build_process_metrics_state_row
    from src.system.statevec import build_state_vector_definition_row
    from tools.process.tool_replay_capsule_window import verify_capsule_replay_window

    tolerance_registry = _load_json(repo_root, "data/registries/tolerance_policy_registry.json")
    compiled_type_registry = _load_json(repo_root, "data/registries/compiled_type_registry.json")
    verification_procedure_registry = _load_json(
        repo_root, "data/registries/verification_procedure_registry.json"
    )
    compile_policy_registry = _load_json(repo_root, "data/registries/compile_policy_registry.json")
    qc_policy_registry = _load_json(repo_root, "data/registries/qc_policy_registry.json")
    sampling_strategy_registry = _load_json(
        repo_root, "data/registries/sampling_strategy_registry.json"
    )
    test_procedure_registry = _load_json(repo_root, "data/registries/test_procedure_registry.json")

    maturity_row = build_process_maturity_record_row(
        record_id="maturity.proc5.fixture",
        process_id=str(process_id),
        version=str(version),
        maturity_state=str(maturity_state),
        stabilization_score=980,
        tick=500,
        deterministic_fingerprint="",
        extensions={"source": "proc5_testlib"},
    )
    metrics_row = build_process_metrics_state_row(
        process_id=str(process_id),
        version=str(version),
        runs_count=64,
        yield_mean=930,
        yield_variance=1500,
        defect_rate=40,
        qc_pass_rate=980,
        env_deviation_score=80,
        calibration_deviation_score=50,
        last_update_tick=500,
        deterministic_fingerprint="",
        extensions={
            "source": "proc5_testlib",
            "observed_input_ranges": {
                "input.total_mass_raw": {"min": 0, "max": 50000},
                "input.batch_quality_permille": {"min": 700, "max": 980},
                "environment.entropy_index": {"min": 0, "max": 1200},
                "tool.wear_permille": {"min": 0, "max": 900},
            },
        },
    )
    owner_id = "process.{}@{}".format(str(process_id), str(version))
    statevec_row = build_state_vector_definition_row(
        owner_id=owner_id,
        version="1.0.0",
        state_fields=[
            {"field_id": "run_id", "path": "run_id", "field_kind": "id", "default": ""},
            {"field_id": "progress", "path": "progress", "field_kind": "fixed_point", "default": 0},
            {"field_id": "status", "path": "status", "field_kind": "text", "default": "idle"},
        ],
        deterministic_fingerprint="",
        extensions={"source": "proc5_testlib"},
    )

    process_definition_row = _process_definition(process_id=str(process_id), version=str(version))
    generation = generate_process_capsule(
        current_tick=600,
        process_id=str(process_id),
        version=str(version),
        process_maturity_record_rows=[maturity_row],
        process_metrics_state_rows=[metrics_row],
        state_vector_definition_rows=[statevec_row],
        tolerance_policy_registry_payload=tolerance_registry,
        process_definition_row=process_definition_row,
        error_bound_policy_id="tol.default",
        coupling_budget_id="budget.coupling.process.default",
        compile_with_compiled_model=bool(compile_with_compiled_model),
        compiled_type_registry_payload=compiled_type_registry,
        verification_procedure_registry_payload=verification_procedure_registry,
        compile_policy_registry_payload=compile_policy_registry,
        compile_policy_id="compile.default",
        extensions={"source": "proc5_testlib"},
    )
    if str(generation.get("result", "")).strip() != "complete":
        return {"generation": dict(generation), "execution": {}, "state": {}}

    input_batch_rows = [
        {
            "batch_id": "batch.input.proc5.a",
            "quantity_mass_raw": 10000,
            "quality_distribution": {"yield_factor_permille": 920},
        },
        {
            "batch_id": "batch.input.proc5.b",
            "quantity_mass_raw": 12000,
            "quality_distribution": {"yield_factor_permille": 930},
        },
    ]
    execution = execute_process_capsule(
        current_tick=601,
        capsule_id=str((dict(generation.get("process_capsule_row") or {})).get("capsule_id", "")),
        process_capsule_rows=[generation.get("process_capsule_row")],
        validity_domain_rows=[generation.get("validity_domain_row")],
        input_batch_rows=input_batch_rows,
        output_batch_ids=["batch.output.proc5.a", "batch.output.proc5.b"],
        process_quality_record_rows=[],
        qc_policy_registry_payload=qc_policy_registry,
        sampling_strategy_registry_payload=sampling_strategy_registry,
        test_procedure_registry_payload=test_procedure_registry,
        tolerance_policy_registry_payload=tolerance_registry,
        compiled_model_rows=(
            [generation.get("compiled_model_row")]
            if isinstance(generation.get("compiled_model_row"), Mapping)
            and generation.get("compiled_model_row")
            else []
        ),
        state_vector_definition_rows=[
            statevec_row,
            dict(generation.get("state_vector_definition_row") or {}),
            dict(generation.get("compiled_state_vector_definition_row") or {}),
        ],
        state_vector_snapshot_rows=[
            dict(generation.get("compiled_state_vector_snapshot_row") or {}),
        ],
        environment_entropy_index=100,
        tool_wear_permille=(950 if out_of_domain else 200),
        allow_forced_expand=True,
        allow_micro_fallback=True,
        requester_subject_id="subject.proc5.operator",
        instrument_id="instrument.proc5.qc",
        calibration_cert_id="cert.proc5.qc",
    )

    state = {
        "process_capsule_rows": [dict(generation.get("process_capsule_row") or {})],
        "capsule_generated_record_rows": [
            dict(generation.get("capsule_generated_record_row") or {})
        ],
        "capsule_execution_record_rows": (
            [dict(execution.get("capsule_execution_record_row") or {})]
            if str(execution.get("result", "")).strip() == "complete"
            else []
        ),
        "compiled_model_rows": (
            [dict(generation.get("compiled_model_row") or {})]
            if isinstance(generation.get("compiled_model_row"), Mapping)
            and generation.get("compiled_model_row")
            else []
        ),
    }
    replay_seed = verify_capsule_replay_window(state_payload=state)
    state["capsule_generation_hash_chain"] = str(
        (dict(replay_seed.get("observed") or {}).get("capsule_generation_hash_chain", ""))
    ).strip()
    state["capsule_execution_hash_chain"] = str(
        (dict(replay_seed.get("observed") or {}).get("capsule_execution_hash_chain", ""))
    ).strip()
    state["compiled_model_hash_chain"] = str(
        (dict(replay_seed.get("observed") or {}).get("compiled_model_hash_chain", ""))
    ).strip()

    return {
        "generation": dict(generation),
        "execution": dict(execution),
        "state": copy.deepcopy(state),
    }
