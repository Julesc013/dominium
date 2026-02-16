"""FAST test: deterministic network disorder simulator output is stable for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.disorder_sim_deterministic"
TEST_TAGS = ["fast", "net", "determinism", "multiplayer"]


def _messages():
    return [
        {"msg_id": "m.001", "sequence": 1, "payload": {"token": "a"}},
        {"msg_id": "m.002", "sequence": 2, "payload": {"token": "b"}},
        {"msg_id": "m.003", "sequence": 3, "payload": {"token": "c"}},
        {"msg_id": "m.004", "sequence": 4, "payload": {"token": "d"}},
    ]


def _run_once():
    from src.net.testing import DeterministicNetDisorderSim

    sim = DeterministicNetDisorderSim(disorder_profile_id="disorder.dup_reorder_delay")
    for tick in range(0, 3):
        sim.inject(channel_id="ch.test", tick=tick, messages=_messages())
    out = []
    for tick in range(0, 6):
        delivered = sim.deliver(channel_id="ch.test", tick=tick)
        out.append(
            {
                "tick": int(tick),
                "hash": str(delivered.get("message_hash", "")),
                "count": int(delivered.get("delivered_count", 0) or 0),
                "ids": [str((row or {}).get("msg_id", "")) for row in (delivered.get("messages") or [])],
            }
        )
    return out


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "deterministic network disorder simulator diverged across repeated runs"}
    return {"status": "pass", "message": "deterministic network disorder simulator is stable"}

