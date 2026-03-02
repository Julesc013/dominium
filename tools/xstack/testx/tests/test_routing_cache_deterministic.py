"""FAST test: SIG routing cache behavior is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.routing_cache_deterministic"
TEST_TAGS = ["fast", "signals", "routing", "determinism"]


def _graph() -> list[dict]:
    return [
        {
            "graph_id": "graph.sig.cache.001",
            "nodes": [
                {"node_id": "node.sig.a"},
                {"node_id": "node.sig.b"},
            ],
            "edges": [
                {
                    "edge_id": "edge.sig.a_b",
                    "from_node_id": "node.sig.a",
                    "to_node_id": "node.sig.b",
                    "delay_ticks": 0,
                    "capacity": 2,
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
    from src.signals import build_signal_channel, process_signal_send, tick_signal_transport

    channels = [
        build_signal_channel(
            channel_id="channel.sig.cache.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.cache.001",
            capacity_per_tick=2,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
            extensions={"routing_policy_id": "route.shortest_delay"},
        )
    ]
    sent = process_signal_send(
        current_tick=40,
        channel_id="channel.sig.cache.001",
        from_node_id="node.sig.a",
        artifact_id="artifact.sig.cache.001",
        sender_subject_id="subject.sig.sender",
        recipient_address={"kind": "single", "subject_id": "subject.sig.receiver", "to_node_id": "node.sig.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = tick_signal_transport(
        current_tick=40,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        existing_delivery_event_rows=[],
        network_graph_rows=_graph(),
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
        route_cache_state={"entries_by_key": {}, "next_sequence": 0},
    )
    events = list(ticked.get("message_delivery_event_rows") or [])
    first_event = dict(events[0]) if events else {}
    extensions = dict(first_event.get("extensions") or {})
    cache_state = dict(ticked.get("route_cache_state") or {})
    entries_by_key = dict(cache_state.get("entries_by_key") or {})
    return {
        "route_cache_key": str(extensions.get("route_cache_key", "")).strip(),
        "cache_entry_count": int(len(entries_by_key)),
        "cache_keys": sorted(str(key) for key in entries_by_key.keys()),
        "event_state": str(first_event.get("delivery_state", "")).strip(),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "routing cache behavior drifted across identical runs"}
    if not first.get("route_cache_key"):
        return {"status": "fail", "message": "expected route_cache_key in delivery event extensions"}
    if int(first.get("cache_entry_count", 0)) != 1:
        return {"status": "fail", "message": "expected a single deterministic route cache entry"}
    if str(first.get("event_state", "")) != "delivered":
        return {"status": "fail", "message": "expected delivered state in routing cache fixture"}
    return {"status": "pass", "message": "routing cache deterministic"}

