"""STRICT test: law-forbidden births refuse deterministic demography tick."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.births_forbidden_by_law_refusal"
TEST_TAGS = ["strict", "civilisation", "demography", "refusal"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import replay_intent_script
    from tools.xstack.testx.tests.demography_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_cohort,
    )

    state = with_cohort(base_state(), "cohort.demo.003", size=1000, location_ref="region.alpha")
    result = replay_intent_script(
        universe_state=copy.deepcopy(state),
        law_profile=law_profile(["process.demography_tick"], births_allowed=False),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        intents=[
            {
                "intent_id": "intent.demography.tick.003",
                "process_id": "process.demography_tick",
                "inputs": {"demography_policy_id": "demo.policy.basic_births"},
            }
        ],
        navigation_indices={},
        policy_context=policy_context(parameter_bundle_id="params.civ.basic_births"),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected refusal when births are forbidden by law"}
    reason = str((result.get("refusal") or {}).get("reason_code", ""))
    if reason != "refusal.civ.births_forbidden_by_law":
        return {"status": "fail", "message": "unexpected refusal code '{}'".format(reason)}
    return {"status": "pass", "message": "law-forbidden births refusal passed"}

