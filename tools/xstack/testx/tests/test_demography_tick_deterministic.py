"""STRICT test: CIV-4 demography tick is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.civilisation.demography_tick_deterministic"
TEST_TAGS = ["strict", "civilisation", "demography", "determinism"]


def _run_once():
    from tools.xstack.sessionx.process_runtime import replay_intent_script
    from tools.xstack.testx.tests.demography_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_cohort,
    )

    state = with_cohort(base_state(), "cohort.demo.001", size=1000, location_ref="region.alpha")
    intents = [
        {
            "intent_id": "intent.demography.tick.001",
            "process_id": "process.demography_tick",
            "inputs": {"demography_policy_id": "demo.policy.basic_births"},
        }
    ]
    return replay_intent_script(
        universe_state=copy.deepcopy(state),
        law_profile=law_profile(["process.demography_tick"], births_allowed=True),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        intents=intents,
        navigation_indices={},
        policy_context=policy_context(parameter_bundle_id="params.civ.basic_births"),
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "demography replay must complete in both runs"}
    if str(first.get("final_state_hash", "")) != str(second.get("final_state_hash", "")):
        return {"status": "fail", "message": "demography final hash diverged across deterministic runs"}

    state = dict(first.get("universe_state") or {})
    rows = [dict(row) for row in list(state.get("cohort_assemblies") or []) if isinstance(row, dict)]
    if len(rows) != 1:
        return {"status": "fail", "message": "expected one cohort row after demography tick"}
    size_after = int(rows[0].get("size", 0) or 0)
    if size_after != 1001:
        return {"status": "fail", "message": "expected deterministic size 1001 after basic births/deaths"}
    return {"status": "pass", "message": "demography tick deterministic baseline passed"}

