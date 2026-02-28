"""FAST test: core flow transfer capacity/delay/loss behavior is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.core.flow_engine_capacity_delay_loss_deterministic"
TEST_TAGS = ["fast", "core", "flow", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.core.flow.flow_engine import flow_transfer
    from tools.xstack.compatx.canonical_json import canonical_sha256

    first = flow_transfer(
        quantity=1000,
        loss_fraction=100,
        scale=1000,
        capacity_per_tick=600,
        delay_ticks=3,
    )
    second = flow_transfer(
        quantity=1000,
        loss_fraction=100,
        scale=1000,
        capacity_per_tick=600,
        delay_ticks=3,
    )
    if first != second:
        return {"status": "fail", "message": "flow_transfer returned non-deterministic outputs"}
    if int(first.get("processed_mass", -1)) != 600:
        return {"status": "fail", "message": "flow_transfer capacity_per_tick not enforced deterministically"}
    if int(first.get("loss_mass", -1)) != 60:
        return {"status": "fail", "message": "flow_transfer deterministic loss rounding mismatch"}
    if int(first.get("delivered_mass", -1)) != 540:
        return {"status": "fail", "message": "flow_transfer delivered_mass mismatch"}
    if int(first.get("deferred_mass", -1)) != 400:
        return {"status": "fail", "message": "flow_transfer deferred_mass mismatch"}
    if int(first.get("delay_ticks", -1)) != 3:
        return {"status": "fail", "message": "flow_transfer delay_ticks mismatch"}

    hash_a = canonical_sha256(first)
    hash_b = canonical_sha256(second)
    if hash_a != hash_b:
        return {"status": "fail", "message": "flow_transfer hash diverged across identical runs"}

    return {"status": "pass", "message": "Flow engine deterministic capacity/delay/loss passed"}

