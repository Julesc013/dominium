"""STRICT test: LOGIC-9 fixed-priority arbitration is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_fixed_priority_arbitration_deterministic"
TEST_TAGS = ["strict", "logic", "protocol", "arbitration"]


def _frame(src_endpoint_id: str, frame_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "frame_id": frame_id,
        "protocol_id": "protocol.fixed.priority.test",
        "src_endpoint_id": src_endpoint_id,
        "dst_address": {"kind": "unicast", "subject_id": "subject.logic.endpoint.target", "to_node_id": "node.not.in.a"},
        "payload_ref": {"signal_type_id": "signal.boolean", "value_payload": {"value": 1}},
        "checksum": "chk",
        "tick_sent": 1,
        "deterministic_fingerprint": "test",
        "extensions": {
            "network_id": "net.logic.protocol.fixed",
            "bus_id": "bus.logic.protocol.1",
            "carrier_type_id": "carrier.electrical",
            "delay_policy_id": "delay.none",
            "noise_policy_id": "noise.none",
            "deliver_delay_ticks": 1,
            "security_policy_id": "sec.none",
            "target_slots": [
                {"network_id": "net.logic.protocol.fixed", "element_id": "inst.logic.not.1", "port_id": "in.a", "node_id": "node.not.in.a", "subject_id": "subject.logic.endpoint.target"}
            ],
            "source_element_id": "inst.logic.and.1",
            "source_port_id": "out.q",
            "status": "queued",
            "next_arbitration_tick": 1,
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from logic.protocol import arbitrate_logic_protocol_frames

    protocol_registry_payload = {
        "record": {
            "protocols": [
                {
                    "protocol_id": "protocol.fixed.priority.test",
                    "bus_id": "bus.logic.protocol.1",
                    "arbitration_policy_id": "arb.fixed_priority",
                    "addressing_mode": "unicast",
                    "error_detection_policy_id": "err.checksum_stub",
                    "security_policy_id": "sec.none",
                    "extensions": {},
                }
            ]
        }
    }
    arbitration_policy_registry_payload = {
        "record": {"arbitration_policies": [{"arbitration_policy_id": "arb.fixed_priority", "extensions": {}}]}
    }
    logic_security_policy_registry_payload = {
        "record": {"logic_security_policies": [{"security_policy_id": "sec.none", "requires_auth": False, "requires_encryption": False, "allowed_credential_types": [], "extensions": {}}]}
    }
    frames = [
        _frame("endpoint.logic.a", "frame.logic.protocol.a"),
        _frame("endpoint.logic.b", "frame.logic.protocol.b"),
    ]

    def run_once():
        return arbitrate_logic_protocol_frames(
            current_tick=1,
            protocol_frame_rows=copy.deepcopy(frames),
            arbitration_state_rows=[],
            protocol_event_record_rows=[],
            pending_signal_update_rows=[],
            signal_transport_state={},
            protocol_registry_payload=protocol_registry_payload,
            arbitration_policy_registry_payload=arbitration_policy_registry_payload,
            logic_security_policy_registry_payload=logic_security_policy_registry_payload,
        )

    first = run_once()
    second = run_once()
    if first != second:
        return {"status": "fail", "message": "fixed-priority arbitration drifted across equivalent runs"}
    events = [dict(row) for row in list(first.get("logic_protocol_event_record_rows") or []) if isinstance(row, dict)]
    if not events or str(events[-1].get("frame_id", "")).strip() != "frame.logic.protocol.a":
        return {"status": "fail", "message": "fixed-priority arbitration did not select the lexicographically lower endpoint"}
    return {"status": "pass", "message": "fixed-priority arbitration is deterministic"}

