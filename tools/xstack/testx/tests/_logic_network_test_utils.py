"""Shared deterministic fixtures for LOGIC-3 network tests."""

from __future__ import annotations

import json
import os


_NODE_SCHEMA_ID = "dominium.schema.logic.logic_node_payload"
_EDGE_SCHEMA_ID = "dominium.schema.logic.logic_edge_payload"


def _load_json(repo_root: str, rel_path: str) -> dict:
    abs_path = os.path.join(repo_root, rel_path.replace("/", os.sep))
    payload = json.load(open(abs_path, "r", encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _rows(payload: dict, key: str) -> list[dict]:
    record = dict(payload.get("record") or {})
    rows = record.get(key)
    if not isinstance(rows, list):
        rows = payload.get(key)
    return [dict(item) for item in list(rows or []) if isinstance(item, dict)]


def validation_inputs(repo_root: str) -> dict:
    return {
        "logic_network_policy_registry_payload": _load_json(repo_root, "data/registries/logic_network_policy_registry.json"),
        "logic_node_kind_registry_payload": _load_json(repo_root, "data/registries/logic_node_kind_registry.json"),
        "logic_edge_kind_registry_payload": _load_json(repo_root, "data/registries/logic_edge_kind_registry.json"),
        "signal_type_registry_payload": _load_json(repo_root, "data/registries/signal_type_registry.json"),
        "carrier_type_registry_payload": _load_json(repo_root, "data/registries/carrier_type_registry.json"),
        "signal_delay_policy_registry_payload": _load_json(repo_root, "data/registries/signal_delay_policy_registry.json"),
        "signal_noise_policy_registry_payload": _load_json(repo_root, "data/registries/signal_noise_policy_registry.json"),
        "protocol_registry_payload": _load_json(repo_root, "data/registries/protocol_registry.json"),
        "logic_element_rows": _rows(_load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_element_registry.json"), "logic_elements"),
        "logic_behavior_model_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_behavior_model_registry.json"),
            "logic_behavior_models",
        ),
        "interface_signature_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_interface_signatures.json"),
            "logic_interface_signatures",
        ),
        "bus_definition_rows": [],
    }


def binding_row(*, network_id: str, graph_id: str, policy_id: str = "logic.policy.default", extensions: dict | None = None) -> dict:
    from logic.network import build_logic_network_binding_row

    return build_logic_network_binding_row(
        network_id=str(network_id),
        graph_id=str(graph_id),
        policy_id=str(policy_id),
        extensions=dict(extensions or {}),
    )


def node_row(
    *,
    node_id: str,
    node_kind: str,
    element_instance_id: str | None = None,
    port_id: str | None = None,
    bus_id: str | None = None,
    protocol_id: str | None = None,
    payload_extensions: dict | None = None,
    node_extensions: dict | None = None,
    tags: list[str] | None = None,
) -> dict:
    from logic.network import build_logic_node_payload_row

    payload = build_logic_node_payload_row(
        node_kind=node_kind,
        element_instance_id=element_instance_id,
        port_id=port_id,
        bus_id=bus_id,
        protocol_id=protocol_id,
        extensions=dict(payload_extensions or {}),
    )
    return {
        "schema_version": "1.0.0",
        "node_id": str(node_id),
        "node_type_id": "node.logic.{}".format(str(payload.get("node_kind", "")).strip()),
        "payload": payload,
        "tags": list(tags or []),
        "extensions": dict(node_extensions or {}),
    }


def edge_row(
    *,
    edge_id: str,
    from_node_id: str,
    to_node_id: str,
    edge_kind: str,
    signal_type_id: str,
    carrier_type_id: str = "carrier.electrical",
    delay_policy_id: str = "delay.none",
    noise_policy_id: str = "noise.none",
    protocol_id: str | None = None,
    capacity: int | None = None,
    payload_extensions: dict | None = None,
    edge_extensions: dict | None = None,
) -> dict:
    from logic.network import build_logic_edge_payload_row

    payload = build_logic_edge_payload_row(
        edge_kind=edge_kind,
        signal_type_id=signal_type_id,
        carrier_type_id=carrier_type_id,
        delay_policy_id=delay_policy_id,
        noise_policy_id=noise_policy_id,
        protocol_id=protocol_id,
        capacity=capacity,
        extensions=dict(payload_extensions or {}),
    )
    return {
        "schema_version": "1.0.0",
        "edge_id": str(edge_id),
        "from_node_id": str(from_node_id),
        "to_node_id": str(to_node_id),
        "edge_type_id": "edge.logic.{}".format(str(payload.get("edge_kind", "")).strip()),
        "payload": payload,
        "capacity": capacity,
        "delay_ticks": None,
        "loss_fraction": None,
        "cost_units": None,
        "extensions": dict(edge_extensions or {}),
    }


def graph_row(*, graph_id: str, nodes: list[dict], edges: list[dict], extensions: dict | None = None) -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": str(graph_id),
        "node_type_schema_id": _NODE_SCHEMA_ID,
        "edge_type_schema_id": _EDGE_SCHEMA_ID,
        "payload_schema_versions": {
            _NODE_SCHEMA_ID: "1.0.0",
            _EDGE_SCHEMA_ID: "1.0.0",
        },
        "validation_mode": "strict",
        "graph_partition_id": None,
        "nodes": [dict(row) for row in list(nodes or [])],
        "edges": [dict(row) for row in list(edges or [])],
        "deterministic_routing_policy_id": "route.direct_only",
        "extensions": dict(extensions or {}),
    }


def validate(repo_root: str, *, binding: dict, graph: dict) -> dict:
    from logic.network import validate_logic_network

    return validate_logic_network(
        binding_row=dict(binding),
        graph_row=dict(graph),
        **validation_inputs(repo_root),
    )
