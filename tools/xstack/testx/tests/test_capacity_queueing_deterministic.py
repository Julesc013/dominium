"""FAST test: SIG channel capacity queueing is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.capacity_queueing_deterministic"
TEST_TAGS = ["fast", "signals", "capacity", "determinism"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig.capacity.001",
            "nodes": [{"node_id": "node.sig.a"}, {"node_id": "node.sig.b"}],
            "edges": [
                {
                    "edge_id": "edge.sig.a_b",
                    "from_node_id": "node.sig.a",
                    "to_node_id": "node.sig.b",
                    "delay_ticks": 0,
                    "capacity": 4,
                }
            ],
        }
    ]


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
    from signals import build_signal_channel, process_signal_send, tick_signal_transport

    channels = [
        build_signal_channel(
            channel_id="channel.sig.capacity.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.capacity.001",
            capacity_per_tick=1,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    send_1 = process_signal_send(
        current_tick=90,
        channel_id="channel.sig.capacity.001",
        from_node_id="node.sig.a",
        artifact_id="artifact.sig.capacity.001",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver.1", "to_node_id": "node.sig.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    send_2 = process_signal_send(
        current_tick=90,
        channel_id="channel.sig.capacity.001",
        from_node_id="node.sig.a",
        artifact_id="artifact.sig.capacity.002",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver.2", "to_node_id": "node.sig.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=list(send_1.get("signal_message_envelope_rows") or []),
        signal_transport_queue_rows=list(send_1.get("signal_transport_queue_rows") or []),
    )
    ticked = tick_signal_transport(
        current_tick=90,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(send_2.get("signal_transport_queue_rows") or []),
        envelope_rows=list(send_2.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=16,
        cost_units_per_delivery=1,
    )
    return {
        "delivered_count": int(len(list(ticked.get("delivered_rows") or []))),
        "queue_count": int(len(list(ticked.get("signal_transport_queue_rows") or []))),
        "processed_queue_keys": list(ticked.get("processed_queue_keys") or []),
        "deferred_queue_keys": list(ticked.get("deferred_queue_keys") or []),
        "budget_outcome": str(ticked.get("budget_outcome", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "capacity queueing drifted across identical runs"}
    if int(first.get("delivered_count", 0)) != 1:
        return {"status": "fail", "message": "expected exactly one delivery under channel capacity_per_tick=1"}
    if int(first.get("queue_count", 0)) != 1:
        return {"status": "fail", "message": "expected one deferred queue row under channel capacity_per_tick=1"}
    if str(first.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected deterministic degraded outcome with deferred queue rows"}
    return {"status": "pass", "message": "capacity queueing deterministic"}

