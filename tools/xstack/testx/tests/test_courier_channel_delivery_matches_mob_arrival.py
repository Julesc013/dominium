"""FAST test: courier channel delivery occurs only on courier arrival."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.courier_channel_delivery_matches_mob_arrival"
TEST_TAGS = ["fast", "signals", "courier", "mobility"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig.courier.001",
            "nodes": [{"node_id": "node.sig.origin"}, {"node_id": "node.sig.dest"}],
            "edges": [
                {
                    "edge_id": "edge.sig.origin_dest",
                    "from_node_id": "node.sig.origin",
                    "to_node_id": "node.sig.dest",
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
            channel_id="channel.sig.courier.001",
            channel_type_id="channel.courier_route",
            network_graph_id="graph.sig.courier.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=400,
        channel_id="channel.sig.courier.001",
        from_node_id="node.sig.origin",
        artifact_id="artifact.sig.courier.001",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver", "to_node_id": "node.sig.dest"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    first_tick = tick_signal_transport(
        current_tick=400,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=16,
        cost_units_per_delivery=1,
        courier_arrival_rows=[],
    )
    queue_rows = list(first_tick.get("signal_transport_queue_rows") or [])
    commitments = list(first_tick.get("created_courier_commitment_rows") or [])
    queue_key = str(dict(queue_rows[0]).get("queue_key", "")).strip() if queue_rows else ""
    envelope_id = str(dict(queue_rows[0]).get("envelope_id", "")).strip() if queue_rows else ""
    second_tick = tick_signal_transport(
        current_tick=401,
        signal_channel_rows=channels,
        signal_transport_queue_rows=queue_rows,
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=list(first_tick.get("message_delivery_event_rows") or []),
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=16,
        cost_units_per_delivery=1,
        courier_arrival_rows=[{"queue_key": queue_key, "envelope_id": envelope_id, "arrival_tick": 401}],
    )
    second_events = list(second_tick.get("message_delivery_event_rows") or [])
    last_event = dict(second_events[-1]) if second_events else {}
    return {
        "first_delivered_count": int(len(list(first_tick.get("delivered_rows") or []))),
        "first_queue_count": int(len(queue_rows)),
        "courier_commitment_count": int(len(commitments)),
        "courier_commitment_id": str(dict(commitments[0]).get("commitment_id", "")).strip() if commitments else "",
        "second_delivered_count": int(len(list(second_tick.get("delivered_rows") or []))),
        "second_queue_count": int(len(list(second_tick.get("signal_transport_queue_rows") or []))),
        "second_event_state": str(last_event.get("delivery_state", "")).strip(),
        "second_event_commitment_id": str((dict(last_event.get("extensions") or {})).get("courier_commitment_id", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    result = _run_once()
    if int(result.get("first_delivered_count", 0)) != 0:
        return {"status": "fail", "message": "courier channel should not deliver before arrival"}
    if int(result.get("first_queue_count", 0)) != 1:
        return {"status": "fail", "message": "courier queue row should remain pending before arrival"}
    if int(result.get("courier_commitment_count", 0)) != 1:
        return {"status": "fail", "message": "expected deterministic courier commitment creation"}
    if int(result.get("second_delivered_count", 0)) != 1:
        return {"status": "fail", "message": "courier channel should deliver exactly once on arrival"}
    if int(result.get("second_queue_count", 0)) != 0:
        return {"status": "fail", "message": "courier queue should be empty after arrival delivery"}
    if str(result.get("second_event_state", "")) != "delivered":
        return {"status": "fail", "message": "courier arrival should result in delivered event"}
    if str(result.get("second_event_commitment_id", "")) != str(result.get("courier_commitment_id", "")):
        return {"status": "fail", "message": "delivery event must reference courier commitment id"}
    return {"status": "pass", "message": "courier delivery matches mobility arrival"}

