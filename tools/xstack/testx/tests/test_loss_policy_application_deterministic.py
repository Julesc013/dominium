"""FAST test: SIG loss policy application is deterministic with attenuation hooks."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.loss_policy_application_deterministic"
TEST_TAGS = ["fast", "signals", "loss", "determinism"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig.loss_apply.001",
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
                    "delay_ticks": 0,
                    "capacity": 4,
                    "tags": ["tag.signal.attenuation.medium"],
                },
                {
                    "edge_id": "edge.sig.b_c",
                    "from_node_id": "node.sig.b",
                    "to_node_id": "node.sig.c",
                    "delay_ticks": 0,
                    "capacity": 4,
                    "tags": ["tag.signal.attenuation.medium"],
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
                    "loss_policy_id": "loss.linear_attenuation",
                    "description": "deterministic linear attenuation",
                    "deterministic_function_id": "loss.linear_attenuation.v1",
                    "parameters": {
                        "base_loss_permille": 200,
                        "distance_loss_permille": 250,
                        "field_visibility_weight_permille": 1000,
                    },
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "extensions": {},
                }
            ]
        }
    }


def _run_once() -> str:
    from signals import build_signal_channel, process_signal_send, tick_signal_transport

    channels = [
        build_signal_channel(
            channel_id="channel.sig.loss_apply.001",
            channel_type_id="channel.radio_basic",
            network_graph_id="graph.sig.loss_apply.001",
            capacity_per_tick=2,
            base_delay_ticks=0,
            loss_policy_id="loss.linear_attenuation",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=300,
        channel_id="channel.sig.loss_apply.001",
        from_node_id="node.sig.a",
        artifact_id="artifact.sig.loss_apply.001",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver", "to_node_id": "node.sig.c"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    result = tick_signal_transport(
        current_tick=300,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
    )
    events = list(result.get("message_delivery_event_rows") or [])
    if not events:
        return ""
    return str(dict(events[0]).get("delivery_state", "")).strip()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if not first:
        return {"status": "fail", "message": "missing delivery state for linear attenuation policy"}
    if first != second:
        return {"status": "fail", "message": "loss policy application drifted across identical runs"}
    if first != "lost":
        return {"status": "fail", "message": "expected deterministic lost state under configured attenuation policy"}
    return {"status": "pass", "message": "loss policy application deterministic"}

