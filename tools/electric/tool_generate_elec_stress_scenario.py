#!/usr/bin/env python3
"""ELEC-5 deterministic stress scenario generator."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.electric import deterministic_power_channel_id  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _pick(seed: int, stream: str, index: int, modulo: int, *, offset: int = 0) -> int:
    if int(modulo) <= 0:
        return int(offset)
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "stream": str(stream),
            "index": int(index),
            "modulo": int(modulo),
        }
    )
    return int(offset + (int(digest[:12], 16) % int(modulo)))


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def generate_elec_stress_scenario(
    *,
    seed: int,
    generator_count: int,
    load_count: int,
    storage_count: int,
    breaker_count: int,
    graph_count: int,
    shard_count: int,
    tick_horizon: int,
) -> dict:
    seed_i = int(seed)
    gen_count = int(max(1, _as_int(generator_count, 1)))
    load_count_i = int(max(1, _as_int(load_count, 1)))
    storage_count_i = int(max(0, _as_int(storage_count, 0)))
    breaker_count_i = int(max(1, _as_int(breaker_count, 1)))
    graph_count_i = int(max(1, _as_int(graph_count, 1)))
    shard_count_i = int(max(1, _as_int(shard_count, 1)))
    tick_horizon_i = int(max(8, _as_int(tick_horizon, 64)))

    scenario_id = "scenario.elec.stress.{}".format(
        canonical_sha256(
            {
                "seed": int(seed_i),
                "graph_count": int(graph_count_i),
                "generator_count": int(gen_count),
                "load_count": int(load_count_i),
                "storage_count": int(storage_count_i),
                "breaker_count": int(breaker_count_i),
                "shard_count": int(shard_count_i),
            }
        )[:12]
    )

    power_network_graphs: List[dict] = []
    model_bindings: List[dict] = []
    channel_override_rows: List[dict] = []
    load_spike_rows: List[dict] = []
    short_circuit_rows: List[dict] = []
    pending_connection_requests: List[dict] = []

    for graph_index in range(graph_count_i):
        graph_id = "graph.elec.stress.{}.{}".format(str(graph_index + 1).zfill(3), scenario_id.split(".")[-1])
        nodes: List[dict] = []
        edges: List[dict] = []
        bus_ids_by_shard: List[str] = []

        for shard_index in range(shard_count_i):
            bus_id = "node.elec.bus.g{}.s{}".format(str(graph_index + 1).zfill(2), str(shard_index + 1).zfill(2))
            bus_ids_by_shard.append(bus_id)
            nodes.append(
                {
                    "node_id": bus_id,
                    "node_type_id": "node.elec.bus",
                    "tags": ["electric", "bus", "shard.{}".format(str(shard_index + 1).zfill(2))],
                    "payload": {
                        "schema_version": "1.0.0",
                        "node_kind": "bus",
                        "spec_id": None,
                        "model_bindings": [],
                        "safety_instances": [],
                        "deterministic_fingerprint": "",
                        "extensions": {
                            "shard_id": "shard.{}".format(str(shard_index + 1).zfill(2)),
                            "boundary_node": bool(shard_count_i > 1),
                        },
                    },
                    "extensions": {
                        "shard_id": "shard.{}".format(str(shard_index + 1).zfill(2)),
                        "boundary_node": bool(shard_count_i > 1),
                    },
                }
            )

        for idx in range(gen_count):
            shard_index = _pick(seed_i, "generator.shard", graph_index * 1000 + idx, shard_count_i)
            node_id = "node.elec.generator.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            nodes.append(
                {
                    "node_id": node_id,
                    "node_type_id": "node.elec.generator",
                    "tags": ["electric", "generator"],
                    "payload": {
                        "schema_version": "1.0.0",
                        "node_kind": "generator",
                        "spec_id": None,
                        "model_bindings": [],
                        "safety_instances": [],
                        "deterministic_fingerprint": "",
                        "extensions": {
                            "shard_id": "shard.{}".format(str(shard_index + 1).zfill(2)),
                        },
                    },
                    "extensions": {
                        "shard_id": "shard.{}".format(str(shard_index + 1).zfill(2)),
                    },
                }
            )
            edge_id = "edge.elec.generator.g{}.e{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            capacity = int(280 + _pick(seed_i, "generator.capacity", graph_index * 2000 + idx, 220))
            edges.append(
                {
                    "edge_id": edge_id,
                    "from_node_id": node_id,
                    "to_node_id": bus_ids_by_shard[shard_index],
                    "edge_type_id": "edge.elec.conductor",
                    "capacity": int(capacity),
                    "delay_ticks": 0,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "conductor",
                        "length": int(300 + _pick(seed_i, "generator.length", graph_index * 3000 + idx, 600)),
                        "resistance_proxy": int(6 + _pick(seed_i, "generator.resistance", graph_index * 4000 + idx, 8)),
                        "capacity_rating": int(capacity),
                        "spec_id": None,
                        "deterministic_fingerprint": "",
                        "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                    },
                    "extensions": {},
                }
            )

        for idx in range(load_count_i):
            shard_index = _pick(seed_i, "load.shard", graph_index * 5000 + idx, shard_count_i)
            node_id = "node.elec.load.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            resistive_binding_id = "binding.elec.load.res.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            motor_binding_id = "binding.elec.load.mot.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            nodes.append(
                {
                    "node_id": node_id,
                    "node_type_id": "node.elec.load",
                    "tags": ["electric", "load"],
                    "payload": {
                        "schema_version": "1.0.0",
                        "node_kind": "load",
                        "spec_id": None,
                        "model_bindings": [resistive_binding_id, motor_binding_id],
                        "safety_instances": [],
                        "deterministic_fingerprint": "",
                        "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                    },
                    "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                }
            )
            resistive_demand = int(40 + _pick(seed_i, "load.res", graph_index * 6000 + idx, 180))
            motor_demand = int(35 + _pick(seed_i, "load.mot", graph_index * 7000 + idx, 170))
            pf_permille = int(650 + _pick(seed_i, "load.pf", graph_index * 8000 + idx, 300))
            model_bindings.extend(
                [
                    {
                        "schema_version": "1.0.0",
                        "binding_id": resistive_binding_id,
                        "model_id": "model.elec_load_resistive_stub",
                        "target_kind": "node",
                        "target_id": node_id,
                        "tier": "meso",
                        "parameters": {"demand_p": int(resistive_demand)},
                        "enabled": True,
                        "deterministic_fingerprint": "",
                        "extensions": {},
                    },
                    {
                        "schema_version": "1.0.0",
                        "binding_id": motor_binding_id,
                        "model_id": "model.elec_load_motor_stub",
                        "target_kind": "node",
                        "target_id": node_id,
                        "tier": "meso",
                        "parameters": {
                            "demand_p": int(motor_demand),
                            "pf_permille": int(max(1, min(1000, pf_permille))),
                        },
                        "enabled": True,
                        "deterministic_fingerprint": "",
                        "extensions": {},
                    },
                ]
            )
            edge_id = "edge.elec.load.g{}.e{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            capacity = int(70 + _pick(seed_i, "load.capacity", graph_index * 9000 + idx, 150))
            edges.append(
                {
                    "edge_id": edge_id,
                    "from_node_id": bus_ids_by_shard[shard_index],
                    "to_node_id": node_id,
                    "edge_type_id": "edge.elec.conductor",
                    "capacity": int(capacity),
                    "delay_ticks": 0,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "conductor",
                        "length": int(500 + _pick(seed_i, "load.length", graph_index * 10000 + idx, 1500)),
                        "resistance_proxy": int(7 + _pick(seed_i, "load.resistance", graph_index * 11000 + idx, 15)),
                        "capacity_rating": int(capacity),
                        "spec_id": None,
                        "deterministic_fingerprint": "",
                        "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                    },
                    "extensions": {},
                }
            )

        for idx in range(storage_count_i):
            shard_index = _pick(seed_i, "storage.shard", graph_index * 12000 + idx, shard_count_i)
            node_id = "node.elec.storage.g{}.n{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            nodes.append(
                {
                    "node_id": node_id,
                    "node_type_id": "node.elec.storage",
                    "tags": ["electric", "storage"],
                    "payload": {
                        "schema_version": "1.0.0",
                        "node_kind": "storage",
                        "spec_id": None,
                        "model_bindings": [],
                        "safety_instances": [],
                        "deterministic_fingerprint": "",
                        "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                    },
                    "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                }
            )
            edge_id = "edge.elec.storage.g{}.e{}".format(str(graph_index + 1).zfill(2), str(idx + 1).zfill(4))
            capacity = int(90 + _pick(seed_i, "storage.capacity", graph_index * 13000 + idx, 140))
            edges.append(
                {
                    "edge_id": edge_id,
                    "from_node_id": bus_ids_by_shard[shard_index],
                    "to_node_id": node_id,
                    "edge_type_id": "edge.elec.conductor",
                    "capacity": int(capacity),
                    "delay_ticks": 0,
                    "cost_units": 1,
                    "payload": {
                        "schema_version": "1.0.0",
                        "edge_kind": "conductor",
                        "length": int(400 + _pick(seed_i, "storage.length", graph_index * 14000 + idx, 1200)),
                        "resistance_proxy": int(6 + _pick(seed_i, "storage.resistance", graph_index * 15000 + idx, 12)),
                        "capacity_rating": int(capacity),
                        "spec_id": None,
                        "deterministic_fingerprint": "",
                        "extensions": {"shard_id": "shard.{}".format(str(shard_index + 1).zfill(2))},
                    },
                    "extensions": {},
                }
            )

        if shard_count_i > 1:
            for shard_index in range(shard_count_i - 1):
                edge_id = "edge.elec.boundary.g{}.s{}to{}".format(
                    str(graph_index + 1).zfill(2),
                    str(shard_index + 1).zfill(2),
                    str(shard_index + 2).zfill(2),
                )
                edges.append(
                    {
                        "edge_id": edge_id,
                        "from_node_id": bus_ids_by_shard[shard_index],
                        "to_node_id": bus_ids_by_shard[shard_index + 1],
                        "edge_type_id": "edge.elec.conductor",
                        "capacity": 260,
                        "delay_ticks": 0,
                        "cost_units": 1,
                        "payload": {
                            "schema_version": "1.0.0",
                            "edge_kind": "conductor",
                            "length": 800,
                            "resistance_proxy": 9,
                            "capacity_rating": 260,
                            "spec_id": None,
                            "deterministic_fingerprint": "",
                            "extensions": {
                                "cross_shard_boundary": True,
                            },
                        },
                        "extensions": {"cross_shard_boundary": True},
                    }
                )

        graph_row = {
            "schema_version": "1.0.0",
            "graph_id": graph_id,
            "node_type_schema_id": "dominium.schema.electric.elec_node_payload.v1",
            "edge_type_schema_id": "dominium.schema.electric.elec_edge_payload.v1",
            "payload_schema_versions": {
                "dominium.schema.electric.elec_node_payload.v1": "1.0.0",
                "dominium.schema.electric.elec_edge_payload.v1": "1.0.0",
            },
            "validation_mode": "strict",
            "deterministic_routing_policy_id": "route.shortest_delay",
            "graph_partition_id": None,
            "nodes": sorted(nodes, key=lambda row: str(row.get("node_id", ""))),
            "edges": sorted(edges, key=lambda row: str(row.get("edge_id", ""))),
            "extensions": {},
        }
        power_network_graphs.append(graph_row)

        for edge_index, edge_row in enumerate(graph_row["edges"]):
            edge_id = str(edge_row.get("edge_id", "")).strip()
            channel_id = deterministic_power_channel_id(graph_id=graph_id, edge_id=edge_id)
            group_suffix = str((_pick(seed_i, "coord.group", graph_index * 20000 + edge_index, breaker_count_i) + 1)).zfill(3)
            channel_override_rows.append(
                {
                    "channel_id": channel_id,
                    "extensions": {
                        "edge_id": edge_id,
                        "graph_id": graph_id,
                        "coordination_group_id": "coord.group.{}".format(group_suffix),
                        "downstream_rank": int(_pick(seed_i, "coord.rank", graph_index * 21000 + edge_index, 8)),
                        "trip_delay_ticks": int(_pick(seed_i, "coord.delay", graph_index * 22000 + edge_index, 3)),
                        "gfci_threshold": int(20 + _pick(seed_i, "coord.gfci", graph_index * 23000 + edge_index, 40)),
                    },
                }
            )

        edge_ids = [str(row.get("edge_id", "")).strip() for row in graph_row["edges"] if str(row.get("edge_id", "")).strip()]
        if edge_ids:
            short_edge_id = edge_ids[_pick(seed_i, "short.edge", graph_index, len(edge_ids))]
            short_channel_id = deterministic_power_channel_id(graph_id=graph_id, edge_id=short_edge_id)
            short_start = int(max(2, tick_horizon_i // 4))
            short_duration = int(max(2, tick_horizon_i // 12))
            short_circuit_rows.append(
                {
                    "graph_id": graph_id,
                    "edge_id": short_edge_id,
                    "channel_id": short_channel_id,
                    "start_tick": int(short_start),
                    "end_tick": int(short_start + short_duration),
                    "fault_kind_id": "fault.short_circuit",
                }
            )

    binding_rows_sorted = sorted(model_bindings, key=lambda row: str(row.get("binding_id", "")))
    motor_binding_ids = [
        str(row.get("binding_id", "")).strip()
        for row in binding_rows_sorted
        if str(row.get("model_id", "")).strip() == "model.elec_load_motor_stub"
    ]
    for tick in range(2, tick_horizon_i, max(2, tick_horizon_i // 12)):
        if not motor_binding_ids:
            break
        binding_id = motor_binding_ids[_pick(seed_i, "spike.binding", tick, len(motor_binding_ids))]
        delta = int(30 + _pick(seed_i, "spike.delta", tick, 90))
        load_spike_rows.append(
            {
                "tick": int(tick),
                "binding_id": binding_id,
                "delta_demand_p": int(delta),
            }
        )

    for idx in range(max(2, breaker_count_i // 2)):
        pending_connection_requests.append(
            {
                "request_id": "conn.req.{}.{}".format(scenario_id.split(".")[-1], str(idx + 1).zfill(3)),
                "priority": "low",
                "created_tick": int(1 + idx),
            }
        )

    initial_state_snapshot = {
        "simulation_time": {"tick": 0, "tick_rate": 1, "deterministic_clock": {"tick_duration_ms": 1000}},
        "power_network_graphs": [dict(row) for row in power_network_graphs],
        "model_bindings": [dict(row) for row in binding_rows_sorted],
        "elec_flow_channels": [dict(row) for row in sorted(channel_override_rows, key=lambda row: str(row.get("channel_id", "")))],
        "elec_fault_states": [],
        "elec_trip_events": [],
        "elec_degradation_events": [],
        "control_decision_log": [],
    }

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": scenario_id,
        "seed": int(seed_i),
        "tick_horizon": int(tick_horizon_i),
        "counts": {
            "generator_count": int(gen_count),
            "load_count": int(load_count_i),
            "storage_count": int(storage_count_i),
            "breaker_count": int(breaker_count_i),
            "graph_count": int(graph_count_i),
            "shard_count": int(shard_count_i),
        },
        "power_network_graphs": [dict(row) for row in power_network_graphs],
        "model_bindings": [dict(row) for row in binding_rows_sorted],
        "initial_flow_channel_overrides": [dict(row) for row in sorted(channel_override_rows, key=lambda row: str(row.get("channel_id", "")))],
        "load_spike_rows": [dict(row) for row in sorted(load_spike_rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("binding_id", ""))))],
        "short_circuit_rows": [dict(row) for row in sorted(short_circuit_rows, key=lambda row: (str(row.get("graph_id", "")), str(row.get("edge_id", ""))))],
        "pending_connection_requests": [dict(row) for row in sorted(pending_connection_requests, key=lambda row: str(row.get("request_id", "")))],
        "initial_state_snapshot": initial_state_snapshot,
        "deterministic_fingerprint": "",
    }
    seed_payload = dict(scenario)
    seed_payload["deterministic_fingerprint"] = ""
    seed_payload["power_network_graphs"] = [dict(row) for row in list(scenario.get("power_network_graphs") or [])]
    seed_payload["model_bindings"] = [dict(row) for row in list(scenario.get("model_bindings") or [])]
    seed_payload["initial_flow_channel_overrides"] = [dict(row) for row in list(scenario.get("initial_flow_channel_overrides") or [])]
    scenario["deterministic_fingerprint"] = canonical_sha256(seed_payload)
    return scenario


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic ELEC stress scenario data.")
    parser.add_argument("--seed", type=int, default=5501)
    parser.add_argument("--generators", type=int, default=24)
    parser.add_argument("--loads", type=int, default=180)
    parser.add_argument("--storage", type=int, default=36)
    parser.add_argument("--breakers", type=int, default=48)
    parser.add_argument("--graphs", type=int, default=2)
    parser.add_argument("--shards", type=int, default=2)
    parser.add_argument("--ticks", type=int, default=64)
    parser.add_argument("--output", default="build/electric/elec_stress_scenario.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

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
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, scenario)
    scenario["output_path"] = output_abs
    print(json.dumps(scenario, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
