#!/usr/bin/env python3
"""FLUID-3 deterministic stress harness."""

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

from control.proof.control_proof_bundle import build_control_proof_bundle_from_markers  # noqa: E402
from fluid import process_start_leak, solve_fluid_network_f1  # noqa: E402
from tools.fluid.tool_generate_fluid_stress import _as_int, _write_json, generate_fluid_stress_scenario  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_DEGRADE_ORDER = [
    "degrade.fluid.tick_bucket",
    "degrade.fluid.subgraph_f0_budget",
    "degrade.fluid.defer_noncritical_models",
    "degrade.fluid.leak_eval_cap",
]


def _envelope_defaults(budget_envelope_id: str) -> dict:
    token = str(budget_envelope_id or "").strip().lower()
    if token == "fluid.envelope.tight":
        return {
            "max_cost_units_per_tick": 1400,
            "base_f1_tick_stride": 2,
            "max_model_cost_units_per_network": 420,
            "max_failure_events_per_tick": 24,
            "base_max_leak_evaluations_per_tick": 24,
        }
    if token == "fluid.envelope.rank_strict":
        return {
            "max_cost_units_per_tick": 2200,
            "base_f1_tick_stride": 1,
            "max_model_cost_units_per_network": 680,
            "max_failure_events_per_tick": 48,
            "base_max_leak_evaluations_per_tick": 48,
        }
    return {
        "max_cost_units_per_tick": 2800,
        "base_f1_tick_stride": 1,
        "max_model_cost_units_per_network": 860,
        "max_failure_events_per_tick": 64,
        "base_max_leak_evaluations_per_tick": 64,
    }


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload) if isinstance(payload, Mapping) else {}


def _sorted_rows(rows: object, key_fn) -> bool:
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    return normalized == sorted(normalized, key=key_fn)


def _hash_chain(rows: object, key_fn) -> str:
    chain = "0" * 64
    for row in sorted([dict(item) for item in list(rows or []) if isinstance(item, Mapping)], key=key_fn):
        chain = canonical_sha256({"previous_hash": chain, "row_hash": canonical_sha256(row)})
    return chain


def _graph_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        graph_id = str(row.get("graph_id", "")).strip()
        if not graph_id:
            continue
        out[graph_id] = copy.deepcopy(dict(row))
    return dict((key, out[key]) for key in sorted(out.keys()))


def _estimate_graph_cost(graph_row: Mapping[str, object]) -> int:
    nodes = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
    edges = [dict(row) for row in list(graph_row.get("edges") or []) if isinstance(row, Mapping)]
    return int(max(1, len(nodes) + (len(edges) * 4)))


def _edge_row_by_id(graph_row: Mapping[str, object]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in list(graph_row.get("edges") or []) if isinstance(item, Mapping)), key=lambda item: str(item.get("edge_id", ""))):
        edge_id = str(row.get("edge_id", "")).strip()
        if not edge_id:
            continue
        out[edge_id] = dict(row)
    return out


def _apply_periodic_demand(*, graph_row: dict, graph_id: str, tick: int, periodic_rows: object) -> List[dict]:
    decision_rows: List[dict] = []
    node_rows = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
    rows_by_id = dict((str(row.get("node_id", "")).strip(), row) for row in node_rows if str(row.get("node_id", "")).strip())
    for row in sorted((dict(item) for item in list(periodic_rows or []) if isinstance(item, Mapping)), key=lambda item: (str(item.get("graph_id", "")), str(item.get("node_id", "")), str(item.get("kind", "")))):
        if str(row.get("graph_id", "")).strip() != str(graph_id):
            continue
        start_tick = int(max(0, _as_int(row.get("start_tick", 0), 0)))
        interval_ticks = int(max(1, _as_int(row.get("interval_ticks", 1), 1)))
        end_tick = int(max(start_tick, _as_int(row.get("end_tick", start_tick), start_tick)))
        if int(tick) < start_tick or int(tick) > end_tick or ((int(tick) - start_tick) % interval_ticks) != 0:
            continue
        node_id = str(row.get("node_id", "")).strip()
        node_row = dict(rows_by_id.get(node_id) or {})
        if not node_row:
            continue
        payload = dict(node_row.get("payload") or {}) if isinstance(node_row.get("payload"), Mapping) else {}
        state_ref = dict(payload.get("state_ref") or {}) if isinstance(payload.get("state_ref"), Mapping) else {}
        kind = str(row.get("kind", "")).strip()
        if kind == "pump_speed_cycle":
            delta = int(_as_int(row.get("delta_speed_permille", 0), 0))
            min_value = int(max(0, _as_int(row.get("min_value", 0), 0)))
            max_value = int(max(min_value, _as_int(row.get("max_value", 2000), 2000)))
            current_value = int(_as_int(state_ref.get("pump_speed_permille", 1000), 1000))
            state_ref["pump_speed_permille"] = int(max(min_value, min(max_value, current_value + delta)))
        elif kind == "valve_cycle":
            delta = int(_as_int(row.get("delta_open_permille", 0), 0))
            min_value = int(max(0, _as_int(row.get("min_value", 0), 0)))
            max_value = int(max(min_value, _as_int(row.get("max_value", 1000), 1000)))
            current_value = int(_as_int(state_ref.get("valve_open_permille", 1000), 1000))
            state_ref["valve_open_permille"] = int(max(min_value, min(max_value, current_value + delta)))
        else:
            continue
        payload["state_ref"] = state_ref
        node_row["payload"] = payload
        rows_by_id[node_id] = node_row
        decision_rows.append(
            {
                "process_id": "process.fluid_periodic_demand",
                "tick": int(tick),
                "target_id": str(node_id),
                "reason_code": "fluid.periodic_demand",
                "details": {"kind": kind},
            }
        )
    graph_row["nodes"] = [dict(rows_by_id[key]) for key in sorted(rows_by_id.keys())]
    return decision_rows


def _apply_fault_events(
    *,
    graph_row: dict,
    graph_id: str,
    tick: int,
    fault_rows: object,
    leak_state_rows: object,
) -> dict:
    node_rows = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
    rows_by_id = dict((str(row.get("node_id", "")).strip(), row) for row in node_rows if str(row.get("node_id", "")).strip())
    edge_rows_by_id = _edge_row_by_id(graph_row)
    out_leak_rows = [dict(row) for row in list(leak_state_rows or []) if isinstance(row, Mapping)]
    leak_event_rows: List[dict] = []
    decision_rows: List[dict] = []
    for row in sorted((dict(item) for item in list(fault_rows or []) if isinstance(item, Mapping)), key=lambda item: (int(max(0, _as_int(item.get("tick", 0), 0))), str(item.get("graph_id", "")), str(item.get("fault_kind", "")), str(item.get("target_id", "")))):
        if int(max(0, _as_int(row.get("tick", 0), 0))) != int(tick):
            continue
        if str(row.get("graph_id", "")).strip() != str(graph_id):
            continue
        fault_kind = str(row.get("fault_kind", "")).strip()
        target_id = str(row.get("target_id", "")).strip()
        if fault_kind == "stuck_valve":
            node_row = dict(rows_by_id.get(target_id) or {})
            if not node_row:
                continue
            payload = dict(node_row.get("payload") or {}) if isinstance(node_row.get("payload"), Mapping) else {}
            state_ref = dict(payload.get("state_ref") or {}) if isinstance(payload.get("state_ref"), Mapping) else {}
            state_ref["valve_open_permille"] = int(max(0, min(1000, _as_int(row.get("stuck_open_permille", 250), 250))))
            ext = dict(state_ref.get("extensions") or {}) if isinstance(state_ref.get("extensions"), Mapping) else {}
            ext["stuck"] = True
            state_ref["extensions"] = ext
            payload["state_ref"] = state_ref
            node_row["payload"] = payload
            rows_by_id[target_id] = node_row
        elif fault_kind == "burst_event":
            node_row = dict(rows_by_id.get(target_id) or {})
            if not node_row:
                continue
            payload = dict(node_row.get("payload") or {}) if isinstance(node_row.get("payload"), Mapping) else {}
            state_ref = dict(payload.get("state_ref") or {}) if isinstance(payload.get("state_ref"), Mapping) else {}
            burst_threshold = int(max(1, _as_int(state_ref.get("burst_threshold", 250), 250)))
            boost = int(max(1, _as_int(row.get("head_boost", 200), 200)))
            state_ref["pressure_head"] = int(max(_as_int(state_ref.get("pressure_head", 0), 0), burst_threshold + boost))
            payload["state_ref"] = state_ref
            node_row["payload"] = payload
            rows_by_id[target_id] = node_row
        elif fault_kind == "leak_event":
            leak_started = process_start_leak(
                leak_state_rows=out_leak_rows,
                target_id=target_id,
                leak_rate=int(max(0, _as_int(row.get("leak_rate", 0), 0))),
                current_tick=int(tick),
                source_node_id=str(row.get("source_node_id", "")).strip(),
                sink_kind=str(row.get("sink_kind", "external")).strip() or "external",
                sink_id=str(row.get("sink_id", "")).strip(),
                originating_process_id="process.start_leak",
            )
            out_leak_rows = [dict(item) for item in list(leak_started.get("leak_state_rows") or []) if isinstance(item, Mapping)]
            leak_event_rows.extend(dict(item) for item in list(leak_started.get("leak_event_rows") or []) if isinstance(item, Mapping))
        elif fault_kind == "cavitation_condition":
            edge_row = dict(edge_rows_by_id.get(target_id) or {})
            from_node_id = str(edge_row.get("from_node_id", "")).strip()
            if not from_node_id:
                continue
            node_row = dict(rows_by_id.get(from_node_id) or {})
            if not node_row:
                continue
            payload = dict(node_row.get("payload") or {}) if isinstance(node_row.get("payload"), Mapping) else {}
            state_ref = dict(payload.get("state_ref") or {}) if isinstance(payload.get("state_ref"), Mapping) else {}
            head_drop = int(max(1, _as_int(row.get("head_drop", 40), 40)))
            state_ref["pressure_head"] = int(max(0, _as_int(state_ref.get("pressure_head", 0), 0) - head_drop))
            payload["state_ref"] = state_ref
            node_row["payload"] = payload
            rows_by_id[from_node_id] = node_row
        else:
            continue
        decision_rows.append(
            {
                "process_id": "process.fluid_fault_injection",
                "tick": int(tick),
                "target_id": str(target_id),
                "reason_code": "fluid.fault_injected",
                "details": {"fault_kind": str(fault_kind)},
            }
        )
    graph_row["nodes"] = [dict(rows_by_id[key]) for key in sorted(rows_by_id.keys())]
    return {
        "graph_row": graph_row,
        "leak_state_rows": sorted((dict(row) for row in out_leak_rows if isinstance(row, Mapping)), key=lambda row: str(row.get("target_id", ""))),
        "leak_event_rows": sorted((dict(row) for row in leak_event_rows if isinstance(row, Mapping)), key=lambda row: str(row.get("event_id", ""))),
        "decision_log_rows": sorted((dict(row) for row in decision_rows if isinstance(row, Mapping)), key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("target_id", "")))),
    }


def _proof_tick_hash(result_row: Mapping[str, object]) -> str:
    return canonical_sha256(
        {
            "fluid_flow_hash_chain": str(result_row.get("fluid_flow_hash_chain", "")).strip(),
            "relief_event_hash_chain": str(result_row.get("relief_event_hash_chain", "")).strip(),
            "leak_hash_chain": str(result_row.get("leak_hash_chain", "")).strip(),
            "burst_hash_chain": str(result_row.get("burst_hash_chain", "")).strip(),
        }
    )


def run_fluid_stress_scenario(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str,
    max_cost_units_per_tick: int,
    max_processed_edges_per_network: int,
    max_model_cost_units_per_network: int,
    base_f1_tick_stride: int,
    max_failure_events_per_tick: int,
    base_max_leak_evaluations_per_tick: int,
) -> dict:
    scenario_row = copy.deepcopy(dict(scenario or {}))
    scenario_id = str(scenario_row.get("scenario_id", "")).strip() or "scenario.fluid.unknown"
    horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 64), 64))))
    budget_id = str(budget_envelope_id or "").strip() or "fluid.envelope.standard"
    budget_per_tick = int(max(1, _as_int(max_cost_units_per_tick, 2400)))
    model_cost_cap = int(max(1, _as_int(max_model_cost_units_per_network, 780)))
    base_stride = int(max(1, _as_int(base_f1_tick_stride, 1)))
    failure_cap = int(max(1, _as_int(max_failure_events_per_tick, 64)))
    base_leak_cap = int(max(1, _as_int(base_max_leak_evaluations_per_tick, 64)))

    graph_rows_by_id = _graph_rows_by_id(
        scenario_row.get("fluid_network_graphs")
        or dict(scenario_row.get("initial_state_snapshot") or {}).get("fluid_network_graphs")
    )
    if not graph_rows_by_id:
        return {
            "schema_version": "1.0.0",
            "result": "refused",
            "scenario_id": scenario_id,
            "tick_count": 0,
            "errors": [{"code": "refusal.fluid.missing_graphs", "message": "scenario has no fluid_network_graphs"}],
        }
    graph_ids = sorted(graph_rows_by_id.keys())

    initial_tank_rows = [dict(row) for row in list((dict(scenario_row.get("initial_state_snapshot") or {})).get("tank_state_rows") or []) if isinstance(row, Mapping)]
    initial_leak_rows = [dict(row) for row in list((dict(scenario_row.get("initial_state_snapshot") or {})).get("leak_state_rows") or []) if isinstance(row, Mapping)]
    initial_burst_rows = [dict(row) for row in list((dict(scenario_row.get("initial_state_snapshot") or {})).get("burst_event_rows") or []) if isinstance(row, Mapping)]

    graph_state: Dict[str, dict] = {}
    for graph_id in graph_ids:
        graph_row = copy.deepcopy(dict(graph_rows_by_id.get(graph_id) or {}))
        node_ids = set(str(row.get("node_id", "")).strip() for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping))
        graph_state[graph_id] = {
            "graph_row": graph_row,
            "tank_state_rows": sorted((dict(row) for row in initial_tank_rows if str(row.get("node_id", "")).strip() in node_ids), key=lambda row: str(row.get("node_id", ""))),
            "leak_state_rows": sorted((dict(row) for row in initial_leak_rows if str(row.get("target_id", "")).strip()), key=lambda row: str(row.get("target_id", ""))),
            "burst_event_rows": sorted((dict(row) for row in initial_burst_rows if str(row.get("event_id", "")).strip()), key=lambda row: str(row.get("event_id", ""))),
        }

    per_tick_max_head: List[int] = []
    per_tick_relief_count: List[int] = []
    per_tick_burst_count: List[int] = []
    per_tick_active_leak_count: List[int] = []
    per_tick_downgrade_count: List[int] = []
    per_tick_model_cache_hit_ratio_permille: List[int] = []
    per_tick_cost_units: List[int] = []
    per_tick_proof_hashes: List[str] = []

    decision_log_rows_all: List[dict] = []
    safety_event_rows_all: List[dict] = []
    leak_event_rows_all: List[dict] = []
    relief_event_rows_all: List[dict] = []
    burst_event_rows_all: List[dict] = []
    degradation_event_rows_all: List[dict] = []

    deterministic_ordering_ok = True
    bounded_evaluation_ok = True
    no_silent_mass_changes = True
    all_failures_logged = True

    periodic_rows = list(scenario_row.get("periodic_demand_rows") or [])
    fault_rows = list(scenario_row.get("fault_schedule_rows") or [])
    expected_total_cost = int(sum(_estimate_graph_cost(graph_rows_by_id[graph_id]) for graph_id in graph_ids))
    proof_flow_tick: List[str] = []
    proof_relief_tick: List[str] = []
    proof_leak_tick: List[str] = []
    proof_burst_tick: List[str] = []

    for tick in range(0, int(horizon)):
        remaining_budget = int(budget_per_tick)
        pressure_ratio_permille = int(max(0, ((expected_total_cost - budget_per_tick) * 1000) // expected_total_cost)) if expected_total_cost > 0 else 0

        tick_max_head = 0
        tick_relief = 0
        tick_burst = 0
        tick_active_leaks = 0
        tick_downgrades = 0
        tick_cache_hits = 0
        tick_cache_total = 0
        tick_cost = 0
        tick_proof_rows: List[dict] = []

        for graph_id in graph_ids:
            state = dict(graph_state.get(graph_id) or {})
            graph_row = copy.deepcopy(dict(state.get("graph_row") or {}))
            tank_rows_before = [dict(row) for row in list(state.get("tank_state_rows") or []) if isinstance(row, Mapping)]
            leak_rows = [dict(row) for row in list(state.get("leak_state_rows") or []) if isinstance(row, Mapping)]
            burst_rows = [dict(row) for row in list(state.get("burst_event_rows") or []) if isinstance(row, Mapping)]

            decision_log_rows_all.extend(
                _apply_periodic_demand(
                    graph_row=graph_row,
                    graph_id=graph_id,
                    tick=int(tick),
                    periodic_rows=periodic_rows,
                )
            )
            fault_out = _apply_fault_events(
                graph_row=graph_row,
                graph_id=graph_id,
                tick=int(tick),
                fault_rows=fault_rows,
                leak_state_rows=leak_rows,
            )
            graph_row = dict(fault_out.get("graph_row") or {})
            leak_rows = [dict(row) for row in list(fault_out.get("leak_state_rows") or []) if isinstance(row, Mapping)]
            leak_event_rows_all.extend(dict(row) for row in list(fault_out.get("leak_event_rows") or []) if isinstance(row, Mapping))
            decision_log_rows_all.extend(dict(row) for row in list(fault_out.get("decision_log_rows") or []) if isinstance(row, Mapping))

            estimated_graph_cost = int(max(1, _estimate_graph_cost(graph_row)))
            pressure_stride_extra = int(max(0, pressure_ratio_permille // 320))
            dynamic_stride = int(max(1, base_stride + pressure_stride_extra))
            subgraph_modulo = 0
            if pressure_ratio_permille > 420:
                subgraph_modulo = 2 if pressure_ratio_permille <= 700 else 3
            subgraph_remainder = int(max(0, int(tick) % int(subgraph_modulo))) if subgraph_modulo > 0 else 0
            defer_types: List[str] = []
            if pressure_ratio_permille > 240:
                defer_types = ["model_type.fluid_cavitation_stub"]
            leak_cap = int(max(1, base_leak_cap - (pressure_ratio_permille // 180)))
            dynamic_model_cost_cap = int(max(estimated_graph_cost + 4, min(model_cost_cap, estimated_graph_cost + 40)))
            allocated_budget = int(max(estimated_graph_cost, min(max(estimated_graph_cost, remaining_budget), dynamic_model_cost_cap)))

            result = solve_fluid_network_f1(
                graph_row=graph_row,
                current_tick=int(tick),
                tank_state_rows=tank_rows_before,
                leak_state_rows=leak_rows,
                burst_event_rows=burst_rows,
                failure_policy_row={
                    "policy_id": "fluid_failure.rank_strict",
                    "relief_preferred": True,
                    "burst_requires_threshold": True,
                    "max_failure_events_per_tick": int(failure_cap),
                },
                max_processed_edges=int(max_processed_edges_per_network),
                max_cost_units=int(allocated_budget),
                max_model_cost_units=int(dynamic_model_cost_cap),
                max_failure_events=int(failure_cap),
                solve_tick_stride=int(dynamic_stride),
                downgrade_subgraph_modulo=int(subgraph_modulo),
                downgrade_subgraph_remainder=int(subgraph_remainder),
                defer_noncritical_model_type_ids=list(defer_types),
                max_leak_evaluations_per_tick=int(leak_cap),
            )

            mode = str(result.get("mode", "")).strip().upper()
            if mode == "F0":
                tick_downgrades += 1
            edge_flow_rows = [dict(row) for row in list(result.get("edge_flow_rows") or []) if isinstance(row, Mapping)]
            if len(edge_flow_rows) > int(max_processed_edges_per_network):
                bounded_evaluation_ok = False

            tank_rows_after = [dict(row) for row in list(result.get("tank_state_rows") or []) if isinstance(row, Mapping)]
            prev_mass = int(sum(max(0, _as_int(row.get("stored_mass", 0), 0)) for row in tank_rows_before))
            next_mass = int(sum(max(0, _as_int(row.get("stored_mass", 0), 0)) for row in tank_rows_after))
            relief_rows = [dict(row) for row in list(result.get("relief_event_rows") or []) if isinstance(row, Mapping)]
            leak_tick_rows = [dict(row) for row in list(result.get("leak_event_rows") or []) if isinstance(row, Mapping)]
            transfer_rows = [dict(row) for row in list(result.get("flow_transfer_events") or []) if isinstance(row, Mapping)]
            accounted_loss = int(
                sum(max(0, _as_int(row.get("vented_mass", 0), 0)) for row in relief_rows)
                + sum(max(0, _as_int(row.get("transferred_mass", 0), 0)) for row in leak_tick_rows)
            )
            transfer_accounted = int(
                sum(
                    max(0, _as_int(row.get("transferred_amount", 0), 0))
                    + max(0, _as_int(row.get("lost_amount", 0), 0))
                    for row in transfer_rows
                )
            )
            mass_drop = int(max(0, prev_mass - next_mass))
            if int(mass_drop) > int(accounted_loss + transfer_accounted):
                no_silent_mass_changes = False

            safety_rows = [dict(row) for row in list(result.get("safety_event_rows") or []) if isinstance(row, Mapping)]
            burst_rows_runtime = [dict(row) for row in list(result.get("burst_event_rows") or []) if isinstance(row, Mapping)]
            previous_burst_event_ids = set(str(row.get("event_id", "")).strip() for row in burst_rows if str(row.get("event_id", "")).strip())
            new_burst_rows = [
                dict(row)
                for row in burst_rows_runtime
                if str(row.get("event_id", "")).strip() and str(row.get("event_id", "")).strip() not in previous_burst_event_ids
            ]
            if new_burst_rows:
                burst_targets = set(str(row.get("target_id", "")).strip() for row in new_burst_rows if str(row.get("target_id", "")).strip())
                burst_safety_targets = set(
                    str(token).strip()
                    for row in safety_rows
                    if str(row.get("pattern_id", "")).strip() == "safety.burst_disk"
                    for token in list(row.get("target_ids") or [])
                    if str(token).strip()
                )
                if not burst_targets.issubset(burst_safety_targets):
                    all_failures_logged = False
            if relief_rows:
                relief_targets = set(str(row.get("target_id", "")).strip() for row in relief_rows if str(row.get("target_id", "")).strip())
                relief_safety_targets = set(
                    str(token).strip()
                    for row in safety_rows
                    if str(row.get("pattern_id", "")).strip() == "safety.relief_pressure"
                    for token in list(row.get("target_ids") or [])
                    if str(token).strip()
                )
                if not relief_targets.issubset(relief_safety_targets):
                    all_failures_logged = False

            deterministic_ordering_ok = bool(
                deterministic_ordering_ok
                and _sorted_rows(edge_flow_rows, key_fn=lambda row: str(row.get("edge_id", "")))
                and _sorted_rows(result.get("leak_state_rows"), key_fn=lambda row: str(row.get("target_id", "")))
                and _sorted_rows(result.get("burst_event_rows"), key_fn=lambda row: str(row.get("event_id", "")))
            )

            graph_state[graph_id] = {
                "graph_row": graph_row,
                "tank_state_rows": tank_rows_after,
                "leak_state_rows": [dict(row) for row in list(result.get("leak_state_rows") or []) if isinstance(row, Mapping)],
                "burst_event_rows": burst_rows_runtime,
            }

            node_head_rows = [dict(row) for row in list(result.get("node_pressure_rows") or []) if isinstance(row, Mapping)]
            tick_max_head = int(
                max(
                    tick_max_head,
                    max((int(max(0, _as_int(row.get("head_value", 0), 0))) for row in node_head_rows), default=0),
                )
            )
            tick_relief += int(len(relief_rows))
            tick_burst += int(len(new_burst_rows))
            tick_active_leaks += int(
                len([row for row in list(result.get("leak_state_rows") or []) if isinstance(row, Mapping) and bool(row.get("active", False))])
            )
            model_rows = [dict(row) for row in list(result.get("model_evaluation_results") or []) if isinstance(row, Mapping)]
            for row in model_rows:
                ext = _as_map(row.get("extensions"))
                tick_cache_total += 1
                if bool(ext.get("cache_hit", False)):
                    tick_cache_hits += 1
            decision_rows = [dict(row) for row in list(result.get("decision_log_rows") or []) if isinstance(row, Mapping)]
            decision_log_rows_all.extend(decision_rows)
            for row in decision_rows:
                reason_code = str(row.get("reason_code", "")).strip()
                if reason_code.startswith("degrade.fluid"):
                    degradation_event_rows_all.append(
                        {
                            "tick": int(max(0, _as_int(row.get("tick", tick), tick))),
                            "graph_id": str(graph_id),
                            "reason_code": str(reason_code),
                            "step_order": int(_DEGRADE_ORDER.index(reason_code) + 1) if reason_code in _DEGRADE_ORDER else 999,
                            "details": _as_map(row.get("details")),
                        }
                    )
            safety_event_rows_all.extend(safety_rows)
            leak_event_rows_all.extend(leak_tick_rows)
            relief_event_rows_all.extend(relief_rows)
            burst_event_rows_all.extend(new_burst_rows)
            tick_cost += int(max(0, _as_int(result.get("model_cost_units", 0), 0)) + len(edge_flow_rows) + len(node_head_rows))
            remaining_budget = int(max(0, remaining_budget - estimated_graph_cost))

            proof_flow_tick.append(str(result.get("fluid_flow_hash_chain", "")).strip())
            proof_relief_tick.append(str(result.get("relief_event_hash_chain", "")).strip())
            proof_leak_tick.append(str(result.get("leak_hash_chain", "")).strip())
            proof_burst_tick.append(str(result.get("burst_hash_chain", "")).strip())
            tick_proof_rows.append(
                {
                    "graph_id": str(graph_id),
                    "fluid_flow_hash_chain": str(result.get("fluid_flow_hash_chain", "")).strip(),
                    "relief_event_hash_chain": str(result.get("relief_event_hash_chain", "")).strip(),
                    "leak_hash_chain": str(result.get("leak_hash_chain", "")).strip(),
                    "burst_hash_chain": str(result.get("burst_hash_chain", "")).strip(),
                }
            )

        per_tick_max_head.append(int(tick_max_head))
        per_tick_relief_count.append(int(tick_relief))
        per_tick_burst_count.append(int(tick_burst))
        per_tick_active_leak_count.append(int(tick_active_leaks))
        per_tick_downgrade_count.append(int(tick_downgrades))
        cache_ratio = int((tick_cache_hits * 1000) // tick_cache_total) if tick_cache_total > 0 else 1000
        per_tick_model_cache_hit_ratio_permille.append(int(cache_ratio))
        per_tick_cost_units.append(int(tick_cost))
        per_tick_proof_hashes.append(
            str(
                (
                    build_control_proof_bundle_from_markers(
                        tick_start=int(tick),
                        tick_end=int(tick),
                        decision_markers=[],
                        mobility_proof_surface={
                            "fluid_flow_hash_chain": _hash_chain(
                                tick_proof_rows,
                                key_fn=lambda row: str(row.get("graph_id", "")),
                            ),
                            "relief_event_hash_chain": canonical_sha256(
                                [
                                    str(row.get("relief_event_hash_chain", ""))
                                    for row in sorted(
                                        tick_proof_rows,
                                        key=lambda row: str(row.get("graph_id", "")),
                                    )
                                ]
                            ),
                            "leak_hash_chain": canonical_sha256(
                                [
                                    str(row.get("leak_hash_chain", ""))
                                    for row in sorted(
                                        tick_proof_rows,
                                        key=lambda row: str(row.get("graph_id", "")),
                                    )
                                ]
                            ),
                            "burst_hash_chain": canonical_sha256(
                                [
                                    str(row.get("burst_hash_chain", ""))
                                    for row in sorted(
                                        tick_proof_rows,
                                        key=lambda row: str(row.get("graph_id", "")),
                                    )
                                ]
                            ),
                        },
                    )
                ).get("deterministic_fingerprint", "")
            ).strip()
        )

    degradation_rows_sorted = sorted(
        (dict(row) for row in degradation_event_rows_all if isinstance(row, Mapping)),
        key=lambda row: (
            int(max(0, _as_int(row.get("tick", 0), 0))),
            str(row.get("graph_id", "")),
            int(max(0, _as_int(row.get("step_order", 999), 999))),
            str(row.get("reason_code", "")),
        ),
    )
    degradation_order_deterministic = degradation_rows_sorted == [
        dict(row) for row in degradation_event_rows_all if isinstance(row, Mapping)
    ]
    if degradation_rows_sorted:
        rows_by_scope: Dict[str, List[int]] = {}
        for row in degradation_rows_sorted:
            key = "{}::{}".format(
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("graph_id", "")).strip(),
            )
            rows_by_scope.setdefault(key, [])
            rows_by_scope[key].append(int(max(0, _as_int(row.get("step_order", 999), 999))))
        for values in rows_by_scope.values():
            if values != sorted(values):
                degradation_order_deterministic = False
                break

    fluid_flow_hash_chain = canonical_sha256(list(proof_flow_tick))
    relief_event_hash_chain = canonical_sha256(list(proof_relief_tick))
    leak_hash_chain = canonical_sha256(list(proof_leak_tick))
    burst_hash_chain = canonical_sha256(list(proof_burst_tick))
    proof_hash_summary = {
        "fluid_flow_hash_chain": str(fluid_flow_hash_chain),
        "relief_event_hash_chain": str(relief_event_hash_chain),
        "leak_hash_chain": str(leak_hash_chain),
        "burst_hash_chain": str(burst_hash_chain),
        "proof_tick_hash_chain": canonical_sha256(list(per_tick_proof_hashes)),
    }

    result = {
        "schema_version": "1.0.0",
        "result": "complete"
        if (
            bool(deterministic_ordering_ok)
            and bool(bounded_evaluation_ok)
            and bool(no_silent_mass_changes)
            and bool(all_failures_logged)
            and bool(degradation_order_deterministic)
        )
        else "refused",
        "scenario_id": str(scenario_id),
        "budget_envelope_id": str(budget_id),
        "tick_count": int(horizon),
        "metrics": {
            "max_head_per_tick": [int(value) for value in per_tick_max_head],
            "relief_event_counts_per_tick": [int(value) for value in per_tick_relief_count],
            "burst_event_counts_per_tick": [int(value) for value in per_tick_burst_count],
            "active_leak_counts_per_tick": [int(value) for value in per_tick_active_leak_count],
            "downgraded_network_counts_per_tick": [int(value) for value in per_tick_downgrade_count],
            "model_cache_hit_ratios_permille": [int(value) for value in per_tick_model_cache_hit_ratio_permille],
            "cost_units_per_tick": [int(value) for value in per_tick_cost_units],
            "proof_hash_summary": proof_hash_summary,
        },
        "assertions": {
            "bounded_evaluation": bool(bounded_evaluation_ok),
            "deterministic_ordering": bool(deterministic_ordering_ok),
            "no_silent_mass_changes": bool(no_silent_mass_changes),
            "all_failures_logged": bool(all_failures_logged),
            "degradation_order_deterministic": bool(degradation_order_deterministic),
        },
        "extensions": {
            "proof_hashes_per_tick": list(per_tick_proof_hashes),
            "fluid_degradation_event_rows": list(degradation_rows_sorted),
            "decision_log_rows": sorted(
                (dict(row) for row in decision_log_rows_all if isinstance(row, Mapping)),
                key=lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("target_id", "")),
                    str(row.get("reason_code", "")),
                ),
            ),
            "safety_event_rows": sorted(
                (dict(row) for row in safety_event_rows_all if isinstance(row, Mapping)),
                key=lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("event_id", "")),
                ),
            ),
            "leak_event_rows": sorted(
                (dict(row) for row in leak_event_rows_all if isinstance(row, Mapping)),
                key=lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("event_id", "")),
                ),
            ),
            "relief_event_rows": sorted(
                (dict(row) for row in relief_event_rows_all if isinstance(row, Mapping)),
                key=lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("event_id", "")),
                ),
            ),
            "burst_event_rows": sorted(
                (dict(row) for row in burst_event_rows_all if isinstance(row, Mapping)),
                key=lambda row: (
                    int(max(0, _as_int(_as_map(row.get("extensions")).get("tick", 0), 0))),
                    str(row.get("event_id", "")),
                ),
            ),
            "cost_units_hash": canonical_sha256(list(per_tick_cost_units)),
            "max_head_hash": canonical_sha256(list(per_tick_max_head)),
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(result)
    seed["deterministic_fingerprint"] = ""
    result["deterministic_fingerprint"] = canonical_sha256(seed)
    if str(result.get("result", "")).strip() == "complete":
        return result
    return {
        **result,
        "errors": [
            {
                "code": "refusal.fluid.stress_assertion_failed",
                "message": "One or more FLUID-3 stress assertions failed",
                "path": "$.assertions",
            }
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic FLUID-3 stress scenario.")
    parser.add_argument("--scenario", default="build/fluid/fluid_stress_scenario.json")
    parser.add_argument("--seed", type=int, default=9601)
    parser.add_argument("--tanks", type=int, default=24)
    parser.add_argument("--vessels", type=int, default=8)
    parser.add_argument("--pipes", type=int, default=180)
    parser.add_argument("--pumps", type=int, default=12)
    parser.add_argument("--valves", type=int, default=20)
    parser.add_argument("--graphs", type=int, default=3)
    parser.add_argument("--tick-count", type=int, default=64)
    parser.add_argument("--interior-compartments", type=int, default=8)
    parser.add_argument("--budget-envelope-id", default="fluid.envelope.standard")
    parser.add_argument("--max-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--max-processed-edges-per-network", type=int, default=4096)
    parser.add_argument("--max-model-cost-units-per-network", type=int, default=0)
    parser.add_argument("--base-f1-tick-stride", type=int, default=0)
    parser.add_argument("--max-failure-events-per-tick", type=int, default=0)
    parser.add_argument("--base-max-leak-evaluations-per-tick", type=int, default=0)
    parser.add_argument("--output", default="build/fluid/fluid_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_path = os.path.normpath(os.path.abspath(str(args.scenario)))
    if os.path.isfile(scenario_path):
        scenario = _load_json(scenario_path)
    else:
        scenario = generate_fluid_stress_scenario(
            seed=int(args.seed),
            tanks=int(args.tanks),
            vessels=int(args.vessels),
            pipes=int(args.pipes),
            pumps=int(args.pumps),
            valves=int(args.valves),
            graphs=int(args.graphs),
            ticks=int(args.tick_count),
            interior_compartment_count=int(args.interior_compartments),
        )
        _write_json(scenario_path, scenario)

    defaults = _envelope_defaults(str(args.budget_envelope_id))
    result = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=int(args.tick_count),
        budget_envelope_id=str(args.budget_envelope_id),
        max_cost_units_per_tick=int(args.max_cost_units_per_tick) or int(defaults["max_cost_units_per_tick"]),
        max_processed_edges_per_network=int(args.max_processed_edges_per_network),
        max_model_cost_units_per_network=int(args.max_model_cost_units_per_network) or int(defaults["max_model_cost_units_per_network"]),
        base_f1_tick_stride=int(args.base_f1_tick_stride) or int(defaults["base_f1_tick_stride"]),
        max_failure_events_per_tick=int(args.max_failure_events_per_tick) or int(defaults["max_failure_events_per_tick"]),
        base_max_leak_evaluations_per_tick=int(args.base_max_leak_evaluations_per_tick) or int(defaults["base_max_leak_evaluations_per_tick"]),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, result)
    print(
        json.dumps(
            {
                "result": str(result.get("result", "")),
                "scenario_id": str(result.get("scenario_id", "")),
                "output_path": output_abs,
                "deterministic_fingerprint": str(result.get("deterministic_fingerprint", "")),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(result.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
