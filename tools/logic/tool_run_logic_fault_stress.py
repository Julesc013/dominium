#!/usr/bin/env python3
"""Run a deterministic LOGIC-8 fault/noise/security stress scenario."""

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

from logic.fault import process_logic_fault_set
from logic.signal import process_signal_set
from tools.logic.tool_replay_fault_window import replay_fault_window_from_payload
from tools.xstack.compatx.canonical_json import canonical_sha256
from tools.xstack.testx.tests._logic_eval_test_utils import load_eval_inputs, make_chain_network, make_scalar_comparator_network


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def build_logic_fault_stress_scenario(*, repo_root: str, tick_count: int) -> dict:
    inputs = load_eval_inputs(repo_root)
    fault_registry = _load_json(os.path.join(repo_root, "data/registries/logic_fault_kind_registry.json"))

    _, chain_state = make_chain_network(network_id="net.logic.stress.fault")
    chain_graph = dict(chain_state["logic_network_graph_rows"][0])
    chain_graph["edges"] = [
        dict(
            edge,
            payload=dict(
                dict(edge.get("payload") or {}),
                extensions=dict(dict(dict(edge.get("payload") or {}).get("extensions") or {}), security_policy_id="sec.auth_required_stub"),
            ),
        )
        if str(edge.get("edge_id", "")) == "edge.and.to.not"
        else dict(edge)
        for edge in list(chain_graph.get("edges") or [])
    ]
    chain_state["logic_network_graph_rows"] = [chain_graph]

    _, scalar_state = make_scalar_comparator_network(network_id="net.logic.stress.noise")
    scalar_graph = dict(scalar_state["logic_network_graph_rows"][0])
    scalar_graph["edges"] = [
        dict(edge, payload=dict(dict(edge.get("payload") or {}), noise_policy_id="noise.named_rng_optional"))
        if str(edge.get("edge_id", "")) == "edge.scalar.value"
        else dict(edge)
        for edge in list(scalar_graph.get("edges") or [])
    ]
    scalar_state["logic_network_graph_rows"] = [scalar_graph]

    signal_store_state = None
    for request in (
        {
            "network_id": "net.logic.stress.fault",
            "element_id": "inst.logic.and.1",
            "port_id": "in.a",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value": 1},
        },
        {
            "network_id": "net.logic.stress.fault",
            "element_id": "inst.logic.and.1",
            "port_id": "in.b",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value": 1},
        },
        {
            "network_id": "net.logic.stress.fault",
            "element_id": "inst.logic.not.1",
            "port_id": "in.a",
            "signal_type_id": "signal.boolean",
            "carrier_type_id": "carrier.sig",
            "value_payload": {"value": 1},
            "extensions": {
                "security_context": {
                    "authenticated": False,
                    "credential_verified": False,
                    "verification_state": "failed",
                }
            },
        },
        {
            "network_id": "net.logic.stress.noise",
            "element_id": "inst.logic.comparator.1",
            "port_id": "in.value",
            "signal_type_id": "signal.scalar",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value_fixed": 75},
        },
        {
            "network_id": "net.logic.stress.noise",
            "element_id": "inst.logic.comparator.1",
            "port_id": "in.threshold",
            "signal_type_id": "signal.scalar",
            "carrier_type_id": "carrier.electrical",
            "value_payload": {"value_fixed": 60},
        },
    ):
        seeded = process_signal_set(
            current_tick=0,
            signal_store_state=signal_store_state,
            signal_request=request,
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

    fault_rows = []
    for request in (
        {
            "fault_kind_id": "fault.open",
            "target_kind": "node",
            "target_id": "node.and.in.a",
        },
        {
            "fault_kind_id": "fault.stuck_at_1",
            "target_kind": "node",
            "target_id": "node.and.in.b",
        },
    ):
        updated = process_logic_fault_set(
            current_tick=0,
            logic_fault_state_rows=fault_rows,
            fault_request=request,
            logic_fault_kind_registry_payload=fault_registry,
        )
        fault_rows = list(updated.get("logic_fault_state_rows") or fault_rows)

    return {
        "logic_network_state": {
            "logic_network_graph_rows": list(chain_state.get("logic_network_graph_rows") or [])
            + list(scalar_state.get("logic_network_graph_rows") or []),
            "logic_network_binding_rows": list(chain_state.get("logic_network_binding_rows") or [])
            + list(scalar_state.get("logic_network_binding_rows") or []),
            "logic_network_validation_records": list(chain_state.get("logic_network_validation_records") or [])
            + list(scalar_state.get("logic_network_validation_records") or []),
            "logic_network_change_records": [],
            "logic_network_explain_artifact_rows": [],
            "compute_runtime_state": {},
        },
        "signal_store_state": signal_store_state,
        "logic_eval_state": {},
        "logic_fault_state_rows": fault_rows,
        "state_vector_snapshot_rows": [],
        "evaluation_requests": [
            request
            for tick in range(1, max(1, int(tick_count)) + 1)
            for request in (
                {"tick": tick, "network_id": "net.logic.stress.fault"},
                {
                    "tick": tick,
                    "network_id": "net.logic.stress.noise",
                    "extensions": {"allow_named_rng_noise": True},
                },
            )
        ],
    }


def run_fault_stress(*, repo_root: str, tick_count: int) -> dict:
    scenario = build_logic_fault_stress_scenario(repo_root=repo_root, tick_count=tick_count)
    report = replay_fault_window_from_payload(repo_root=repo_root, payload=scenario)
    if str(report.get("result", "")).strip() != "complete":
        return dict(report)
    logic_eval_state = dict(report.get("final_logic_eval_state") or {})
    stress_report = {
        "result": "complete",
        "tick_count": int(max(1, int(tick_count))),
        "fault_state_count": int(len(list(report.get("logic_fault_state_rows") or []))),
        "noise_decision_count": int(len(list(logic_eval_state.get("logic_noise_decision_rows") or []))),
        "security_fail_count": int(len(list(logic_eval_state.get("logic_security_fail_rows") or []))),
        "logic_fault_state_hash_chain": str(report.get("logic_fault_state_hash_chain", "")),
        "logic_noise_decision_hash_chain": str(report.get("logic_noise_decision_hash_chain", "")),
        "logic_security_fail_hash_chain": str(report.get("logic_security_fail_hash_chain", "")),
        "final_signal_hash": str(report.get("final_signal_hash", "")),
    }
    stress_report["deterministic_fingerprint"] = canonical_sha256(stress_report)
    return stress_report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--tick-count", type=int, default=6)
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_fault_stress(repo_root=args.repo_root, tick_count=args.tick_count)
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
