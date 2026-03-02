"""FAST test: deterministic RNG loss policy yields stable delivery state."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.loss_policy_deterministic"
TEST_TAGS = ["fast", "signals", "loss", "determinism"]


def _loss_registry() -> dict:
    return {
        "record": {
            "loss_policies": [
                {
                    "schema_version": "1.0.0",
                    "loss_policy_id": "loss.deterministic_rng",
                    "description": "deterministic RNG loss",
                    "deterministic_function_id": "loss.named_rng.v1",
                    "parameters": {"loss_permille": 550},
                    "uses_rng_stream": True,
                    "rng_stream_name": "rng.signals.loss.default",
                    "extensions": {},
                }
            ]
        }
    }


def _delivery_state_once() -> str:
    from src.signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channels = [
        build_signal_channel(
            channel_id="channel.sig.loss.001",
            channel_type_id="channel.radio_basic",
            network_graph_id="graph.sig.loss.001",
            capacity_per_tick=2,
            base_delay_ticks=0,
            loss_policy_id="loss.deterministic_rng",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=220,
        channel_id="channel.sig.loss.001",
        from_node_id="node.sig.loss.a",
        artifact_id="artifact.sig.loss.001",
        sender_subject_id="subject.sig.loss.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.loss.receiver", "to_node_id": "node.sig.loss.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = process_signal_transport_tick(
        current_tick=220,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=[
            {
                "graph_id": "graph.sig.loss.001",
                "nodes": [{"node_id": "node.sig.loss.a"}, {"node_id": "node.sig.loss.b"}],
                "edges": [
                    {
                        "edge_id": "edge.sig.loss.a_b",
                        "from_node_id": "node.sig.loss.a",
                        "to_node_id": "node.sig.loss.b",
                    }
                ],
            }
        ],
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
    )
    events = list(ticked.get("message_delivery_event_rows") or [])
    if not events:
        return ""
    return str(dict(events[0]).get("delivery_state", "")).strip()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _delivery_state_once()
    second = _delivery_state_once()
    if not first:
        return {"status": "fail", "message": "missing delivery state under deterministic_rng policy"}
    if first != second:
        return {"status": "fail", "message": "deterministic_rng loss state drifted across identical runs"}
    if first not in {"delivered", "lost"}:
        return {"status": "fail", "message": "unexpected delivery state '{}'".format(first)}
    return {"status": "pass", "message": "loss policy deterministic"}

