"""FAST test: FIELD-scaled attenuation changes delivery state deterministically."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.field_scaled_loss_effect"
TEST_TAGS = ["fast", "signals", "quality", "field"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig3.field.001",
            "nodes": [
                {"node_id": "node.sig3.field.a"},
                {"node_id": "node.sig3.field.b"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig3.field.a_b",
                    "from_node_id": "node.sig3.field.a",
                    "to_node_id": "node.sig3.field.b",
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
                    "description": "field scaled loss",
                    "deterministic_function_id": "loss.linear_attenuation.v1",
                    "attenuation_policy_id": "att.field_scaled",
                    "parameters": {
                        "base_loss_permille": 600,
                        "distance_loss_permille": 0,
                        "field_visibility_weight_permille": 1000,
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
                    "attenuation_policy_id": "att.field_scaled",
                    "description": "field scaled attenuation",
                    "base_loss_rate": 0,
                    "field_modifier_ids": ["field.visibility", "field.radiation", "field.wind"],
                    "deterministic_function_id": "att.field_scaled.v1",
                    "uses_rng_stream": False,
                    "rng_stream_name": None,
                    "extensions": {
                        "field_visibility_weight_permille": 1000
                    },
                }
            ]
        }
    }


def _delivery_state(*, visibility_permille: int) -> str:
    from src.signals import build_signal_channel, process_signal_send, tick_signal_transport

    channels = [
        build_signal_channel(
            channel_id="channel.sig3.field.001",
            channel_type_id="channel.optical_line_of_sight",
            network_graph_id="graph.sig3.field.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.linear_attenuation",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=101,
        channel_id="channel.sig3.field.001",
        from_node_id="node.sig3.field.a",
        artifact_id="artifact.sig3.field.001",
        sender_subject_id="subject.sig3.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig3.receiver", "to_node_id": "node.sig3.field.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = tick_signal_transport(
        current_tick=101,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        attenuation_policy_registry=_attenuation_registry(),
        routing_policy_registry={},
        field_samples_by_node_id={
            "node.sig3.field.b": {
                "field.visibility": int(max(0, visibility_permille)),
            }
        },
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

    clear_state = _delivery_state(visibility_permille=0)
    degraded_state = _delivery_state(visibility_permille=500)
    if not clear_state or not degraded_state:
        return {"status": "fail", "message": "missing delivery state rows"}
    if clear_state == degraded_state:
        return {
            "status": "fail",
            "message": "field scaling did not change delivery outcome under configured thresholds",
        }
    if clear_state != "delivered" or degraded_state != "lost":
        return {
            "status": "fail",
            "message": "expected delivered->lost transition from high field visibility attenuation",
        }
    return {"status": "pass", "message": "field-scaled attenuation affects loss deterministically"}
