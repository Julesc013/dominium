"""FAST test: active jamming increases deterministic loss outcomes."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.jamming_increases_loss"
TEST_TAGS = ["fast", "signals", "quality", "jamming"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig3.jam.001",
            "nodes": [
                {"node_id": "node.sig3.jam.a"},
                {"node_id": "node.sig3.jam.b"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig3.jam.a_b",
                    "from_node_id": "node.sig3.jam.a",
                    "to_node_id": "node.sig3.jam.b",
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
                    "description": "rng loss",
                    "deterministic_function_id": "loss.named_rng.v1",
                    "attenuation_policy_id": "att.none",
                    "parameters": {
                        "loss_permille": 0,
                        "corruption_permille": 0,
                    },
                    "uses_rng_stream": True,
                    "rng_stream_name": "rng.signals.loss.jam_test",
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


def _state_with_jam(*, jam: bool) -> str:
    from src.signals import (
        build_signal_channel,
        process_signal_jam_start,
        process_signal_send,
        tick_signal_transport,
    )

    channels = [
        build_signal_channel(
            channel_id="channel.sig3.jam.001",
            channel_type_id="channel.radio_basic",
            network_graph_id="graph.sig3.jam.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.deterministic_rng",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=144,
        channel_id="channel.sig3.jam.001",
        from_node_id="node.sig3.jam.a",
        artifact_id="artifact.sig3.jam.001",
        sender_subject_id="subject.sig3.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig3.receiver", "to_node_id": "node.sig3.jam.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    jamming_rows = []
    if jam:
        jammed = process_signal_jam_start(
            current_tick=144,
            channel_id="channel.sig3.jam.001",
            strength_modifier=1000,
            duration_ticks=5,
            signal_channel_rows=channels,
            jamming_effect_rows=[],
            decision_log_rows=[],
        )
        jamming_rows = list(jammed.get("jamming_effect_rows") or [])
    ticked = tick_signal_transport(
        current_tick=144,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        attenuation_policy_registry=_attenuation_registry(),
        routing_policy_registry={},
        jamming_effect_rows=jamming_rows,
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

    clear_state = _state_with_jam(jam=False)
    jammed_state = _state_with_jam(jam=True)
    if not clear_state or not jammed_state:
        return {"status": "fail", "message": "missing delivery event state"}
    if clear_state != "delivered":
        return {"status": "fail", "message": "expected non-jammed baseline to deliver"}
    if jammed_state != "lost":
        return {"status": "fail", "message": "expected jammed signal to be lost under strong jamming"}
    return {"status": "pass", "message": "jamming deterministically increases loss"}
