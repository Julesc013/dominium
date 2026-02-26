"""STRICT test: over-demand degrades deterministically instead of refusing tick execution."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.performance.budget_exceeded_triggers_degrade_not_lag"
TEST_TAGS = ["strict", "performance", "budget", "determinism"]


def _policy_context():
    from tools.xstack.testx.tests.cohort_testlib import policy_context_for_roi

    context = policy_context_for_roi(max_entities_micro=128, mapping_max_micro=32)
    context["physics_profile_id"] = "physics.test.performance"
    context["budget_envelope_id"] = "budget.test.tiny"
    context["budget_envelope_registry"] = {
        "envelopes": [
            {
                "envelope_id": "budget.test.tiny",
                "max_micro_entities_per_shard": 4,
                "max_micro_regions_per_shard": 1,
                "max_solver_cost_units_per_tick": 8,
                "max_inspection_cost_units_per_tick": 2,
                "extensions": {},
            }
        ]
    }
    context["arbitration_policy_id"] = "arb.equal_share"
    context["arbitration_policy_registry"] = {
        "policies": [
            {
                "arbitration_policy_id": "arb.equal_share",
                "mode": "equal_share",
                "weight_source": "none",
                "tie_break_rule_id": "tie.player_region_tick",
                "extensions": {},
            }
        ]
    }
    return context


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.cohort_testlib import authority_context, base_state, law_profile, navigation_indices_for_roi

    state = copy.deepcopy(base_state())
    result = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.performance.degrade.tick.001",
            "process_id": "process.region_management_tick",
            "inputs": {},
        },
        law_profile=law_profile(["process.region_management_tick"]),
        authority_context=authority_context(["session.boot"], privilege_level="observer"),
        navigation_indices=navigation_indices_for_roi(),
        policy_context=_policy_context(),
    )
    if str(result.get("result", "")) != "complete":
        return {"status": "fail", "message": "budget exceed fixture refused; expected deterministic degrade/cap path"}
    outcome = str(result.get("budget_outcome", ""))
    if outcome not in ("degraded", "capped"):
        return {"status": "fail", "message": "budget exceed fixture did not trigger degrade/cap outcome"}
    cost = dict(result.get("cost_snapshot") or {})
    envelope = dict(result.get("envelope_evaluation") or {})
    if int(cost.get("solver_cost_units", 0) or 0) > int(envelope.get("max_solver_cost_units_per_tick", 0) or 0):
        return {"status": "fail", "message": "solver cost exceeded capped envelope after degradation"}
    return {"status": "pass", "message": "budget pressure degraded deterministically without lag/refusal"}

