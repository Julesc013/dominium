#!/usr/bin/env python3
"""Run a deterministic LOGIC-5 timing stress scenario and summarize timing hashes."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Iterable

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.logic.network import build_logic_edge_payload_row, build_logic_network_binding_row, build_logic_node_payload_row
from src.logic.signal import canonical_signal_hash, process_signal_set
from tools.logic.tool_replay_logic_window import _load_eval_inputs, _write_json
from tools.logic.tool_replay_timing_window import replay_timing_window_from_payload
from tools.xstack.compatx.canonical_json import canonical_sha256


_NODE_SCHEMA_ID = "dominium.schema.logic.logic_node_payload"
_EDGE_SCHEMA_ID = "dominium.schema.logic.logic_edge_payload"


def _node_row(
    *,
    node_id: str,
    node_kind: str,
    element_instance_id: str | None = None,
    port_id: str | None = None,
    payload_extensions: dict | None = None,
) -> dict:
    payload = build_logic_node_payload_row(
        node_kind=node_kind,
        element_instance_id=element_instance_id,
        port_id=port_id,
        extensions=dict(payload_extensions or {}),
    )
    return {
        "schema_version": "1.0.0",
        "node_id": str(node_id),
        "node_type_id": "node.logic.{}".format(str(payload.get("node_kind", "")).strip()),
        "payload": payload,
        "tags": [],
        "extensions": {},
    }


def _edge_row(
    *,
    edge_id: str,
    from_node_id: str,
    to_node_id: str,
    signal_type_id: str = "signal.boolean",
    carrier_type_id: str = "carrier.electrical",
    delay_policy_id: str = "delay.none",
) -> dict:
    payload = build_logic_edge_payload_row(
        edge_kind="link",
        signal_type_id=signal_type_id,
        carrier_type_id=carrier_type_id,
        delay_policy_id=delay_policy_id,
        noise_policy_id="noise.none",
        extensions={},
    )
    return {
        "schema_version": "1.0.0",
        "edge_id": str(edge_id),
        "from_node_id": str(from_node_id),
        "to_node_id": str(to_node_id),
        "edge_type_id": "edge.logic.link",
        "payload": payload,
        "capacity": None,
        "delay_ticks": None,
        "loss_fraction": None,
        "cost_units": None,
        "extensions": {},
    }


def _graph_row(*, graph_id: str, nodes: list[dict], edges: list[dict]) -> dict:
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
        "extensions": {},
    }


def build_logic_timing_stress_scenario(
    *,
    repo_root: str,
    oscillator_count: int = 12,
    tick_count: int = 8,
) -> dict:
    count = int(max(1, int(oscillator_count)))
    total_ticks = int(max(4, int(tick_count)))
    network_id = "net.logic.timing.stress"
    graph_id = "graph.logic.timing.stress"
    binding = build_logic_network_binding_row(
        network_id=network_id,
        graph_id=graph_id,
        policy_id="logic.policy.default",
        extensions={"validation_status": "validated", "logic_policy_id": "logic.lab_experimental"},
    )

    nodes: list[dict] = []
    edges: list[dict] = []
    loop_classifications: list[dict] = []
    for index in range(1, count + 1):
        relay_id = "inst.logic.relay.{}".format(index)
        not_id = "inst.logic.not.{}".format(index)
        watchdog_id = "inst.logic.watchdog.{}".format(index)
        nodes.extend(
            [
                _node_row(
                    node_id="node.relay.{}.in.coil".format(index),
                    node_kind="port_in",
                    element_instance_id=relay_id,
                    port_id="in.coil",
                    payload_extensions={"element_definition_id": "logic.relay"},
                ),
                _node_row(
                    node_id="node.relay.{}.in.reset".format(index),
                    node_kind="port_in",
                    element_instance_id=relay_id,
                    port_id="in.reset",
                    payload_extensions={"element_definition_id": "logic.relay"},
                ),
                _node_row(
                    node_id="node.relay.{}.out.q".format(index),
                    node_kind="port_out",
                    element_instance_id=relay_id,
                    port_id="out.q",
                    payload_extensions={"element_definition_id": "logic.relay"},
                ),
                _node_row(
                    node_id="node.not.{}.in.a".format(index),
                    node_kind="port_in",
                    element_instance_id=not_id,
                    port_id="in.a",
                    payload_extensions={"element_definition_id": "logic.not"},
                ),
                _node_row(
                    node_id="node.not.{}.out.q".format(index),
                    node_kind="port_out",
                    element_instance_id=not_id,
                    port_id="out.q",
                    payload_extensions={"element_definition_id": "logic.not"},
                ),
                _node_row(
                    node_id="node.watchdog.{}.in.enable".format(index),
                    node_kind="port_in",
                    element_instance_id=watchdog_id,
                    port_id="in.enable",
                    payload_extensions={"element_definition_id": "logic.watchdog_basic"},
                ),
                _node_row(
                    node_id="node.watchdog.{}.in.observe".format(index),
                    node_kind="port_in",
                    element_instance_id=watchdog_id,
                    port_id="in.observe",
                    payload_extensions={"element_definition_id": "logic.watchdog_basic"},
                ),
                _node_row(
                    node_id="node.watchdog.{}.out.timeout".format(index),
                    node_kind="port_out",
                    element_instance_id=watchdog_id,
                    port_id="out.timeout",
                    payload_extensions={"element_definition_id": "logic.watchdog_basic"},
                ),
            ]
        )
        edges.extend(
            [
                _edge_row(
                    edge_id="edge.relay_to_not.{}".format(index),
                    from_node_id="node.relay.{}.out.q".format(index),
                    to_node_id="node.not.{}.in.a".format(index),
                ),
                _edge_row(
                    edge_id="edge.not_to_relay_coil.{}".format(index),
                    from_node_id="node.not.{}.out.q".format(index),
                    to_node_id="node.relay.{}.in.coil".format(index),
                ),
                _edge_row(
                    edge_id="edge.relay_to_reset.{}".format(index),
                    from_node_id="node.relay.{}.out.q".format(index),
                    to_node_id="node.relay.{}.in.reset".format(index),
                ),
            ]
        )
        loop_classifications.append(
            {
                "classification": "sequential",
                "node_ids": [
                    "node.relay.{}.in.coil".format(index),
                    "node.relay.{}.out.q".format(index),
                    "node.not.{}.in.a".format(index),
                    "node.not.{}.out.q".format(index),
                ],
                "element_instance_ids": [not_id, relay_id],
                "behavior_kinds": ["combinational", "sequential"],
                "policy_resolution": "allow",
                "requires_l2_roi": False,
            }
        )

    graph = _graph_row(graph_id=graph_id, nodes=nodes, edges=edges)
    logic_network_state = {
        "logic_network_graph_rows": [graph],
        "logic_network_binding_rows": [binding],
        "logic_network_validation_records": [
            {
                "tick": 0,
                "network_id": network_id,
                "validation_hash": canonical_sha256({"network_id": network_id, "oscillator_count": count}),
                "loop_classifications": loop_classifications,
            }
        ],
        "logic_network_change_records": [],
        "logic_network_explain_artifact_rows": [],
        "compute_runtime_state": {},
    }

    inputs = _load_eval_inputs(repo_root)
    signal_store_state = None
    for index in range(1, count + 1):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request={
                "network_id": network_id,
                "element_id": "inst.logic.watchdog.{}".format(index),
                "port_id": "in.enable",
                "signal_type_id": "signal.boolean",
                "carrier_type_id": "carrier.electrical",
                "value_payload": {"value": 1},
            },
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
        signal_store_state = dict(seeded.get("signal_store_state") or {})

    return {
        "scenario_id": "scenario.logic5.timing.{}".format(
            canonical_sha256({"oscillator_count": count, "tick_count": total_ticks})[:12]
        ),
        "oscillator_count": count,
        "tick_count": total_ticks,
        "logic_network_state": logic_network_state,
        "signal_store_state": signal_store_state or {},
        "logic_eval_state": {},
        "state_vector_snapshot_rows": [],
        "evaluation_requests": [{"tick": tick, "network_id": network_id} for tick in range(1, total_ticks + 1)],
        "deterministic_fingerprint": canonical_sha256(
            {"network_id": network_id, "oscillator_count": count, "tick_count": total_ticks}
        ),
    }


def run_logic_timing_stress(
    *,
    repo_root: str,
    oscillator_count: int = 12,
    tick_count: int = 8,
) -> dict:
    scenario = build_logic_timing_stress_scenario(
        repo_root=repo_root,
        oscillator_count=oscillator_count,
        tick_count=tick_count,
    )
    report = replay_timing_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(report.get("result", "")).strip() != "complete":
        return report
    return {
        "result": "complete",
        "scenario_id": scenario["scenario_id"],
        "network_id": "net.logic.timing.stress",
        "oscillator_count": int(scenario["oscillator_count"]),
        "tick_count": int(scenario["tick_count"]),
        "final_signal_hash": str(report.get("final_signal_hash", "")),
        "logic_oscillation_record_hash_chain": str(report.get("logic_oscillation_record_hash_chain", "")),
        "logic_timing_violation_hash_chain": str(report.get("logic_timing_violation_hash_chain", "")),
        "logic_watchdog_timeout_hash_chain": str(report.get("logic_watchdog_timeout_hash_chain", "")),
        "oscillation_record_count": int(report.get("oscillation_record_count", 0) or 0),
        "timing_violation_count": int(report.get("timing_violation_count", 0) or 0),
        "watchdog_timeout_count": int(report.get("watchdog_timeout_count", 0) or 0),
        "final_signal_store_hash": canonical_signal_hash(state=(dict(report.get("final_signal_store_state") or {}))),
        "deterministic_fingerprint": canonical_sha256(
            {
                "scenario_id": scenario["scenario_id"],
                "final_signal_hash": report.get("final_signal_hash"),
                "logic_oscillation_record_hash_chain": report.get("logic_oscillation_record_hash_chain"),
                "logic_timing_violation_hash_chain": report.get("logic_timing_violation_hash_chain"),
                "logic_watchdog_timeout_hash_chain": report.get("logic_watchdog_timeout_hash_chain"),
                "oscillation_record_count": report.get("oscillation_record_count"),
                "watchdog_timeout_count": report.get("watchdog_timeout_count"),
            }
        ),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--oscillator-count", type=int, default=12)
    parser.add_argument("--tick-count", type=int, default=8)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_logic_timing_stress(
        repo_root=args.repo_root,
        oscillator_count=int(args.oscillator_count),
        tick_count=int(args.tick_count),
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
