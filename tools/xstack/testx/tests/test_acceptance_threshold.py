"""FAST test: SIG-5 receipt acceptance follows belief policy threshold."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.acceptance_threshold"
TEST_TAGS = ["fast", "signals", "trust", "acceptance"]


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


def _belief_registry() -> dict:
    return {
        "record": {
            "belief_policies": [
                {
                    "schema_version": "1.0.0",
                    "belief_policy_id": "belief.default",
                    "acceptance_threshold": 0.6,
                    "decay_rate_per_tick": 0.0,
                    "update_rule_id": "update.linear_adjust",
                    "extensions": {},
                }
            ]
        }
    }


def _run_once(trust_weight: float) -> bool:
    from signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channel_rows = [
        build_signal_channel(
            channel_id="channel.sig.accept.001",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.accept.001",
            capacity_per_tick=4,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=101,
        channel_id="channel.sig.accept.001",
        from_node_id="node.a",
        artifact_id="artifact.sig.accept.001",
        sender_subject_id="subject.sender",
        recipient_address={"kind": "single", "subject_id": "subject.receiver", "to_node_id": "node.b"},
        signal_channel_rows=channel_rows,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = process_signal_transport_tick(
        current_tick=101,
        signal_channel_rows=channel_rows,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=[
            {
                "graph_id": "graph.sig.accept.001",
                "nodes": [{"node_id": "node.a"}, {"node_id": "node.b"}],
                "edges": [{"edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b"}],
            }
        ],
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
        trust_edge_rows=[
            {
                "from_subject_id": "subject.receiver",
                "to_subject_id": "subject.sender",
                "trust_weight": float(trust_weight),
                "evidence_count": 0,
                "last_updated_tick": 0,
                "extensions": {},
            }
        ],
        belief_policy_registry=_belief_registry(),
        belief_policy_id="belief.default",
    )
    receipts = list(ticked.get("knowledge_receipt_rows") or [])
    if not receipts:
        return False
    return bool(dict(dict(receipts[0]).get("extensions") or {}).get("accepted", False))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    low = _run_once(0.2)
    high = _run_once(0.9)
    if low:
        return {"status": "fail", "message": "low-trust receipt should be untrusted under threshold policy"}
    if not high:
        return {"status": "fail", "message": "high-trust receipt should be accepted under threshold policy"}
    return {"status": "pass", "message": "acceptance threshold enforced"}
