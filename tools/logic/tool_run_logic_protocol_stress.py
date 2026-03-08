#!/usr/bin/env python3
"""Run a deterministic LOGIC-9 protocol contention stress scenario."""

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

from src.logic.protocol import arbitrate_logic_protocol_frames, build_protocol_frame_row, transport_logic_sig_receipts
from src.logic.signal import process_signal_set
from tools.xstack.compatx.canonical_json import canonical_sha256


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _registry_rows(payload: dict, key: str) -> list[dict]:
    record = dict(payload.get("record") or {})
    rows = record.get(key)
    if not isinstance(rows, list):
        rows = payload.get(key)
    return [dict(item) for item in list(rows or []) if isinstance(item, dict)]


def run_protocol_stress(*, repo_root: str, frame_count: int, tick_count: int, use_sig: bool) -> dict:
    protocol_registry_payload = _load_json(os.path.join(repo_root, "data/registries/protocol_registry.json"))
    arbitration_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/arbitration_policy_registry.json"))
    logic_security_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/logic_security_policy_registry.json"))
    signal_type_registry_payload = _load_json(os.path.join(repo_root, "data/registries/signal_type_registry.json"))
    carrier_type_registry_payload = _load_json(os.path.join(repo_root, "data/registries/carrier_type_registry.json"))
    signal_delay_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/signal_delay_policy_registry.json"))
    signal_noise_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/signal_noise_policy_registry.json"))
    bus_encoding_registry_payload = _load_json(os.path.join(repo_root, "data/registries/bus_encoding_registry.json"))
    compute_budget_profile_registry_payload = _load_json(os.path.join(repo_root, "data/registries/compute_budget_profile_registry.json"))
    compute_degrade_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/compute_degrade_policy_registry.json"))
    tolerance_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/tolerance_policy_registry.json"))
    loss_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/loss_policy_registry.json"))
    routing_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/core_routing_policy_registry.json"))
    attenuation_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/attenuation_policy_registry.json"))
    belief_policy_registry_payload = _load_json(os.path.join(repo_root, "data/registries/belief_policy_registry.json"))

    protocol_rows = {
        str(row.get("protocol_id", "")).strip(): dict(row)
        for row in _registry_rows(protocol_registry_payload, "protocols")
    }
    protocol_row = dict(protocol_rows.get("protocol.bus_arbitration_stub") or {})
    if use_sig:
        protocol_row["security_policy_id"] = "sec.none"

    frame_rows = []
    for index in range(int(max(1, frame_count))):
        endpoint_id = "endpoint.logic.protocol.{:04d}".format(index)
        frame_rows.append(
            build_protocol_frame_row(
                frame_id="frame.logic.protocol.stress.{:04d}".format(index),
                protocol_id=str(protocol_row.get("protocol_id", "")).strip() or "protocol.bus_arbitration_stub",
                src_endpoint_id=endpoint_id,
                dst_address={
                    "kind": "multicast",
                    "subject_id": "subject.logic.endpoint.target",
                    "subject_ids": ["subject.logic.endpoint.target"],
                    "broadcast_subject_ids": ["subject.logic.endpoint.target"],
                    "broadcast_scope": "bus.logic.protocol.stress",
                    "to_node_id": "node.protocol.target",
                },
                payload_ref={"signal_type_id": "signal.boolean", "value_payload": {"value": 1}},
                checksum="stress",
                tick_sent=0,
                extensions={
                    "network_id": "net.logic.protocol.stress",
                    "bus_id": "bus.logic.protocol.stress",
                    "carrier_type_id": "carrier.sig" if use_sig else "carrier.electrical",
                    "delay_policy_id": "delay.none",
                    "noise_policy_id": "noise.none",
                    "deliver_delay_ticks": 1,
                    "security_policy_id": str(protocol_row.get("security_policy_id", "")).strip() or "sec.none",
                    "security_context": {"authenticated": True, "credential_verified": True, "encrypted": True},
                    "source_element_id": "inst.logic.source.{:04d}".format(index),
                    "source_port_id": "out.q",
                    "status": "queued",
                    "next_arbitration_tick": 0,
                    "target_slots": [
                        {
                            "network_id": "net.logic.protocol.stress",
                            "element_id": "inst.logic.target.0000",
                            "port_id": "in.a",
                            "node_id": "node.protocol.target",
                            "subject_id": "subject.logic.endpoint.target",
                        }
                    ],
                },
            )
        )

    signal_store_state = {}
    signal_transport_state = {
        "signal_channel_rows": [],
        "signal_message_envelope_rows": [],
        "signal_transport_queue_rows": [],
        "message_delivery_event_rows": [],
        "knowledge_receipt_rows": [],
        "network_graph_rows": [],
        "signal_trust_edge_rows": [],
        "loss_policy_registry_payload": loss_policy_registry_payload,
        "routing_policy_registry_payload": routing_policy_registry_payload,
        "attenuation_policy_registry_payload": attenuation_policy_registry_payload,
        "belief_policy_registry_payload": belief_policy_registry_payload,
        "belief_policy_id": "belief.default",
    }
    arbitration_state_rows = []
    protocol_event_record_rows = []
    pending_signal_update_rows = []
    tick_reports = []

    for tick in range(int(max(1, tick_count))):
        runtime = arbitrate_logic_protocol_frames(
            current_tick=tick,
            protocol_frame_rows=frame_rows,
            arbitration_state_rows=arbitration_state_rows,
            protocol_event_record_rows=protocol_event_record_rows,
            pending_signal_update_rows=pending_signal_update_rows,
            signal_transport_state=signal_transport_state,
            protocol_registry_payload={"record": {"protocols": [protocol_row]}},
            arbitration_policy_registry_payload=arbitration_policy_registry_payload,
            logic_security_policy_registry_payload=logic_security_policy_registry_payload,
        )
        frame_rows = list(runtime.get("logic_protocol_frame_rows") or [])
        arbitration_state_rows = list(runtime.get("logic_arbitration_state_rows") or [])
        protocol_event_record_rows = list(runtime.get("logic_protocol_event_record_rows") or [])
        pending_signal_update_rows = list(runtime.get("logic_pending_signal_update_rows") or [])
        signal_transport_state = dict(runtime.get("signal_transport_state") or signal_transport_state)
        if use_sig:
            delivered = transport_logic_sig_receipts(
                current_tick=tick + 1,
                signal_store_state=signal_store_state,
                signal_transport_state=signal_transport_state,
                signal_type_registry_payload=signal_type_registry_payload,
                carrier_type_registry_payload=carrier_type_registry_payload,
                signal_delay_policy_registry_payload=signal_delay_policy_registry_payload,
                signal_noise_policy_registry_payload=signal_noise_policy_registry_payload,
                bus_encoding_registry_payload=bus_encoding_registry_payload,
                protocol_registry_payload=protocol_registry_payload,
                protocol_frame_rows=frame_rows,
                protocol_event_record_rows=protocol_event_record_rows,
                compute_budget_profile_registry_payload=compute_budget_profile_registry_payload,
                compute_degrade_policy_registry_payload=compute_degrade_policy_registry_payload,
                tolerance_policy_registry_payload=tolerance_policy_registry_payload,
                process_signal_set_fn=process_signal_set,
            )
            signal_store_state = dict(delivered.get("signal_store_state") or signal_store_state)
            signal_transport_state = dict(delivered.get("signal_transport_state") or signal_transport_state)
            frame_rows = list(delivered.get("logic_protocol_frame_rows") or frame_rows)
            protocol_event_record_rows = list(delivered.get("logic_protocol_event_record_rows") or protocol_event_record_rows)
        tick_reports.append(
            {
                "tick": tick,
                "queued_frames": int(
                    sum(1 for row in frame_rows if str(dict(row.get("extensions") or {}).get("status", "")).strip() == "queued")
                ),
                "event_count": int(len(protocol_event_record_rows)),
                "delivered_events": int(
                    sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "delivered")
                ),
                "blocked_events": int(
                    sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "blocked")
                ),
                "dropped_events": int(
                    sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "dropped")
                ),
                "corrupted_events": int(
                    sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "corrupted")
                ),
                "delivery_event_count": int(len(list(signal_transport_state.get("message_delivery_event_rows") or []))),
            }
        )

    report = {
        "result": "complete",
        "frame_count": int(max(1, frame_count)),
        "tick_count": int(max(1, tick_count)),
        "use_sig": bool(use_sig),
        "tick_reports": tick_reports,
        "final_queued_frame_count": int(
            sum(1 for row in frame_rows if str(dict(row.get("extensions") or {}).get("status", "")).strip() == "queued")
        ),
        "protocol_event_count": int(len(protocol_event_record_rows)),
        "blocked_event_count": int(
            sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "blocked")
        ),
        "dropped_event_count": int(
            sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "dropped")
        ),
        "corrupted_event_count": int(
            sum(1 for row in protocol_event_record_rows if str(row.get("result", "")).strip() == "corrupted")
        ),
        "delivery_event_count": int(len(list(signal_transport_state.get("message_delivery_event_rows") or []))),
        "receipt_count": int(len(list(signal_transport_state.get("knowledge_receipt_rows") or []))),
        "delivered_signal_count": int(len(list(signal_store_state.get("signal_rows") or []))),
        "max_queue_depth": int(max((int(dict(row).get("queued_frames", 0) or 0) for row in tick_reports), default=0)),
        "logic_protocol_frame_hash_chain": canonical_sha256(frame_rows),
        "logic_protocol_event_hash_chain": canonical_sha256(protocol_event_record_rows),
        "message_delivery_event_hash_chain": canonical_sha256(signal_transport_state.get("message_delivery_event_rows") or []),
    }
    report["deterministic_fingerprint"] = canonical_sha256(report)
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--frame-count", type=int, default=16)
    parser.add_argument("--tick-count", type=int, default=8)
    parser.add_argument("--use-sig", choices=("true", "false"), default="true")
    parser.add_argument("--out-json", default="")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = run_protocol_stress(
        repo_root=args.repo_root,
        frame_count=args.frame_count,
        tick_count=args.tick_count,
        use_sig=str(args.use_sig).lower() == "true",
    )
    if args.out_json:
        _write_json(os.path.join(args.repo_root, args.out_json.replace("/", os.sep)), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
