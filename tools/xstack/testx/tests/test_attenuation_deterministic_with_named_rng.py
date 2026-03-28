"""FAST test: SIG-3 named RNG attenuation remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.attenuation_deterministic_with_named_rng"
TEST_TAGS = ["fast", "signals", "quality", "determinism", "rng"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig3.rng.001",
            "nodes": [
                {"node_id": "node.sig3.rng.a"},
                {"node_id": "node.sig3.rng.b"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig3.rng.a_b",
                    "from_node_id": "node.sig3.rng.a",
                    "to_node_id": "node.sig3.rng.b",
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
                    "loss_policy_id": "loss.deterministic_rng",
                    "description": "rng loss policy",
                    "deterministic_function_id": "loss.named_rng.v1",
                    "attenuation_policy_id": "att.deterministic_rng",
                    "parameters": {
                        "loss_permille": 250,
                        "corruption_permille": 150,
                    },
                    "uses_rng_stream": True,
                    "rng_stream_name": "rng.signals.loss.quality",
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
                    "attenuation_policy_id": "att.deterministic_rng",
                    "description": "rng attenuation",
                    "base_loss_rate": 0,
                    "field_modifier_ids": [],
                    "deterministic_function_id": "att.named_rng.v1",
                    "uses_rng_stream": True,
                    "rng_stream_name": "rng.signals.attenuation.quality",
                    "extensions": {},
                }
            ]
        }
    }


def _run_once() -> str:
    from signals import build_signal_channel, process_signal_send, tick_signal_transport

    channels = [
        build_signal_channel(
            channel_id="channel.sig3.rng.001",
            channel_type_id="channel.radio_basic",
            network_graph_id="graph.sig3.rng.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.deterministic_rng",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=77,
        channel_id="channel.sig3.rng.001",
        from_node_id="node.sig3.rng.a",
        artifact_id="artifact.sig3.rng.001",
        sender_subject_id="subject.sig3.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig3.receiver", "to_node_id": "node.sig3.rng.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = tick_signal_transport(
        current_tick=77,
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
        return ""
    return str(dict(events[0]).get("delivery_state", "")).strip()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if not first:
        return {"status": "fail", "message": "missing delivery event"}
    if first != second:
        return {"status": "fail", "message": "named RNG attenuation drifted"}
    return {"status": "pass", "message": "named RNG attenuation deterministic"}
