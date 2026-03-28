"""FAST test: SIG-2 queue ordering remains deterministic by envelope then subject."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.queue_order_deterministic"
TEST_TAGS = ["fast", "signals", "queue", "determinism"]


def _channel():
    from signals import build_signal_channel

    return [
        build_signal_channel(
            channel_id="channel.sig.queue.001",
            channel_type_id="channel.local_institutional",
            network_graph_id="graph.sig.queue.001",
            capacity_per_tick=8,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]


def _run_once() -> list[tuple[str, str]]:
    from signals import process_signal_send

    sent = process_signal_send(
        current_tick=11,
        channel_id="channel.sig.queue.001",
        from_node_id="node.sig.queue.a",
        artifact_id="artifact.sig.queue.001",
        sender_subject_id="subject.sender",
        recipient_address={
            "kind": "group",
            "group_id": "group.queue.alpha",
            "to_node_id": "node.sig.queue.b",
        },
        signal_channel_rows=_channel(),
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
        info_artifact_rows=[
            {"artifact_id": "artifact.sig.queue.001", "artifact_family_id": "INFO.RECORD", "created_tick": 10}
        ],
        group_membership_rows=[
            {
                "group_id": "group.queue.alpha",
                "subject_ids": ["subject.z", "subject.x", "subject.y"],
            }
        ],
    )
    queue_rows = list(sent.get("signal_transport_queue_rows") or [])
    return [
        (
            str(dict(row).get("envelope_id", "")).strip(),
            str(dict(row).get("recipient_subject_id", "")).strip(),
        )
        for row in queue_rows
    ]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "queue ordering drifted across identical runs"}
    expected = [
        (first[0][0], "subject.x"),
        (first[0][0], "subject.y"),
        (first[0][0], "subject.z"),
    ]
    if first != expected:
        return {"status": "fail", "message": "queue order must be envelope_id then recipient subject_id"}
    return {"status": "pass", "message": "queue ordering deterministic"}
