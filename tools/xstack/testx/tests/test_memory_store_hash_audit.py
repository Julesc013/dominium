"""STRICT test: memory store hash is stable and mismatch auditing emits deterministic events."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.epistemics.memory_store_hash_audit"
TEST_TAGS = ["strict", "epistemics", "net", "anti_cheat"]


def _runtime_fixture() -> dict:
    return {
        "anti_cheat": {
            "policy_id": "policy.ac.detect_only",
            "modules_enabled": ["ac.module.state_integrity"],
            "default_actions": {"ac.module.state_integrity": "audit"},
            "extensions": {},
        },
        "server": {
            "anti_cheat_events": [],
            "anti_cheat_enforcement_actions": [],
            "anti_cheat_refusal_injections": [],
            "anti_cheat_anchor_mismatches": [],
            "anti_cheat_violation_counters": {},
            "terminated_peers": [],
        },
    }


def _memory_store(update_memory_store):
    retention = {
        "retention_policy_id": "ep.retention.session_basic",
        "memory_allowed": True,
        "max_memory_items": 16,
        "decay_model_id": "ep.decay.session_basic",
        "eviction_rule_id": "evict.oldest_first",
        "deterministic_eviction_rule_id": "evict.oldest_first",
        "extensions": {},
    }
    decay = {
        "decay_model_id": "ep.decay.session_basic",
        "description": "test",
        "ttl_rules": [{"rule_id": "ttl.default", "channel_id": "*", "subject_kind": "*", "ttl_ticks": 12}],
        "refresh_rules": [{"rule_id": "refresh.default", "channel_id": "*", "subject_kind": "*", "refresh_on_observed": True}],
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
    payload = {
        "channels": ["ch.core.time", "ch.camera.state"],
        "time": {"tick": 1},
        "time_state": {"tick": 1, "rate_permille": 1000, "paused": False},
        "camera_viewpoint": {
            "assembly_id": "camera.main",
            "frame_id": "frame.world",
            "position_mm": {"x": 10, "y": 20, "z": 5},
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
            "lens_id": "lens.test",
        },
    }
    updated = update_memory_store(
        perceived_now=payload,
        owner_subject_id="peer.alpha",
        retention_policy=copy.deepcopy(retention),
        decay_model=copy.deepcopy(decay),
        eviction_rule=copy.deepcopy(eviction),
        previous_store={},
        tick=1,
    )
    return dict(updated.get("memory_store") or {})


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from epistemics.memory import memory_store_hash, update_memory_store
    from net.anti_cheat.anti_cheat_engine import check_state_integrity

    store = _memory_store(update_memory_store=update_memory_store)
    store_hash = str(store.get("store_hash", ""))
    recomputed_hash = str(memory_store_hash(store))
    if not store_hash or store_hash != recomputed_hash:
        return {"status": "fail", "message": "memory store_hash mismatch against deterministic recomputation"}

    runtime_one = _runtime_fixture()
    mismatch_one = check_state_integrity(
        repo_root=repo_root,
        runtime=runtime_one,
        tick=4,
        peer_id="peer.alpha",
        expected_hash=store_hash,
        actual_hash="0" * 64,
        reason_code="refusal.net.resync_required",
        default_action_token="audit",
    )
    if str(mismatch_one.get("result", "")) != "violation":
        return {"status": "fail", "message": "expected memory hash mismatch to emit deterministic state-integrity violation"}
    events_one = list((dict(runtime_one.get("server") or {}).get("anti_cheat_events") or []))
    if not events_one:
        return {"status": "fail", "message": "state-integrity mismatch did not emit anti-cheat event"}
    fingerprint_one = str((events_one[0] or {}).get("deterministic_fingerprint", ""))

    runtime_two = _runtime_fixture()
    mismatch_two = check_state_integrity(
        repo_root=repo_root,
        runtime=runtime_two,
        tick=4,
        peer_id="peer.alpha",
        expected_hash=store_hash,
        actual_hash="0" * 64,
        reason_code="refusal.net.resync_required",
        default_action_token="audit",
    )
    if str(mismatch_two.get("result", "")) != "violation":
        return {"status": "fail", "message": "second mismatch run did not emit deterministic state-integrity violation"}
    events_two = list((dict(runtime_two.get("server") or {}).get("anti_cheat_events") or []))
    fingerprint_two = str((events_two[0] or {}).get("deterministic_fingerprint", ""))
    if not fingerprint_one or fingerprint_one != fingerprint_two:
        return {"status": "fail", "message": "anti-cheat deterministic fingerprint drift for identical memory hash mismatch inputs"}
    return {"status": "pass", "message": "memory store hash audit and mismatch event checks passed"}

