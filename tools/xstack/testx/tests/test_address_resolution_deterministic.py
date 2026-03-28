"""FAST test: SIG-2 address resolution is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.address_resolution_deterministic"
TEST_TAGS = ["fast", "signals", "addressing", "determinism"]


def _run_once() -> dict:
    from signals import address_from_recipient_address, resolve_address_recipients

    group_address = address_from_recipient_address(
        {
            "kind": "group",
            "group_id": "group.dispatch.alpha",
            "to_node_id": "node.dispatch.alpha",
        }
    )
    group_resolved = resolve_address_recipients(
        address_row=group_address,
        group_membership_rows=[
            {"group_id": "group.dispatch.alpha", "subject_ids": ["subject.c", "subject.a", "subject.b"]}
        ],
    )

    broadcast_address = address_from_recipient_address(
        {
            "kind": "broadcast",
            "broadcast_scope": "scope.station.alpha",
            "to_node_id": "node.station.alpha",
        }
    )
    broadcast_resolved = resolve_address_recipients(
        address_row=broadcast_address,
        broadcast_scope_rows=[
            {"broadcast_scope": "scope.station.alpha", "subject_ids": ["subject.3", "subject.1", "subject.2"]}
        ],
    )

    return {
        "group_ids": list(group_resolved.get("recipient_subject_ids") or []),
        "broadcast_ids": list(broadcast_resolved.get("recipient_subject_ids") or []),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "address resolution drifted across identical runs"}
    if list(first.get("group_ids") or []) != ["subject.a", "subject.b", "subject.c"]:
        return {"status": "fail", "message": "group recipient ordering should be lexicographic"}
    if list(first.get("broadcast_ids") or []) != ["subject.1", "subject.2", "subject.3"]:
        return {"status": "fail", "message": "broadcast recipient ordering should be lexicographic"}
    return {"status": "pass", "message": "address resolution deterministic"}
