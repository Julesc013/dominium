"""FAST test: CHEM-3 scaling effects reduce FLUID edge effective capacity deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_scaling_reduces_pipe_capacity"
TEST_TAGS = ["fast", "chem", "fluid", "degradation", "coupling"]


def _graph_payload() -> dict:
    return {
        "graph_id": "graph.fluid.scaling",
        "node_type_schema_id": "dominium.schema.fluid.fluid_node_payload",
        "edge_type_schema_id": "dominium.schema.fluid.fluid_edge_payload",
        "payload_schema_versions": {
            "dominium.schema.fluid.fluid_node_payload": "1.0.0",
            "dominium.schema.fluid.fluid_edge_payload": "1.0.0",
        },
        "validation_mode": "strict",
        "deterministic_routing_policy_id": "route.direct",
        "nodes": [
            {
                "node_id": "node.tank.source",
                "node_type_id": "fluid.node.tank",
                "payload": {
                    "node_kind": "tank",
                    "fluid_profile_id": "fluid.water",
                    "model_bindings": [],
                    "safety_instances": [],
                    "state_ref": {"stored_mass": 120, "max_mass": 120, "pressure_head": 180},
                    "extensions": {},
                },
            },
            {
                "node_id": "node.tank.sink",
                "node_type_id": "fluid.node.tank",
                "payload": {
                    "node_kind": "tank",
                    "fluid_profile_id": "fluid.water",
                    "model_bindings": [],
                    "safety_instances": [],
                    "state_ref": {"stored_mass": 0, "max_mass": 120, "pressure_head": 0},
                    "extensions": {},
                },
            },
        ],
        "edges": [
            {
                "edge_id": "edge.fluid.main",
                "from_node_id": "node.tank.source",
                "to_node_id": "node.tank.sink",
                "edge_type_id": "fluid.edge.pipe",
                "capacity": 0,
                "delay_ticks": 0,
                "cost_units": 1,
                "payload": {
                    "edge_kind": "pipe",
                    "length": 100,
                    "diameter_proxy": 80,
                    "roughness_proxy": 10,
                    "capacity_rating": 100,
                    "model_bindings": [],
                    "extensions": {},
                },
                "extensions": {},
            }
        ],
        "extensions": {},
    }


def _first_edge(result: dict) -> dict:
    rows = [dict(row) for row in list(result.get("edge_flow_rows") or []) if isinstance(row, dict)]
    return rows[0] if rows else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from fluid.network.fluid_network_engine import solve_fluid_network_f1
    from tools.xstack.testx.tests.chem_degradation_testlib import (
        execute_process,
        load_registry_payload,
        seed_degradation_state,
    )

    state = seed_degradation_state()
    tick = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.degradation_tick",
        inputs={
            "target_id": "edge.fluid.main",
            "profile_id": "profile.tank_basic",
            "target_kind": "edge",
            "parameters": {
                "mass_flow": 900,
                "temperature": 38215,
                "hardness_tag": "hard_scale",
            },
        },
    )
    if str(tick.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "degradation_tick refused for scaling fixture"}

    effect_rows = [
        dict(row)
        for row in list(state.get("effect_rows") or [])
        if isinstance(row, dict)
        and str(row.get("target_id", "")).strip() == "edge.fluid.main"
        and str(row.get("effect_type_id", "")).strip() == "effect.pipe_capacity_reduction"
    ]
    if not effect_rows:
        return {"status": "fail", "message": "missing effect.pipe_capacity_reduction rows for scaling fixture"}

    effect_type_registry = load_registry_payload(repo_root, "data/registries/effect_type_registry.json")
    stacking_policy_registry = load_registry_payload(repo_root, "data/registries/stacking_policy_registry.json")
    graph = _graph_payload()
    tank_rows = [
        {"node_id": "node.tank.source", "stored_mass": 120, "max_mass": 120, "last_update_tick": 0, "extensions": {}},
        {"node_id": "node.tank.sink", "stored_mass": 0, "max_mass": 120, "last_update_tick": 0, "extensions": {}},
    ]

    # Degradation effects are one-tick; evaluate at the same tick they are applied.
    baseline = solve_fluid_network_f1(
        graph_row=graph,
        current_tick=0,
        tank_state_rows=tank_rows,
        effect_rows=[],
        effect_type_registry=effect_type_registry,
        stacking_policy_registry=stacking_policy_registry,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    degraded = solve_fluid_network_f1(
        graph_row=graph,
        current_tick=0,
        tank_state_rows=tank_rows,
        effect_rows=effect_rows,
        effect_type_registry=effect_type_registry,
        stacking_policy_registry=stacking_policy_registry,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    if str(baseline.get("mode", "")).strip() != "F1" or str(degraded.get("mode", "")).strip() != "F1":
        return {"status": "fail", "message": "expected F1 solve mode for scaling fixture"}

    base_edge = _first_edge(baseline)
    degraded_edge = _first_edge(degraded)
    if not base_edge or not degraded_edge:
        return {"status": "fail", "message": "missing edge_flow_rows for scaling fixture"}

    base_capacity = int(base_edge.get("capacity_effective", 0) or 0)
    degraded_capacity = int(degraded_edge.get("capacity_effective", 0) or 0)
    if base_capacity <= 0:
        return {"status": "fail", "message": "baseline effective capacity should be positive"}
    if degraded_capacity >= base_capacity:
        return {
            "status": "fail",
            "message": "scaling should reduce effective capacity (baseline={}, degraded={})".format(
                base_capacity,
                degraded_capacity,
            ),
        }
    return {"status": "pass", "message": "scaling effect deterministically reduces fluid capacity"}
