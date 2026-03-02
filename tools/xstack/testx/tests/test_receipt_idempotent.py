"""FAST test: SIG-2 receipts are idempotent by subject and artifact."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.receipt_idempotent"
TEST_TAGS = ["fast", "signals", "receipt", "idempotent"]


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


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig.idem.001",
            "nodes": [{"node_id": "node.a"}, {"node_id": "node.b"}],
            "edges": [{"edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b"}],
        }
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channel_rows = [
        build_signal_channel(
            channel_id="channel.sig.idem.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.idem.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    artifact_rows = [{"artifact_id": "artifact.sig.idem.001", "artifact_family_id": "INFO.RECORD", "created_tick": 1}]

    sent_a = process_signal_send(
        current_tick=20,
        channel_id="channel.sig.idem.001",
        from_node_id="node.a",
        artifact_id="artifact.sig.idem.001",
        sender_subject_id="subject.sender",
        recipient_address={"kind": "single", "subject_id": "subject.receiver", "to_node_id": "node.b"},
        signal_channel_rows=channel_rows,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
        info_artifact_rows=artifact_rows,
    )
    tick_a = process_signal_transport_tick(
        current_tick=20,
        signal_channel_rows=channel_rows,
        signal_transport_queue_rows=list(sent_a.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent_a.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
    )

    sent_b = process_signal_send(
        current_tick=21,
        channel_id="channel.sig.idem.001",
        from_node_id="node.a",
        artifact_id="artifact.sig.idem.001",
        sender_subject_id="subject.sender",
        recipient_address={"kind": "single", "subject_id": "subject.receiver", "to_node_id": "node.b"},
        signal_channel_rows=channel_rows,
        signal_message_envelope_rows=list(sent_a.get("signal_message_envelope_rows") or []),
        signal_transport_queue_rows=[],
        info_artifact_rows=artifact_rows,
        envelope_id="env.signal.idempotent.override",
    )
    tick_b = process_signal_transport_tick(
        current_tick=21,
        signal_channel_rows=channel_rows,
        signal_transport_queue_rows=list(sent_b.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent_b.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=list(tick_a.get("message_delivery_event_rows") or []),
        knowledge_receipt_rows=list(tick_a.get("knowledge_receipt_rows") or []),
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
    )

    receipts = list(tick_b.get("knowledge_receipt_rows") or [])
    if len(receipts) != 1:
        return {"status": "fail", "message": "duplicate delivery should not create duplicate subject/artifact receipt"}
    return {"status": "pass", "message": "receipt idempotency enforced"}
