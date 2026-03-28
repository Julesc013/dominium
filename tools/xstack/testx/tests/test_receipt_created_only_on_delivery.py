"""FAST test: knowledge receipt rows are created only for delivered envelopes."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.receipt_created_only_on_delivery"
TEST_TAGS = ["fast", "signals", "receipt"]


def _loss_registry(policy_id: str, loss_permille: int) -> dict:
    return {
        "record": {
            "loss_policies": [
                {
                    "schema_version": "1.0.0",
                    "loss_policy_id": policy_id,
                    "description": "test policy",
                    "deterministic_function_id": "loss.named_rng.v1",
                    "parameters": {"loss_permille": int(loss_permille)},
                    "uses_rng_stream": True,
                    "rng_stream_name": "rng.signals.loss.default",
                    "extensions": {},
                }
            ]
        }
    }


def _tick_once(policy_id: str, loss_permille: int) -> dict:
    from signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channels = [
        build_signal_channel(
            channel_id="channel.sig.receipt.{}".format(policy_id.replace(".", "_")),
            channel_type_id="channel.radio_basic",
            network_graph_id="graph.sig.receipt.001",
            capacity_per_tick=2,
            base_delay_ticks=0,
            loss_policy_id=policy_id,
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=301,
        channel_id=str(channels[0].get("channel_id", "")),
        from_node_id="node.sig.receipt.a",
        artifact_id="artifact.sig.receipt.001",
        sender_subject_id="subject.sig.receipt.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receipt.receiver", "to_node_id": "node.sig.receipt.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = process_signal_transport_tick(
        current_tick=301,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=[
            {
                "graph_id": "graph.sig.receipt.001",
                "nodes": [{"node_id": "node.sig.receipt.a"}, {"node_id": "node.sig.receipt.b"}],
                "edges": [
                    {
                        "edge_id": "edge.sig.receipt.a_b",
                        "from_node_id": "node.sig.receipt.a",
                        "to_node_id": "node.sig.receipt.b",
                    }
                ],
            }
        ],
        loss_policy_registry=_loss_registry(policy_id=policy_id, loss_permille=loss_permille),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
    )
    events = list(ticked.get("message_delivery_event_rows") or [])
    receipts = list(ticked.get("knowledge_receipt_rows") or [])
    return {
        "event_state": str(dict(events[0]).get("delivery_state", "")).strip() if events else "",
        "receipt_count": int(len(receipts)),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    delivered = _tick_once(policy_id="loss.deterministic_rng", loss_permille=0)
    lost = _tick_once(policy_id="loss.deterministic_rng", loss_permille=1000)
    if delivered.get("event_state") != "delivered":
        return {"status": "fail", "message": "expected delivered state for zero-loss policy"}
    if int(delivered.get("receipt_count", 0)) < 1:
        return {"status": "fail", "message": "receipt should be created when delivery succeeds"}
    if lost.get("event_state") != "lost":
        return {"status": "fail", "message": "expected lost state for 100% loss policy"}
    if int(lost.get("receipt_count", 0)) != 0:
        return {"status": "fail", "message": "receipt must not be created for lost delivery"}
    return {"status": "pass", "message": "receipt creation only occurs on delivered envelopes"}
