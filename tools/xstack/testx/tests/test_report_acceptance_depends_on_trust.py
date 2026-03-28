"""FAST test: institutional report receipt acceptance follows trust threshold."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.institutions.report_acceptance_depends_on_trust"
TEST_TAGS = ["fast", "signals", "institutions", "trust", "receipt"]


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
                    "acceptance_threshold": 0.7,
                    "decay_rate_per_tick": 0.0,
                    "update_rule_id": "update.linear_adjust",
                    "extensions": {},
                }
            ]
        }
    }


def _run_once(*, trust_weight: float) -> bool:
    from signals import build_signal_channel, process_signal_send, process_signal_transport_tick

    channels = [
        build_signal_channel(
            channel_id="channel.local_institutional",
            channel_type_id="channel.wired_basic",
            network_graph_id="graph.sig.trust.inst.001",
            capacity_per_tick=8,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    sent = process_signal_send(
        current_tick=900,
        channel_id="channel.local_institutional",
        from_node_id="node.inst.a",
        artifact_id="artifact.report.institution.001",
        sender_subject_id="subject.institution.metro_dispatch",
        recipient_address={"kind": "single", "subject_id": "subject.driver.001", "to_node_id": "node.inst.b"},
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
    )
    ticked = process_signal_transport_tick(
        current_tick=900,
        signal_channel_rows=channels,
        signal_transport_queue_rows=list(sent.get("signal_transport_queue_rows") or []),
        signal_message_envelope_rows=list(sent.get("signal_message_envelope_rows") or []),
        message_delivery_event_rows=[],
        knowledge_receipt_rows=[],
        network_graph_rows=[
            {
                "graph_id": "graph.sig.trust.inst.001",
                "nodes": [{"node_id": "node.inst.a"}, {"node_id": "node.inst.b"}],
                "edges": [{"edge_id": "edge.inst.a_b", "from_node_id": "node.inst.a", "to_node_id": "node.inst.b"}],
            }
        ],
        loss_policy_registry=_loss_registry(),
        routing_policy_registry={},
        max_cost_units=8,
        cost_units_per_delivery=1,
        trust_edge_rows=[
            {
                "from_subject_id": "subject.driver.001",
                "to_subject_id": "subject.institution.metro_dispatch",
                "trust_weight": float(trust_weight),
                "evidence_count": 1,
                "last_updated_tick": 800,
                "extensions": {},
            }
        ],
        belief_policy_registry=_belief_registry(),
        belief_policy_id="belief.default",
    )
    receipts = list(ticked.get("created_receipt_rows") or [])
    if not receipts:
        return False
    row = dict(receipts[0])
    ext = dict(row.get("extensions") or {})
    return bool(ext.get("accepted", False))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    low_trust_accept = _run_once(trust_weight=0.6)
    high_trust_accept = _run_once(trust_weight=0.9)
    if low_trust_accept:
        return {"status": "fail", "message": "low-trust report receipt should be untrusted under threshold 0.7"}
    if not high_trust_accept:
        return {"status": "fail", "message": "high-trust report receipt should be accepted"}
    return {"status": "pass", "message": "report acceptance depends on trust threshold"}

