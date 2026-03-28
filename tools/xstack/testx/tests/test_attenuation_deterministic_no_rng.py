"""FAST test: SIG-3 attenuation without RNG remains deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.attenuation_deterministic_no_rng"
TEST_TAGS = ["fast", "signals", "quality", "determinism"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig3.no_rng.001",
            "nodes": [
                {"node_id": "node.sig3.a"},
                {"node_id": "node.sig3.b"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig3.a_b",
                    "from_node_id": "node.sig3.a",
                    "to_node_id": "node.sig3.b",
                    "delay_ticks": 0,
                    "capacity": 8,
                    "tags": ["tag.signal.attenuation.medium"],
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
                    "description": "deterministic linear attenuation",
                    "deterministic_function_id": "loss.linear_attenuation.v1",
                    "attenuation_policy_id": "att.linear_distance",
                    "parameters": {
                        "base_loss_permille": 150,
                        "distance_loss_permille": 200,
                        "loss_threshold_permille": 1000,
                        "corruption_threshold_permille": 1200,
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
                    "attenuation_policy_id": "att.linear_distance",
                    "description": "distance attenuation",
                    "base_loss_rate": 0,
                    "field_modifier_ids": [],
                    "deterministic_function_id": "att.linear_distance.v1",
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "extensions": {"distance_loss_permille": 200},
                }
            ]
        }
    }


def _run_once() -> str:
    from signals import build_signal_channel, process_signal_send, tick_signal_transport

    channel_rows = [
        build_signal_channel(
            channel_id="channel.sig3.no_rng.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig3.no_rng.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.linear_attenuation",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=33,
        channel_id="channel.sig3.no_rng.001",
        from_node_id="node.sig3.a",
        artifact_id="artifact.sig3.no_rng.001",
        sender_subject_id="subject.sig3.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig3.receiver", "to_node_id": "node.sig3.b"},
        signal_channel_rows=channel_rows,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = tick_signal_transport(
        current_tick=33,
        signal_channel_rows=channel_rows,
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
    rows = list(ticked.get("message_delivery_event_rows") or [])
    if not rows:
        return ""
    return str(dict(rows[0]).get("delivery_state", "")).strip()


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if not first:
        return {"status": "fail", "message": "missing delivery event"}
    if first != second:
        return {"status": "fail", "message": "no-rng attenuation state drifted"}
    return {"status": "pass", "message": "no-rng attenuation deterministic"}
