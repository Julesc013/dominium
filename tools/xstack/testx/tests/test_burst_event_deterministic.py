"""FAST test: burst events are deterministic for equivalent FLUID-2 inputs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_burst_event_deterministic"
TEST_TAGS = ["fast", "fluid", "containment", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _graph_payload() -> dict:
    return {
        "graph_id": "graph.fluid.burst",
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
                "node_id": "node.vessel.b",
                "node_type_id": "fluid.node.pressure_vessel",
                "payload": {
                    "node_kind": "pressure_vessel",
                    "fluid_profile_id": "fluid.water",
                    "model_bindings": [],
                    "safety_instances": ["instance.safety.burst_disk.node.vessel.b"],
                    "state_ref": {
                        "pressure_head": 200,
                        "relief_threshold": 120,
                        "burst_threshold": 160,
                        "burst_sink_kind": "external",
                    },
                    "extensions": {},
                },
            }
        ],
        "edges": [],
        "extensions": {},
    }


def _run_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.fluid import solve_fluid_network_f1

    return solve_fluid_network_f1(
        graph_row=_graph_payload(),
        current_tick=22,
        tank_state_rows=[
            {
                "node_id": "node.vessel.b",
                "stored_mass": 100,
                "max_mass": 100,
                "last_update_tick": 21,
                "extensions": {},
            }
        ],
        failure_policy_row={
            "relief_preferred": False,
            "max_failure_events_per_tick": 8,
        },
    )


def run(repo_root: str):
    first = _run_once(repo_root)
    second = _run_once(repo_root)
    burst_a = [dict(row) for row in list(first.get("burst_event_rows") or []) if isinstance(row, dict)]
    burst_b = [dict(row) for row in list(second.get("burst_event_rows") or []) if isinstance(row, dict)]
    if not burst_a:
        return {"status": "fail", "message": "expected burst event rows"}
    if burst_a != burst_b:
        return {"status": "fail", "message": "burst rows drifted across equivalent runs"}
    hash_a = str(first.get("burst_hash_chain", "")).strip().lower()
    hash_b = str(second.get("burst_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(hash_a)) or (not _HASH64.fullmatch(hash_b)):
        return {"status": "fail", "message": "burst_hash_chain missing/invalid"}
    if hash_a != hash_b:
        return {"status": "fail", "message": "burst_hash_chain drifted across equivalent runs"}
    return {"status": "pass", "message": "burst events are deterministic"}