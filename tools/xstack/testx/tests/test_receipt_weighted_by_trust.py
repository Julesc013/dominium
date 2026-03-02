"""FAST test: SIG-5 receipt trust weight is derived from trust graph edges."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.receipt_weighted_by_trust"
TEST_TAGS = ["fast", "signals", "trust", "receipt"]


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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channel_rows = [
        build_signal_channel(
            channel_id="channel.sig.trust.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.trust.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=90,
        channel_id="channel.sig.trust.001",
        from_node_id="node.a",
        artifact_id="artifact.sig.trust.001",
        sender_subject_id="subject.sender",
        recipient_address={"kind": "single", "subject_id": "subject.receiver", "to_node_id": "node.b"},
        signal_channel_rows=channel_rows,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = process_signal_transport_tick(
        current_tick=90,
        signal_channel_rows=channel_rows,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=[
            {
                "graph_id": "graph.sig.trust.001",
                "nodes": [{"node_id": "node.a"}, {"node_id": "node.b"}],
                "edges": [{"edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b"}],
            }
        ],
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
        default_trust_weight=1.0,
        trust_edge_rows=[
            {
                "from_subject_id": "subject.receiver",
                "to_subject_id": "subject.sender",
                "trust_weight": 0.2,
                "evidence_count": 1,
                "last_updated_tick": 40,
                "extensions": {},
            }
        ],
    )
    receipts = list(ticked.get("knowledge_receipt_rows") or [])
    if not receipts:
        return {"status": "fail", "message": "expected delivered receipt"}
    trust_weight = float(dict(receipts[0]).get("trust_weight", 1.0))
    if abs(trust_weight - 0.2) > 0.000001:
        return {"status": "fail", "message": "receipt trust weight should come from trust edge (recipient -> sender)"}
    return {"status": "pass", "message": "receipt trust weighting uses trust graph"}
