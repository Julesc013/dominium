"""FAST test: process.time_adjust applies bounded deterministic correction."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_time_adjust_bounded"
TEST_TAGS = ["fast", "time", "temp2", "sync"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


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
            "intent_id": "intent.temp2.sync.adjust.001",
            "process_id": "process.time_adjust",
            "inputs": {
                "sync_policy_id": "sync.adjust_on_receipt",
                "temporal_domain_id": "time.civil",
                "target_id": "session.default",
                "local_domain_time": 100,
                "remote_domain_time": 135,
                "max_adjust_per_tick": 4,
                "max_skew_allowed": 50,
                "originating_receipt_id": "receipt.temp2.sync.001",
            },
        },
        law_profile=law,
        authority_context=authority,
        navigation_indices={},
        policy_context=policy,
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "time_adjust execution failed: {}".format(result)}

    metadata = dict(result.get("metadata") or {})
    adjustment_delta = int(metadata.get("adjustment_delta", 0) or 0)
    if int(abs(adjustment_delta)) > 4:
        return {"status": "fail", "message": "adjustment_delta exceeded max_adjust_per_tick bound"}
    if adjustment_delta != 4:
        return {"status": "fail", "message": "expected bounded adjustment_delta=4, observed {}".format(adjustment_delta)}

    event_rows = [dict(row) for row in list(state.get("time_adjust_events") or []) if isinstance(row, dict)]
    if not event_rows:
        return {"status": "fail", "message": "time_adjust_events were not emitted"}
    latest = dict(event_rows[-1])
    if int(latest.get("adjustment_delta", 0) or 0) != 4:
        return {"status": "fail", "message": "time_adjust_event adjustment_delta mismatch"}

    hash_chain = str(state.get("time_adjust_event_hash_chain", "")).strip().lower()
    if not _HASH64.fullmatch(hash_chain):
        return {"status": "fail", "message": "time_adjust_event_hash_chain missing/invalid"}
    return {"status": "pass", "message": "time_adjust bounded correction enforced"}
