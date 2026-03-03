#!/usr/bin/env python3
"""ELEC-5 deterministic stress harness."""

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

from tools.electric.tool_generate_elec_stress_scenario import (  # noqa: E402
    _as_int,
    _write_json,
    generate_elec_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402
from tools.xstack.sessionx.process_runtime import execute_intent  # noqa: E402


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        row = json.load(handle)
    return dict(row) if isinstance(row, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _chain_hash(rows: object, *, row_sort_key) -> str:
    chain = "0" * 64
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    for row in sorted(normalized, key=row_sort_key):
        row_hash = canonical_sha256(row)
        chain = canonical_sha256({"previous_hash": chain, "row_hash": row_hash})
    return chain


def _law_profile() -> dict:
    return {
        "law_profile_id": "law.tool.electric.stress",
        "allowed_processes": ["process.elec.network_tick"],
        "forbidden_processes": [],
        "process_entitlement_requirements": {"process.elec.network_tick": "session.boot"},
        "process_privilege_requirements": {"process.elec.network_tick": "observer"},
        "epistemic_limits": {"allow_hidden_state_access": True},
        "allowed_lenses": ["lens.observer.admin"],
    }


def _authority_context() -> dict:
    return {
        "subject_id": "subject.tool.electric.stress",
        "authority_origin": "tool",
        "law_profile_id": "law.tool.electric.stress",
        "entitlements": ["session.boot", "entitlement.control.admin", "entitlement.inspect"],
        "privilege_level": "observer",
    }


def _policy_context(
    *,
    budget_envelope_id: str,
    max_network_solves_per_tick: int,
    max_edges_per_network: int,
    max_fault_evals_per_tick: int,
    max_trip_actions_per_tick: int,
    cascade_max_iterations: int,
) -> dict:
    return {
        "budget_envelope_id": str(budget_envelope_id or "").strip() or "elec.envelope.standard",
        "elec_e1_enabled": True,
        "elec_max_network_solves_per_tick": int(max(1, _as_int(max_network_solves_per_tick, 16))),
        "elec_max_edges_per_network": int(max(0, _as_int(max_edges_per_network, 4096))),
        "elec_max_fault_evals_per_tick": int(max(1, _as_int(max_fault_evals_per_tick, 4096))),
        "elec_max_trip_actions_per_tick": int(max(1, _as_int(max_trip_actions_per_tick, 4096))),
        "elec_cascade_max_iterations": int(max(1, _as_int(cascade_max_iterations, 4))),
        "active_shard_id": "shard.01",
    }


def _binding_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict(
        (str(row.get("binding_id", "")).strip(), dict(row))
        for row in list(rows or [])
        if isinstance(row, Mapping) and str(row.get("binding_id", "")).strip()
    )


def _apply_load_spikes(state: dict, *, tick: int, load_spike_rows: object) -> None:
    rows_by_id = _binding_rows_by_id(state.get("model_bindings"))
    for row in list(load_spike_rows or []):
        if not isinstance(row, Mapping):
            continue
        if int(max(0, _as_int(row.get("tick", 0), 0))) != int(tick):
            continue
        binding_id = str(row.get("binding_id", "")).strip()
        if not binding_id:
            continue
        binding_row = dict(rows_by_id.get(binding_id) or {})
        if not binding_row:
            continue
        params = _as_map(binding_row.get("parameters"))
        delta = int(max(0, _as_int(row.get("delta_demand_p", 0), 0)))
        params["demand_p"] = int(max(0, _as_int(params.get("demand_p", 0), 0) + delta))
        binding_row["parameters"] = params
        rows_by_id[binding_id] = binding_row
    state["model_bindings"] = [dict(rows_by_id[key]) for key in sorted(rows_by_id.keys())]


def _channel_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict(
        (str(row.get("channel_id", "")).strip(), dict(row))
        for row in list(rows or [])
        if isinstance(row, Mapping) and str(row.get("channel_id", "")).strip()
    )


def _apply_short_circuit_flags(state: dict, *, tick: int, short_circuit_rows: object) -> None:
    by_id = _channel_rows_by_id(state.get("elec_flow_channels"))
    for row in list(short_circuit_rows or []):
        if not isinstance(row, Mapping):
            continue
        channel_id = str(row.get("channel_id", "")).strip()
        if not channel_id:
            continue
        start_tick = int(max(0, _as_int(row.get("start_tick", 0), 0)))
        end_tick = int(max(start_tick, _as_int(row.get("end_tick", start_tick), start_tick)))
        active = bool(int(tick) >= int(start_tick) and int(tick) <= int(end_tick))
        channel_row = dict(by_id.get(channel_id) or {"channel_id": channel_id})
        ext = _as_map(channel_row.get("extensions"))
        ext["short_circuit"] = bool(active)
        ext["source_fault_kind_id"] = str(row.get("fault_kind_id", "fault.short_circuit")).strip() or "fault.short_circuit"
        channel_row["extensions"] = ext
        by_id[channel_id] = channel_row
    state["elec_flow_channels"] = [dict(by_id[key]) for key in sorted(by_id.keys())]


def _assert_sorted_rows(rows: object, key_fn) -> bool:
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    return normalized == sorted(normalized, key=key_fn)


def run_elec_stress_scenario(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str,
    max_network_solves_per_tick: int,
    max_edges_per_network: int,
    max_fault_evals_per_tick: int,
    max_trip_actions_per_tick: int,
    cascade_max_iterations: int,
) -> dict:
    scenario_row = copy.deepcopy(dict(scenario or {}))
    scenario_id = str(scenario_row.get("scenario_id", "")).strip() or "scenario.elec.unknown"
    horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 64), 64))))
    budget_id = str(budget_envelope_id or "").strip() or "elec.envelope.standard"

    initial_state = copy.deepcopy(dict(scenario_row.get("initial_state_snapshot") or {}))
    state = copy.deepcopy(dict(initial_state))
    state["power_network_graphs"] = [
        copy.deepcopy(dict(row))
        for row in list(scenario_row.get("power_network_graphs") or state.get("power_network_graphs") or [])
        if isinstance(row, Mapping)
    ]
    state["model_bindings"] = [
        copy.deepcopy(dict(row))
        for row in list(scenario_row.get("model_bindings") or state.get("model_bindings") or [])
        if isinstance(row, Mapping)
    ]
    if not isinstance(state.get("elec_flow_channels"), list):
        state["elec_flow_channels"] = [
            copy.deepcopy(dict(row))
            for row in list(scenario_row.get("initial_flow_channel_overrides") or [])
            if isinstance(row, Mapping)
        ]
    state.setdefault("control_decision_log", [])
    state.setdefault("elec_degradation_events", [])
    state.setdefault("elec_fault_states", [])
    state.setdefault("elec_trip_events", [])
    state.setdefault("simulation_time", {"tick": 0, "tick_rate": 1, "deterministic_clock": {"tick_duration_ms": 1000}})

    per_tick_cost_units: List[int] = []
    per_tick_proof_hashes: List[str] = []
    per_tick_power_flow_hashes: List[str] = []
    per_tick_fault_hashes: List[str] = []
    per_tick_trip_hashes: List[str] = []
    per_tick_degrade_hashes: List[str] = []
    downgrade_count = 0
    tripped_count = 0
    max_trip_cascade_depth = 0
    steady_state_tick = None
    silent_mutation_detected = False
    cascade_limit_reached = False
    previous_state_anchor = ""
    stable_streak = 0

    for tick in range(1, int(horizon) + 1):
        _apply_load_spikes(state, tick=int(tick), load_spike_rows=scenario_row.get("load_spike_rows"))
        _apply_short_circuit_flags(state, tick=int(tick), short_circuit_rows=scenario_row.get("short_circuit_rows"))

        result = execute_intent(
            state=state,
            intent={
                "intent_id": "intent.elec.stress.tick.{}.{}".format(scenario_id.split(".")[-1], str(tick).zfill(4)),
                "process_id": "process.elec.network_tick",
                "inputs": {
                    "max_network_solves_per_tick": int(max_network_solves_per_tick),
                    "max_edges_per_network": int(max_edges_per_network),
                    "max_fault_evals_per_tick": int(max_fault_evals_per_tick),
                    "max_trip_actions_per_tick": int(max_trip_actions_per_tick),
                    "cascade_max_iterations": int(cascade_max_iterations),
                    "budget_envelope_id": str(budget_id),
                    "pending_low_priority_connections": [
                        dict(row)
                        for row in list(scenario_row.get("pending_connection_requests") or [])
                        if isinstance(row, Mapping)
                    ],
                },
            },
            law_profile=_law_profile(),
            authority_context=_authority_context(),
            navigation_indices={},
            policy_context=_policy_context(
                budget_envelope_id=str(budget_id),
                max_network_solves_per_tick=int(max_network_solves_per_tick),
                max_edges_per_network=int(max_edges_per_network),
                max_fault_evals_per_tick=int(max_fault_evals_per_tick),
                max_trip_actions_per_tick=int(max_trip_actions_per_tick),
                cascade_max_iterations=int(cascade_max_iterations),
            ),
        )
        if str(result.get("result", "")).strip() != "complete":
            return {
                "schema_version": "1.0.0",
                "result": "refused",
                "scenario_id": scenario_id,
                "tick_count": int(tick),
                "errors": [
                    {
                        "code": str((dict(result.get("error") or {})).get("code", "refusal.elec.stress_runtime_error")),
                        "message": str((dict(result.get("error") or {})).get("message", "process.elec.network_tick refused during stress run")),
                    }
                ],
            }

        power_flow_hash = str(state.get("power_flow_hash", "")).strip()
        fault_hash = str(state.get("fault_state_hash_chain", "")).strip()
        trip_hash = str(state.get("trip_event_hash_chain", "")).strip()
        degrade_hash = str(state.get("degradation_event_hash_chain", "")).strip()
        proof_surface = dict(state.get("elec_proof_surface") or {})
        proof_hash = str(proof_surface.get("deterministic_fingerprint", "")).strip()

        per_tick_power_flow_hashes.append(power_flow_hash)
        per_tick_fault_hashes.append(fault_hash)
        per_tick_trip_hashes.append(trip_hash)
        per_tick_degrade_hashes.append(degrade_hash)
        per_tick_proof_hashes.append(proof_hash)

        edge_count = int(len(list(state.get("elec_edge_status_rows") or [])))
        active_fault_count = int(len([row for row in list(state.get("elec_fault_states") or []) if isinstance(row, Mapping) and bool(row.get("active", False))]))
        trip_count = int(len(list(state.get("elec_trip_events") or [])))
        degrade_count = int(len(list(state.get("elec_degradation_events") or [])))
        tick_cost_units = int(max(0, edge_count + active_fault_count + trip_count + degrade_count))
        per_tick_cost_units.append(int(tick_cost_units))

        downgrade_count += int(len(list(result.get("downgraded_graph_ids") or [])))
        tripped_count = int(max(tripped_count, trip_count))
        max_trip_cascade_depth = int(max(max_trip_cascade_depth, len(list(state.get("elec_trip_cascade_rows") or []))))
        cascade_limit_reached = bool(cascade_limit_reached or bool(result.get("cascade_iteration_limit_reached", False)))

        state_anchor = canonical_sha256(
            {
                "power_flow_hash": power_flow_hash,
                "fault_state_hash_chain": fault_hash,
                "trip_event_hash_chain": trip_hash,
                "degradation_event_hash_chain": degrade_hash,
            }
        )
        if state_anchor == previous_state_anchor:
            stable_streak += 1
            if steady_state_tick is None and stable_streak >= 3:
                steady_state_tick = int(tick - 2)
        else:
            stable_streak = 1
            previous_state_anchor = state_anchor

        if len(per_tick_power_flow_hashes) >= 2:
            if per_tick_power_flow_hashes[-1] != per_tick_power_flow_hashes[-2]:
                if int(len(list(state.get("elec_edge_status_rows") or []))) <= 0:
                    silent_mutation_detected = True

    deterministic_ordering_ok = bool(
        _assert_sorted_rows(
            state.get("elec_edge_status_rows"),
            key_fn=lambda row: (str(row.get("graph_id", "")), str(row.get("edge_id", ""))),
        )
        and _assert_sorted_rows(
            state.get("elec_fault_states"),
            key_fn=lambda row: (str(row.get("fault_kind_id", "")), str(row.get("target_id", "")), str(row.get("fault_id", ""))),
        )
    )
    unlogged_trip_detected = bool(tripped_count > 0 and (not str(state.get("trip_event_hash_chain", "")).strip()))
    no_silent_mutation = not bool(silent_mutation_detected)
    no_infinite_loop = not bool(cascade_limit_reached)

    proof_hash_summary = {
        "power_flow_hash_chain": str(state.get("power_flow_hash_chain", "")).strip(),
        "fault_state_hash_chain": str(state.get("fault_state_hash_chain", "")).strip(),
        "protection_state_hash_chain": str(state.get("protection_state_hash_chain", "")).strip(),
        "degradation_event_hash_chain": str(state.get("degradation_event_hash_chain", "")).strip(),
        "trip_event_hash_chain": str(state.get("trip_event_hash_chain", "")).strip(),
        "trip_explanation_hash_chain": str(state.get("trip_explanation_hash_chain", "")).strip(),
        "proof_surface_hash": str((dict(state.get("elec_proof_surface") or {})).get("deterministic_fingerprint", "")).strip(),
    }

    report = {
        "schema_version": "1.0.0",
        "result": "complete"
        if (deterministic_ordering_ok and no_infinite_loop and (not unlogged_trip_detected) and no_silent_mutation)
        else "refused",
        "scenario_id": scenario_id,
        "budget_envelope_id": str(budget_id),
        "tick_count": int(horizon),
        "metrics": {
            "ticks_to_steady_state": int(steady_state_tick if steady_state_tick is not None else horizon),
            "cascaded_trip_count": int(max_trip_cascade_depth),
            "degraded_solve_count": int(downgrade_count),
            "cost_units_per_tick": [int(value) for value in per_tick_cost_units],
            "decision_log_stability": canonical_sha256(
                [
                    {
                        "decision_id": str(row.get("decision_id", "")).strip(),
                        "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                        "process_id": str(row.get("process_id", "")).strip(),
                    }
                    for row in sorted(
                        [dict(row) for row in list(state.get("control_decision_log") or []) if isinstance(row, Mapping)],
                        key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("decision_id", ""))),
                    )
                ]
            ),
            "proof_hash_summary": proof_hash_summary,
        },
        "assertions": {
            "deterministic_ordering": bool(deterministic_ordering_ok),
            "no_infinite_loops": bool(no_infinite_loop),
            "no_unlogged_trips": not bool(unlogged_trip_detected),
            "no_silent_flow_mutation": bool(no_silent_mutation),
        },
        "extensions": {
            "power_flow_hashes_per_tick": list(per_tick_power_flow_hashes),
            "fault_hashes_per_tick": list(per_tick_fault_hashes),
            "trip_hashes_per_tick": list(per_tick_trip_hashes),
            "degradation_hashes_per_tick": list(per_tick_degrade_hashes),
            "proof_hashes_per_tick": list(per_tick_proof_hashes),
            "cost_units_hash": canonical_sha256(list(per_tick_cost_units)),
            "trip_event_count": int(len(list(state.get("elec_trip_events") or []))),
            "fault_event_count": int(len(list(state.get("elec_fault_events") or []))),
            "degradation_event_count": int(len(list(state.get("elec_degradation_events") or []))),
            "boundary_transfer_count": int(len(list(state.get("elec_boundary_transfer_artifacts") or []))),
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    if str(report.get("result", "")).strip() == "complete":
        return report
    return {
        **report,
        "errors": [
            {
                "code": "refusal.elec.stress_assertion_failed",
                "message": "One or more electrical stress assertions failed",
                "path": "$.assertions",
            }
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic ELEC stress harness.")
    parser.add_argument("--scenario", default="")
    parser.add_argument("--seed", type=int, default=5501)
    parser.add_argument("--generators", type=int, default=24)
    parser.add_argument("--loads", type=int, default=180)
    parser.add_argument("--storage", type=int, default=36)
    parser.add_argument("--breakers", type=int, default=48)
    parser.add_argument("--graphs", type=int, default=2)
    parser.add_argument("--shards", type=int, default=2)
    parser.add_argument("--ticks", type=int, default=64)
    parser.add_argument("--budget-envelope-id", default="elec.envelope.standard")
    parser.add_argument("--max-network-solves-per-tick", type=int, default=8)
    parser.add_argument("--max-edges-per-network", type=int, default=4096)
    parser.add_argument("--max-fault-evals-per-tick", type=int, default=4096)
    parser.add_argument("--max-trip-actions-per-tick", type=int, default=4096)
    parser.add_argument("--cascade-max-iterations", type=int, default=4)
    parser.add_argument("--output", default="build/electric/elec_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_path = str(args.scenario).strip()
    if scenario_path:
        scenario = _load_json(os.path.normpath(os.path.abspath(scenario_path)))
    else:
        scenario = generate_elec_stress_scenario(
            seed=int(args.seed),
            generator_count=int(args.generators),
            load_count=int(args.loads),
            storage_count=int(args.storage),
            breaker_count=int(args.breakers),
            graph_count=int(args.graphs),
            shard_count=int(args.shards),
            tick_horizon=int(args.ticks),
        )
    report = run_elec_stress_scenario(
        scenario=scenario,
        tick_count=int(args.ticks),
        budget_envelope_id=str(args.budget_envelope_id),
        max_network_solves_per_tick=int(args.max_network_solves_per_tick),
        max_edges_per_network=int(args.max_edges_per_network),
        max_fault_evals_per_tick=int(args.max_fault_evals_per_tick),
        max_trip_actions_per_tick=int(args.max_trip_actions_per_tick),
        cascade_max_iterations=int(args.cascade_max_iterations),
    )
    report["scenario_id"] = str(scenario.get("scenario_id", "")).strip() or str(report.get("scenario_id", ""))
    report["scenario_fingerprint"] = str(scenario.get("deterministic_fingerprint", "")).strip()
    if scenario_path:
        report["scenario_path"] = os.path.normpath(os.path.abspath(scenario_path))

    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, report)
    report["output_path"] = output_abs
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
