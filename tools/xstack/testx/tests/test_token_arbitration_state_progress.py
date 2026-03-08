"""STRICT test: LOGIC-9 token arbitration advances deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_token_arbitration_state_progress"
TEST_TAGS = ["strict", "logic", "protocol", "arbitration"]


def _frame(src_endpoint_id: str, frame_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "frame_id": frame_id,
        "protocol_id": "protocol.token.test",
        "src_endpoint_id": src_endpoint_id,
        "dst_address": {"kind": "unicast", "subject_id": "subject.logic.endpoint.target", "to_node_id": "node.not.in.a"},
        "payload_ref": {"signal_type_id": "signal.boolean", "value_payload": {"value": 1}},
        "checksum": "chk",
        "tick_sent": 1,
        "deterministic_fingerprint": "test",
        "extensions": {
            "network_id": "net.logic.protocol.token",
            "bus_id": "bus.logic.protocol.1",
            "carrier_type_id": "carrier.electrical",
            "delay_policy_id": "delay.none",
            "noise_policy_id": "noise.none",
            "deliver_delay_ticks": 1,
            "security_policy_id": "sec.none",
            "target_slots": [
                {"network_id": "net.logic.protocol.token", "element_id": "inst.logic.not.1", "port_id": "in.a", "node_id": "node.not.in.a", "subject_id": "subject.logic.endpoint.target"}
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

    from src.logic.protocol import arbitrate_logic_protocol_frames

    protocol_registry_payload = {
        "record": {
            "protocols": [
                {
                    "protocol_id": "protocol.token.test",
                    "bus_id": "bus.logic.protocol.1",
                    "arbitration_policy_id": "arb.token",
                    "addressing_mode": "unicast",
                    "error_detection_policy_id": "err.checksum_stub",
                    "security_policy_id": "sec.none",
                    "extensions": {},
                }
            ]
        }
    }
    arbitration_policy_registry_payload = {
        "record": {"arbitration_policies": [{"arbitration_policy_id": "arb.token", "extensions": {}}]}
    }
    logic_security_policy_registry_payload = {
        "record": {"logic_security_policies": [{"security_policy_id": "sec.none", "requires_auth": False, "requires_encryption": False, "allowed_credential_types": [], "extensions": {}}]}
    }

    first = arbitrate_logic_protocol_frames(
        current_tick=1,
        protocol_frame_rows=[_frame("endpoint.logic.a", "frame.logic.protocol.a"), _frame("endpoint.logic.b", "frame.logic.protocol.b")],
        arbitration_state_rows=[{"schema_version": "1.0.0", "bus_id": "bus.logic.protocol.1", "policy_id": "arb.token", "token_holder": "endpoint.logic.b", "last_winner": None, "deterministic_fingerprint": "test", "extensions": {}}],
        protocol_event_record_rows=[],
        pending_signal_update_rows=[],
        signal_transport_state={},
        protocol_registry_payload=protocol_registry_payload,
        arbitration_policy_registry_payload=arbitration_policy_registry_payload,
        logic_security_policy_registry_payload=logic_security_policy_registry_payload,
    )
    arbitration_rows = [dict(row) for row in list(first.get("logic_arbitration_state_rows") or []) if isinstance(row, dict)]
    if not arbitration_rows or str(arbitration_rows[0].get("last_winner", "")).strip() != "endpoint.logic.b":
        return {"status": "fail", "message": "token arbitration did not honor the current token holder"}
    if str(arbitration_rows[0].get("token_holder", "")).strip() != "endpoint.logic.a":
        return {"status": "fail", "message": "token arbitration did not advance the token holder deterministically"}
    return {"status": "pass", "message": "token arbitration state advances deterministically"}

