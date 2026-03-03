#!/usr/bin/env python3
"""THERM-5 deterministic stress scenario generator."""

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


def _material_for_index(seed: int, index: int) -> str:
    materials = [
        "material.wood_basic",
        "material.plastic_stub",
        "material.fuel_oil_stub",
    ]
    return str(materials[_pick(seed, "material", index, len(materials))])


def _node_row(
    *,
    seed: int,
    graph_index: int,
    node_index: int,
    node_id: str,
    is_radiator: bool,
) -> dict:
    capacity = int(60 + _pick(seed, "node.capacity", graph_index * 10000 + node_index, 260))
    energy = int(500 + _pick(seed, "node.energy", graph_index * 11000 + node_index, 8500))
    ambient_coupling = int(120 + _pick(seed, "node.ambient", graph_index * 12000 + node_index, 320))
    insulation = int(450 + _pick(seed, "node.insulation", graph_index * 13000 + node_index, 700))
    combustible = bool(_pick(seed, "node.combustible", graph_index * 14000 + node_index, 5) == 0)
    boundary_to_ambient = bool(is_radiator or (_pick(seed, "node.boundary", graph_index * 15000 + node_index, 4) == 0))

    node_kind = "radiator" if is_radiator else "thermal_mass"
    if node_index == 0:
        node_kind = "source"
    elif node_index == 1:
        node_kind = "sink"

    ext = {
        "ambient_coupling_coefficient": int(ambient_coupling),
        "insulation_factor_permille": int(insulation),
        "boundary_to_ambient": bool(boundary_to_ambient),
        "combustible": bool(combustible),
        "oxygen_available": True,
        "material_id": _material_for_index(seed=seed, index=graph_index * 20000 + node_index),
        "overtemp_threshold": int(100 + _pick(seed, "node.overtemp", graph_index * 16000 + node_index, 140)),
    }
    if is_radiator:
        ext["radiator_profile_id"] = "radiator.forced_basic"
        ext["base_conductance"] = int(180 + _pick(seed, "node.radiator.base", graph_index * 17000 + node_index, 260))
        ext["forced_cooling_multiplier"] = int(1100 + _pick(seed, "node.radiator.mult", graph_index * 18000 + node_index, 900))
        ext["forced_cooling_on"] = bool(_pick(seed, "node.radiator.on", graph_index * 19000 + node_index, 2) == 0)

    return {
        "node_id": str(node_id),
        "node_type_id": "node.therm.mass",
        "tags": ["thermal", str(node_kind)],
        "payload": {
            "schema_version": "1.0.0",
            "node_kind": str(node_kind),
            "heat_capacity_value": int(max(1, capacity)),
            "current_thermal_energy": int(max(0, energy)),
            "spec_id": None,
            "model_bindings": [],
            "safety_instances": ["instance.safety.overtemp.{}".format(str(node_id))],
            "deterministic_fingerprint": "",
            "extensions": ext,
        },
    }


def _edge_row(
    *,
    seed: int,
    graph_index: int,
    edge_index: int,
    edge_id: str,
    from_node_id: str,
    to_node_id: str,
) -> dict:
    conductance = int(35 + _pick(seed, "edge.conductance", graph_index * 21000 + edge_index, 220))
    insulation = int(420 + _pick(seed, "edge.insulation", graph_index * 22000 + edge_index, 680))
    edge_kind = "insulated_link" if (_pick(seed, "edge.kind", graph_index * 23000 + edge_index, 5) == 0) else "conduction_link"
    if edge_kind == "insulated_link":
        conductance = int(max(1, conductance // 2))

    return {
        "edge_id": str(edge_id),
        "from_node_id": str(from_node_id),
        "to_node_id": str(to_node_id),
        "edge_type_id": "edge.therm.conduction",
        "capacity": 0,
        "delay_ticks": 0,
        "cost_units": 1,
        "payload": {
            "schema_version": "1.0.0",
            "edge_kind": str(edge_kind),
            "conductance_value": int(max(0, conductance)),
            "spec_id": None,
            "model_bindings": [],
            "deterministic_fingerprint": "",
            "extensions": {
                "insulation_factor_permille": int(insulation),
            },
        },
        "extensions": {},
    }


def _graph_rows(
    *,
    seed: int,
    graph_count: int,
    node_count_per_graph: int,
    edge_count_per_graph: int,
    radiator_count_per_graph: int,
) -> List[dict]:
    graphs: List[dict] = []
    for graph_index in range(graph_count):
        graph_id = "graph.therm.stress.{}.{}".format(
            str(graph_index + 1).zfill(3),
            canonical_sha256({"seed": int(seed), "graph_index": int(graph_index)})[:8],
        )
        node_ids = [
            "node.therm.g{}.n{}".format(str(graph_index + 1).zfill(3), str(idx + 1).zfill(4))
            for idx in range(node_count_per_graph)
        ]
        radiator_indices = set(
            _pick(seed, "graph.radiator", graph_index * 30000 + idx, node_count_per_graph)
            for idx in range(max(0, radiator_count_per_graph))
        )
        node_rows = [
            _node_row(
                seed=seed,
                graph_index=graph_index,
                node_index=node_index,
                node_id=node_id,
                is_radiator=bool(node_index in radiator_indices),
            )
            for node_index, node_id in enumerate(node_ids)
        ]

        edge_rows: List[dict] = []
        used_pairs = set()
        for idx in range(node_count_per_graph):
            from_node = node_ids[idx]
            to_node = node_ids[(idx + 1) % node_count_per_graph]
            pair_key = (from_node, to_node)
            if pair_key in used_pairs:
                continue
            used_pairs.add(pair_key)
            edge_rows.append(
                _edge_row(
                    seed=seed,
                    graph_index=graph_index,
                    edge_index=len(edge_rows),
                    edge_id="edge.therm.g{}.e{}".format(str(graph_index + 1).zfill(3), str(len(edge_rows) + 1).zfill(5)),
                    from_node_id=from_node,
                    to_node_id=to_node,
                )
            )

        extra_edges_needed = max(0, edge_count_per_graph - len(edge_rows))
        candidate_index = 0
        while len(edge_rows) < edge_count_per_graph:
            from_idx = _pick(seed, "edge.extra.from", graph_index * 40000 + candidate_index, node_count_per_graph)
            to_idx = _pick(seed, "edge.extra.to", graph_index * 41000 + candidate_index, node_count_per_graph)
            candidate_index += 1
            if from_idx == to_idx:
                continue
            from_node = node_ids[from_idx]
            to_node = node_ids[to_idx]
            pair_key = (from_node, to_node)
            if pair_key in used_pairs:
                continue
            used_pairs.add(pair_key)
            edge_rows.append(
                _edge_row(
                    seed=seed,
                    graph_index=graph_index,
                    edge_index=len(edge_rows),
                    edge_id="edge.therm.g{}.e{}".format(str(graph_index + 1).zfill(3), str(len(edge_rows) + 1).zfill(5)),
                    from_node_id=from_node,
                    to_node_id=to_node,
                )
            )
            if int(candidate_index) > int(max(1024, extra_edges_needed * 12 + 128)):
                break

        graphs.append(
            {
                "schema_version": "1.0.0",
                "graph_id": str(graph_id),
                "node_type_schema_id": "dominium.schema.thermal.thermal_node_payload.v1",
                "edge_type_schema_id": "dominium.schema.thermal.thermal_edge_payload.v1",
                "payload_schema_versions": {
                    "dominium.schema.thermal.thermal_node_payload.v1": "1.0.0",
                    "dominium.schema.thermal.thermal_edge_payload.v1": "1.0.0",
                },
                "validation_mode": "strict",
                "deterministic_routing_policy_id": "route.shortest_delay",
                "graph_partition_id": None,
                "nodes": sorted(node_rows, key=lambda row: str(row.get("node_id", ""))),
                "edges": sorted(edge_rows, key=lambda row: str(row.get("edge_id", ""))),
                "extensions": {
                    "tier_default": "T1",
                },
            }
        )
    return sorted(graphs, key=lambda row: str(row.get("graph_id", "")))


def _periodic_heat_sources(*, seed: int, graphs: List[dict], tick_horizon: int) -> List[dict]:
    rows: List[dict] = []
    for graph_index, graph_row in enumerate(sorted(graphs, key=lambda row: str(row.get("graph_id", "")))):
        graph_id = str(graph_row.get("graph_id", "")).strip()
        node_rows = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
        node_ids = [
            str(row.get("node_id", "")).strip()
            for row in node_rows
            if str(row.get("node_id", "")).strip()
        ]
        source_count = max(1, min(12, len(node_ids) // 6))
        for source_index in range(source_count):
            pick_index = _pick(seed, "heat.source.node", graph_index * 50000 + source_index, len(node_ids))
            node_id = node_ids[pick_index]
            interval = int(1 + _pick(seed, "heat.source.interval", graph_index * 51000 + source_index, 7))
            start_tick = int(_pick(seed, "heat.source.start", graph_index * 52000 + source_index, max(1, interval)))
            heat_input = int(80 + _pick(seed, "heat.source.value", graph_index * 53000 + source_index, 650))
            rows.append(
                {
                    "source_id": "heat.source.{}.{}".format(str(graph_index + 1).zfill(3), str(source_index + 1).zfill(3)),
                    "graph_id": graph_id,
                    "node_id": node_id,
                    "start_tick": int(start_tick),
                    "interval_ticks": int(max(1, interval)),
                    "heat_input": int(max(0, heat_input)),
                    "end_tick": int(max(0, tick_horizon - 1)),
                    "source_domain_id": "ELEC",
                }
            )
    return sorted(rows, key=lambda row: (str(row.get("graph_id", "")), str(row.get("source_id", ""))))


def _fire_ignitions(*, seed: int, graphs: List[dict], include_fire_ignitions: bool, tick_horizon: int) -> List[dict]:
    if not bool(include_fire_ignitions):
        return []
    rows: List[dict] = []
    for graph_index, graph_row in enumerate(sorted(graphs, key=lambda row: str(row.get("graph_id", "")))):
        graph_id = str(graph_row.get("graph_id", "")).strip()
        node_rows = [dict(row) for row in list(graph_row.get("nodes") or []) if isinstance(row, Mapping)]
        combustible_ids = []
        for row in node_rows:
            node_id = str(row.get("node_id", "")).strip()
            payload = dict(row.get("payload") or {}) if isinstance(row.get("payload"), Mapping) else {}
            ext = dict(payload.get("extensions") or {}) if isinstance(payload.get("extensions"), Mapping) else {}
            if not node_id:
                continue
            if bool(ext.get("combustible", False)):
                combustible_ids.append(node_id)
        if not combustible_ids:
            continue
        event_count = max(1, min(6, len(combustible_ids) // 8))
        for event_index in range(event_count):
            node_id = combustible_ids[_pick(seed, "fire.node", graph_index * 54000 + event_index, len(combustible_ids))]
            tick = int(2 + _pick(seed, "fire.tick", graph_index * 55000 + event_index, max(2, tick_horizon - 2)))
            rows.append(
                {
                    "event_id": "event.therm.ignite.{}.{}".format(str(graph_index + 1).zfill(3), str(event_index + 1).zfill(3)),
                    "graph_id": graph_id,
                    "target_id": node_id,
                    "tick": int(tick),
                    "material_id": _material_for_index(seed=seed, index=graph_index * 56000 + event_index),
                    "initial_fuel": int(300 + _pick(seed, "fire.fuel", graph_index * 57000 + event_index, 1800)),
                }
            )
    return sorted(rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))


def generate_therm_stress_scenario(
    *,
    seed: int,
    node_count: int,
    link_count: int,
    radiator_count: int,
    graph_count: int,
    tick_horizon: int,
    include_fire_ignitions: bool,
) -> dict:
    seed_i = int(max(1, _as_int(seed, 1)))
    graph_count_i = int(max(1, _as_int(graph_count, 1)))
    node_count_i = int(max(8, _as_int(node_count, 8)))
    link_count_i = int(max(node_count_i, _as_int(link_count, node_count_i)))
    radiator_count_i = int(max(0, min(node_count_i, _as_int(radiator_count, 0))))
    tick_horizon_i = int(max(8, _as_int(tick_horizon, 64)))

    node_count_per_graph = int(max(8, node_count_i // graph_count_i))
    edge_count_per_graph = int(max(node_count_per_graph, link_count_i // graph_count_i))
    radiator_count_per_graph = int(max(0, radiator_count_i // graph_count_i))

    graph_rows = _graph_rows(
        seed=seed_i,
        graph_count=graph_count_i,
        node_count_per_graph=node_count_per_graph,
        edge_count_per_graph=edge_count_per_graph,
        radiator_count_per_graph=radiator_count_per_graph,
    )
    heat_rows = _periodic_heat_sources(seed=seed_i, graphs=graph_rows, tick_horizon=tick_horizon_i)
    fire_rows = _fire_ignitions(
        seed=seed_i,
        graphs=graph_rows,
        include_fire_ignitions=bool(include_fire_ignitions),
        tick_horizon=tick_horizon_i,
    )

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": "scenario.therm.stress.{}".format(
            canonical_sha256(
                {
                    "seed": int(seed_i),
                    "graph_count": int(graph_count_i),
                    "node_count": int(node_count_i),
                    "link_count": int(link_count_i),
                    "radiator_count": int(radiator_count_i),
                    "tick_horizon": int(tick_horizon_i),
                    "include_fire_ignitions": bool(include_fire_ignitions),
                }
            )[:12]
        ),
        "seed": int(seed_i),
        "tick_horizon": int(tick_horizon_i),
        "thermal_network_graphs": [copy.deepcopy(row) for row in graph_rows],
        "periodic_heat_source_rows": [copy.deepcopy(row) for row in heat_rows],
        "fire_ignition_rows": [copy.deepcopy(row) for row in fire_rows],
        "initial_state_snapshot": {
            "schema_version": "1.0.0",
            "thermal_network_graphs": [copy.deepcopy(row) for row in graph_rows],
            "thermal_fire_states": [],
            "thermal_fire_events": [],
            "thermal_heat_input_rows": [],
            "control_decision_log": [],
            "simulation_time": {
                "tick": 0,
                "tick_rate": 1,
                "deterministic_clock": {
                    "tick_duration_ms": 1000,
                },
            },
        },
        "deterministic_fingerprint": "",
        "extensions": {
            "node_count": int(node_count_i),
            "link_count": int(link_count_i),
            "radiator_count": int(radiator_count_i),
            "graph_count": int(graph_count_i),
            "include_fire_ignitions": bool(include_fire_ignitions),
            "node_count_per_graph": int(node_count_per_graph),
            "edge_count_per_graph": int(edge_count_per_graph),
            "radiator_count_per_graph": int(radiator_count_per_graph),
        },
    }
    seed_payload = dict(scenario)
    seed_payload["deterministic_fingerprint"] = ""
    scenario["deterministic_fingerprint"] = canonical_sha256(seed_payload)
    return scenario


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic THERM-5 stress scenario.")
    parser.add_argument("--seed", type=int, default=7501)
    parser.add_argument("--node-count", type=int, default=256)
    parser.add_argument("--link-count", type=int, default=512)
    parser.add_argument("--radiator-count", type=int, default=64)
    parser.add_argument("--graph-count", type=int, default=4)
    parser.add_argument("--tick-horizon", type=int, default=64)
    parser.add_argument("--include-fire-ignitions", action="store_true")
    parser.add_argument("--output", default="build/thermal/therm_stress_scenario.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario = generate_therm_stress_scenario(
        seed=int(args.seed),
        node_count=int(args.node_count),
        link_count=int(args.link_count),
        radiator_count=int(args.radiator_count),
        graph_count=int(args.graph_count),
        tick_horizon=int(args.tick_horizon),
        include_fire_ignitions=bool(args.include_fire_ignitions),
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, scenario)
    result = {
        "result": "complete",
        "scenario_id": str(scenario.get("scenario_id", "")),
        "output_path": output_abs,
        "deterministic_fingerprint": str(scenario.get("deterministic_fingerprint", "")),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
