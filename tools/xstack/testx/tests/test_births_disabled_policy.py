"""STRICT test: births-disabled policy keeps births at zero."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.births_disabled_policy"
TEST_TAGS = ["strict", "civilisation", "demography"]


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

    state = with_cohort(base_state(), "cohort.demo.002", size=1000, location_ref="region.alpha")
    result = replay_intent_script(
        universe_state=copy.deepcopy(state),
        law_profile=law_profile(["process.demography_tick"], births_allowed=True),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        intents=[
            {
                "intent_id": "intent.demography.tick.002",
                "process_id": "process.demography_tick",
                "inputs": {"demography_policy_id": "demo.policy.stable_no_birth"},
            }
        ],
        navigation_indices={},
        policy_context=policy_context(parameter_bundle_id="params.civ.nobirths"),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "demography tick refused under births-disabled policy"}
    state_after = dict(result.get("universe_state") or {})
    rows = [dict(row) for row in list(state_after.get("cohort_assemblies") or []) if isinstance(row, dict)]
    if len(rows) != 1:
        return {"status": "fail", "message": "expected one cohort row after stable_no_birth policy tick"}
    extensions = dict(rows[0].get("extensions") or {})
    if int(extensions.get("demography_last_births", -1)) != 0:
        return {"status": "fail", "message": "births-disabled policy produced nonzero births"}
    if int(rows[0].get("size", 0) or 0) != 999:
        return {"status": "fail", "message": "expected deterministic size 999 under stable_no_birth policy"}
    return {"status": "pass", "message": "births-disabled policy behavior passed"}
