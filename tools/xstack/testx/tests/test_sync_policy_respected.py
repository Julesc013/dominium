"""FAST test: sync policy strategy (reject) is respected deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_sync_policy_respected"
TEST_TAGS = ["fast", "time", "temp2", "sync"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import authority_context, base_state, law_profile, policy_context

    state = base_state()
    law = law_profile(["process.time_adjust"])
    authority = authority_context(["session.boot"], privilege_level="observer")
    policy = policy_context()

    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.temp2.sync.reject.001",
            "process_id": "process.time_adjust",
            "inputs": {
                "sync_policy_id": "sync.strict_reject",
                "temporal_domain_id": "time.civil",
                "target_id": "session.default",
                "local_domain_time": 100,
                "remote_domain_time": 180,
                "max_adjust_per_tick": 5,
                "max_skew_allowed": 10,
                "originating_receipt_id": "receipt.temp2.sync.reject.001",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "time_adjust reject execution failed: {}".format(result)}

    metadata = dict(result.get("metadata") or {})
    if not bool(metadata.get("rejected", False)):
        return {"status": "fail", "message": "sync.strict_reject should reject skew above bound"}
    if int(metadata.get("adjustment_delta", 0) or 0) != 0:
        return {"status": "fail", "message": "reject strategy must keep adjustment_delta at zero"}

    event_rows = [dict(row) for row in list(state.get("time_adjust_events") or []) if isinstance(row, dict)]
    if not event_rows:
        return {"status": "fail", "message": "reject strategy must still log time_adjust_event"}
    latest = dict(event_rows[-1])
    extensions = dict(latest.get("extensions") or {})
    if not bool(extensions.get("rejected", False)):
        return {"status": "fail", "message": "time_adjust_event extensions missing rejected=true"}
    return {"status": "pass", "message": "sync policy strategy enforced deterministically"}
