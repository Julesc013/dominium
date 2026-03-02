"""FAST test: SIG delivery events are deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.message_delivery_deterministic"
TEST_TAGS = ["fast", "signals", "determinism"]


def _loss_registry() -> dict:
    return {
        "record": {
            "loss_policies": [
                {
                    "schema_version": "1.0.0",
                    "loss_policy_id": "loss.none",
                    "description": "no loss",
                    "deterministic_function_id": "loss.none",
                    "parameters": {},
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "extensions": {},
                }
            ]
        }
    }


def _run_once() -> dict:
    from src.signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channels = [
        build_signal_channel(
            channel_id="channel.sig.det.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.det.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=100,
        channel_id="channel.sig.det.001",
        from_node_id="node.sig.a",
        artifact_id="artifact.sig.det.001",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver", "to_node_id": "node.sig.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = process_signal_transport_tick(
        current_tick=100,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=[
            {
                "graph_id": "graph.sig.det.001",
                "nodes": [{"node_id": "node.sig.a"}, {"node_id": "node.sig.b"}],
                "edges": [
                    {
                        "edge_id": "edge.sig.a_b",
                        "from_node_id": "node.sig.a",
                        "to_node_id": "node.sig.b",
                    }
                ],
            }
        ],
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=16,
        cost_units_per_delivery=1,
    )
    return {
        "events": list(ticked.get("message_delivery_event_rows") or []),
        "receipts": list(ticked.get("knowledge_receipt_rows") or []),
        "processed": list(ticked.get("processed_queue_keys") or []),
        "deferred": list(ticked.get("deferred_queue_keys") or []),
        "budget_outcome": str(ticked.get("budget_outcome", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "signal delivery output drifted across identical runs"}
    if not list(first.get("events") or []):
        return {"status": "fail", "message": "missing signal delivery events"}
    event_state = str(dict(list(first.get("events") or [])[0]).get("delivery_state", "")).strip()
    if event_state != "delivered":
        return {"status": "fail", "message": "expected delivered state for loss.none policy"}
    if not list(first.get("receipts") or []):
        return {"status": "fail", "message": "knowledge receipt should be created for delivered message"}
    return {"status": "pass", "message": "signal delivery deterministic"}
