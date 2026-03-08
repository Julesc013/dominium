"""STRICT test: LOGIC-9 blocks unverified protocol frames under security policy."""

from __future__ import annotations

import sys


TEST_ID = "test_security_blocks_unverified_frames"
TEST_TAGS = ["strict", "logic", "protocol", "security"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.logic.protocol import arbitrate_logic_protocol_frames

    protocol_registry_payload = {
        "record": {
            "protocols": [
                {
                    "protocol_id": "protocol.secure.test",
                    "bus_id": "bus.logic.protocol.1",
                    "arbitration_policy_id": "arb.fixed_priority",
                    "addressing_mode": "unicast",
                    "error_detection_policy_id": "err.checksum_stub",
                    "security_policy_id": "sec.auth_required_stub",
                    "extensions": {},
                }
            ]
        }
    }
    arbitration_policy_registry_payload = {
        "record": {"arbitration_policies": [{"arbitration_policy_id": "arb.fixed_priority", "extensions": {}}]}
    }
    logic_security_policy_registry_payload = {
        "record": {"logic_security_policies": [{"security_policy_id": "sec.auth_required_stub", "requires_auth": True, "requires_encryption": False, "allowed_credential_types": ["credential.stub"], "extensions": {}}]}
    }
    frame = {
        "schema_version": "1.0.0",
        "frame_id": "frame.logic.protocol.secure",
        "protocol_id": "protocol.secure.test",
        "src_endpoint_id": "endpoint.logic.a",
        "dst_address": {"kind": "unicast", "subject_id": "subject.logic.endpoint.target", "to_node_id": "node.not.in.a"},
        "payload_ref": {"signal_type_id": "signal.boolean", "value_payload": {"value": 1}},
        "checksum": "chk",
        "tick_sent": 1,
        "deterministic_fingerprint": "test",
        "extensions": {
            "network_id": "net.logic.protocol.secure",
            "bus_id": "bus.logic.protocol.1",
            "carrier_type_id": "carrier.electrical",
            "delay_policy_id": "delay.none",
            "noise_policy_id": "noise.none",
            "deliver_delay_ticks": 1,
            "security_policy_id": "sec.auth_required_stub",
            "security_context": {"authenticated": False, "credential_verified": False},
            "target_slots": [
                {"network_id": "net.logic.protocol.secure", "element_id": "inst.logic.not.1", "port_id": "in.a", "node_id": "node.not.in.a", "subject_id": "subject.logic.endpoint.target"}
            ],
            "source_element_id": "inst.logic.and.1",
            "source_port_id": "out.q",
            "status": "queued",
            "next_arbitration_tick": 1,
        },
    }
    result = arbitrate_logic_protocol_frames(
        current_tick=1,
        protocol_frame_rows=[frame],
        arbitration_state_rows=[],
        protocol_event_record_rows=[],
        pending_signal_update_rows=[],
        signal_transport_state={},
        protocol_registry_payload=protocol_registry_payload,
        arbitration_policy_registry_payload=arbitration_policy_registry_payload,
        logic_security_policy_registry_payload=logic_security_policy_registry_payload,
    )
    events = [dict(row) for row in list(result.get("logic_protocol_event_record_rows") or []) if isinstance(row, dict)]
    if not events or str(events[-1].get("result", "")).strip() != "blocked":
        return {"status": "fail", "message": "unverified frame was not blocked deterministically"}
    if list(result.get("logic_pending_signal_update_rows") or []):
        return {"status": "fail", "message": "blocked frame still produced pending signal delivery"}
    security_rows = [dict(row) for row in list(result.get("logic_security_fail_rows") or []) if isinstance(row, dict)]
    if not security_rows:
        return {"status": "fail", "message": "blocked frame did not emit a security failure row"}
    return {"status": "pass", "message": "unverified protocol frames are blocked deterministically"}

