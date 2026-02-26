"""STRICT test: transition hysteresis prevents deterministic thrash across adjacent ticks."""

from __future__ import annotations

import sys


TEST_ID = "testx.reality.hysteresis_no_thrash_deterministic"
TEST_TAGS = ["strict", "reality", "transition", "determinism"]


def _transition_policy() -> dict:
    return {
        "transition_policy_id": "transition.policy.test_hysteresis",
        "description": "hysteresis transition fixture",
        "max_micro_regions": 2,
        "max_micro_entities": 16,
        "hysteresis_rules": {"min_transition_interval_ticks": 5},
        "arbitration_rule_id": "arb.priority_by_distance",
        "degrade_order": ["fine", "medium", "coarse"],
        "refuse_thresholds": {},
        "extensions": {"distance_quantization_mm": 1000},
    }


def _budget_policy() -> dict:
    return {
        "policy_id": "policy.budget.test_hysteresis",
        "max_regions_micro": 2,
        "max_entities_micro": 24,
        "max_compute_units_per_tick": 200,
        "entity_compute_weight": 1,
        "fallback_behavior": "degrade_fidelity",
        "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 4},
    }


def _run_tick(tick: int) -> dict:
    from src.reality.transitions.transition_controller import compute_transition_plan

    return compute_transition_plan(
        tick=int(tick),
        transition_policy=_transition_policy(),
        budget_policy=_budget_policy(),
        interest_regions_by_id={"region.earth": {"last_transition_tick": 9}},
        candidates=[{"region_id": "region.earth", "priority": 0, "distance_mm": 1000, "tier": "fine", "server_weight": 1}],
        current_active={"region.earth": "coarse"},
        forced_expand_region_ids=[],
        forced_collapse_region_ids=[],
        forced_expand_tiers={},
        tier_weight_by_tier={"coarse": 1, "medium": 2, "fine": 4},
        tier_entity_target_by_tier={"coarse": 0, "medium": 4, "fine": 8},
        entity_compute_weight=1,
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    tick_10 = _run_tick(10)
    tick_11 = _run_tick(11)
    tick_15 = _run_tick(15)
    tick_15_repeat = _run_tick(15)

    for row in (tick_10, tick_11, tick_15, tick_15_repeat):
        if str(row.get("result", "")) != "complete":
            return {"status": "fail", "message": "hysteresis fixture refused unexpectedly"}

    for row, label in ((tick_10, "tick_10"), (tick_11, "tick_11")):
        if dict(row.get("desired_active") or {}) != {"region.earth": "coarse"}:
            return {"status": "fail", "message": "hysteresis did not hold previous tier at {}".format(label)}
        if list(row.get("expand_ids") or []):
            return {"status": "fail", "message": "hysteresis produced unwanted expand transition at {}".format(label)}

    if dict(tick_15.get("desired_active") or {}) != {"region.earth": "fine"}:
        return {"status": "fail", "message": "hysteresis window expiry did not allow deterministic upgrade at tick 15"}
    if list(tick_15.get("expand_ids") or []) != ["region.earth"]:
        return {"status": "fail", "message": "hysteresis upgrade expand_ids mismatch at tick 15"}
    if dict(tick_15.get("desired_active") or {}) != dict(tick_15_repeat.get("desired_active") or {}):
        return {"status": "fail", "message": "hysteresis output is nondeterministic across repeated tick 15 runs"}

    return {"status": "pass", "message": "hysteresis anti-thrash determinism check passed"}
