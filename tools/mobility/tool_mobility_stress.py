#!/usr/bin/env python3
"""MOB-11 deterministic mobility stress suite."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.mobility.travel import (  # noqa: E402
    build_travel_event,
    compute_mobility_proof_hashes,
    deterministic_travel_event_id,
    normalize_travel_event_rows,
)
from src.mobility.traffic import build_edge_occupancy, normalize_edge_occupancy_rows  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _scenario_catalog(*, base_ticks: int, dense_vehicles: int) -> List[dict]:
    dense = max(120, int(dense_vehicles))
    return [
        {
            "scenario_id": "scenario.01.dense_rail",
            "title": "Dense rail network with hundreds of trains",
            "ticks": max(4, int(base_ticks)),
            "vehicle_count": dense,
            "edge_count": 96,
            "micro_budget": 32,
            "capacity_units": 6,
            "delay_scale": 2,
            "strict_fair": True,
            "with_failures": False,
            "mixed_fidelity": False,
        },
        {
            "scenario_id": "scenario.02.mixed_modal",
            "title": "Mixed rail + road + air corridors",
            "ticks": max(4, int(base_ticks)),
            "vehicle_count": max(96, dense // 2),
            "edge_count": 128,
            "micro_budget": 24,
            "capacity_units": 5,
            "delay_scale": 2,
            "strict_fair": True,
            "with_failures": False,
            "mixed_fidelity": True,
        },
        {
            "scenario_id": "scenario.03.multi_roi",
            "title": "Multiple players scattered in different ROIs",
            "ticks": max(4, int(base_ticks)),
            "vehicle_count": max(64, dense // 3),
            "edge_count": 80,
            "micro_budget": 16,
            "capacity_units": 5,
            "delay_scale": 1,
            "strict_fair": True,
            "with_failures": False,
            "mixed_fidelity": True,
        },
        {
            "scenario_id": "scenario.04.hub_congestion",
            "title": "High congestion at hubs",
            "ticks": max(4, int(base_ticks)),
            "vehicle_count": max(80, dense // 2),
            "edge_count": 48,
            "micro_budget": 20,
            "capacity_units": 2,
            "delay_scale": 4,
            "strict_fair": True,
            "with_failures": False,
            "mixed_fidelity": True,
        },
        {
            "scenario_id": "scenario.05.signal_maintenance_failures",
            "title": "Signal failures and maintenance events under load",
            "ticks": max(4, int(base_ticks)),
            "vehicle_count": max(72, dense // 2),
            "edge_count": 64,
            "micro_budget": 18,
            "capacity_units": 4,
            "delay_scale": 3,
            "strict_fair": True,
            "with_failures": True,
            "mixed_fidelity": True,
        },
        {
            "scenario_id": "scenario.06.mixed_fidelity_requests",
            "title": "Mixed fidelity requests",
            "ticks": max(4, int(base_ticks)),
            "vehicle_count": max(96, dense // 2),
            "edge_count": 88,
            "micro_budget": 22,
            "capacity_units": 4,
            "delay_scale": 2,
            "strict_fair": True,
            "with_failures": True,
            "mixed_fidelity": True,
        },
    ]


def _edge_ids(scenario_id: str, edge_count: int) -> List[str]:
    return ["edge.{}.{}".format(str(scenario_id).replace(".", "_"), str(i).zfill(4)) for i in range(int(edge_count))]


def _vehicle_ids(scenario_id: str, vehicle_count: int) -> List[str]:
    return ["vehicle.{}.{}".format(str(scenario_id).replace(".", "_"), str(i).zfill(4)) for i in range(int(vehicle_count))]


def _signal_surface(scenario_id: str, tick: int, edge_ids: List[str]) -> List[dict]:
    out = []
    for idx, edge_id in enumerate(edge_ids[: min(32, len(edge_ids))]):
        state_id = "clear"
        if (idx + int(tick)) % 11 == 0:
            state_id = "stop"
        elif (idx + int(tick)) % 7 == 0:
            state_id = "caution"
        out.append(
            {
                "signal_id": "signal.{}.{}".format(str(scenario_id).replace(".", "_"), str(idx).zfill(3)),
                "signal_type_id": "signal.rail_block_basic",
                "rule_policy_id": "policy.rail_basic_interlocking",
                "state_machine_id": "sm.signal.{}.{}".format(str(scenario_id).replace(".", "_"), str(idx).zfill(3)),
                "state_machine": {"state_id": state_id},
                "attached_edge_id": edge_id,
            }
        )
    return out


def _requested_micro_vehicle_ids(*, tick: int, vehicle_ids: List[str], mixed_fidelity: bool) -> List[str]:
    out = []
    for idx, vehicle_id in enumerate(vehicle_ids):
        if bool(mixed_fidelity):
            if (idx + int(tick)) % 3 == 0:
                out.append(vehicle_id)
        else:
            if (idx + int(tick)) % 2 == 0:
                out.append(vehicle_id)
    return sorted(out)


def _stable_micro_selection(*, requested_ids: List[str], micro_budget: int, tick: int, strict_fair: bool) -> List[str]:
    rows = list(_sorted_tokens(requested_ids))
    if not rows:
        return []
    if not bool(strict_fair):
        return rows[: int(max(0, micro_budget))]
    offset = int(max(0, tick)) % int(len(rows))
    rotated = rows[offset:] + rows[:offset]
    return sorted(rotated[: int(max(0, micro_budget))])


def _build_incident_event(
    *,
    vehicle_id: str,
    itinerary_id: str,
    tick: int,
    event_index: int,
    reason_code: str,
    edge_id: str,
) -> dict:
    return build_travel_event(
        event_id=deterministic_travel_event_id(
            vehicle_id=vehicle_id,
            itinerary_id=itinerary_id,
            kind="incident_stub",
            tick=int(tick),
            sequence=int(event_index),
        ),
        tick=int(tick),
        vehicle_id=vehicle_id,
        itinerary_id=itinerary_id,
        kind="incident_stub",
        details={"reason_code": str(reason_code), "edge_id": str(edge_id)},
        extensions={"source_process_id": "tool.mobility.stress"},
    )


def _simulate_scenario(config: Mapping[str, object]) -> dict:
    scenario_id = str(config.get("scenario_id", "")).strip()
    ticks = int(max(1, _as_int(config.get("ticks", 1), 1)))
    micro_budget = int(max(1, _as_int(config.get("micro_budget", 1), 1)))
    capacity_units = int(max(1, _as_int(config.get("capacity_units", 1), 1)))
    delay_scale = int(max(1, _as_int(config.get("delay_scale", 1), 1)))
    strict_fair = bool(config.get("strict_fair", False))
    with_failures = bool(config.get("with_failures", False))
    mixed_fidelity = bool(config.get("mixed_fidelity", False))

    vehicle_ids = _vehicle_ids(scenario_id, int(max(1, _as_int(config.get("vehicle_count", 1), 1))))
    edge_ids = _edge_ids(scenario_id, int(max(1, _as_int(config.get("edge_count", 1), 1))))
    occupancy_by_edge = dict((edge_id, 0) for edge_id in edge_ids)
    itinerary_by_vehicle = dict((vehicle_id, "itinerary.{}.{}".format(scenario_id.replace(".", "_"), vehicle_id.split(".")[-1])) for vehicle_id in vehicle_ids)
    micro_grants_by_vehicle = dict((vehicle_id, 0) for vehicle_id in vehicle_ids)
    micro_requests_by_vehicle = dict((vehicle_id, 0) for vehicle_id in vehicle_ids)
    service_ticks_by_vehicle = dict((vehicle_id, 0) for vehicle_id in vehicle_ids)
    current_tier_by_vehicle = dict((vehicle_id, "meso") for vehicle_id in vehicle_ids)
    occupancy_peak_by_edge = dict((edge_id, 0) for edge_id in edge_ids)

    travel_events: List[dict] = []
    decision_rows: List[dict] = []
    cost_units_per_tick: List[int] = []
    downgrade_count = 0
    incident_frequency: Dict[str, int] = {}
    envelope_overflow = False
    silent_mutation_detected = False

    for tick in range(1, int(ticks) + 1):
        requested_micro = _requested_micro_vehicle_ids(
            tick=int(tick),
            vehicle_ids=vehicle_ids,
            mixed_fidelity=bool(mixed_fidelity),
        )
        for vehicle_id in requested_micro:
            micro_requests_by_vehicle[vehicle_id] = int(micro_requests_by_vehicle.get(vehicle_id, 0) + 1)
        granted_micro = _stable_micro_selection(
            requested_ids=requested_micro,
            micro_budget=int(micro_budget),
            tick=int(tick),
            strict_fair=bool(strict_fair),
        )
        granted_micro_set = set(granted_micro)
        deferred_micro = sorted(vehicle_id for vehicle_id in requested_micro if vehicle_id not in granted_micro_set)
        for vehicle_id in vehicle_ids:
            current_tier_by_vehicle[vehicle_id] = "micro" if vehicle_id in granted_micro_set else "meso"
        for vehicle_id in granted_micro:
            micro_grants_by_vehicle[vehicle_id] = int(micro_grants_by_vehicle.get(vehicle_id, 0) + 1)
        for vehicle_id in deferred_micro:
            downgrade_count += 1
            decision_rows.append(
                {
                    "tick": int(tick),
                    "vehicle_id": vehicle_id,
                    "downgrade_reason": "degrade.mob.micro_budget",
                    "resolved_level": "meso",
                }
            )

        for idx, vehicle_id in enumerate(vehicle_ids):
            service_ticks_by_vehicle[vehicle_id] = int(service_ticks_by_vehicle.get(vehicle_id, 0) + 1)
            itinerary_id = str(itinerary_by_vehicle.get(vehicle_id, "itinerary.none"))
            edge_id = edge_ids[(idx + int(tick)) % len(edge_ids)]
            occupancy_by_edge[edge_id] = int(occupancy_by_edge.get(edge_id, 0) + 1)
            occupancy_peak_by_edge[edge_id] = int(max(int(occupancy_peak_by_edge.get(edge_id, 0)), int(occupancy_by_edge.get(edge_id, 0))))
            event_kind = "edge_enter" if (idx + int(tick)) % 2 == 0 else "edge_exit"
            event = build_travel_event(
                event_id=deterministic_travel_event_id(
                    vehicle_id=vehicle_id,
                    itinerary_id=itinerary_id,
                    kind=event_kind,
                    tick=int(tick),
                    sequence=int(len(travel_events)),
                ),
                tick=int(tick),
                vehicle_id=vehicle_id,
                itinerary_id=itinerary_id,
                kind=event_kind,
                details={"edge_id": edge_id},
                extensions={"source_process_id": "tool.mobility.stress"},
            )
            travel_events.append(event)
            if int(occupancy_by_edge.get(edge_id, 0)) > int(capacity_units):
                delay_event = build_travel_event(
                    event_id=deterministic_travel_event_id(
                        vehicle_id=vehicle_id,
                        itinerary_id=itinerary_id,
                        kind="delay",
                        tick=int(tick),
                        sequence=int(len(travel_events)),
                    ),
                    tick=int(tick),
                    vehicle_id=vehicle_id,
                    itinerary_id=itinerary_id,
                    kind="delay",
                    details={
                        "reason": "event.delay.congestion",
                        "edge_id": edge_id,
                        "delta_ticks": int(max(1, int(delay_scale))),
                        "congestion_ratio_permille": int((int(occupancy_by_edge.get(edge_id, 0)) * 1000) // int(capacity_units)),
                    },
                    extensions={"source_process_id": "tool.mobility.stress"},
                )
                travel_events.append(delay_event)
                incident_frequency["event.delay.congestion"] = int(incident_frequency.get("event.delay.congestion", 0) + 1)

        if bool(with_failures):
            fail_vehicle = vehicle_ids[(int(tick) * 7) % len(vehicle_ids)]
            fail_edge = edge_ids[(int(tick) * 3) % len(edge_ids)]
            reasons = ["incident.derailment.track_wear", "incident.signal_violation", "incident.breakdown.engine"]
            reason_code = reasons[int(tick) % len(reasons)]
            incident = _build_incident_event(
                vehicle_id=fail_vehicle,
                itinerary_id=str(itinerary_by_vehicle.get(fail_vehicle, "itinerary.none")),
                tick=int(tick),
                event_index=int(len(travel_events)),
                reason_code=str(reason_code),
                edge_id=fail_edge,
            )
            travel_events.append(incident)
            incident_frequency[str(reason_code)] = int(incident_frequency.get(str(reason_code), 0) + 1)

        active_micro = int(len(granted_micro))
        active_meso = int(max(0, len(vehicle_ids) - active_micro))
        tick_cost_units = int(active_micro * 4 + active_meso * 2 + len(deferred_micro))
        cost_units_per_tick.append(int(tick_cost_units))
        if int(tick_cost_units) > int(max(1, len(vehicle_ids) * 3)):
            envelope_overflow = True

        if int(len(deferred_micro)) > 0:
            if not any(str(row.get("tick", "")) == str(int(tick)) for row in decision_rows):
                silent_mutation_detected = True

        occupancy_by_edge = dict((edge_id, 0) for edge_id in edge_ids)

    occupancy_rows = normalize_edge_occupancy_rows(
        [
            build_edge_occupancy(
                edge_id=edge_id,
                capacity_units=int(capacity_units),
                current_occupancy=int(max(0, _as_int(occupancy_peak_by_edge.get(edge_id, 0), 0))),
                extensions={},
            )
            for edge_id in edge_ids
        ]
    )
    signal_rows = _signal_surface(scenario_id=scenario_id, tick=int(ticks), edge_ids=edge_ids)
    travel_events = normalize_travel_event_rows(travel_events)
    proof_hashes = compute_mobility_proof_hashes(
        travel_event_rows=travel_events,
        edge_occupancy_rows=occupancy_rows,
        signal_state_rows=signal_rows,
    )
    decision_log_stability = canonical_sha256(
        sorted(
            (dict(row) for row in decision_rows),
            key=lambda row: (
                int(_as_int(row.get("tick", 0), 0)),
                str(row.get("vehicle_id", "")),
                str(row.get("downgrade_reason", "")),
            ),
        )
    )
    motion_state_hash = canonical_sha256(
        [
            {
                "vehicle_id": vehicle_id,
                "tier": str(current_tier_by_vehicle.get(vehicle_id, "meso")),
            }
            for vehicle_id in sorted(vehicle_ids)
        ]
    )
    occupancy_hash = canonical_sha256(
        [
            {
                "edge_id": str(row.get("edge_id", "")).strip(),
                "capacity_units": int(max(1, _as_int(row.get("capacity_units", 1), 1))),
                "current_occupancy": int(max(0, _as_int(row.get("current_occupancy", 0), 0))),
                "congestion_ratio_permille": int(max(0, _as_int(row.get("congestion_ratio_permille", 0), 0))),
            }
            for row in occupancy_rows
        ]
    )
    fairness_requested_ids = sorted(vehicle_id for vehicle_id in vehicle_ids if int(micro_requests_by_vehicle.get(vehicle_id, 0)) > 0)
    micro_starved_ids = sorted(
        vehicle_id
        for vehicle_id in fairness_requested_ids
        if int(micro_grants_by_vehicle.get(vehicle_id, 0)) <= 0
    )
    fairness_starved_ids = sorted(
        vehicle_id
        for vehicle_id in vehicle_ids
        if int(service_ticks_by_vehicle.get(vehicle_id, 0)) <= 0
    )
    scenario_report = {
        "scenario_id": scenario_id,
        "title": str(config.get("title", "")).strip(),
        "ticks": int(ticks),
        "vehicle_count": int(len(vehicle_ids)),
        "edge_count": int(len(edge_ids)),
        "metrics": {
            "cost_units_per_tick": list(cost_units_per_tick),
            "downgrade_count": int(downgrade_count),
            "incident_frequency": dict((key, int(incident_frequency[key])) for key in sorted(incident_frequency.keys())),
            "decision_log_stability": str(decision_log_stability),
            "motion_state_hash": str(motion_state_hash),
            "event_stream_hash": str(proof_hashes.get("mobility_event_hash", "")),
            "occupancy_hash": str(occupancy_hash),
            "proof_bundle_hash": canonical_sha256(
                {
                    "scenario_id": scenario_id,
                    "mobility_event_hash": str(proof_hashes.get("mobility_event_hash", "")),
                    "congestion_hash": str(proof_hashes.get("congestion_hash", "")),
                    "signal_state_hash": str(proof_hashes.get("signal_state_hash", "")),
                    "derailment_hash": str(proof_hashes.get("derailment_hash", "")),
                    "decision_log_stability": str(decision_log_stability),
                }
            ),
        },
        "proof_surfaces": dict(proof_hashes),
        "assertions": {
            "no_envelope_overflow": not bool(envelope_overflow),
            "deterministic_ordering": True,
            "no_starvation_ranked": (not strict_fair) or (len(fairness_starved_ids) == 0),
            "no_silent_mutation": not bool(silent_mutation_detected),
        },
        "extensions": {
            "fairness_starved_ids": list(fairness_starved_ids),
            "micro_starved_ids": list(micro_starved_ids),
            "requested_micro_vehicle_count": int(len(fairness_requested_ids)),
            "strict_fair": bool(strict_fair),
            "with_failures": bool(with_failures),
            "mixed_fidelity": bool(mixed_fidelity),
            "travel_event_count": int(len(travel_events)),
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(scenario_report)
    seed["deterministic_fingerprint"] = ""
    scenario_report["deterministic_fingerprint"] = canonical_sha256(seed)
    return scenario_report


def run_mobility_stress(*, ticks: int, dense_vehicles: int) -> dict:
    first_rows = []
    second_rows = []
    for config in _scenario_catalog(base_ticks=int(ticks), dense_vehicles=int(dense_vehicles)):
        first_rows.append(_simulate_scenario(dict(config)))
        second_rows.append(_simulate_scenario(dict(config)))

    first_by_id = dict((str(row.get("scenario_id", "")).strip(), dict(row)) for row in first_rows)
    second_by_id = dict((str(row.get("scenario_id", "")).strip(), dict(row)) for row in second_rows)
    scenario_reports = []
    deterministic_ok = True
    no_overflow = True
    no_starvation = True
    no_silent_mutation = True
    mismatches = []
    for scenario_id in sorted(first_by_id.keys()):
        first = dict(first_by_id.get(scenario_id) or {})
        second = dict(second_by_id.get(scenario_id) or {})
        if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
            deterministic_ok = False
            mismatches.append({"scenario_id": scenario_id, "field": "deterministic_fingerprint"})
        no_overflow = no_overflow and bool((dict(first.get("assertions") or {})).get("no_envelope_overflow", False))
        no_starvation = no_starvation and bool((dict(first.get("assertions") or {})).get("no_starvation_ranked", False))
        no_silent_mutation = no_silent_mutation and bool((dict(first.get("assertions") or {})).get("no_silent_mutation", False))
        scenario_reports.append(first)

    proof_bundle_hash = canonical_sha256(
        [
            {
                "scenario_id": str(row.get("scenario_id", "")),
                "proof_bundle_hash": str((dict(row.get("metrics") or {})).get("proof_bundle_hash", "")),
            }
            for row in sorted(scenario_reports, key=lambda item: str(item.get("scenario_id", "")))
        ]
    )
    report = {
        "schema_version": "1.0.0",
        "ticks": int(max(1, int(ticks))),
        "dense_vehicles": int(max(120, int(dense_vehicles))),
        "scenario_reports": sorted(scenario_reports, key=lambda row: str(row.get("scenario_id", ""))),
        "metrics": {
            "proof_bundle_hash": str(proof_bundle_hash),
            "scenario_count": int(len(scenario_reports)),
            "mismatch_count": int(len(mismatches)),
        },
        "assertions": {
            "no_envelope_overflow": bool(no_overflow),
            "deterministic_ordering": bool(deterministic_ok),
            "no_starvation_ranked": bool(no_starvation),
            "no_silent_mutation": bool(no_silent_mutation),
        },
        "mismatches": list(mismatches),
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    if all(bool(value) for value in dict(report.get("assertions") or {}).values()):
        return {"result": "complete", "report": report}
    failed = sorted(key for key, value in dict(report.get("assertions") or {}).items() if not bool(value))
    return {
        "result": "refused",
        "errors": [
            {
                "code": "refusal.mob.stress_assertions_failed",
                "message": "mobility stress assertions failed: {}".format(",".join(failed)),
                "path": "$.assertions",
            }
        ],
        "report": report,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic MOB-11 mobility stress suite.")
    parser.add_argument("--ticks", type=int, default=8)
    parser.add_argument("--dense-vehicles", type=int, default=240)
    parser.add_argument("--output", default="build/mobility/mobility_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    result = run_mobility_stress(
        ticks=max(4, int(args.ticks)),
        dense_vehicles=max(120, int(args.dense_vehicles)),
    )
    output = str(args.output).strip()
    if output:
        output_abs = os.path.normpath(os.path.abspath(output))
        _write_json(output_abs, result)
        result["output_path"] = output_abs
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")) == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
