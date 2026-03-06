#!/usr/bin/env python3
"""PROC-9 deterministic process stress scenario generator."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable, List, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _pick(seed: int, stream: str, index: int, modulo: int, *, offset: int = 0) -> int:
    mod = int(modulo)
    if mod <= 0:
        return int(offset)
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "stream": str(stream),
            "index": int(index),
            "modulo": int(mod),
        }
    )
    return int(int(offset) + (int(digest[:12], 16) % int(mod)))


def _policy_from_permille(value: int) -> str:
    sample = int(max(0, min(999, _as_int(value, 0))))
    if sample < 200:
        return "qc.none"
    if sample < 760:
        return "qc.basic_sampling"
    return "qc.strict_sampling"


def _stable_tokens(values: Iterable[object]) -> List[str]:
    return sorted(
        set(str(item).strip() for item in list(values or []) if str(item).strip())
    )


def _initial_state_snapshot() -> dict:
    return {
        "tick": 0,
        "simulation_time": {
            "tick": 0,
            "tick_rate": 1,
            "deterministic_clock": {"tick_duration_ms": 1000},
        },
        "process_run_record_rows": [],
        "process_step_record_rows": [],
        "process_quality_record_rows": [],
        "qc_result_record_rows": [],
        "process_maturity_record_rows": [],
        "process_drift_state_rows": [],
        "drift_event_record_rows": [],
        "capsule_execution_record_rows": [],
        "process_capsule_rows": [],
        "process_capsule_invalidation_rows": [],
        "compiled_model_rows": [],
        "candidate_process_definition_rows": [],
        "candidate_model_binding_rows": [],
        "candidate_promotion_record_rows": [],
        "experiment_result_rows": [],
        "reverse_engineering_record_rows": [],
        "software_artifact_rows": [],
        "deployment_record_rows": [],
        "sig_outbound_rows": [],
        "forced_expand_event_rows": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "control_decision_log": [],
        "compaction_markers": [],
    }


def generate_proc_stress_scenario(
    *,
    seed: int,
    stabilized_count: int,
    exploration_count: int,
    drifting_count: int,
    research_campaign_count: int,
    software_run_count: int,
    tick_horizon: int,
) -> dict:
    seed_value = int(_as_int(seed, 99001))
    stabilized = int(max(1, _as_int(stabilized_count, 1024)))
    exploration = int(max(1, _as_int(exploration_count, max(64, stabilized // 4))))
    drifting = int(max(1, _as_int(drifting_count, max(64, stabilized // 6))))
    campaigns = int(max(1, _as_int(research_campaign_count, max(24, exploration // 2))))
    software_runs = int(max(1, _as_int(software_run_count, max(128, stabilized // 6))))
    horizon = int(max(8, _as_int(tick_horizon, 96)))

    scenario_id = "scenario.proc.stress.{}".format(
        canonical_sha256(
            {
                "seed": seed_value,
                "stabilized": stabilized,
                "exploration": exploration,
                "drifting": drifting,
                "campaigns": campaigns,
                "software_runs": software_runs,
                "horizon": horizon,
            }
        )[:12]
    )

    stabilized_rows = []
    for idx in range(stabilized):
        process_id = "proc.stress.stabilized.{:05d}".format(idx + 1)
        capsule_id = "process_capsule.{}".format(
            canonical_sha256({"process_id": process_id})[:16]
        )
        safety_critical = bool(_pick(seed_value, "proc9.stab.critical", idx, 11) == 0)
        qc_policy_id = _policy_from_permille(
            _pick(seed_value, "proc9.stab.qc_policy", idx, 1000)
        )
        stabilized_rows.append(
            {
                "process_id": process_id,
                "version": "1.0.0",
                "maturity_state": "capsule_eligible",
                "capsule_id": capsule_id,
                "priority_class": "safety_critical" if safety_critical else "background",
                "safety_critical": safety_critical,
                "qc_policy_id": qc_policy_id,
            }
        )

    exploration_rows = []
    for idx in range(exploration):
        process_id = "proc.stress.explore.{:05d}".format(idx + 1)
        exploration_rows.append(
            {
                "process_id": process_id,
                "version": "1.0.0",
                "maturity_state": "exploration",
                "priority_class": "background",
                "qc_policy_id": _policy_from_permille(
                    _pick(seed_value, "proc9.exp.qc_policy", idx, 1000)
                ),
            }
        )

    drifting_rows = []
    drift_injections = []
    for idx in range(drifting):
        process_id = "proc.stress.drift.{:05d}".format(idx + 1)
        start_tick = int(_pick(seed_value, "proc9.drift.tick", idx, max(2, horizon - 2), offset=1))
        severity = int(_pick(seed_value, "proc9.drift.severity", idx, 1000))
        drifting_rows.append(
            {
                "process_id": process_id,
                "version": "1.0.0",
                "maturity_state": "stabilized",
                "scheduled_drift_tick": start_tick,
                "tool_degradation_score": int(350 + (severity // 2)),
                "environment_deviation_score": int(250 + (severity // 3)),
                "qc_policy_id": "qc.strict_sampling" if severity >= 640 else "qc.basic_sampling",
            }
        )
        drift_injections.append(
            {
                "tick": start_tick,
                "process_id": process_id,
                "tool_degradation_score": int(350 + (severity // 2)),
                "environment_deviation_score": int(250 + (severity // 3)),
                "entropy_growth_rate": int(180 + (severity // 4)),
            }
        )

    campaigns_rows = []
    for idx in range(campaigns):
        process_id = "proc.stress.research.{:05d}".format((idx % exploration) + 1)
        run_tick = int(_pick(seed_value, "proc9.research.tick", idx, max(2, horizon - 2), offset=1))
        campaigns_rows.append(
            {
                "experiment_id": "experiment.proc9.{:05d}".format(idx + 1),
                "candidate_id": "candidate.proc9.{:05d}".format(idx + 1),
                "target_process_id": process_id,
                "run_tick": run_tick,
                "promotion_tick": int(min(horizon - 1, run_tick + 1)),
                "required_replication_count": int(3 + _pick(seed_value, "proc9.research.repl", idx, 3)),
            }
        )

    software_rows = []
    signing_keys = [
        "cred.signing.proc9.alpha",
        "cred.signing.proc9.bravo",
        "cred.signing.proc9.charlie",
        "cred.signing.proc9.delta",
    ]
    for idx in range(software_runs):
        source_hash = canonical_sha256(
            {"source": "proc9.source.{}".format(_pick(seed_value, "proc9.soft.src", idx, 64))}
        )
        config_hash = canonical_sha256(
            {"config": "proc9.config.{}".format(_pick(seed_value, "proc9.soft.cfg", idx, 12))}
        )
        software_rows.append(
            {
                "run_id": "run.proc9.software.{:05d}".format(idx + 1),
                "tick": int(_pick(seed_value, "proc9.soft.tick", idx, max(2, horizon - 2), offset=1)),
                "pipeline_id": "pipeline.build_test_package_sign_deploy",
                "toolchain_id": (
                    "toolchain.stub_c89"
                    if (_pick(seed_value, "proc9.soft.tc", idx, 2) == 0)
                    else "toolchain.stub_cpp98"
                ),
                "source_hash": source_hash,
                "config_hash": config_hash,
                "signing_key_artifact_id": str(signing_keys[idx % len(signing_keys)]),
                "deploy_to_address": "sig://station.proc9.{}".format(
                    _pick(seed_value, "proc9.soft.station", idx, 16)
                ),
            }
        )

    qc_profiles = [
        {
            "qc_policy_id": "qc.none",
            "sampling_strategy_id": "sample.hash_based",
            "risk_class": "low",
        },
        {
            "qc_policy_id": "qc.basic_sampling",
            "sampling_strategy_id": "sample.every_n",
            "risk_class": "medium",
        },
        {
            "qc_policy_id": "qc.strict_sampling",
            "sampling_strategy_id": "sample.risk_weighted",
            "risk_class": "high",
        },
    ]

    summary = {
        "deterministic_ordering": True,
        "bounded_micro_execution_required": True,
        "capsule_execution_must_be_logged": True,
        "drift_actions_must_be_logged": True,
        "inference_must_remain_derived_only": True,
        "compaction_replay_must_match_anchor": True,
    }

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": scenario_id,
        "seed": seed_value,
        "tick_horizon": horizon,
        "industrial_set": {
            "stabilized_capsule_processes": stabilized_rows,
            "exploration_processes": exploration_rows,
            "drifting_processes": drifting_rows,
        },
        "qc_regime": {
            "profiles": qc_profiles,
            "deterministic_sampling_modulus": 1000,
        },
        "drift_revalidation": {
            "drift_injections": sorted(
                drift_injections, key=lambda row: (int(row["tick"]), str(row["process_id"]))
            ),
            "default_revalidation_trials": 3,
        },
        "research_campaigns": sorted(
            campaigns_rows, key=lambda row: (int(row["run_tick"]), str(row["experiment_id"]))
        ),
        "software_pipelines": sorted(
            software_rows, key=lambda row: (int(row["tick"]), str(row["run_id"]))
        ),
        "budget_defaults": {
            "max_micro_steps_per_tick": 48,
            "max_total_tasks_per_tick": 192,
            "max_research_inference_per_tick": 12,
            "max_qc_checks_per_tick": 64,
            "max_safety_critical_per_tick": 64,
        },
        "degradation_policy_order": [
            "degrade.proc.cap_micro_steps",
            "degrade.proc.prefer_capsules",
            "degrade.proc.defer_research_inference",
            "degrade.proc.reduce_low_risk_qc_sampling",
            "degrade.proc.never_defer_safety_checks",
        ],
        "expected_invariants_summary": summary,
        "initial_state_snapshot": _initial_state_snapshot(),
        "deterministic_fingerprint": "",
        "extensions": {
            "counts": {
                "stabilized_capsule_processes": len(stabilized_rows),
                "exploration_processes": len(exploration_rows),
                "drifting_processes": len(drifting_rows),
                "research_campaigns": len(campaigns_rows),
                "software_runs": len(software_rows),
            },
            "qc_policy_ids": _stable_tokens(
                [row.get("qc_policy_id") for row in stabilized_rows + exploration_rows + drifting_rows]
            ),
        },
    }
    scenario["deterministic_fingerprint"] = canonical_sha256(
        dict(scenario, deterministic_fingerprint="")
    )
    return scenario


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate deterministic PROC-9 stress scenario packs."
    )
    parser.add_argument("--seed", type=int, default=99001)
    parser.add_argument("--stabilized-count", type=int, default=1024)
    parser.add_argument("--exploration-count", type=int, default=320)
    parser.add_argument("--drifting-count", type=int, default=192)
    parser.add_argument("--research-campaign-count", type=int, default=160)
    parser.add_argument("--software-run-count", type=int, default=320)
    parser.add_argument("--tick-horizon", type=int, default=96)
    parser.add_argument(
        "--out-scenario",
        default=os.path.join("build", "process", "proc9_scenario.json"),
    )
    parser.add_argument(
        "--out-state",
        default=os.path.join("build", "process", "proc9_initial_state.json"),
    )
    args = parser.parse_args()

    scenario = generate_proc_stress_scenario(
        seed=int(args.seed),
        stabilized_count=int(args.stabilized_count),
        exploration_count=int(args.exploration_count),
        drifting_count=int(args.drifting_count),
        research_campaign_count=int(args.research_campaign_count),
        software_run_count=int(args.software_run_count),
        tick_horizon=int(args.tick_horizon),
    )
    _write_json(str(args.out_scenario), scenario)
    _write_json(str(args.out_state), _as_map(scenario.get("initial_state_snapshot")))

    summary = {
        "result": "complete",
        "scenario_id": str(scenario.get("scenario_id", "")),
        "seed": int(_as_int(scenario.get("seed", 0), 0)),
        "out_scenario": os.path.normpath(str(args.out_scenario)),
        "out_state": os.path.normpath(str(args.out_state)),
        "counts": _as_map(_as_map(scenario.get("extensions")).get("counts")),
        "expected_invariants_summary": _as_map(
            scenario.get("expected_invariants_summary")
        ),
        "deterministic_fingerprint": str(
            scenario.get("deterministic_fingerprint", "")
        ),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
