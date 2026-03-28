"""Shared PROC-7 research/reverse-engineering TestX fixtures."""

from __future__ import annotations

import copy
import sys
from typing import Mapping, Sequence

from tools.xstack.compatx.canonical_json import canonical_sha256


def _default_process_definition(*, process_id: str, version: str) -> dict:
    return {
        "process_id": str(process_id).strip(),
        "version": str(version).strip() or "1.0.0",
        "description": "PROC-7 deterministic research fixture process",
        "step_graph": {
            "steps": [
                {
                    "step_id": "step.transform",
                    "step_kind": "transform",
                    "domain_process_id": "process.test.proc7.transform",
                    "inputs": [],
                    "outputs": [{"ref_id": "batch.output.proc7", "ref_type": "batch"}],
                    "cost_units": 1,
                }
            ],
            "edges": [],
        },
        "input_signature": [],
        "output_signature": [],
        "required_tools": [],
        "required_environment": [],
        "tier_contract_id": "tier.proc.default",
        "coupling_budget_id": "budget.coupling.process.default",
        "qc_policy_id": "qc.none",
        "stabilization_policy_id": "stab.default",
        "process_lifecycle_policy_id": "proc.lifecycle.default",
        "process_cert_type_id": "cert.process.basic",
        "drift_policy_id": "drift.default",
        "yield_model_id": "yield.default_deterministic",
        "defect_model_id": "defect.default_deterministic",
        "deterministic_fingerprint": "",
        "extensions": {"source": "test.proc7"},
    }


def base_state(
    repo_root: str,
    *,
    process_id: str = "proc.test.proc7",
    version: str = "1.0.0",
    experiment_id: str = "experiment.proc7.default",
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.research import build_experiment_definition_row

    process_definition = _default_process_definition(process_id=process_id, version=version)
    experiment_definition = build_experiment_definition_row(
        experiment_id=str(experiment_id).strip(),
        process_definition_ref="{}@{}".format(
            str(process_definition.get("process_id", "")).strip(),
            str(process_definition.get("version", "")).strip() or "1.0.0",
        ),
        hypothesis_text_ref="doc.hypothesis.proc7.default",
        variable_defs=[
            {"variable_id": "temperature", "range": {"min": 400, "max": 900}},
            {"variable_id": "pressure_head", "range": {"min": 50, "max": 300}},
        ],
        measurement_plan_ref="plan.measure.proc7.default",
        extensions={"source": "test.proc7"},
    )
    return {
        "tick": 0,
        "process_definition_rows": [dict(process_definition)],
        "experiment_definition_rows": [dict(experiment_definition)],
        "experiment_run_binding_rows": [],
        "experiment_result_rows": [],
        "candidate_process_definition_rows": [],
        "candidate_model_binding_rows": [],
        "candidate_promotion_record_rows": [],
        "reverse_engineering_record_rows": [],
        "pollution_measurement_rows": [],
        "qc_result_record_rows": [],
        "process_metrics_state_rows": [],
        "state_vector_definition_rows": [],
        "compiled_model_rows": [],
        "equivalence_proof_rows": [],
        "validity_domain_rows": [],
        "knowledge_receipt_rows": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "destroyed_item_ids": [],
        "control_decision_log": [],
    }


def law_profile() -> dict:
    return {
        "law_profile_id": "law.proc7.test",
        "allowed_processes": [
            "process.experiment_run_start",
            "process.experiment_run_complete",
            "process.candidate_promote_to_defined",
            "process.reverse_engineering_action",
        ],
        "forbidden_processes": [],
        "process_entitlement_requirements": {
            "process.experiment_run_start": "entitlement.tool.use",
            "process.experiment_run_complete": "entitlement.tool.use",
            "process.candidate_promote_to_defined": "entitlement.control.admin",
            "process.reverse_engineering_action": "entitlement.tool.use",
        },
        "process_privilege_requirements": {
            "process.experiment_run_start": "operator",
            "process.experiment_run_complete": "operator",
            "process.candidate_promote_to_defined": "operator",
            "process.reverse_engineering_action": "operator",
        },
    }


def authority_context() -> dict:
    return {
        "authority_origin": "tool",
        "law_profile_id": "law.proc7.test",
        "entitlements": ["entitlement.tool.use", "entitlement.control.admin"],
        "privilege_level": "operator",
    }


def execute_process(
    *,
    repo_root: str,
    state: dict,
    process_id: str,
    inputs: Mapping[str, object] | None = None,
    policy_context: Mapping[str, object] | None = None,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.sessionx.process_runtime import execute_intent

    input_payload = dict(inputs or {})
    return execute_intent(
        state=state,
        intent={
            "intent_id": "intent.proc7.{}.{}".format(
                str(process_id).replace(".", "_"),
                canonical_sha256(input_payload)[:12],
            ),
            "process_id": str(process_id),
            "inputs": input_payload,
        },
        law_profile=law_profile(),
        authority_context=authority_context(),
        navigation_indices={},
        policy_context=dict(policy_context or {}),
    )


def run_experiment_cycle(
    *,
    repo_root: str,
    state: dict,
    experiment_id: str = "experiment.proc7.default",
    run_id: str = "run.proc7.default",
    measurement_rows: Sequence[Mapping[str, object]] | None = None,
    research_policy_id: str = "research.default",
    model_id_hint: str | None = None,
) -> dict:
    start = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.experiment_run_start",
        inputs={
            "experiment_id": str(experiment_id).strip(),
            "run_id": str(run_id).strip(),
        },
    )
    default_measurements = [
        {
            "measurement_id": "measurement.proc7.b",
            "pollutant_id": "pollutant.pm25",
            "measured_concentration": 18,
            "calibration_cert_id": "cert.measurement.proc7",
        },
        {
            "measurement_id": "measurement.proc7.a",
            "pollutant_id": "pollutant.co2",
            "measured_concentration": 42,
        },
    ]
    complete_inputs = {
        "experiment_id": str(experiment_id).strip(),
        "run_id": str(run_id).strip(),
        "measurement_rows": [
            dict(row)
            for row in list(measurement_rows or default_measurements)
            if isinstance(row, Mapping)
        ],
        "publish_report_via_sig": False,
        "research_policy_id": str(research_policy_id).strip() or "research.default",
    }
    if model_id_hint is not None:
        complete_inputs["model_id_hint"] = str(model_id_hint).strip()
    complete = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.experiment_run_complete",
        inputs=complete_inputs,
    )
    return {"start": dict(start), "complete": dict(complete), "state": state}


def run_reverse_action(
    *,
    repo_root: str,
    state: dict,
    target_item_id: str = "item.proc7.sample",
    method: str = "disassemble",
    research_policy_id: str = "research.default",
    destroyed: bool | None = None,
    model_id_hint: str | None = None,
    proposed_process_definition_ref: str | None = None,
) -> dict:
    inputs = {
        "target_item_id": str(target_item_id).strip(),
        "method": str(method).strip(),
        "subject_id": "subject.proc7.researcher",
        "research_policy_id": str(research_policy_id).strip() or "research.default",
    }
    if destroyed is not None:
        inputs["destroyed"] = bool(destroyed)
    if model_id_hint is not None:
        inputs["model_id_hint"] = str(model_id_hint).strip()
    if proposed_process_definition_ref is not None:
        inputs["proposed_process_definition_ref"] = str(
            proposed_process_definition_ref
        ).strip()
    return execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.reverse_engineering_action",
        inputs=inputs,
    )


def seed_candidate_for_promotion(
    *,
    repo_root: str,
    state: dict,
    candidate_id: str,
    process_id: str,
    version: str = "1.0.0",
    replications: int = 1,
) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from process.research import build_candidate_process_definition_row

    process_token = str(process_id).strip()
    version_token = str(version).strip() or "1.0.0"
    candidate_row = build_candidate_process_definition_row(
        candidate_id=str(candidate_id).strip(),
        inferred_from_artifact_ids=[
            "result.experiment.proc7.seed",
            "record.reverse_engineering.proc7.seed",
        ],
        proposed_process_definition_ref="{}@{}".format(process_token, version_token),
        confidence_score=900,
        deterministic_fingerprint="",
        extensions={"source": "test.proc7"},
    )
    state["candidate_process_definition_rows"] = [dict(candidate_row)]
    state["experiment_run_binding_rows"] = [
        {
            "schema_version": "1.0.0",
            "experiment_id": "experiment.proc7.seed",
            "run_id": "run.proc7.seed.{:03d}".format(index + 1),
            "process_id": process_token,
            "version": version_token,
            "start_tick": index,
            "end_tick": index + 1,
            "status": "completed",
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        for index in range(int(max(0, int(replications))))
    ]
    state["process_metrics_state_rows"] = [
        {
            "schema_version": "1.0.0",
            "process_id": process_token,
            "version": version_token,
            "runs_count": int(max(0, int(replications))),
            "yield_mean": 900,
            "yield_variance": 10,
            "defect_rate": 0,
            "qc_pass_rate": 1000,
            "env_deviation_score": 0,
            "calibration_deviation_score": 0,
            "last_update_tick": int(max(0, int(replications))),
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]


def disallow_destructive_policy_context() -> dict:
    return {
        "research_policy_registry": {
            "schema_id": "dominium.registry.research_policy_registry",
            "schema_version": "1.0.0",
            "record": {
                "registry_id": "dominium.registry.research_policy_registry",
                "registry_version": "1.0.0",
                "research_policies": [
                    {
                        "schema_version": "1.0.0",
                        "research_policy_id": "research.default",
                        "max_experiments_per_tick": 64,
                        "max_inference_jobs_per_tick": 128,
                        "promotion_replication_threshold": 3,
                        "allow_destructive_reverse_engineering": True,
                        "allow_named_rng": False,
                        "allow_candidate_compiled_model_before_validation": False,
                        "require_state_vector_for_candidate_capsule": True,
                        "deterministic_fingerprint": "",
                        "extensions": {"source": "test.proc7"},
                    },
                    {
                        "schema_version": "1.0.0",
                        "research_policy_id": "research.no_destroy",
                        "max_experiments_per_tick": 64,
                        "max_inference_jobs_per_tick": 128,
                        "promotion_replication_threshold": 3,
                        "allow_destructive_reverse_engineering": False,
                        "allow_named_rng": False,
                        "allow_candidate_compiled_model_before_validation": False,
                        "require_state_vector_for_candidate_capsule": True,
                        "deterministic_fingerprint": "",
                        "extensions": {"source": "test.proc7"},
                    },
                ],
                "extensions": {},
            },
        }
    }


def cloned_state(
    repo_root: str,
    *,
    process_id: str = "proc.test.proc7",
    version: str = "1.0.0",
    experiment_id: str = "experiment.proc7.default",
) -> dict:
    return copy.deepcopy(
        base_state(
            repo_root=repo_root,
            process_id=process_id,
            version=version,
            experiment_id=experiment_id,
        )
    )

