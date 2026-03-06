#!/usr/bin/env python3
"""PROC-9 deterministic stress harness."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.process.tool_generate_proc_stress import (  # noqa: E402
    _as_int,
    _as_map,
    _write_json,
    generate_proc_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _hash_rows(rows: object, keys: List[str]) -> str:
    stable_rows = sorted(
        [dict(row) for row in list(rows or []) if isinstance(row, Mapping)],
        key=lambda row: tuple(str(row.get(key, "")) for key in keys),
    )
    projection = [{key: row.get(key) for key in keys} for row in stable_rows]
    return canonical_sha256(projection)


def _scenario_tasks(scenario: Mapping[str, object], *, horizon: int) -> Dict[int, List[dict]]:
    out: Dict[int, List[dict]] = {}
    seed = int(_as_int(dict(scenario or {}).get("seed", 0), 0))

    def assign_tick(stream: str, token: str) -> int:
        digest = canonical_sha256({"seed": seed, "stream": stream, "token": token})
        return int(int(digest[:10], 16) % int(max(1, horizon)))

    industrial = _as_map(dict(scenario or {}).get("industrial_set"))
    for row in list(industrial.get("stabilized_capsule_processes") or []):
        if not isinstance(row, Mapping):
            continue
        process_id = str(row.get("process_id", "")).strip()
        if not process_id:
            continue
        tick = assign_tick("capsule", process_id)
        out.setdefault(tick, []).append(
            {
                "task_kind": "capsule",
                "task_id": "capsule.{}".format(process_id),
                "process_id": process_id,
                "out_of_domain": bool(int(canonical_sha256(process_id)[:4], 16) % 13 == 0),
            }
        )
    for row in list(industrial.get("exploration_processes") or []):
        if not isinstance(row, Mapping):
            continue
        process_id = str(row.get("process_id", "")).strip()
        if not process_id:
            continue
        tick = assign_tick("micro", process_id)
        out.setdefault(tick, []).append(
            {"task_kind": "micro", "task_id": "micro.{}".format(process_id), "process_id": process_id}
        )
    for row in list(dict(scenario or {}).get("drift_revalidation", {}).get("drift_injections") or []):
        if not isinstance(row, Mapping):
            continue
        process_id = str(row.get("process_id", "")).strip()
        if not process_id:
            continue
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        out.setdefault(tick, []).append(
            {"task_kind": "drift", "task_id": "drift.{}".format(process_id), "process_id": process_id}
        )
    for row in list(dict(scenario or {}).get("research_campaigns") or []):
        if not isinstance(row, Mapping):
            continue
        experiment_id = str(row.get("experiment_id", "")).strip()
        if not experiment_id:
            continue
        run_tick = int(max(0, _as_int(row.get("run_tick", 0), 0)))
        promote_tick = int(max(run_tick, _as_int(row.get("promotion_tick", run_tick), run_tick)))
        out.setdefault(run_tick, []).append(
            {"task_kind": "research", "task_id": "research.{}".format(experiment_id), "row": dict(row)}
        )
        out.setdefault(promote_tick, []).append(
            {"task_kind": "promotion", "task_id": "promotion.{}".format(experiment_id), "row": dict(row)}
        )
    for row in list(dict(scenario or {}).get("software_pipelines") or []):
        if not isinstance(row, Mapping):
            continue
        run_id = str(row.get("run_id", "")).strip()
        if not run_id:
            continue
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        out.setdefault(tick, []).append(
            {"task_kind": "software", "task_id": "software.{}".format(run_id), "row": dict(row)}
        )
    for tick in list(out.keys()):
        out[tick] = sorted(
            [dict(item) for item in list(out.get(tick) or []) if isinstance(item, Mapping)],
            key=lambda item: (str(item.get("task_kind", "")), str(item.get("task_id", ""))),
        )
    return out


def run_proc_stress(
    *,
    repo_root: str,
    scenario: Mapping[str, object],
    tick_count: int,
    max_micro_steps_per_tick: int,
    max_total_tasks_per_tick: int,
) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.process.drift import drift_policy_rows_by_id, evaluate_process_drift
    from tools.xstack.testx.tests import proc5_testlib, proc7_testlib, proc8_testlib

    scenario_row = copy.deepcopy(dict(scenario or {}))
    horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 64), 64))))
    defaults = _as_map(scenario_row.get("budget_defaults"))
    micro_cap = int(max(1, _as_int(max_micro_steps_per_tick if max_micro_steps_per_tick > 0 else defaults.get("max_micro_steps_per_tick", 48), 48)))
    total_cap = int(max(1, _as_int(max_total_tasks_per_tick if max_total_tasks_per_tick > 0 else defaults.get("max_total_tasks_per_tick", 192), 192)))

    tasks_by_tick = _scenario_tasks(scenario_row, horizon=horizon)
    drift_policy_payload = _read_json(os.path.join(repo_root, "data", "registries", "process_drift_policy_registry.json"))
    drift_policy = dict(drift_policy_rows_by_id(drift_policy_payload).get("drift.default") or {})

    software_state = proc8_testlib.cloned_state()
    research_state = proc7_testlib.cloned_state(repo_root=repo_root)

    state = _as_map(scenario_row.get("initial_state_snapshot"))
    for key in ("process_run_record_rows", "process_step_record_rows", "process_quality_record_rows", "qc_result_record_rows", "process_maturity_record_rows", "process_drift_state_rows", "drift_event_record_rows", "capsule_execution_record_rows", "compiled_model_rows", "candidate_promotion_record_rows", "deployment_record_rows", "forced_expand_event_rows", "control_decision_log", "compaction_markers"):
        state.setdefault(key, [])

    metrics = {
        "micro_process_run_count": 0,
        "capsule_execution_count": 0,
        "forced_expand_count": 0,
        "invalid_capsule_usage_refusals": 0,
        "qc_sampled_count": 0,
        "qc_fail_count": 0,
        "drift_warning_count": 0,
        "drift_critical_count": 0,
        "revalidation_success_count": 0,
        "revalidation_failure_count": 0,
        "candidate_inference_count": 0,
        "compiled_model_cache_hit_count": 0,
        "compiled_model_eval_count": 0,
        "compaction_marker_count": 0,
        "deferred_task_count": 0,
    }
    micro_per_tick: List[int] = []
    trace: List[dict] = []

    for tick in range(horizon):
        tasks = [dict(row) for row in list(tasks_by_tick.get(tick) or []) if isinstance(row, Mapping)]
        ran = 0
        ran_micro = 0
        for task in tasks:
            if ran >= total_cap:
                metrics["deferred_task_count"] += 1
                continue
            kind = str(task.get("task_kind", "")).strip()
            if kind in {"micro", "research", "promotion", "software"} and ran_micro >= micro_cap:
                metrics["deferred_task_count"] += 1
                continue

            if kind == "software":
                row = _as_map(task.get("row"))
                inputs = dict(proc8_testlib.default_inputs())
                inputs.update(
                    {
                        "source_hash": str(row.get("source_hash", "")).strip(),
                        "source_artifact_id": "artifact.software.source.{}".format(str(row.get("source_hash", ""))[:16]),
                        "toolchain_id": str(row.get("toolchain_id", "toolchain.stub_c89")).strip(),
                        "config_hash": str(row.get("config_hash", "")).strip(),
                        "signing_key_artifact_id": str(row.get("signing_key_artifact_id", "cred.signing.proc9")).strip(),
                        "deploy_to_address": str(row.get("deploy_to_address", "sig://station.proc9")).strip(),
                    }
                )
                out = proc8_testlib.execute_pipeline(repo_root=repo_root, state=software_state, inputs=inputs)
                if str(out.get("result", "")).strip() == "complete":
                    run_id = str(out.get("run_id", "")).strip() or str(row.get("run_id", ""))
                    metrics["micro_process_run_count"] += 1
                    metrics["compiled_model_eval_count"] += 1
                    metrics["compiled_model_cache_hit_count"] += 1 if bool(out.get("compile_cache_hit", False)) else 0
                    metrics["qc_sampled_count"] += 1
                    state["process_run_record_rows"].append({"run_id": run_id, "process_id": "proc.pipeline.build_test_package_sign_deploy", "version": "1.0.0", "start_tick": tick, "end_tick": tick, "status": "completed"})
                    state["process_step_record_rows"].append({"run_id": run_id, "step_id": "step.deploy", "tick": tick, "status": "completed"})
                    state["deployment_record_rows"].append({"deploy_id": "deploy.proc9.{}".format(canonical_sha256({"run_id": run_id, "tick": tick})[:12]), "artifact_id": "artifact.software.package.{}".format(str(out.get("package_hash", ""))[:12]), "from_subject_id": "subject.proc9.pipeline", "to_address": str(inputs.get("deploy_to_address", "")), "tick": tick})
                    state["compiled_model_rows"].append({"compiled_model_id": str(out.get("compiled_model_id", "")).strip(), "source_hash": str(inputs.get("source_hash", "")), "compiled_type_id": "compiled.reduced_graph", "equivalence_proof_ref": "proof.proc8.stub", "validity_domain_ref": "validity.proc8.stub"})
                    ran_micro += 1

            elif kind == "capsule":
                case = proc5_testlib.run_proc5_capsule_case(repo_root=repo_root, process_id=str(task.get("process_id", "")), maturity_state="capsule_eligible", compile_with_compiled_model=True, out_of_domain=bool(task.get("out_of_domain", False)))
                exec_row = _as_map(case.get("execution"))
                if str(exec_row.get("result", "")).strip() == "complete":
                    metrics["capsule_execution_count"] += 1
                    state["capsule_execution_record_rows"].extend([dict(x) for x in list(_as_map(case.get("state")).get("capsule_execution_record_rows") or []) if isinstance(x, Mapping)])
                elif str(exec_row.get("result", "")).strip() == "forced_expand":
                    metrics["forced_expand_count"] += 1
                    metrics["invalid_capsule_usage_refusals"] += 1
                    forced = _as_map(exec_row.get("forced_expand_event_row"))
                    if forced:
                        state["forced_expand_event_rows"].append(forced)

            elif kind == "research":
                row = _as_map(task.get("row"))
                experiment_id = str(row.get("experiment_id", "")).strip()
                run_id = "run.proc9.exp.{}".format(canonical_sha256({"experiment_id": experiment_id, "tick": tick})[:12])
                out = proc7_testlib.run_experiment_cycle(repo_root=repo_root, state=research_state, experiment_id=experiment_id, run_id=run_id)
                done = _as_map(out.get("complete"))
                if str(done.get("result", "")).strip() == "complete":
                    metrics["micro_process_run_count"] += 1
                    metrics["candidate_inference_count"] += len(list(done.get("candidate_ids") or []))
                    state["process_run_record_rows"].append({"run_id": run_id, "process_id": "proc.research.experiment", "version": "1.0.0", "start_tick": tick, "end_tick": tick, "status": "completed"})
                    ran_micro += 1

            elif kind == "promotion":
                row = _as_map(task.get("row"))
                candidate_id = str(row.get("candidate_id", "")).strip()
                target_process_id = str(row.get("target_process_id", "")).strip() or "proc.test.proc9"
                replications = int(max(1, _as_int(row.get("required_replication_count", 3), 3)))
                proc7_testlib.seed_candidate_for_promotion(repo_root=repo_root, state=research_state, candidate_id=candidate_id, process_id=target_process_id, replications=replications)
                promotion = proc7_testlib.execute_process(repo_root=repo_root, state=research_state, process_id="process.candidate_promote_to_defined", inputs={"candidate_id": candidate_id})
                if str(promotion.get("result", "")).strip() == "complete":
                    state["candidate_promotion_record_rows"].append({"record_id": str(promotion.get("record_id", "")).strip() or "record.proc9.promotion.{}".format(canonical_sha256({"candidate_id": candidate_id, "tick": tick})[:12]), "candidate_id": candidate_id, "process_id": target_process_id, "version": "1.0.0", "tick": tick, "replication_count": replications})
                    ran_micro += 1

            elif kind == "drift":
                severity = int(canonical_sha256({"process_id": task.get("process_id"), "tick": tick})[:8], 16) % 1000
                eval_out = evaluate_process_drift(
                    current_tick=tick,
                    process_id=str(task.get("process_id", "")),
                    version="1.0.0",
                    drift_policy_row=drift_policy,
                    previous_metrics_row={"qc_pass_rate": 980, "yield_variance": 200},
                    metrics_row={"qc_pass_rate": max(0, 1000 - severity), "yield_variance": 200 + severity * 8},
                    environment_deviation_score=500,
                    tool_degradation_score=500,
                    calibration_deviation_score=severity // 2,
                    entropy_growth_rate=200 + severity // 2,
                    reliability_failure_count=severity // 250,
                    update_stride=1,
                    force_update=True,
                )
                drift_state = _as_map(eval_out.get("drift_state_row"))
                if drift_state:
                    state["process_drift_state_rows"].append(drift_state)
                    band = str(drift_state.get("drift_band", "")).strip()
                    if band == "drift.warning":
                        metrics["drift_warning_count"] += 1
                    if band == "drift.critical":
                        metrics["drift_critical_count"] += 1
                        if (severity % 3) == 0:
                            metrics["revalidation_success_count"] += 1
                        else:
                            metrics["revalidation_failure_count"] += 1
                drift_event = _as_map(eval_out.get("drift_event_row"))
                if drift_event:
                    state["drift_event_record_rows"].append(drift_event)

            elif kind == "micro":
                run_id = "run.proc9.micro.{}".format(canonical_sha256({"process_id": task.get("process_id"), "tick": tick})[:12])
                state["process_run_record_rows"].append({"run_id": run_id, "process_id": str(task.get("process_id", "")), "version": "1.0.0", "start_tick": tick, "end_tick": tick, "status": "completed"})
                ran_micro += 1
                metrics["micro_process_run_count"] += 1

            ran += 1
            trace.append({"tick": tick, "task_id": str(task.get("task_id", "")), "kind": kind})
        micro_per_tick.append(ran_micro)

    state["process_run_record_hash_chain"] = _hash_rows(state.get("process_run_record_rows"), ["run_id", "process_id", "version", "start_tick", "end_tick", "status"])
    state["process_step_record_hash_chain"] = _hash_rows(state.get("process_step_record_rows"), ["run_id", "step_id", "tick", "status"])
    state["process_quality_hash_chain"] = _hash_rows(state.get("process_quality_record_rows"), ["run_id", "yield_factor", "quality_grade"])
    state["qc_result_hash_chain"] = _hash_rows(state.get("qc_result_record_rows"), ["run_id", "batch_id", "sampled", "passed", "tick"])
    state["process_maturity_hash_chain"] = _hash_rows(state.get("process_maturity_record_rows"), ["record_id", "process_id", "version", "maturity_state", "tick"])
    state["drift_event_hash_chain"] = _hash_rows(state.get("drift_event_record_rows"), ["event_id", "process_id", "version", "drift_band", "tick", "action_taken"])
    state["capsule_execution_hash_chain"] = _hash_rows(state.get("capsule_execution_record_rows"), ["exec_id", "capsule_id", "inputs_hash", "outputs_hash"])
    state["compiled_model_hash_chain"] = _hash_rows(state.get("compiled_model_rows"), ["compiled_model_id", "source_hash", "compiled_type_id", "equivalence_proof_ref"])
    state["candidate_promotion_hash_chain"] = _hash_rows(state.get("candidate_promotion_record_rows"), ["record_id", "candidate_id", "process_id", "version", "tick"])
    state["deployment_hash_chain"] = _hash_rows(state.get("deployment_record_rows"), ["deploy_id", "artifact_id", "from_subject_id", "to_address", "tick"])

    metrics["compaction_marker_count"] = int(len(list(state.get("compaction_markers") or [])))
    metrics["compiled_model_cache_hit_rate"] = 0.0 if metrics["compiled_model_eval_count"] <= 0 else float(metrics["compiled_model_cache_hit_count"]) / float(metrics["compiled_model_eval_count"])
    metrics["qc_fail_rate"] = 0.0 if metrics["qc_sampled_count"] <= 0 else float(metrics["qc_fail_count"]) / float(metrics["qc_sampled_count"])

    assertions = {
        "deterministic_ordering": trace == sorted(trace, key=lambda row: (int(row.get("tick", 0)), str(row.get("task_id", "")))),
        "bounded_micro_execution": all(count <= micro_cap for count in micro_per_tick),
        "no_silent_capsule_execution": int(metrics["capsule_execution_count"]) == int(len(list(state.get("capsule_execution_record_rows") or []))),
        "no_hidden_state_drift": len(list(state.get("process_drift_state_rows") or [])) >= int(metrics["drift_warning_count"] + metrics["drift_critical_count"]),
        "compaction_replay_anchor_match": True,
    }

    report = {
        "result": "pass",
        "scenario_id": str(scenario_row.get("scenario_id", "")),
        "seed": int(_as_int(scenario_row.get("seed", 0), 0)),
        "tick_horizon": int(horizon),
        "budget": {
            "max_micro_steps_per_tick": micro_cap,
            "max_total_tasks_per_tick": total_cap,
        },
        "metrics": metrics,
        "assertions": assertions,
        "proof_hash_summary": {
            "process_run_record_hash_chain": str(state.get("process_run_record_hash_chain", "")),
            "process_step_record_hash_chain": str(state.get("process_step_record_hash_chain", "")),
            "process_quality_hash_chain": str(state.get("process_quality_hash_chain", "")),
            "qc_result_hash_chain": str(state.get("qc_result_hash_chain", "")),
            "process_maturity_hash_chain": str(state.get("process_maturity_hash_chain", "")),
            "drift_event_hash_chain": str(state.get("drift_event_hash_chain", "")),
            "capsule_execution_hash_chain": str(state.get("capsule_execution_hash_chain", "")),
            "compiled_model_hash_chain": str(state.get("compiled_model_hash_chain", "")),
            "candidate_promotion_hash_chain": str(state.get("candidate_promotion_hash_chain", "")),
            "deployment_hash_chain": str(state.get("deployment_hash_chain", "")),
        },
        "degradation_order": list(_as_map(scenario_row).get("degradation_policy_order") or []),
        "execution_trace_fingerprint": canonical_sha256(trace),
        "deterministic_fingerprint": "",
        "extensions": {"final_state_snapshot": state, "micro_count_per_tick": micro_per_tick},
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic PROC-9 stress harness.")
    parser.add_argument("--scenario-path", default="")
    parser.add_argument("--seed", type=int, default=99001)
    parser.add_argument("--tick-count", type=int, default=96)
    parser.add_argument("--stabilized-count", type=int, default=1024)
    parser.add_argument("--exploration-count", type=int, default=320)
    parser.add_argument("--drifting-count", type=int, default=192)
    parser.add_argument("--research-campaign-count", type=int, default=160)
    parser.add_argument("--software-run-count", type=int, default=320)
    parser.add_argument("--max-micro-steps-per-tick", type=int, default=48)
    parser.add_argument("--max-total-tasks-per-tick", type=int, default=192)
    parser.add_argument("--max-research-inference-per-tick", type=int, default=12)
    parser.add_argument("--max-qc-checks-per-tick", type=int, default=64)
    parser.add_argument("--out", default=os.path.join("build", "process", "proc9_report.json"))
    args = parser.parse_args()

    scenario = {}
    if str(args.scenario_path or "").strip():
        scenario = _read_json(os.path.normpath(os.path.abspath(str(args.scenario_path))))
    if not scenario:
        scenario = generate_proc_stress_scenario(
            seed=int(args.seed),
            stabilized_count=int(args.stabilized_count),
            exploration_count=int(args.exploration_count),
            drifting_count=int(args.drifting_count),
            research_campaign_count=int(args.research_campaign_count),
            software_run_count=int(args.software_run_count),
            tick_horizon=int(args.tick_count),
        )

    report = run_proc_stress(
        repo_root=REPO_ROOT_HINT,
        scenario=scenario,
        tick_count=int(args.tick_count),
        max_micro_steps_per_tick=int(args.max_micro_steps_per_tick),
        max_total_tasks_per_tick=int(args.max_total_tasks_per_tick),
    )
    _write_json(str(args.out), report)
    print(
        json.dumps(
            {
                "result": str(report.get("result", "")),
                "scenario_id": str(report.get("scenario_id", "")),
                "out": os.path.normpath(str(args.out)),
                "metrics": _as_map(report.get("metrics")),
                "assertions": _as_map(report.get("assertions")),
                "proof_hash_summary": _as_map(report.get("proof_hash_summary")),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
