"""STRICT test: SRZ per-tick hash includes ledger_hash contribution."""

from __future__ import annotations

import sys


TEST_ID = "testx.reality.test_mp_hash_includes_ledger"
TEST_TAGS = ["strict", "reality", "determinism", "net"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.srz import build_single_shard, per_tick_hash

    universe_state = {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 1},
        "agent_states": [],
        "world_assemblies": [],
        "active_law_references": [],
        "session_references": [],
        "history_anchors": [],
        "camera_assemblies": [],
        "controller_assemblies": [],
        "control_bindings": [],
        "time_control": {"rate_permille": 1000, "paused": False},
        "process_log": [],
        "interest_regions": [],
        "macro_capsules": [],
        "micro_regions": [],
        "performance_state": {},
    }
    shard = build_single_shard(
        universe_state=dict(universe_state),
        authority_origin="server",
        compatibility_version="1.0.0",
        last_hash_anchor="",
    )
    args = {
        "universe_state": dict(universe_state),
        "shards": [dict(shard)],
        "pack_lock_hash": "pack_lock_hash.testx.rs2",
        "registry_hashes": {"law_registry_hash": "hash.law"},
        "last_tick_hash": "",
    }
    without_ledger = per_tick_hash(**args, ledger_hash="")
    with_ledger_a = per_tick_hash(**args, ledger_hash="ledger.hash.a")
    with_ledger_b = per_tick_hash(**args, ledger_hash="ledger.hash.b")

    if with_ledger_a == with_ledger_b:
        return {"status": "fail", "message": "per_tick_hash did not change when ledger_hash changed"}
    if without_ledger == with_ledger_a or without_ledger == with_ledger_b:
        return {"status": "fail", "message": "per_tick_hash did not include ledger_hash in digest payload"}
    return {"status": "pass", "message": "SRZ per-tick hash digest includes ledger hash input"}
