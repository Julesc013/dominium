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
        "logic_noise_policy_registry_payload": _load_json(repo_root, "data/registries/logic_noise_policy_registry.json"),
        "logic_security_policy_registry_payload": _load_json(repo_root, "data/registries/logic_security_policy_registry.json"),
        "bus_encoding_registry_payload": _load_json(repo_root, "data/registries/bus_encoding_registry.json"),
        "protocol_registry_payload": _load_json(repo_root, "data/registries/protocol_registry.json"),
        "arbitration_policy_registry_payload": _load_json(repo_root, "data/registries/arbitration_policy_registry.json"),
        "error_detection_policy_registry_payload": _load_json(repo_root, "data/registries/error_detection_policy_registry.json"),
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
        "loss_policy_registry_payload": _load_json(repo_root, "data/registries/loss_policy_registry.json"),
        "routing_policy_registry_payload": _load_json(repo_root, "data/registries/core_routing_policy_registry.json"),
        "attenuation_policy_registry_payload": _load_json(repo_root, "data/registries/attenuation_policy_registry.json"),
        "belief_policy_registry_payload": _load_json(repo_root, "data/registries/belief_policy_registry.json"),
    }


def load_compile_inputs(repo_root: str) -> dict:
    return {
        "compiled_type_registry_payload": _load_json(repo_root, "data/registries/compiled_type_registry.json"),
        "verification_procedure_registry_payload": _load_json(
            repo_root, "data/registries/verification_procedure_registry.json"
        ),
        "logic_compile_policy_registry_payload": _load_json(
            repo_root, "data/registries/logic_compile_policy_registry.json"
        ),
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


def make_scalar_comparator_network(*, network_id: str) -> tuple[dict, dict]:
    binding = binding_row(
        network_id=network_id,
        graph_id="graph.{}".format(network_id),
        policy_id="logic.policy.default",
        extensions={"validation_status": "validated", "logic_policy_id": "logic.default"},
    )
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
            node_row(node_id="node.source.value", node_kind="junction"),
            node_row(node_id="node.source.threshold", node_kind="junction"),
            node_row(
                node_id="node.comparator.in.value",
                node_kind="port_in",
                element_instance_id="inst.logic.comparator.1",
                port_id="in.value",
                payload_extensions={"element_definition_id": "logic.comparator_scalar"},
            ),
            node_row(
                node_id="node.comparator.in.threshold",
                node_kind="port_in",
                element_instance_id="inst.logic.comparator.1",
                port_id="in.threshold",
                payload_extensions={"element_definition_id": "logic.comparator_scalar"},
            ),
            node_row(
                node_id="node.comparator.out.gte",
                node_kind="port_out",
                element_instance_id="inst.logic.comparator.1",
                port_id="out.gte",
                payload_extensions={"element_definition_id": "logic.comparator_scalar"},
            ),
        ],
        edges=[
            edge_row(
                edge_id="edge.scalar.value",
                from_node_id="node.source.value",
                to_node_id="node.comparator.in.value",
                edge_kind="link",
                signal_type_id="signal.scalar",
            ),
            edge_row(
                edge_id="edge.scalar.threshold",
                from_node_id="node.source.threshold",
                to_node_id="node.comparator.in.threshold",
                edge_kind="link",
                signal_type_id="signal.scalar",
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
                "validation_hash": "comparator.validated",
                "loop_classifications": [],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state


def make_flip_flop_network(*, network_id: str) -> tuple[dict, dict]:
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
                node_id="node.flipflop.in.clock",
                node_kind="port_in",
                element_instance_id="inst.logic.flipflop.1",
                port_id="in.clock",
                payload_extensions={"element_definition_id": "logic.flip_flop"},
            ),
            node_row(
                node_id="node.flipflop.in.data",
                node_kind="port_in",
                element_instance_id="inst.logic.flipflop.1",
                port_id="in.data",
                payload_extensions={"element_definition_id": "logic.flip_flop"},
            ),
            node_row(
                node_id="node.flipflop.out.q",
                node_kind="port_out",
                element_instance_id="inst.logic.flipflop.1",
                port_id="out.q",
                payload_extensions={"element_definition_id": "logic.flip_flop"},
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
                "validation_hash": "flipflop.validated",
                "loop_classifications": [],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state


def make_protocol_network(
    *,
    network_id: str,
    protocol_id: str = "protocol.bus_arbitration_stub",
    carrier_type_id: str = "carrier.electrical",
    delay_policy_id: str = "delay.none",
    edge_extensions: dict | None = None,
    binding_extensions: dict | None = None,
) -> tuple[dict, dict]:
    binding = binding_row(
        network_id=network_id,
        graph_id="graph.{}".format(network_id),
        policy_id="logic.policy.default",
        extensions=dict({"validation_status": "validated", "logic_policy_id": "logic.default"}, **dict(binding_extensions or {})),
    )
    graph = graph_row(
        graph_id=binding["graph_id"],
        nodes=[
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
        ],
        edges=[
            edge_row(
                edge_id="edge.protocol.and.to.not",
                from_node_id="node.and.out.q",
                to_node_id="node.not.in.a",
                edge_kind="protocol_link",
                signal_type_id="signal.boolean",
                carrier_type_id=carrier_type_id,
                delay_policy_id=delay_policy_id,
                protocol_id=protocol_id,
                payload_extensions=dict({"bus_id": "bus.logic.protocol.1"}, **dict(edge_extensions or {})),
            )
        ],
    )
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [
            {
                "tick": 0,
                "network_id": network_id,
                "validation_hash": "protocol.validated",
                "loop_classifications": [],
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }
    return binding, logic_network_state


def seed_signal_requests(*, signal_store_state: dict | None, signal_requests: list[dict], inputs: dict):
    from src.logic.signal import process_signal_set

    state = dict(signal_store_state or {}) if isinstance(signal_store_state, dict) else None
    for request in list(signal_requests or []):
        seeded = process_signal_set(
            current_tick=int(max(0, int(dict(request).get("tick", 0) or 0))),
            signal_store_state=state,
            signal_request=dict(request),
            signal_type_registry_payload=inputs["signal_type_registry_payload"],
            carrier_type_registry_payload=inputs["carrier_type_registry_payload"],
            signal_delay_policy_registry_payload=inputs["signal_delay_policy_registry_payload"],
            signal_noise_policy_registry_payload=inputs["signal_noise_policy_registry_payload"],
            bus_encoding_registry_payload=inputs["bus_encoding_registry_payload"],
            protocol_registry_payload=inputs["protocol_registry_payload"],
            compute_budget_profile_registry_payload=inputs["compute_budget_profile_registry_payload"],
            compute_degrade_policy_registry_payload=inputs["compute_degrade_policy_registry_payload"],
            tolerance_policy_registry_payload=inputs["tolerance_policy_registry_payload"],
        )
        state = dict(seeded.get("signal_store_state") or {})
    return state


def compile_logic_network_fixture(*, repo_root: str, network_id: str, logic_network_state: dict, compile_policy_id: str = "compile.logic.default") -> dict:
    from src.logic.compile import compile_logic_network
    from src.system import build_state_vector_definition_row, normalize_state_vector_definition_rows

    inputs = load_eval_inputs(repo_root)
    compile_inputs = load_compile_inputs(repo_root)
    compile_eval = compile_logic_network(
        current_tick=0,
        compile_request={"network_id": network_id, "compile_policy_id": compile_policy_id},
        logic_network_state=logic_network_state,
        logic_policy_registry_payload=inputs["logic_policy_registry_payload"],
        logic_network_policy_registry_payload=inputs["logic_network_policy_registry_payload"],
        logic_compile_policy_registry_payload=compile_inputs["logic_compile_policy_registry_payload"],
        compiled_type_registry_payload=compile_inputs["compiled_type_registry_payload"],
        verification_procedure_registry_payload=compile_inputs["verification_procedure_registry_payload"],
        logic_element_rows=inputs["logic_element_rows"],
        logic_behavior_model_rows=inputs["logic_behavior_model_rows"],
        logic_interface_signature_rows=inputs["logic_interface_signature_rows"],
        logic_state_machine_rows=inputs["logic_state_machine_rows"],
        state_vector_definition_rows=normalize_state_vector_definition_rows(inputs["state_vector_definition_rows"]),
        build_state_vector_definition_row=build_state_vector_definition_row,
        normalize_state_vector_definition_rows=normalize_state_vector_definition_rows,
    )
    return {
        "inputs": inputs,
        "compile_inputs": compile_inputs,
        "compile_eval": compile_eval,
    }
