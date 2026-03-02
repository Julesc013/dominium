"""FAST test: breaker safety pattern disconnects channel flow deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_breaker_trip_disconnects_flow"
TEST_TAGS = ["fast", "safety", "breaker", "flow"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.safety_testlib import authority_context, base_state, law_profile, policy_context

    channel_id = "channel.safety.breaker"
    state = base_state(current_tick=7)
    state["signal_channel_rows"] = [
        {
            "schema_version": "1.0.0",
            "channel_id": channel_id,
            "channel_type_id": "channel.wired_basic",
            "network_graph_id": "graph.signal.test",
            "capacity_per_tick": 32,
            "base_delay_ticks": 1,
            "loss_policy_id": "loss.none",
            "encryption_policy_id": None,
            "deterministic_fingerprint": "",
            "extensions": {"queue_depth": 0},
        }
    ]
    state["safety_instances"] = [
        {
            "schema_version": "1.0.0",
            "instance_id": "instance.safety.breaker.main",
            "pattern_id": "safety.breaker_trip",
            "target_ids": [channel_id],
            "active": True,
            "created_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {},
        }
    ]
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.safety.breaker.tick.001",
            "process_id": "process.safety_tick",
            "inputs": {
                "condition_overrides": {
                    channel_id: {
                        "flow.load_units": 4,
                    }
                }
            },
        },
        law_profile=copy.deepcopy(law_profile(["process.safety_tick"])),
        authority_context=copy.deepcopy(authority_context()),
        navigation_indices={},
        policy_context=copy.deepcopy(policy_context()),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "safety tick failed for breaker fixture"}
    channels = [dict(row) for row in list(state.get("signal_channel_rows") or []) if isinstance(row, dict)]
    channel_row = {}
    for row in channels:
        if str(row.get("channel_id", "")).strip() == channel_id:
            channel_row = dict(row)
            break
    if not channel_row:
        return {"status": "fail", "message": "channel row missing after breaker trip safety tick"}
    if int(max(0, int(channel_row.get("capacity_per_tick", 0)))) != 0:
        return {"status": "fail", "message": "breaker trip should force channel capacity_per_tick to 0"}
    ext = dict(channel_row.get("extensions") or {})
    if not bool(ext.get("safety_disconnected", False)):
        return {"status": "fail", "message": "breaker trip should mark safety_disconnected in channel extensions"}
    return {"status": "pass", "message": "breaker trip disconnected flow deterministically"}
