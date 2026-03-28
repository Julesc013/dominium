"""FAST test: SIG-3 loss/corruption outcomes are replay-stable."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.replay_stability_under_loss"
TEST_TAGS = ["fast", "signals", "quality", "replay", "determinism"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig3.replay.001",
            "nodes": [
                {"node_id": "node.sig3.replay.a"},
                {"node_id": "node.sig3.replay.b"},
                {"node_id": "node.sig3.replay.c"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig3.replay.a_b",
                    "from_node_id": "node.sig3.replay.a",
                    "to_node_id": "node.sig3.replay.b",
                    "delay_ticks": 0,
                    "capacity": 8,
                    "tags": ["tag.signal.attenuation.low"],
                },
                {
                    "edge_id": "edge.sig3.replay.b_c",
                    "from_node_id": "node.sig3.replay.b",
                    "to_node_id": "node.sig3.replay.c",
                    "delay_ticks": 0,
                    "capacity": 8,
                    "tags": ["tag.signal.attenuation.low"],
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
                    "loss_policy_id": "loss.deterministic_rng",
                    "description": "replay loss policy",
                    "deterministic_function_id": "loss.named_rng.v1",
                    "attenuation_policy_id": "att.field_scaled",
                    "parameters": {
                        "loss_permille": 220,
                        "corruption_permille": 180,
                    },
                    "uses_rng_stream": True,
                    "rng_stream_name": "rng.signals.loss.replay",
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
                    "attenuation_policy_id": "att.field_scaled",
                    "description": "field scaled",
                    "base_loss_rate": 0,
                    "field_modifier_ids": ["field.visibility", "field.radiation", "field.wind"],
                    "deterministic_function_id": "att.field_scaled.v1",
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "extensions": {
                        "distance_loss_permille": 10,
                        "field_visibility_weight_permille": 200,
                        "field_radiation_weight_permille": 250,
                        "field_wind_weight_permille": 100
                    },
                }
            ]
        }
    }


def _hash_once() -> str:
    from signals import build_signal_channel, process_signal_send, tick_signal_transport
    from tools.xstack.compatx.canonical_json import canonical_sha256

    channels = [
        build_signal_channel(
            channel_id="channel.sig3.replay.001",
            channel_type_id="channel.radio_basic",
            network_graph_id="graph.sig3.replay.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.deterministic_rng",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=255,
        channel_id="channel.sig3.replay.001",
        from_node_id="node.sig3.replay.a",
        artifact_id="artifact.sig3.replay.001",
        sender_subject_id="subject.sig3.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig3.receiver", "to_node_id": "node.sig3.replay.c"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = tick_signal_transport(
        current_tick=255,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        attenuation_policy_registry=_attenuation_registry(),
        routing_policy_registry={},
        field_samples_by_node_id={
            "node.sig3.replay.b": {"field.visibility": 200, "field.radiation": 100, "field.wind": 80},
            "node.sig3.replay.c": {"field.visibility": 260, "field.radiation": 120, "field.wind": 120},
        },
        max_cost_units=8,
        cost_units_per_delivery=1,
    )
    return canonical_sha256(
        {
            "events": list(ticked.get("message_delivery_event_rows") or []),
            "delivered_rows": list(ticked.get("delivered_rows") or []),
            "queue_rows": list(ticked.get("signal_transport_queue_rows") or []),
            "budget_outcome": str(ticked.get("budget_outcome", "")),
            "cost_units": int(ticked.get("cost_units", 0)),
        }
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first_hash = _hash_once()
    second_hash = _hash_once()
    if not first_hash:
        return {"status": "fail", "message": "missing replay hash"}
    if first_hash != second_hash:
        return {"status": "fail", "message": "loss replay hash drifted across identical runs"}
    return {"status": "pass", "message": "loss replay hash stable"}
