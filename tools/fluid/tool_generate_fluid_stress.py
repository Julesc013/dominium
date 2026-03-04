#!/usr/bin/env python3
"""FLUID-3 deterministic stress scenario generator."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping, Sequence, Tuple


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


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _node_row(*, node_id: str, node_kind: str, fluid_profile_id: str, state_ref: Mapping[str, object], model_bindings: Sequence[str], safety_instances: Sequence[str], shard_id: str) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "node_kind": str(node_kind),
        "fluid_profile_id": str(fluid_profile_id),
        "spec_id": None,
        "model_bindings": _sorted_tokens(list(model_bindings)),
        "safety_instances": _sorted_tokens(list(safety_instances)),
        "state_ref": dict(state_ref or {}),
        "deterministic_fingerprint": "",
        "extensions": {"shard_id": str(shard_id)},
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return {
        "node_id": str(node_id),
        "node_type_id": "node.fluid.{}".format(str(node_kind)),
        "tags": sorted(["fluid", str(node_kind), str(shard_id)]),
        "payload": payload,
        "extensions": {"shard_id": str(shard_id)},
    }


def _edge_row(
    *,
    edge_id: str,
    from_node_id: str,
    to_node_id: str,
    model_bindings: Sequence[str],
    seed: int,
    graph_index: int,
    edge_index: int,
    interior_compartment_count: int,
) -> dict:
    leak_sink_kind = "interior" if _pick(seed, "edge.leak.sink", graph_index * 10000 + edge_index, 4) == 0 else "external"
    sink_id = (
        "comp.interior.{}".format(str(_pick(seed, "edge.leak.compartment", graph_index * 11000 + edge_index, max(1, interior_compartment_count)) + 1).zfill(3))
        if leak_sink_kind == "interior"
        else "sink.external.void"
    )
    payload = {
        "schema_version": "1.0.0",
        "edge_kind": "pipe",
        "length": int(80 + _pick(seed, "edge.length", graph_index * 12000 + edge_index, 1400)),
        "diameter_proxy": int(35 + _pick(seed, "edge.diameter", graph_index * 13000 + edge_index, 120)),
        "roughness_proxy": int(1 + _pick(seed, "edge.roughness", graph_index * 14000 + edge_index, 15)),
        "capacity_rating": int(55 + _pick(seed, "edge.capacity", graph_index * 15000 + edge_index, 260)),
        "spec_id": None,
        "model_bindings": _sorted_tokens(list(model_bindings)),
        "deterministic_fingerprint": "",
        "extensions": {
            "leak_coefficient_permille": int(_pick(seed, "edge.leak.coeff", graph_index * 16000 + edge_index, 180)),
            "leak_sink_kind": str(leak_sink_kind),
            "leak_sink_id": str(sink_id),
        },
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return {
        "edge_id": str(edge_id),
        "from_node_id": str(from_node_id),
        "to_node_id": str(to_node_id),
        "edge_type_id": "edge.fluid.pipe",
        "capacity": int(payload["capacity_rating"]),
        "delay_ticks": 0,
        "cost_units": 1,
        "payload": payload,
        "extensions": {},
    }


def _graph_rows(
    *,
    seed: int,
    graph_count: int,
    tanks_per_graph: int,
    vessels_per_graph: int,
    pumps_per_graph: int,
    valves_per_graph: int,
    pipes_per_graph: int,
    interior_compartment_count: int,
) -> Tuple[List[dict], List[dict]]:
    graphs: List[dict] = []
    initial_tank_rows: List[dict] = []
    for graph_index in range(graph_count):
        graph_token = canonical_sha256({"seed": int(seed), "graph_index": int(graph_index)})[:8]
        graph_id = "graph.fluid.stress.{}.{}".format(str(graph_index + 1).zfill(3), graph_token)
        shard_id = "shard.{}".format(str((graph_index % 3) + 1).zfill(2))

        node_rows: List[dict] = []
        node_ids: List[str] = []

        for idx in range(max(1, tanks_per_graph)):
            node_id = "node.fluid.tank.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            max_mass = int(800 + _pick(seed, "tank.max_mass", graph_index * 2000 + idx, 4200))
            stored_mass = int((max_mass * (520 + _pick(seed, "tank.fill", graph_index * 2100 + idx, 300))) // 1000)
            node_rows.append(
                _node_row(
                    node_id=node_id,
                    node_kind="tank",
                    fluid_profile_id="fluid.water",
                    state_ref={
                        "pressure_head": int(80 + _pick(seed, "tank.head", graph_index * 2200 + idx, 140)),
                        "head_scale": int(80 + _pick(seed, "tank.head_scale", graph_index * 2300 + idx, 120)),
                        "max_mass": int(max_mass),
                        "stored_mass": int(stored_mass),
                    },
                    model_bindings=[],
                    safety_instances=[],
                    shard_id=shard_id,
                )
            )
            initial_tank_rows.append(
                {
                    "schema_version": "1.0.0",
                    "node_id": str(node_id),
                    "stored_mass": int(stored_mass),
                    "max_mass": int(max_mass),
                    "last_update_tick": 0,
                    "deterministic_fingerprint": "",
                    "extensions": {"graph_id": str(graph_id)},
                }
            )
            node_ids.append(node_id)

        for idx in range(max(1, vessels_per_graph)):
            node_id = "node.fluid.vessel.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            max_mass = int(600 + _pick(seed, "vessel.max_mass", graph_index * 2400 + idx, 2600))
            stored_mass = int((max_mass * (560 + _pick(seed, "vessel.fill", graph_index * 2500 + idx, 320))) // 1000)
            relief_threshold = int(180 + _pick(seed, "vessel.relief", graph_index * 2600 + idx, 140))
            burst_threshold = int(relief_threshold + 40 + _pick(seed, "vessel.burst", graph_index * 2700 + idx, 200))
            node_rows.append(
                _node_row(
                    node_id=node_id,
                    node_kind="pressure_vessel",
                    fluid_profile_id="fluid.water",
                    state_ref={
                        "pressure_head": int(120 + _pick(seed, "vessel.head", graph_index * 2800 + idx, 220)),
                        "head_scale": int(120 + _pick(seed, "vessel.head_scale", graph_index * 2900 + idx, 140)),
                        "max_mass": int(max_mass),
                        "stored_mass": int(stored_mass),
                        "relief_threshold": int(relief_threshold),
                        "burst_threshold": int(burst_threshold),
                        "vessel_rating": int(relief_threshold),
                    },
                    model_bindings=[],
                    safety_instances=["instance.safety.pressure_relief.{}".format(str(node_id))],
                    shard_id=shard_id,
                )
            )
            initial_tank_rows.append(
                {
                    "schema_version": "1.0.0",
                    "node_id": str(node_id),
                    "stored_mass": int(stored_mass),
                    "max_mass": int(max_mass),
                    "last_update_tick": 0,
                    "deterministic_fingerprint": "",
                    "extensions": {"graph_id": str(graph_id)},
                }
            )
            node_ids.append(node_id)

        for idx in range(max(1, pumps_per_graph)):
            node_id = "node.fluid.pump.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            node_rows.append(
                _node_row(
                    node_id=node_id,
                    node_kind="pump",
                    fluid_profile_id="fluid.water",
                    state_ref={
                        "pressure_head": int(90 + _pick(seed, "pump.head", graph_index * 3000 + idx, 120)),
                        "pump_speed_permille": int(700 + _pick(seed, "pump.speed", graph_index * 3100 + idx, 500)),
                        "base_head_gain": int(30 + _pick(seed, "pump.gain", graph_index * 3200 + idx, 180)),
                    },
                    model_bindings=["model.fluid_pump_curve_stub"],
                    safety_instances=[],
                    shard_id=shard_id,
                )
            )
            node_ids.append(node_id)

        for idx in range(max(1, valves_per_graph)):
            node_id = "node.fluid.valve.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            node_rows.append(
                _node_row(
                    node_id=node_id,
                    node_kind="valve",
                    fluid_profile_id="fluid.water",
                    state_ref={
                        "pressure_head": int(80 + _pick(seed, "valve.head", graph_index * 3300 + idx, 100)),
                        "valve_open_permille": int(500 + _pick(seed, "valve.open", graph_index * 3400 + idx, 500)),
                        "valve_cv_permille": int(600 + _pick(seed, "valve.cv", graph_index * 3500 + idx, 360)),
                    },
                    model_bindings=["model.fluid_valve_curve_stub"],
                    safety_instances=[],
                    shard_id=shard_id,
                )
            )
            node_ids.append(node_id)

        junction_count = max(1, min(10, pipes_per_graph // 6))
        for idx in range(junction_count):
            node_id = "node.fluid.junction.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            node_rows.append(
                _node_row(
                    node_id=node_id,
                    node_kind="junction",
                    fluid_profile_id="fluid.water",
                    state_ref={"pressure_head": int(70 + _pick(seed, "junction.head", graph_index * 3600 + idx, 90))},
                    model_bindings=[],
                    safety_instances=[],
                    shard_id=shard_id,
                )
            )
            node_ids.append(node_id)

        node_ids = [str(row.get("node_id", "")).strip() for row in sorted(node_rows, key=lambda row: str(row.get("node_id", "")))]
        edges: List[dict] = []
        used_pairs = set()

        def add_edge(from_node: str, to_node: str) -> None:
            if not from_node or not to_node or from_node == to_node:
                return
            key = (str(from_node), str(to_node))
            if key in used_pairs:
                return
            used_pairs.add(key)
            edge_index = len(edges)
            from_payload = dict((next((row for row in node_rows if str(row.get("node_id", "")) == from_node), {}) or {}).get("payload") or {})
            to_payload = dict((next((row for row in node_rows if str(row.get("node_id", "")) == to_node), {}) or {}).get("payload") or {})
            model_bindings = ["model.fluid_pipe_loss_stub"]
            model_bindings.extend(list(from_payload.get("model_bindings") or []))
            model_bindings.extend(list(to_payload.get("model_bindings") or []))
            if _pick(seed, "edge.cavitation.flag", graph_index * 50000 + edge_index, 5) == 0:
                model_bindings.append("model.fluid_cavitation_stub")
            if _pick(seed, "edge.leak.flag", graph_index * 51000 + edge_index, 4) == 0:
                model_bindings.append("model.fluid_leak_rate_stub")
            edges.append(
                _edge_row(
                    edge_id="edge.fluid.g{}.e{}".format(str(graph_index + 1).zfill(2), str(edge_index + 1).zfill(5)),
                    from_node_id=str(from_node),
                    to_node_id=str(to_node),
                    model_bindings=model_bindings,
                    seed=seed,
                    graph_index=graph_index,
                    edge_index=edge_index,
                    interior_compartment_count=interior_compartment_count,
                )
            )

        for idx in range(len(node_ids)):
            add_edge(node_ids[idx], node_ids[(idx + 1) % len(node_ids)])
            if len(edges) >= pipes_per_graph:
                break
        extra_index = 0
        while len(edges) < pipes_per_graph:
            from_idx = _pick(seed, "edge.extra.from", graph_index * 52000 + extra_index, len(node_ids))
            to_idx = _pick(seed, "edge.extra.to", graph_index * 53000 + extra_index, len(node_ids))
            extra_index += 1
            add_edge(node_ids[from_idx], node_ids[to_idx])
            if extra_index > int(max(256, pipes_per_graph * 24)):
                break

        graph_row = {
            "schema_version": "1.0.0",
            "graph_id": str(graph_id),
            "node_type_schema_id": "dominium.schema.fluid.fluid_node_payload",
            "edge_type_schema_id": "dominium.schema.fluid.fluid_edge_payload",
            "payload_schema_versions": {
                "dominium.schema.fluid.fluid_node_payload": "1.0.0",
                "dominium.schema.fluid.fluid_edge_payload": "1.0.0",
            },
            "validation_mode": "strict",
            "deterministic_routing_policy_id": "route.fluid.default",
            "nodes": sorted(node_rows, key=lambda row: str(row.get("node_id", ""))),
            "edges": sorted(edges, key=lambda row: str(row.get("edge_id", ""))),
            "extensions": {"tier_default": "F1", "shard_id": str(shard_id)},
        }
        graphs.append(graph_row)
    return sorted(graphs, key=lambda row: str(row.get("graph_id", ""))), sorted(initial_tank_rows, key=lambda row: str(row.get("node_id", "")))


def _periodic_demand_rows(*, seed: int, graph_rows: Sequence[Mapping[str, object]], tick_horizon: int) -> List[dict]:
    out: List[dict] = []
    for graph_index, graph_row in enumerate(sorted((dict(row) for row in graph_rows), key=lambda row: str(row.get("graph_id", "")))):
        graph_id = str(graph_row.get("graph_id", "")).strip()
        node_rows = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
        pump_ids = [str(row.get("node_id", "")).strip() for row in node_rows if str((dict(row.get("payload") or {})).get("node_kind", "")).strip() == "pump"]
        valve_ids = [str(row.get("node_id", "")).strip() for row in node_rows if str((dict(row.get("payload") or {})).get("node_kind", "")).strip() == "valve"]
        for idx, node_id in enumerate(sorted(pump_ids)):
            out.append(
                {
                    "kind": "pump_speed_cycle",
                    "graph_id": str(graph_id),
                    "node_id": str(node_id),
                    "start_tick": int(_pick(seed, "demand.pump.start", graph_index * 7000 + idx, 5)),
                    "interval_ticks": int(2 + _pick(seed, "demand.pump.interval", graph_index * 7100 + idx, 8)),
                    "delta_speed_permille": int(-180 + _pick(seed, "demand.pump.delta", graph_index * 7200 + idx, 360)),
                    "min_value": 200,
                    "max_value": 1400,
                    "end_tick": int(max(0, tick_horizon - 1)),
                }
            )
        for idx, node_id in enumerate(sorted(valve_ids)):
            out.append(
                {
                    "kind": "valve_cycle",
                    "graph_id": str(graph_id),
                    "node_id": str(node_id),
                    "start_tick": int(_pick(seed, "demand.valve.start", graph_index * 7300 + idx, 5)),
                    "interval_ticks": int(3 + _pick(seed, "demand.valve.interval", graph_index * 7400 + idx, 10)),
                    "delta_open_permille": int(-220 + _pick(seed, "demand.valve.delta", graph_index * 7500 + idx, 440)),
                    "min_value": 100,
                    "max_value": 1000,
                    "end_tick": int(max(0, tick_horizon - 1)),
                }
            )
    return sorted(out, key=lambda row: (str(row.get("graph_id", "")), str(row.get("node_id", "")), str(row.get("kind", ""))))


def _fault_rows(*, seed: int, graph_rows: Sequence[Mapping[str, object]], tick_horizon: int) -> List[dict]:
    out: List[dict] = []
    horizon = int(max(8, _as_int(tick_horizon, 64)))
    for graph_index, graph_row in enumerate(sorted((dict(row) for row in graph_rows), key=lambda row: str(row.get("graph_id", "")))):
        graph_id = str(graph_row.get("graph_id", "")).strip()
        nodes = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
        edges = [dict(row) for row in list(graph_row.get("edges") or []) if isinstance(row, Mapping)]
        vessel_ids = [str(row.get("node_id", "")).strip() for row in nodes if str((dict(row.get("payload") or {})).get("node_kind", "")).strip() == "pressure_vessel"]
        valve_ids = [str(row.get("node_id", "")).strip() for row in nodes if str((dict(row.get("payload") or {})).get("node_kind", "")).strip() == "valve"]
        edge_ids = [str(row.get("edge_id", "")).strip() for row in edges if str(row.get("edge_id", "")).strip()]

        if valve_ids:
            valve_id = valve_ids[_pick(seed, "fault.valve.pick", graph_index, len(valve_ids))]
            out.append(
                {
                    "fault_kind": "stuck_valve",
                    "graph_id": str(graph_id),
                    "target_id": str(valve_id),
                    "tick": int(3 + _pick(seed, "fault.valve.tick", graph_index, max(2, horizon - 6))),
                    "stuck_open_permille": int(100 + _pick(seed, "fault.valve.value", graph_index, 260)),
                }
            )
        if vessel_ids:
            vessel_id = vessel_ids[_pick(seed, "fault.burst.pick", graph_index, len(vessel_ids))]
            out.append(
                {
                    "fault_kind": "burst_event",
                    "graph_id": str(graph_id),
                    "target_id": str(vessel_id),
                    "tick": int(4 + _pick(seed, "fault.burst.tick", graph_index, max(2, horizon - 8))),
                    "head_boost": int(220 + _pick(seed, "fault.burst.boost", graph_index, 240)),
                }
            )
        if edge_ids:
            edge_id = edge_ids[_pick(seed, "fault.leak.pick", graph_index, len(edge_ids))]
            source_node_id = str((dict(next((row for row in edges if str(row.get("edge_id", "")) == edge_id), {}) or {})).get("from_node_id", "")).strip()
            out.append(
                {
                    "fault_kind": "leak_event",
                    "graph_id": str(graph_id),
                    "target_id": str(edge_id),
                    "tick": int(2 + _pick(seed, "fault.leak.tick", graph_index, max(2, horizon - 4))),
                    "leak_rate": int(20 + _pick(seed, "fault.leak.rate", graph_index, 140)),
                    "source_node_id": str(source_node_id),
                    "sink_kind": "interior" if _pick(seed, "fault.leak.sink", graph_index, 3) == 0 else "external",
                    "sink_id": "comp.interior.001" if _pick(seed, "fault.leak.sink_id", graph_index, 3) == 0 else "sink.external.void",
                }
            )
            cav_edge = edge_ids[_pick(seed, "fault.cav.pick", graph_index, len(edge_ids))]
            out.append(
                {
                    "fault_kind": "cavitation_condition",
                    "graph_id": str(graph_id),
                    "target_id": str(cav_edge),
                    "tick": int(1 + _pick(seed, "fault.cav.tick", graph_index, max(2, horizon - 2))),
                    "head_drop": int(40 + _pick(seed, "fault.cav.drop", graph_index, 120)),
                }
            )
    return sorted(out, key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("graph_id", "")), str(row.get("fault_kind", "")), str(row.get("target_id", ""))))


def generate_fluid_stress_scenario(
    *,
    seed: int,
    tanks: int,
    vessels: int,
    pipes: int,
    pumps: int,
    valves: int,
    graphs: int,
    ticks: int,
    interior_compartment_count: int = 6,
) -> dict:
    seed_i = int(seed)
    graph_count = int(max(1, _as_int(graphs, 1)))
    tank_count = int(max(1, _as_int(tanks, 1)))
    vessel_count = int(max(1, _as_int(vessels, 1)))
    pump_count = int(max(1, _as_int(pumps, 1)))
    valve_count = int(max(1, _as_int(valves, 1)))
    pipe_count = int(max(4, _as_int(pipes, 4)))
    tick_horizon = int(max(8, _as_int(ticks, 64)))
    scenario_id = "scenario.fluid.stress.{}".format(
        canonical_sha256(
            {
                "seed": int(seed_i),
                "graphs": int(graph_count),
                "tanks": int(tank_count),
                "vessels": int(vessel_count),
                "pipes": int(pipe_count),
                "pumps": int(pump_count),
                "valves": int(valve_count),
                "ticks": int(tick_horizon),
            }
        )[:12]
    )
    graph_rows, tank_rows = _graph_rows(
        seed=seed_i,
        graph_count=graph_count,
        tanks_per_graph=tank_count,
        vessels_per_graph=vessel_count,
        pumps_per_graph=pump_count,
        valves_per_graph=valve_count,
        pipes_per_graph=pipe_count,
        interior_compartment_count=int(max(1, _as_int(interior_compartment_count, 6))),
    )
    periodic_rows = _periodic_demand_rows(seed=seed_i, graph_rows=graph_rows, tick_horizon=tick_horizon)
    fault_rows = _fault_rows(seed=seed_i, graph_rows=graph_rows, tick_horizon=tick_horizon)
    payload = {
        "schema_version": "1.0.0",
        "scenario_id": str(scenario_id),
        "scenario_seed": int(seed_i),
        "tick_horizon": int(tick_horizon),
        "fluid_network_graphs": list(graph_rows),
        "periodic_demand_rows": list(periodic_rows),
        "fault_schedule_rows": list(fault_rows),
        "initial_state_snapshot": {
            "fluid_network_graphs": list(graph_rows),
            "tank_state_rows": list(tank_rows),
            "leak_state_rows": [],
            "burst_event_rows": [],
        },
        "extensions": {
            "generator_tool": "tools/fluid/tool_generate_fluid_stress.py",
            "interior_compartment_count": int(max(1, _as_int(interior_compartment_count, 6))),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic FLUID stress scenario for FLUID-3 envelope checks.")
    parser.add_argument("--seed", type=int, default=9601)
    parser.add_argument("--tanks", type=int, default=24)
    parser.add_argument("--vessels", type=int, default=8)
    parser.add_argument("--pipes", type=int, default=180)
    parser.add_argument("--pumps", type=int, default=12)
    parser.add_argument("--valves", type=int, default=20)
    parser.add_argument("--graphs", type=int, default=3)
    parser.add_argument("--ticks", type=int, default=64)
    parser.add_argument("--interior-compartments", type=int, default=8)
    parser.add_argument("--output", default="build/fluid/fluid_stress_scenario.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    scenario = generate_fluid_stress_scenario(
        seed=int(args.seed),
        tanks=int(args.tanks),
        vessels=int(args.vessels),
        pipes=int(args.pipes),
        pumps=int(args.pumps),
        valves=int(args.valves),
        graphs=int(args.graphs),
        ticks=int(args.ticks),
        interior_compartment_count=int(args.interior_compartments),
    )
    out_path = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(out_path, scenario)
    scenario["output_path"] = out_path
    print(json.dumps(scenario, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

