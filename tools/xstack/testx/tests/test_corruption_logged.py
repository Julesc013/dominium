"""FAST test: corruption outcomes are explicitly logged in delivery events."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.corruption_logged"
TEST_TAGS = ["fast", "signals", "quality", "corruption"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig3.corrupt.001",
            "nodes": [
                {"node_id": "node.sig3.corrupt.a"},
                {"node_id": "node.sig3.corrupt.b"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig3.corrupt.a_b",
                    "from_node_id": "node.sig3.corrupt.a",
                    "to_node_id": "node.sig3.corrupt.b",
                    "delay_ticks": 0,
                    "capacity": 8,
                    "tags": [],
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
                    "loss_policy_id": "loss.linear_attenuation",
                    "description": "corruption threshold policy",
                    "deterministic_function_id": "loss.linear_attenuation.v1",
                    "attenuation_policy_id": "att.none",
                    "parameters": {
                        "base_loss_permille": 650,
                        "distance_loss_permille": 0,
                        "loss_threshold_permille": 900,
                        "corruption_threshold_permille": 500,
                    },
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "extensions": {},
                }
            ]
        }
    }


def _attenuation_registry() -> dict:
    return {
        "record": {
            "attenuation_policies": [
                {
                    "schema_version": "1.0.0",
                    "attenuation_policy_id": "att.none",
                    "description": "none",
                    "base_loss_rate": 0,
                    "field_modifier_ids": [],
                    "deterministic_function_id": "att.none.v1",
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

    from src.signals import build_signal_channel, process_signal_send, tick_signal_transport

    channels = [
        build_signal_channel(
            channel_id="channel.sig3.corrupt.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig3.corrupt.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.linear_attenuation",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=190,
        channel_id="channel.sig3.corrupt.001",
        from_node_id="node.sig3.corrupt.a",
        artifact_id="artifact.sig3.corrupt.001",
        sender_subject_id="subject.sig3.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig3.receiver", "to_node_id": "node.sig3.corrupt.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = tick_signal_transport(
        current_tick=190,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        attenuation_policy_registry=_attenuation_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
    )
    events = list(ticked.get("message_delivery_event_rows") or [])
    if not events:
        return {"status": "fail", "message": "missing delivery event"}
    event_row = dict(events[0])
    if str(event_row.get("delivery_state", "")).strip() != "corrupted":
        return {"status": "fail", "message": "expected corrupted delivery_state"}
    extensions = dict(event_row.get("extensions") or {})
    if not bool(extensions.get("corrupted_view", False)):
        return {"status": "fail", "message": "corrupted delivery missing corrupted_view marker"}
    return {"status": "pass", "message": "corruption outcome logged explicitly"}
