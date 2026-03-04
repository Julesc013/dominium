"""Shared THERM-1 TestX fixtures."""

from __future__ import annotations

from typing import List


def build_thermal_graph(
    *,
    graph_id: str = "graph.therm.main",
    source_energy: int = 2000,
    sink_energy: int = 200,
    source_capacity: int = 100,
    sink_capacity: int = 100,
    conductance_value: int = 40,
) -> dict:
    node_rows = [
        {
            "node_id": "node.therm.source",
            "node_type_id": "node.therm.mass",
            "tags": ["thermal", "source"],
            "payload": {
                "schema_version": "1.0.0",
                "node_kind": "source",
                "heat_capacity_value": int(max(1, int(source_capacity))),
                "current_thermal_energy": int(max(0, int(source_energy))),
                "spec_id": None,
                "model_bindings": [
                    "binding.therm.loss_to_temp.node.therm.source",
                    "binding.therm.heat_capacity.node.therm.source",
                ],
                "safety_instances": ["instance.safety.overtemp.node.therm.source"],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
        },
        {
            "node_id": "node.therm.sink",
            "node_type_id": "node.therm.mass",
            "tags": ["thermal", "sink"],
            "payload": {
                "schema_version": "1.0.0",
                "node_kind": "sink",
                "heat_capacity_value": int(max(1, int(sink_capacity))),
                "current_thermal_energy": int(max(0, int(sink_energy))),
                "spec_id": None,
                "model_bindings": [
                    "binding.therm.loss_to_temp.node.therm.sink",
                    "binding.therm.heat_capacity.node.therm.sink",
                ],
                "safety_instances": ["instance.safety.overtemp.node.therm.sink"],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
        },
    ]
    edge_rows = [
        {
            "edge_id": "edge.therm.main",
            "from_node_id": "node.therm.source",
            "to_node_id": "node.therm.sink",
            "edge_type_id": "edge.therm.conduction",
            "capacity": 0,
            "delay_ticks": 0,
            "cost_units": 1,
            "payload": {
                "schema_version": "1.0.0",
                "edge_kind": "conduction_link",
                "conductance_value": int(max(0, int(conductance_value))),
                "spec_id": None,
                "model_bindings": ["binding.therm.conductance.edge.therm.main"],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
            "extensions": {},
        }
    ]
    return {
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
        "nodes": node_rows,
        "edges": edge_rows,
        "extensions": {},
    }


def heat_input_rows(*, source_heat: int = 0, sink_heat: int = 0) -> List[dict]:
    rows = []
    if int(source_heat) > 0:
        rows.append({"node_id": "node.therm.source", "heat_input": int(max(0, int(source_heat)))})
    if int(sink_heat) > 0:
        rows.append({"node_id": "node.therm.sink", "heat_input": int(max(0, int(sink_heat)))})
    return rows
