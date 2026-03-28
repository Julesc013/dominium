"""FAST test: SIG receipts map deterministically to LOGIC message signals."""

from __future__ import annotations


TEST_ID = "test_sig_receipt_to_message_signal_mapping"
TEST_TAGS = ["fast", "logic", "sig", "adapter"]


def run(repo_root: str):
    del repo_root
    from logic.signal import sig_receipt_to_signal_request

    receipt = {
        "receipt_id": "receipt.knowledge.test",
        "subject_id": "subject.test",
        "artifact_id": "artifact.report.test",
        "envelope_id": "envelope.signal.test",
        "delivery_event_id": "event.signal.delivery",
        "acquired_tick": 17,
        "trust_weight": 0.5,
        "verification_state": "verified",
    }
    request = sig_receipt_to_signal_request(
        network_id="net.logic",
        element_id="elem.router",
        port_id="port.rx",
        receipt_row=receipt,
    )
    if str(request.get("signal_type_id", "")).strip() != "signal.message":
        return {"status": "fail", "message": "receipt mapping must produce signal.message"}
    if str(request.get("carrier_type_id", "")).strip() != "carrier.sig":
        return {"status": "fail", "message": "receipt mapping must preserve carrier.sig"}
    value_payload = dict(request.get("value_payload") or {})
    if str(value_payload.get("artifact_id", "")).strip() != "artifact.report.test":
        return {"status": "fail", "message": "receipt mapping lost artifact_id"}
    if str(value_payload.get("receipt_id", "")).strip() != "receipt.knowledge.test":
        return {"status": "fail", "message": "receipt mapping lost receipt_id"}
    return {"status": "pass", "message": "SIG receipt maps to deterministic message signal request"}
