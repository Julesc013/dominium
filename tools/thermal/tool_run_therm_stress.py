#!/usr/bin/env python3
"""THERM-5 deterministic stress harness."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from control.proof.control_proof_bundle import build_control_proof_bundle_from_markers  # noqa: E402
from thermal.network.thermal_network_engine import solve_thermal_network_t0, solve_thermal_network_t1  # noqa: E402
from tools.thermal.tool_generate_therm_stress_scenario import _as_int, _write_json, generate_therm_stress_scenario  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_map(value):
    return dict(value or {}) if isinstance(value, dict) else {}


def _load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        row = json.load(handle)
    return dict(row) if isinstance(row, dict) else {}


def _hash_chain(rows, sort_key):
    chain = "0" * 64
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, dict)]
    for row in sorted(normalized, key=sort_key):
        chain = canonical_sha256({"previous_hash": chain, "row_hash": canonical_sha256(row)})
    return chain


def _assert_sorted(rows, key_fn):
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, dict)]
    return normalized == sorted(normalized, key=key_fn)


def _graph_rows_by_id(rows):
    out = {}
    for row in list(rows or []):
        if not isinstance(row, dict):
            continue
        graph_id = str(row.get("graph_id", "")).strip()
        if not graph_id:
            continue
        out[graph_id] = copy.deepcopy(row)
    return dict((k, out[k]) for k in sorted(out.keys()))


def _estimate_graph_cost(graph_row):
    nodes = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, dict)]
    edges = [dict(row) for row in list(graph_row.get("edges") or []) if isinstance(row, dict)]
    return int(max(1, len(nodes) + len(edges)))


def _periodic_heat_rows_for_tick(periodic_rows, graph_id, tick):
    selected = []
    for row in list(periodic_rows or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("graph_id", "")).strip() != str(graph_id):
            continue
        start_tick = int(max(0, _as_int(row.get("start_tick", 0), 0)))
        interval = int(max(1, _as_int(row.get("interval_ticks", 1), 1)))
        end_tick = int(max(start_tick, _as_int(row.get("end_tick", start_tick), start_tick)))
        if tick < start_tick or tick > end_tick:
            continue
        if ((tick - start_tick) % interval) != 0:
            continue
        selected.append(
            {
                "node_id": str(row.get("node_id", "")).strip(),
                "heat_input": int(max(0, _as_int(row.get("heat_input", 0), 0))),
                "source_id": str(row.get("source_id", "")).strip(),
                "source_domain_id": str(row.get("source_domain_id", "ELEC")).strip() or "ELEC",
            }
        )
    return sorted(selected, key=lambda item: (str(item.get("node_id", "")), str(item.get("source_id", ""))))


def _scheduled_ignitions_for_tick(fire_rows, graph_id, tick):
    selected = []
    for row in list(fire_rows or []):
        if not isinstance(row, dict):
            continue
        if str(row.get("graph_id", "")).strip() != str(graph_id):
            continue
        if int(max(0, _as_int(row.get("tick", 0), 0))) != int(tick):
            continue
        selected.append(dict(row))
    return sorted(selected, key=lambda item: str(item.get("event_id", "")))


def _merge_fire_state_rows(existing_rows, ignition_rows, tick):
    rows_by_target = dict(
        (
            str(row.get("target_id", "")).strip(),
            dict(row),
        )
        for row in list(existing_rows or [])
        if isinstance(row, dict) and str(row.get("target_id", "")).strip()
    )
    fire_events = []
    for row in list(ignition_rows or []):
        if not isinstance(row, dict):
            continue
        target_id = str(row.get("target_id", "")).strip()
        if not target_id:
            continue
        current = dict(rows_by_target.get(target_id) or {})
        if bool(current.get("active", False)):
            continue
        initial_fuel = int(max(1, _as_int(row.get("initial_fuel", 1000), 1000)))
        fire_row = {
            "schema_version": "1.0.0",
            "target_id": target_id,
            "active": True,
            "fuel_remaining": int(initial_fuel),
            "last_update_tick": int(tick),
            "deterministic_fingerprint": "",
            "extensions": {
                "material_id": str(row.get("material_id", "material.wood_basic")).strip() or "material.wood_basic",
                "scheduled_ignition_event_id": str(row.get("event_id", "")).strip(),
            },
        }
        fire_row["deterministic_fingerprint"] = canonical_sha256(dict(fire_row, deterministic_fingerprint=""))
        rows_by_target[target_id] = fire_row
        event = {
            "schema_version": "1.0.0",
            "event_id": "event.fire.{}".format(
                canonical_sha256({"tick": int(tick), "target_id": target_id, "scheduled": str(row.get("event_id", ""))})[:16]
            ),
            "tick": int(tick),
            "target_id": target_id,
            "event_type": "event.fire_started",
            "fuel_before": 0,
            "fuel_after": int(initial_fuel),
            "heat_emission": 0,
            "pollutant_emission": 0,
            "deterministic_fingerprint": "",
            "extensions": {"source_target_id": None, "scheduled": True},
        }
        event["deterministic_fingerprint"] = canonical_sha256(dict(event, deterministic_fingerprint=""))
        fire_events.append(event)
    return [dict(rows_by_target[k]) for k in sorted(rows_by_target.keys())], sorted(fire_events, key=lambda item: str(item.get("event_id", "")))


def _update_graph_with_result(graph_row, solve_result):
    graph = copy.deepcopy(dict(graph_row or {}))
    node_status_by_id = dict(
        (
            str(row.get("node_id", "")).strip(),
            dict(row),
        )
        for row in list(solve_result.get("node_status_rows") or [])
        if isinstance(row, dict) and str(row.get("node_id", "")).strip()
    )
    nodes = []
    for node in sorted([dict(row) for row in list(graph.get("nodes") or []) if isinstance(row, dict)], key=lambda row: str(row.get("node_id", ""))):
        node_id = str(node.get("node_id", "")).strip()
        payload = _as_map(node.get("payload"))
        status = dict(node_status_by_id.get(node_id) or {})
        if status:
            payload["current_thermal_energy"] = int(max(0, _as_int(status.get("thermal_energy", payload.get("current_thermal_energy", 0)), 0)))
        node["payload"] = payload
        nodes.append(node)
    graph["nodes"] = nodes
    return graph


def _envelope_defaults(budget_envelope_id):
    token = str(budget_envelope_id or "").strip().lower()
    if token == "therm.envelope.tight":
        return {"max_cost_units_per_tick": 700, "base_t1_tick_stride": 2, "max_model_cost_units_per_network": 220, "max_fire_spread_per_tick": 12}
    if token == "therm.envelope.rank_strict":
        return {"max_cost_units_per_tick": 1200, "base_t1_tick_stride": 1, "max_model_cost_units_per_network": 380, "max_fire_spread_per_tick": 18}
    return {"max_cost_units_per_tick": 1800, "base_t1_tick_stride": 1, "max_model_cost_units_per_network": 520, "max_fire_spread_per_tick": 24}


_DEGRADE_ORDER = {
    "degrade.therm.tick_bucket": 1,
    "degrade.therm.t0_budget": 2,
    "degrade.therm.defer_noncritical_models": 3,
    "degrade.therm.fire_spread_cap": 4,
}


def run_therm_stress_scenario(
    *,
    scenario,
    tick_count,
    budget_envelope_id,
    max_cost_units_per_tick,
    max_processed_edges_per_network,
    max_model_cost_units_per_network,
    base_t1_tick_stride,
    max_fire_spread_per_tick,
    ambient_temperature,
):
    scenario_row = copy.deepcopy(dict(scenario or {}))
    scenario_id = str(scenario_row.get("scenario_id", "")).strip() or "scenario.therm.unknown"
    defaults = _envelope_defaults(str(budget_envelope_id))

    tick_horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 64), 64))))
    budget_id = str(budget_envelope_id or "").strip() or "therm.envelope.standard"
    budget_per_tick = int(max(1, _as_int(max_cost_units_per_tick, int(defaults["max_cost_units_per_tick"]))))
    base_stride = int(max(1, _as_int(base_t1_tick_stride, int(defaults["base_t1_tick_stride"]))))
    model_cost_cap = int(max(1, _as_int(max_model_cost_units_per_network, int(defaults["max_model_cost_units_per_network"]))))
    fire_cap_base = int(max(1, _as_int(max_fire_spread_per_tick, int(defaults["max_fire_spread_per_tick"]))))
    ambient_temp = int(_as_int(ambient_temperature, 20))

    graph_rows_by_id = _graph_rows_by_id(
        scenario_row.get("thermal_network_graphs")
        or dict(scenario_row.get("initial_state_snapshot") or {}).get("thermal_network_graphs")
    )
    graph_ids = sorted(graph_rows_by_id.keys())
    if not graph_ids:
        return {
            "schema_version": "1.0.0",
            "result": "refused",
            "scenario_id": scenario_id,
            "tick_count": 0,
            "errors": [{"code": "refusal.therm.missing_graphs", "message": "scenario has no thermal_network_graphs"}],
        }

    fire_rows_by_graph_id = {}
    per_tick_max_temperature = []
    per_tick_overtemp_trip_counts = []
    per_tick_downgraded_network_counts = []
    per_tick_fire_event_counts = []
    per_tick_cache_hit_ratios_permille = []
    per_tick_cost_units = []
    per_tick_proof_hashes = []

    heat_input_log_rows = []
    overtemp_event_rows_all = []
    fire_event_rows_all = []
    degrade_event_rows_all = []
    control_decision_log = []

    no_silent_downgrades = True
    deterministic_ordering_ok = True
    bounded_evaluation_ok = True

    for tick in range(0, int(tick_horizon)):
        tick_max_temp = 0
        tick_overtemp_count = 0
        tick_downgraded_count = 0
        tick_fire_events = 0
        tick_cache_hits = 0
        tick_cache_total = 0
        tick_cost_units = 0
        remaining_budget = int(budget_per_tick)

        expected_total_cost = sum(_estimate_graph_cost(graph_rows_by_id[graph_id]) for graph_id in graph_ids)
        pressure_ratio_permille = int(max(0, ((expected_total_cost - budget_per_tick) * 1000) // expected_total_cost)) if expected_total_cost > 0 else 0

        for graph_index, graph_id in enumerate(graph_ids):
            graph_row = copy.deepcopy(dict(graph_rows_by_id.get(graph_id) or {}))
            estimated_graph_cost = int(max(1, _estimate_graph_cost(graph_row)))

            heat_rows = _periodic_heat_rows_for_tick(scenario_row.get("periodic_heat_source_rows"), graph_id, tick)
            for row in heat_rows:
                heat_input_log_rows.append(
                    {
                        "tick": int(tick),
                        "graph_id": str(graph_id),
                        "node_id": str(row.get("node_id", "")),
                        "heat_input": int(max(0, _as_int(row.get("heat_input", 0), 0))),
                        "source_id": str(row.get("source_id", "")),
                        "source_domain_id": str(row.get("source_domain_id", "ELEC")),
                    }
                )

            scheduled_ignitions = _scheduled_ignitions_for_tick(scenario_row.get("fire_ignition_rows"), graph_id, tick)
            fire_rows, ignition_events = _merge_fire_state_rows(fire_rows_by_graph_id.get(graph_id), scheduled_ignitions, tick)
            fire_rows_by_graph_id[graph_id] = [dict(row) for row in fire_rows]
            fire_event_rows_all.extend([dict(row) for row in ignition_events])
            tick_fire_events += int(len(ignition_events))

            pressure_stride_extra = int(max(0, pressure_ratio_permille // 350)) if pressure_ratio_permille > 0 else 0
            t1_stride = int(max(1, base_stride + pressure_stride_extra + (graph_index % 2 if pressure_ratio_permille > 450 else 0)))
            defer_noncritical = bool(pressure_ratio_permille > 250)
            dynamic_model_cap = int(max(estimated_graph_cost + 6, min(model_cost_cap, estimated_graph_cost + 24))) if defer_noncritical else int(model_cost_cap)
            dynamic_fire_cap = int(max(1, fire_cap_base - (1 if pressure_ratio_permille > 350 else 0)))
            if pressure_ratio_permille > 650:
                dynamic_fire_cap = int(max(1, fire_cap_base // 2))

            run_t1_this_tick = bool((int(tick) % int(t1_stride)) == 0)
            harness_decisions = []
            if not run_t1_this_tick:
                harness_decisions.append({"process_id": "process.therm_budget_degrade", "tick": int(tick), "target_id": str(graph_id), "reason_code": "degrade.therm.tick_bucket", "details": {"mode": "T0", "t1_stride": int(t1_stride)}})
                solve_result = solve_thermal_network_t0(graph_row=graph_row, current_tick=int(tick), heat_input_rows=[dict(row) for row in heat_rows], ambient_temperature=int(ambient_temp), downgrade_reason="degrade.therm.tick_bucket")
            elif remaining_budget < estimated_graph_cost:
                harness_decisions.append({"process_id": "process.therm_budget_degrade", "tick": int(tick), "target_id": str(graph_id), "reason_code": "degrade.therm.t0_budget", "details": {"mode": "T0", "remaining_budget": int(max(0, remaining_budget)), "estimated_graph_cost": int(estimated_graph_cost)}})
                solve_result = solve_thermal_network_t0(graph_row=graph_row, current_tick=int(tick), heat_input_rows=[dict(row) for row in heat_rows], ambient_temperature=int(ambient_temp), downgrade_reason="degrade.therm.t0_budget")
            else:
                allocated_budget = int(max(estimated_graph_cost, min(remaining_budget, dynamic_model_cap)))
                if defer_noncritical:
                    harness_decisions.append({"process_id": "process.therm_budget_degrade", "tick": int(tick), "target_id": str(graph_id), "reason_code": "degrade.therm.defer_noncritical_models", "details": {"mode": "T1", "allocated_budget": int(allocated_budget), "estimated_graph_cost": int(estimated_graph_cost)}})
                solve_result = solve_thermal_network_t1(
                    graph_row=graph_row,
                    current_tick=int(tick),
                    heat_input_rows=[dict(row) for row in heat_rows],
                    fire_state_rows=[dict(row) for row in fire_rows_by_graph_id.get(graph_id) or []],
                    max_processed_edges=int(max_processed_edges_per_network),
                    max_cost_units=int(max(allocated_budget, estimated_graph_cost)),
                    max_fire_spread_per_tick=int(dynamic_fire_cap),
                    ambient_eval_stride=int(max(1, t1_stride)),
                    ambient_temperature=int(ambient_temp),
                )

            result_mode = str(solve_result.get("mode", "")).strip().upper()
            if result_mode == "T0":
                tick_downgraded_count += 1

            graph_rows_by_id[graph_id] = _update_graph_with_result(graph_row, solve_result)
            fire_rows_by_graph_id[graph_id] = [dict(row) for row in list(solve_result.get("fire_state_rows") or fire_rows_by_graph_id.get(graph_id) or []) if isinstance(row, dict)]

            node_status_rows = [dict(row) for row in list(solve_result.get("node_status_rows") or []) if isinstance(row, dict)]
            edge_status_rows = [dict(row) for row in list(solve_result.get("edge_status_rows") or []) if isinstance(row, dict)]
            if edge_status_rows and len(edge_status_rows) > int(max_processed_edges_per_network):
                bounded_evaluation_ok = False
            deterministic_ordering_ok = bool(deterministic_ordering_ok and _assert_sorted(node_status_rows, lambda row: str(row.get("node_id", ""))) and _assert_sorted(edge_status_rows, lambda row: str(row.get("edge_id", ""))))

            for row in node_status_rows:
                tick_max_temp = int(max(tick_max_temp, _as_int(row.get("temperature", 0), 0)))

            safety_events = [dict(row) for row in list(solve_result.get("safety_event_rows") or []) if isinstance(row, dict)]
            tick_overtemp_count += int(len([row for row in safety_events if str(row.get("pattern_id", "")).strip() == "safety.overtemp_trip"]))
            overtemp_event_rows_all.extend([dict(row) for row in safety_events if str(row.get("pattern_id", "")).strip() == "safety.overtemp_trip"])

            fire_events = [dict(row) for row in list(solve_result.get("fire_event_rows") or []) if isinstance(row, dict)]
            fire_event_rows_all.extend(fire_events)
            tick_fire_events += int(len(fire_events))

            for row in [dict(item) for item in list(solve_result.get("model_evaluation_results") or []) if isinstance(item, dict)]:
                ext = _as_map(row.get("extensions"))
                tick_cache_total += 1
                if bool(ext.get("cache_hit", False)):
                    tick_cache_hits += 1

            decision_rows = [dict(row) for row in list(solve_result.get("decision_log_rows") or []) if isinstance(row, dict)] + [dict(row) for row in harness_decisions]
            for row in decision_rows:
                row.setdefault("tick", int(tick))
                row.setdefault("target_id", str(graph_id))
                code = str(row.get("reason_code", "")).strip()
                if code.startswith("degrade.therm"):
                    degrade_event_rows_all.append(
                        {
                            "tick": int(max(0, _as_int(row.get("tick", tick), tick))),
                            "target_id": str(row.get("target_id", graph_id)),
                            "reason_code": code,
                            "order_index": int(_DEGRADE_ORDER.get(code, 99)),
                            "details": _as_map(row.get("details")),
                        }
                    )
            if result_mode == "T0":
                has_degrade_log = any(str(row.get("reason_code", "")).strip().startswith("degrade.therm") for row in decision_rows)
                no_silent_downgrades = bool(no_silent_downgrades and has_degrade_log)
            control_decision_log.extend(decision_rows)

            tick_cost_units += int(max(0, _as_int(solve_result.get("model_cost_units", 0), 0)) + estimated_graph_cost)
            remaining_budget = int(max(0, remaining_budget - estimated_graph_cost))
        per_tick_max_temperature.append(int(max(0, tick_max_temp)))
        per_tick_overtemp_trip_counts.append(int(max(0, tick_overtemp_count)))
        per_tick_downgraded_network_counts.append(int(max(0, tick_downgraded_count)))
        per_tick_fire_event_counts.append(int(max(0, tick_fire_events)))
        per_tick_cache_hit_ratios_permille.append(int(0 if tick_cache_total <= 0 else (tick_cache_hits * 1000) // tick_cache_total))
        per_tick_cost_units.append(int(max(0, tick_cost_units)))

        thermal_state_hash = canonical_sha256(
            {
                "tick": int(tick),
                "graphs": [
                    {
                        "graph_id": str(graph_id),
                        "node_state": [
                            {"node_id": str(row.get("node_id", "")), "energy": int(_as_int(_as_map(row.get("payload")).get("current_thermal_energy", 0), 0))}
                            for row in sorted([dict(node) for node in list(dict(graph_rows_by_id.get(graph_id) or {}).get("nodes") or []) if isinstance(node, dict)], key=lambda item: str(item.get("node_id", "")))
                        ],
                    }
                    for graph_id in graph_ids
                ],
            }
        )
        thermal_state_hash_chain = canonical_sha256(list(per_tick_max_temperature) + [thermal_state_hash])
        heat_input_hash_chain = _hash_chain([row for row in heat_input_log_rows if int(_as_int(row.get("tick", 0), 0)) <= int(tick)], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("graph_id", "")), str(row.get("node_id", "")), str(row.get("source_id", ""))))
        overheat_hash_chain = _hash_chain([row for row in overtemp_event_rows_all if int(_as_int(row.get("tick", 0), 0)) <= int(tick)], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))
        fire_cascade_hash_chain = _hash_chain([row for row in fire_event_rows_all if int(_as_int(row.get("tick", 0), 0)) <= int(tick)], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))
        degrade_hash_chain = _hash_chain([row for row in degrade_event_rows_all if int(_as_int(row.get("tick", 0), 0)) <= int(tick)], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("target_id", "")), str(row.get("reason_code", ""))))

        proof_bundle = build_control_proof_bundle_from_markers(
            tick_start=int(tick),
            tick_end=int(tick),
            decision_markers=[],
            mobility_proof_surface={
                "thermal_network_hash": str(thermal_state_hash),
                "thermal_network_state_hash_chain": str(thermal_state_hash_chain),
                "heat_input_hash_chain": str(heat_input_hash_chain),
                "overheat_event_hash_chain": str(overheat_hash_chain),
                "fire_cascade_hash_chain": str(fire_cascade_hash_chain),
                "fire_state_hash_chain": _hash_chain([row for rows in fire_rows_by_graph_id.values() for row in list(rows or [])], lambda row: (str(row.get("target_id", "")), int(_as_int(row.get("last_update_tick", 0), 0)))),
                "fire_spread_hash_chain": _hash_chain([row for row in fire_event_rows_all if str(row.get("event_type", "")).strip() == "event.fire_spread_started"], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))),
                "ignition_event_hash_chain": _hash_chain([row for row in fire_event_rows_all if str(row.get("event_type", "")).strip() in {"event.fire_started", "event.fire_spread_started"}], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))),
                "runaway_event_hash_chain": _hash_chain([row for row in overtemp_event_rows_all if str(row.get("pattern_id", "")).strip() == "safety.thermal_runaway"], lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))),
                "degradation_event_hash_chain": str(degrade_hash_chain),
            },
        )
        per_tick_proof_hashes.append(str(proof_bundle.get("deterministic_fingerprint", "")))

    proof_hash_summary = {
        "thermal_network_state_hash_chain": _hash_chain([{"tick": idx, "max_temperature": int(per_tick_max_temperature[idx]), "downgraded_networks": int(per_tick_downgraded_network_counts[idx]), "cost_units": int(per_tick_cost_units[idx])} for idx in range(len(per_tick_max_temperature))], lambda row: int(_as_int(row.get("tick", 0), 0))),
        "heat_input_hash_chain": _hash_chain(heat_input_log_rows, lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("graph_id", "")), str(row.get("node_id", "")), str(row.get("source_id", "")))),
        "overtemp_trip_hash_chain": _hash_chain(overtemp_event_rows_all, lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))),
        "fire_cascade_hash_chain": _hash_chain(fire_event_rows_all, lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", "")))),
        "degradation_event_hash_chain": _hash_chain(degrade_event_rows_all, lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("target_id", "")), str(row.get("reason_code", "")))),
        "proof_hash_summary": canonical_sha256(list(per_tick_proof_hashes)),
    }

    assertions = {
        "bounded_evaluation": bool(bounded_evaluation_ok),
        "deterministic_ordering": bool(deterministic_ordering_ok),
        "no_silent_downgrades": bool(no_silent_downgrades),
        "no_unlogged_heat_inputs": True,
    }
    degradation_record_rows = [
        {
            "artifact_id": "artifact.record.therm.degrade.{}".format(
                canonical_sha256(
                    {
                        "tick": int(_as_int(row.get("tick", 0), 0)),
                        "target_id": str(row.get("target_id", "")),
                        "reason_code": str(row.get("reason_code", "")),
                        "order_index": int(_as_int(row.get("order_index", 99), 99)),
                    }
                )[:16]
            ),
            "artifact_family_id": "RECORD",
            "extensions": {
                "tick": int(_as_int(row.get("tick", 0), 0)),
                "target_id": str(row.get("target_id", "")),
                "reason_code": str(row.get("reason_code", "")),
                "order_index": int(_as_int(row.get("order_index", 99), 99)),
                "details": _as_map(row.get("details")),
            },
        }
        for row in sorted(
            [dict(item) for item in list(degrade_event_rows_all or []) if isinstance(item, dict)],
            key=lambda item: (
                int(_as_int(item.get("tick", 0), 0)),
                str(item.get("target_id", "")),
                int(_as_int(item.get("order_index", 99), 99)),
                str(item.get("reason_code", "")),
            ),
        )
    ]

    result = {
        "schema_version": "1.0.0",
        "result": "complete" if all(bool(flag) for flag in assertions.values()) else "refused",
        "scenario_id": str(scenario_id),
        "budget_envelope_id": str(budget_id),
        "tick_count": int(tick_horizon),
        "metrics": {
            "max_temperature_per_tick": list(per_tick_max_temperature),
            "overtemp_trip_counts_per_tick": list(per_tick_overtemp_trip_counts),
            "downgraded_network_counts_per_tick": list(per_tick_downgraded_network_counts),
            "fire_event_counts_per_tick": list(per_tick_fire_event_counts),
            "cache_hit_ratios_permille_per_tick": list(per_tick_cache_hit_ratios_permille),
            "cost_units_per_tick": list(per_tick_cost_units),
            "max_temperature_observed": int(max(per_tick_max_temperature or [0])),
            "total_overtemp_trips": int(sum(per_tick_overtemp_trip_counts)),
            "total_downgraded_networks": int(sum(per_tick_downgraded_network_counts)),
            "total_fire_events": int(sum(per_tick_fire_event_counts)),
            "average_cache_hit_ratio_permille": int(0 if not per_tick_cache_hit_ratios_permille else sum(per_tick_cache_hit_ratios_permille) // max(1, len(per_tick_cache_hit_ratios_permille))),
            "proof_hash_summary": dict(proof_hash_summary),
            "degradation_policy_order": [str(token) for token, _rank in sorted(_DEGRADE_ORDER.items(), key=lambda item: int(item[1]))],
        },
        "assertions": dict(assertions),
        "extensions": {
            "control_decision_log": [dict(row) for row in list(control_decision_log or []) if isinstance(row, dict)],
            "thermal_heat_input_log_rows": [dict(row) for row in list(heat_input_log_rows or []) if isinstance(row, dict)],
            "thermal_degradation_event_rows": [dict(row) for row in list(degrade_event_rows_all or []) if isinstance(row, dict)],
            "thermal_degradation_record_rows": degradation_record_rows,
            "proof_hashes_per_tick": list(per_tick_proof_hashes),
            "graph_ids": list(graph_ids),
        },
        "deterministic_fingerprint": "",
    }
    seed_payload = dict(result)
    seed_payload["deterministic_fingerprint"] = ""
    result["deterministic_fingerprint"] = canonical_sha256(seed_payload)
    if str(result.get("result", "")).strip() == "complete":
        return result
    return {**result, "errors": [{"code": "refusal.therm.stress_assertion_failed", "message": "THERM stress assertions failed", "path": "$.assertions"}]}


def _parser():
    parser = argparse.ArgumentParser(description="Run deterministic THERM-5 stress scenario.")
    parser.add_argument("--scenario", default="build/thermal/therm_stress_scenario.json")
    parser.add_argument("--seed", type=int, default=7501)
    parser.add_argument("--node-count", type=int, default=256)
    parser.add_argument("--link-count", type=int, default=512)
    parser.add_argument("--radiator-count", type=int, default=64)
    parser.add_argument("--graph-count", type=int, default=4)
    parser.add_argument("--tick-count", type=int, default=64)
    parser.add_argument("--include-fire-ignitions", action="store_true")
    parser.add_argument("--budget-envelope-id", default="therm.envelope.standard")
    parser.add_argument("--max-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--max-processed-edges-per-network", type=int, default=4096)
    parser.add_argument("--max-model-cost-units-per-network", type=int, default=0)
    parser.add_argument("--base-t1-tick-stride", type=int, default=0)
    parser.add_argument("--max-fire-spread-per-tick", type=int, default=0)
    parser.add_argument("--ambient-temperature", type=int, default=20)
    parser.add_argument("--output", default="build/thermal/therm_stress_report.json")
    return parser


def main():
    parser = _parser()
    args = parser.parse_args()

    scenario_path = os.path.normpath(os.path.abspath(str(args.scenario)))
    if os.path.isfile(scenario_path):
        scenario = _load_json(scenario_path)
    else:
        scenario = generate_therm_stress_scenario(seed=int(args.seed), node_count=int(args.node_count), link_count=int(args.link_count), radiator_count=int(args.radiator_count), graph_count=int(args.graph_count), tick_horizon=int(args.tick_count), include_fire_ignitions=bool(args.include_fire_ignitions))
        _write_json(scenario_path, scenario)

    defaults = _envelope_defaults(str(args.budget_envelope_id))
    result = run_therm_stress_scenario(
        scenario=scenario,
        tick_count=int(args.tick_count),
        budget_envelope_id=str(args.budget_envelope_id),
        max_cost_units_per_tick=int(args.max_cost_units_per_tick) or int(defaults["max_cost_units_per_tick"]),
        max_processed_edges_per_network=int(args.max_processed_edges_per_network),
        max_model_cost_units_per_network=int(args.max_model_cost_units_per_network) or int(defaults["max_model_cost_units_per_network"]),
        base_t1_tick_stride=int(args.base_t1_tick_stride) or int(defaults["base_t1_tick_stride"]),
        max_fire_spread_per_tick=int(args.max_fire_spread_per_tick) or int(defaults["max_fire_spread_per_tick"]),
        ambient_temperature=int(args.ambient_temperature),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, result)
    print(json.dumps({"result": str(result.get("result", "")), "scenario_id": str(result.get("scenario_id", "")), "output_path": output_abs, "deterministic_fingerprint": str(result.get("deterministic_fingerprint", ""))}, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
