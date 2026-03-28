"""STRICT test: memory decay uses deterministic tick deltas only."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.epistemics.memory_decay_tick_based"
TEST_TAGS = ["strict", "epistemics", "memory"]


def _policies():
    retention = {
        "retention_policy_id": "ep.retention.session_strict",
        "memory_allowed": True,
        "max_memory_items": 16,
        "decay_model_id": "ep.decay.session_strict",
        "eviction_rule_id": "evict.oldest_first",
        "deterministic_eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }
    decay = {
        "decay_model_id": "ep.decay.session_strict",
        "description": "strict short ttl",
        "ttl_rules": [
            {
                "rule_id": "ttl.default",
                "channel_id": "*",
                "subject_kind": "*",
                "ttl_ticks": 3,
            }
        ],
        "refresh_rules": [
            {
                "rule_id": "refresh.disabled",
                "channel_id": "*",
                "subject_kind": "*",
                "refresh_on_observed": False,
            }
        ],
        "eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }
    eviction = {
        "eviction_rule_id": "evict.oldest_first",
        "description": "oldest",
        "algorithm_id": "evict.oldest_first",
        "priority_by_channel": {},
        "priority_by_subject_kind": {},
        "extensions": {},
    }
    return retention, decay, eviction


def _perceived_payload(tick: int, include_channels: bool) -> dict:
    channels = ["ch.core.time"] if include_channels else []
    return {
        "channels": channels,
        "time": {"tick": int(tick)},
        "time_state": {"tick": int(tick), "rate_permille": 1000, "paused": False},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from epistemics.memory import update_memory_store

    retention, decay, eviction = _policies()
    first = update_memory_store(
        perceived_now=_perceived_payload(tick=1, include_channels=True),
        owner_subject_id="peer.alpha",
        retention_policy=copy.deepcopy(retention),
        decay_model=copy.deepcopy(decay),
        eviction_rule=copy.deepcopy(eviction),
        previous_store={},
        tick=1,
    )
    if str(first.get("result", "")) != "complete":
        return {"status": "fail", "message": "initial memory update refused unexpectedly"}
    first_state = dict(first.get("memory_state") or {})
    first_items = list(first_state.get("items") or [])
    if not first_items:
        return {"status": "fail", "message": "expected memory item missing at tick=1"}
    ttl_1 = int((first_items[0] or {}).get("ttl_ticks", 0) or 0)

    second = update_memory_store(
        perceived_now=_perceived_payload(tick=2, include_channels=False),
        owner_subject_id="peer.alpha",
        retention_policy=copy.deepcopy(retention),
        decay_model=copy.deepcopy(decay),
        eviction_rule=copy.deepcopy(eviction),
        previous_store=copy.deepcopy(first_state),
        tick=2,
    )
    third = update_memory_store(
        perceived_now=_perceived_payload(tick=3, include_channels=False),
        owner_subject_id="peer.alpha",
        retention_policy=copy.deepcopy(retention),
        decay_model=copy.deepcopy(decay),
        eviction_rule=copy.deepcopy(eviction),
        previous_store=dict(second.get("memory_state") or {}),
        tick=3,
    )
    fourth = update_memory_store(
        perceived_now=_perceived_payload(tick=4, include_channels=False),
        owner_subject_id="peer.alpha",
        retention_policy=copy.deepcopy(retention),
        decay_model=copy.deepcopy(decay),
        eviction_rule=copy.deepcopy(eviction),
        previous_store=dict(third.get("memory_state") or {}),
        tick=4,
    )
    if any(str(row.get("result", "")) != "complete" for row in (second, third, fourth)):
        return {"status": "fail", "message": "memory decay sequence refused unexpectedly"}

    ttl_2 = int((((dict(second.get("memory_state") or {}).get("items") or [{}])[0] or {}).get("ttl_ticks", 0) or 0))
    ttl_3 = int((((dict(third.get("memory_state") or {}).get("items") or [{}])[0] or {}).get("ttl_ticks", 0) or 0))
    ttl_4_items = list(dict(fourth.get("memory_state") or {}).get("items") or [])

    if [ttl_1, ttl_2, ttl_3] != [3, 2, 1]:
        return {"status": "fail", "message": "tick-based ttl progression mismatch; expected 3->2->1"}
    if ttl_4_items:
        return {"status": "fail", "message": "expired memory items should be removed deterministically at tick=4"}
    return {"status": "pass", "message": "tick-based memory decay check passed"}
