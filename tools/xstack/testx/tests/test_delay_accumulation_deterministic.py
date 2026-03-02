"""FAST test: SIG delay accumulation over channel + route is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.delay_accumulation_deterministic"
TEST_TAGS = ["fast", "signals", "delay", "determinism"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig.delay.001",
            "nodes": [
                {"node_id": "node.sig.a"},
                {"node_id": "node.sig.b"},
                {"node_id": "node.sig.c"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig.a_b",
                    "from_node_id": "node.sig.a",
                    "to_node_id": "node.sig.b",
                    "delay_ticks": 2,
                    "capacity": 4,
                },
                {
                    "edge_id": "edge.sig.b_c",
                    "from_node_id": "node.sig.b",
                    "to_node_id": "node.sig.c",
                    "delay_ticks": 3,
                    "capacity": 4,
                },
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
    from src.signals import build_signal_channel, process_signal_send, tick_signal_transport

    start_tick = 200
    channels = [
        build_signal_channel(
            channel_id="channel.sig.delay.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.delay.001",
            capacity_per_tick=2,
            base_delay_ticks=1,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=start_tick,
        channel_id="channel.sig.delay.001",
        from_node_id="node.sig.a",
        artifact_id="artifact.sig.delay.001",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver", "to_node_id": "node.sig.c"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    queue_rows = list(sent.get("signal_transport_queue_rows") or [])
    envelope_rows = list(sent.get("signal_message_envelope_rows") or [])
    event_rows = []
    delivered_tick = None
    for tick in range(start_tick, start_tick + 16):
        result = tick_signal_transport(
            current_tick=tick,
            signal_channel_rows=channels,
            signal_transport_queue_rows=queue_rows,
            envelope_rows=envelope_rows,
            existing_delivery_event_rows=event_rows,
            network_graph_rows=_graph(),
            loss_policy_registry=_loss_registry(),
            routing_policy_registry={},
            max_cost_units=16,
            cost_units_per_delivery=1,
        )
        queue_rows = list(result.get("signal_transport_queue_rows") or [])
        event_rows = list(result.get("message_delivery_event_rows") or [])
        if list(result.get("delivered_rows") or []):
            delivered_tick = tick
            break
    return {
        "delivered_tick": delivered_tick,
        "start_tick": start_tick,
        "event_count": int(len(event_rows)),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "delay accumulation drifted across identical runs"}
    delivered_tick = first.get("delivered_tick")
    if delivered_tick is None:
        return {"status": "fail", "message": "signal was not delivered in delay accumulation fixture"}
    # base_delay(1) + path_delay(2+3) => delivery at start_tick + 6 with current executor semantics
    expected_tick = int(first.get("start_tick", 0)) + 6
    if int(delivered_tick) != int(expected_tick):
        return {
            "status": "fail",
            "message": "expected delivery at tick {} but got {}".format(expected_tick, delivered_tick),
        }
    return {"status": "pass", "message": "delay accumulation deterministic"}

