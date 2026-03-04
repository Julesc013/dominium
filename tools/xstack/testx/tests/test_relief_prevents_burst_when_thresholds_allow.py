"""FAST test: relief path vents overpressure without burst when thresholds allow."""

from __future__ import annotations

import sys


TEST_ID = "test_relief_prevents_burst_when_thresholds_allow"
TEST_TAGS = ["fast", "fluid", "containment", "safety"]


def _graph_payload() -> dict:
    return {
        "graph_id": "graph.fluid.relief",
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
                "node_id": "node.vessel.a",
                "node_type_id": "fluid.node.pressure_vessel",
                "payload": {
                    "node_kind": "pressure_vessel",
                    "fluid_profile_id": "fluid.water",
                    "model_bindings": [],
                    "safety_instances": ["instance.safety.pressure_relief.node.vessel.a"],
                    "state_ref": {
                        "pressure_head": 150,
                        "relief_threshold": 120,
                        "burst_threshold": 260,
                    },
                    "extensions": {},
                },
            }
        ],
        "edges": [],
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.fluid import solve_fluid_network_f1

    result = solve_fluid_network_f1(
        graph_row=_graph_payload(),
        current_tick=11,
        tank_state_rows=[
            {
                "node_id": "node.vessel.a",
                "stored_mass": 100,
                "max_mass": 100,
                "last_update_tick": 10,
                "extensions": {},
            }
        ],
        failure_policy_row={
            "relief_preferred": True,
            "max_failure_events_per_tick": 8,
        },
    )
    relief_rows = [dict(row) for row in list(result.get("relief_event_rows") or []) if isinstance(row, dict)]
    burst_rows = [dict(row) for row in list(result.get("burst_event_rows") or []) if isinstance(row, dict)]
    if not relief_rows:
        return {"status": "fail", "message": "expected at least one relief event"}
    if burst_rows:
        return {"status": "fail", "message": "burst should not fire when head is below burst_threshold"}
    return {"status": "pass", "message": "relief path prevented burst as expected"}