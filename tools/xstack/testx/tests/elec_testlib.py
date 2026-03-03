"""Shared ELEC-1 TestX fixtures."""

from __future__ import annotations

import copy
from typing import List


def law_profile(allowed_processes: List[str]) -> dict:
    from tools.xstack.testx.tests.construction_testlib import law_profile as construction_law_profile

    rows = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    law = construction_law_profile(rows)
    entitlements = dict(law.get("process_entitlement_requirements") or {})
    privileges = dict(law.get("process_privilege_requirements") or {})
    for process_id in rows:
        if process_id == "process.elec.connect_wire":
            entitlements[process_id] = "entitlement.control.admin"
            privileges[process_id] = "operator"
        elif process_id in {"process.elec.flip_breaker", "process.elec.lockout_tagout"}:
            entitlements[process_id] = "entitlement.tool.operating"
            privileges[process_id] = "operator"
        elif process_id == "process.elec.network_tick":
            entitlements[process_id] = "session.boot"
            privileges[process_id] = "observer"
    law["process_entitlement_requirements"] = entitlements
    law["process_privilege_requirements"] = privileges
    return law


def authority_context() -> dict:
    from tools.xstack.testx.tests.construction_testlib import authority_context as construction_authority_context

    return construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.tool.operating", "entitlement.inspect"],
        privilege_level="operator",
    )


def policy_context(
    *,
    max_compute_units_per_tick: int = 4096,
    e1_enabled: bool = True,
    max_network_solves_per_tick: int = 16,
    max_edges_per_network: int = 2048,
    spec_sheet_rows: List[dict] | None = None,
) -> dict:
    from tools.xstack.testx.tests.construction_testlib import policy_context as construction_policy_context

    policy = copy.deepcopy(construction_policy_context(max_compute_units_per_tick=int(max_compute_units_per_tick)))
    policy["elec_e1_enabled"] = bool(e1_enabled)
    policy["elec_max_network_solves_per_tick"] = int(max(1, int(max_network_solves_per_tick)))
    policy["elec_max_edges_per_network"] = int(max(0, int(max_edges_per_network)))
    if isinstance(spec_sheet_rows, list):
        policy["spec_sheet_rows"] = [dict(row) for row in spec_sheet_rows if isinstance(row, dict)]
    return policy


def base_state(*, current_tick: int = 0) -> dict:
    from tools.xstack.testx.tests.construction_testlib import base_state as construction_base_state

    state = copy.deepcopy(construction_base_state())
    state["simulation_time"] = {
        "tick": int(max(0, int(current_tick))),
        "tick_rate": 1,
        "deterministic_clock": {"tick_duration_ms": 1000},
    }
    state.setdefault("model_bindings", [])
    state.setdefault("power_network_graphs", [])
    state.setdefault("elec_flow_channels", [])
    state.setdefault("elec_edge_status_rows", [])
    state.setdefault("elec_node_status_rows", [])
    state.setdefault("elec_network_runtime_state", {"extensions": {}})
    state.setdefault("safety_instances", [])
    state.setdefault("safety_events", [])
    state.setdefault(
        "safety_runtime_state",
        {
            "schema_version": "1.0.0",
            "last_tick": 0,
            "last_budget_outcome": "complete",
            "last_processed_instance_count": 0,
            "last_deferred_instance_count": 0,
            "last_triggered_instance_count": 0,
            "last_event_count": 0,
            "heartbeat_rows": [],
            "extensions": {},
        },
    )
    return state


def model_binding_rows(
    *,
    resistive_demand_p: int = 80,
    motor_demand_p: int = 60,
    motor_pf_permille: int = 850,
) -> List[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "binding_id": "binding.elec.load.resistive",
            "model_id": "model.elec_load_resistive_stub",
            "target_kind": "node",
            "target_id": "node.elec.load.main",
            "tier": "meso",
            "parameters": {"demand_p": int(max(0, int(resistive_demand_p)))},
            "enabled": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "binding_id": "binding.elec.load.motor",
            "model_id": "model.elec_load_motor_stub",
            "target_kind": "node",
            "target_id": "node.elec.load.main",
            "tier": "meso",
            "parameters": {
                "demand_p": int(max(0, int(motor_demand_p))),
                "pf_permille": int(max(1, min(1000, int(motor_pf_permille)))),
            },
            "enabled": True,
            "deterministic_fingerprint": "",
            "extensions": {},
        },
    ]


def build_power_graph(
    *,
    graph_id: str = "graph.elec.main",
    edge_count: int = 1,
    resistance_proxy: int = 10,
    capacity_rating: int = 240,
    with_edge_spec: bool = False,
) -> dict:
    node_rows = [
        {
            "node_id": "node.elec.bus.main",
            "node_type_id": "node.elec.bus",
            "tags": ["electric", "bus"],
            "payload": {
                "schema_version": "1.0.0",
                "node_kind": "bus",
                "spec_id": None,
                "model_bindings": [],
                "safety_instances": [],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
        },
        {
            "node_id": "node.elec.load.main",
            "node_type_id": "node.elec.load",
            "tags": ["electric", "load"],
            "payload": {
                "schema_version": "1.0.0",
                "node_kind": "load",
                "spec_id": None,
                "model_bindings": [
                    "binding.elec.load.resistive",
                    "binding.elec.load.motor",
                ],
                "safety_instances": [],
                "deterministic_fingerprint": "",
                "extensions": {},
            },
        },
    ]
    edge_rows = []
    for index in range(max(1, int(edge_count))):
        edge_id = "edge.elec.main" if int(edge_count) == 1 else "edge.elec.main.{}".format(index + 1)
        edge_rows.append(
            {
                "edge_id": edge_id,
                "from_node_id": "node.elec.bus.main",
                "to_node_id": "node.elec.load.main",
                "edge_type_id": "edge.elec.conductor",
                "capacity": int(max(0, int(capacity_rating))),
                "delay_ticks": 0,
                "cost_units": 1,
                "payload": {
                    "schema_version": "1.0.0",
                    "edge_kind": "conductor",
                    "length": 1000,
                    "resistance_proxy": int(max(0, int(resistance_proxy))),
                    "capacity_rating": int(max(0, int(capacity_rating))),
                    "spec_id": "spec.elec.edge.main" if bool(with_edge_spec) else None,
                    "deterministic_fingerprint": "",
                    "extensions": {},
                },
                "extensions": {},
            }
        )
    return {
        "schema_version": "1.0.0",
        "graph_id": str(graph_id),
        "node_type_schema_id": "dominium.schema.electric.elec_node_payload.v1",
        "edge_type_schema_id": "dominium.schema.electric.elec_edge_payload.v1",
        "payload_schema_versions": {
            "dominium.schema.electric.elec_node_payload.v1": "1.0.0",
            "dominium.schema.electric.elec_edge_payload.v1": "1.0.0",
        },
        "validation_mode": "strict",
        "deterministic_routing_policy_id": "route.shortest_delay",
        "graph_partition_id": None,
        "nodes": node_rows,
        "edges": edge_rows,
        "extensions": {},
    }


def mismatched_spec_rows() -> List[dict]:
    return [
        {
            "schema_version": "1.0.0",
            "spec_id": "spec.elec.connector.main",
            "spec_type_id": "spec.track",
            "description": "Connector-side electrical compatibility fixture.",
            "parameters": {
                "gauge_mm": 1000,
                "connector_type": "A",
                "voltage_rating": 400,
                "current_rating": 40,
            },
            "tolerance_policy_id": "tol.default",
            "compliance_check_ids": [],
            "version_introduced": "1.0.0",
            "deprecated": False,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "spec_id": "spec.elec.edge.main",
            "spec_type_id": "spec.track",
            "description": "Edge-side electrical compatibility fixture.",
            "parameters": {
                "gauge_mm": 1000,
                "connector_type": "B",
                "voltage_rating": 240,
                "current_rating": 20,
            },
            "tolerance_policy_id": "tol.default",
            "compliance_check_ids": [],
            "version_introduced": "1.0.0",
            "deprecated": False,
            "extensions": {},
        },
    ]

