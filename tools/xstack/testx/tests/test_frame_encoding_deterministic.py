"""STRICT test: LOGIC-9 protocol frame encoding is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "test_frame_encoding_deterministic"
TEST_TAGS = ["strict", "logic", "protocol", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.protocol import build_protocol_frame_from_delivery

    protocol_row = {
        "protocol_id": "protocol.bus_arbitration_stub",
        "bus_id": "bus.logic.protocol.1",
        "addressing_mode": "unicast",
        "arbitration_policy_id": "arb.fixed_priority",
        "error_detection_policy_id": "err.checksum_stub",
        "security_policy_id": "sec.none",
        "extensions": {},
    }
    delivery = {
        "target_element_id": "inst.logic.not.1",
        "target_port_id": "in.a",
        "target_node_id": "node.not.in.a",
        "signal_type_id": "signal.boolean",
        "carrier_type_id": "carrier.electrical",
        "delay_policy_id": "delay.none",
        "noise_policy_id": "noise.none",
        "deliver_delay_ticks": 1,
        "bus_id": "bus.logic.protocol.1",
    }
    value_payload = {"value": 1}
    first = build_protocol_frame_from_delivery(
        current_tick=5,
        network_id="net.logic.protocol.det",
        source_element_id="inst.logic.and.1",
        source_port_id="out.q",
        delivery=delivery,
        value_payload=value_payload,
        protocol_row=protocol_row,
    )
    second = build_protocol_frame_from_delivery(
        current_tick=5,
        network_id="net.logic.protocol.det",
        source_element_id="inst.logic.and.1",
        source_port_id="out.q",
        delivery=delivery,
        value_payload=value_payload,
        protocol_row=protocol_row,
    )
    if first != second:
        return {"status": "fail", "message": "protocol frame encoding drifted across equivalent inputs"}
    if str(first.get("checksum", "")).strip() in {"", "none"}:
        return {"status": "fail", "message": "protocol frame checksum stub was not computed"}
    return {"status": "pass", "message": "protocol frame encoding is deterministic"}

