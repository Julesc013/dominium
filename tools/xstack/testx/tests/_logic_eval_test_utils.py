"""Shared deterministic fixtures for LOGIC-4 evaluation tests."""

from __future__ import annotations

import json
import os

from tools.xstack.testx.tests._logic_network_test_utils import binding_row, edge_row, graph_row, node_row


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


def load_eval_inputs(repo_root: str) -> dict:
    state_vector_rows = _rows(_load_json(repo_root, "data/registries/state_vector_registry.json"), "state_vector_definitions")
    state_vector_rows.extend(
        _rows(_load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_state_vectors.json"), "state_vector_definitions")
    )
    return {
        "signal_type_registry_payload": _load_json(repo_root, "data/registries/signal_type_registry.json"),
        "carrier_type_registry_payload": _load_json(repo_root, "data/registries/carrier_type_registry.json"),
        "signal_delay_policy_registry_payload": _load_json(repo_root, "data/registries/signal_delay_policy_registry.json"),
        "signal_noise_policy_registry_payload": _load_json(repo_root, "data/registries/signal_noise_policy_registry.json"),
        "bus_encoding_registry_payload": _load_json(repo_root, "data/registries/bus_encoding_registry.json"),
        "protocol_registry_payload": _load_json(repo_root, "data/registries/protocol_registry.json"),
        "logic_policy_registry_payload": _load_json(repo_root, "data/registries/logic_policy_registry.json"),
        "logic_network_policy_registry_payload": _load_json(repo_root, "data/registries/logic_network_policy_registry.json"),
        "logic_element_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_element_registry.json"),
            "logic_elements",
        ),
        "logic_behavior_model_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_behavior_model_registry.json"),
            "logic_behavior_models",
        ),
        "logic_interface_signature_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_interface_signatures.json"),
            "logic_interface_signatures",
        ),
        "logic_state_machine_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_state_machine_registry.json"),
            "state_machine_definitions",
        ),
        "watchdog_definition_rows": _rows(
            _load_json(repo_root, "packs/core/pack.core.logic_base/data/logic_watchdog_definitions.json"),
            "watchdog_definitions",
        ),
        "state_vector_definition_rows": state_vector_rows,
        "compute_budget_profile_registry_payload": _load_json(
            repo_root, "data/registries/compute_budget_profile_registry.json"
        ),
        "compute_degrade_policy_registry_payload": _load_json(
            repo_root, "data/registries/compute_degrade_policy_registry.json"
        ),
        "tolerance_policy_registry_payload": _load_json(repo_root, "data/registries/tolerance_policy_registry.json"),
        "temporal_domain_registry_payload": _load_json(repo_root, "data/registries/temporal_domain_registry.json"),
        "time_mapping_registry_payload": _load_json(repo_root, "data/registries/time_mapping_registry.json"),
        "drift_policy_registry_payload": _load_json(repo_root, "data/registries/drift_policy_registry.json"),
        "model_type_registry_payload": _load_json(repo_root, "data/registries/model_type_registry.json"),
        "constitutive_model_registry_payload": _load_json(repo_root, "data/registries/constitutive_model_registry.json"),
    }


def make_chain_network(
    *,
    network_id: str,
    delay_policy_id: str = "delay.none",
    delay_extensions: dict | None = None,
    binding_extensions: dict | None = None,
) -> tuple[dict, dict]:
    binding = binding_row(
        network_id=network_id,
        graph_id="graph.{}".format(network_id),
        policy_id="logic.policy.default",
        extensions=dict({"validation_status": "validated", "logic_policy_id": "logic.default"}, **dict(binding_extensions or {})),
    )
    nodes = [
        node_row(
            node_id="node.and.in.a",
            node_kind="port_in",
            element_instance_id="inst.logic.and.1",
            port_id="in.a",
            payload_extensions={"element_definition_id": "logic.and"},
        ),
        node_row(
            node_id="node.and.in.b",
            node_kind="port_in",
            element_instance_id="inst.logic.and.1",
            port_id="in.b",
            payload_extensions={"element_definition_id": "logic.and"},
        ),
        node_row(
            node_id="node.and.out.q",
            node_kind="port_out",
            element_instance_id="inst.logic.and.1",
            port_id="out.q",
            payload_extensions={"element_definition_id": "logic.and"},
        ),
        node_row(
            node_id="node.not.in.a",
            node_kind="port_in",
            element_instance_id="inst.logic.not.1",
            port_id="in.a",
            payload_extensions={"element_definition_id": "logic.not"},
        ),
        node_row(
            node_id="node.not.out.q",
            node_kind="port_out",
            element_instance_id="inst.logic.not.1",
            port_id="out.q",
            payload_extensions={"element_definition_id": "logic.not"},
        ),
    ]
    edges = [
        edge_row(
            edge_id="edge.and.to.not",
            from_node_id="node.and.out.q",
            to_node_id="node.not.in.a",
            edge_kind="link",
            signal_type_id="signal.boolean",
            delay_policy_id=delay_policy_id,
            payload_extensions=dict(delay_extensions or {}),
        )
    ]
    graph = graph_row(graph_id=binding["graph_id"], nodes=nodes, edges=edges)
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [
            {
                "tick": 0,
                "network_id": network_id,
                "validation_hash": "validated",
                "loop_classifications": [],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state


def make_loop_network(*, network_id: str) -> tuple[dict, dict]:
    binding = binding_row(
        network_id=network_id,
        graph_id="graph.{}".format(network_id),
        policy_id="logic.policy.default",
        extensions={"validation_status": "validated", "logic_policy_id": "logic.default"},
    )
    nodes = [
        node_row(
            node_id="node.not.in.a",
            node_kind="port_in",
            element_instance_id="inst.logic.not.1",
            port_id="in.a",
            payload_extensions={"element_definition_id": "logic.not"},
        ),
        node_row(
            node_id="node.not.out.q",
            node_kind="port_out",
            element_instance_id="inst.logic.not.1",
            port_id="out.q",
            payload_extensions={"element_definition_id": "logic.not"},
        ),
    ]
    edges = [
        edge_row(
            edge_id="edge.loop",
            from_node_id="node.not.out.q",
            to_node_id="node.not.in.a",
            edge_kind="link",
            signal_type_id="signal.boolean",
        )
    ]
    graph = graph_row(graph_id=binding["graph_id"], nodes=nodes, edges=edges)
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [
            {
                "tick": 0,
                "network_id": network_id,
                "validation_hash": "loop.refused",
                "loop_classifications": [
                    {
                        "classification": "combinational",
                        "node_ids": ["node.not.in.a", "node.not.out.q"],
                        "element_instance_ids": ["inst.logic.not.1"],
                        "behavior_kinds": ["combinational"],
                        "policy_resolution": "refuse",
                        "requires_l2_roi": False,
                    }
                ],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state


def make_watchdog_network(*, network_id: str) -> tuple[dict, dict]:
    binding = binding_row(
        network_id=network_id,
        graph_id="graph.{}".format(network_id),
        policy_id="logic.policy.default",
        extensions={"validation_status": "validated", "logic_policy_id": "logic.default"},
    )
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(
                node_id="node.watchdog.enable",
                node_kind="port_in",
                element_instance_id="inst.logic.watchdog.1",
                port_id="in.enable",
                payload_extensions={"element_definition_id": "logic.watchdog_basic"},
            ),
            node_row(
                node_id="node.watchdog.observe",
                node_kind="port_in",
                element_instance_id="inst.logic.watchdog.1",
                port_id="in.observe",
                payload_extensions={"element_definition_id": "logic.watchdog_basic"},
            ),
            node_row(
                node_id="node.watchdog.timeout",
                node_kind="port_out",
                element_instance_id="inst.logic.watchdog.1",
                port_id="out.timeout",
                payload_extensions={"element_definition_id": "logic.watchdog_basic"},
            ),
        ],
        edges=[],
    )
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [
            {
                "tick": 0,
                "network_id": network_id,
                "validation_hash": "watchdog.validated",
                "loop_classifications": [],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state


def make_relay_feedback_oscillator_network(*, network_id: str) -> tuple[dict, dict]:
    binding = binding_row(
        network_id=network_id,
        graph_id="graph.{}".format(network_id),
        policy_id="logic.policy.default",
        extensions={"validation_status": "validated", "logic_policy_id": "logic.default"},
    )
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(
                node_id="node.relay.in.coil",
                node_kind="port_in",
                element_instance_id="inst.logic.relay.1",
                port_id="in.coil",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
            node_row(
                node_id="node.relay.in.reset",
                node_kind="port_in",
                element_instance_id="inst.logic.relay.1",
                port_id="in.reset",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
            node_row(
                node_id="node.relay.out.q",
                node_kind="port_out",
                element_instance_id="inst.logic.relay.1",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.relay"},
            ),
            node_row(
                node_id="node.not.in.a",
                node_kind="port_in",
                element_instance_id="inst.logic.not.1",
                port_id="in.a",
                payload_extensions={"element_definition_id": "logic.not"},
            ),
            node_row(
                node_id="node.not.out.q",
                node_kind="port_out",
                element_instance_id="inst.logic.not.1",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.not"},
            ),
        ],
        edges=[
            edge_row(
                edge_id="edge.relay_to_not",
                from_node_id="node.relay.out.q",
                to_node_id="node.not.in.a",
                edge_kind="link",
                signal_type_id="signal.boolean",
            ),
            edge_row(
                edge_id="edge.not_to_relay_coil",
                from_node_id="node.not.out.q",
                to_node_id="node.relay.in.coil",
                edge_kind="link",
                signal_type_id="signal.boolean",
            ),
            edge_row(
                edge_id="edge.relay_to_reset",
                from_node_id="node.relay.out.q",
                to_node_id="node.relay.in.reset",
                edge_kind="link",
                signal_type_id="signal.boolean",
            ),
        ],
    )
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [
            {
                "tick": 0,
                "network_id": network_id,
                "validation_hash": "oscillator.validated",
                "loop_classifications": [
                    {
                        "classification": "sequential",
                        "node_ids": [
                            "node.relay.in.coil",
                            "node.relay.out.q",
                            "node.not.in.a",
                            "node.not.out.q",
                        ],
                        "element_instance_ids": ["inst.logic.not.1", "inst.logic.relay.1"],
                        "behavior_kinds": ["combinational", "sequential"],
                        "policy_resolution": "allow",
                        "requires_l2_roi": False,
                    }
                ],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state
