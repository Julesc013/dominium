"""STRICT test: cohort population never becomes negative under demography tick."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.population_never_negative"
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

    state = with_cohort(base_state(), "cohort.demo.004", size=1, location_ref="region.alpha")
    result = replay_intent_script(
        universe_state=copy.deepcopy(state),
        law_profile=law_profile(["process.demography_tick"], births_allowed=False),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        intents=[
            {
                "intent_id": "intent.demography.tick.004",
                "process_id": "process.demography_tick",
                "inputs": {"demography_policy_id": "demo.policy.overkill"},
            }
        ],
        navigation_indices={},
        policy_context=policy_context(
            parameter_bundle_id="params.civ.nobirths",
            include_overkill=True,
        ),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "demography overkill policy should complete deterministically"}
    state_after = dict(result.get("universe_state") or {})
    rows = [dict(row) for row in list(state_after.get("cohort_assemblies") or []) if isinstance(row, dict)]
    if len(rows) != 1:
        return {"status": "fail", "message": "expected one cohort after overkill demography tick"}
    size_after = int(rows[0].get("size", 0) or 0)
    if size_after < 0:
        return {"status": "fail", "message": "cohort size became negative"}
    if size_after != 0:
        return {"status": "fail", "message": "expected cohort size to clamp at zero under overkill death rate"}
    return {"status": "pass", "message": "population non-negative clamp passed"}

