"""STRICT test: transition selection is deterministic for equivalent candidate sets."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.reality.transition_selection_deterministic"
TEST_TAGS = ["strict", "reality", "transition", "determinism"]


def _transition_policy() -> dict:
    return {
        "transition_policy_id": "transition.policy.test",
        "description": "deterministic transition policy fixture",
        "max_micro_regions": 3,
        "max_micro_entities": 24,
        "hysteresis_rules": {"min_transition_interval_ticks": 0},
        "arbitration_rule_id": "arb.priority_by_distance",
        "degrade_order": ["fine", "medium", "coarse"],
        "refuse_thresholds": {},
        "extensions": {"distance_quantization_mm": 1000},
    }


def _budget_policy() -> dict:
    return {
        "policy_id": "policy.budget.test_transition_selection",
        "max_regions_micro": 3,
        "max_entities_micro": 12,
        "max_compute_units_per_tick": 100,
        "entity_compute_weight": 1,
        "fallback_behavior": "degrade_fidelity",
        "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 4},
    }


def _interest_regions() -> dict:
    return {
        "region.alpha": {"last_transition_tick": 0},
        "region.beta": {"last_transition_tick": 0},
        "region.gamma": {"last_transition_tick": 0},
        "region.delta": {"last_transition_tick": 0},
    }


def _candidate_rows() -> list:
    return [
        {"region_id": "region.gamma", "priority": 3, "distance_mm": 5000, "tier": "fine", "server_weight": 10},
        {"region_id": "region.alpha", "priority": 1, "distance_mm": 1000, "tier": "fine", "server_weight": 20},
        {"region_id": "region.delta", "priority": 4, "distance_mm": 8000, "tier": "medium", "server_weight": 30},
        {"region_id": "region.beta", "priority": 2, "distance_mm": 3000, "tier": "medium", "server_weight": 40},
    ]


def _run_once(candidates: list) -> dict:
    from src.reality.transitions.transition_controller import compute_transition_plan

    return compute_transition_plan(
        tick=10,
        transition_policy=_transition_policy(),
        budget_policy=_budget_policy(),
        interest_regions_by_id=_interest_regions(),
        candidates=list(candidates),
        current_active={},
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

    first = _run_once(_candidate_rows())
    second = _run_once(list(reversed(copy.deepcopy(_candidate_rows()))))
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "transition selection fixture refused unexpectedly"}
    if dict(first.get("desired_active") or {}) != dict(second.get("desired_active") or {}):
        return {"status": "fail", "message": "transition desired_active differs when candidate list order changes"}
    if list(first.get("expand_ids") or []) != list(second.get("expand_ids") or []):
        return {"status": "fail", "message": "transition expand_ids differs when candidate list order changes"}
    if list(first.get("collapse_ids") or []) != list(second.get("collapse_ids") or []):
        return {"status": "fail", "message": "transition collapse_ids differs when candidate list order changes"}

    usage = dict(first.get("usage") or {})
    max_compute = int(_budget_policy().get("max_compute_units_per_tick", 0) or 0)
    max_entities = int(_budget_policy().get("max_entities_micro", 0) or 0)
    if int(usage.get("compute_units", 0) or 0) > max_compute:
        return {"status": "fail", "message": "transition selection exceeded max_compute_units_per_tick"}
    if int(usage.get("entity_count", 0) or 0) > max_entities:
        return {"status": "fail", "message": "transition selection exceeded max_entities_micro"}
    if list(first.get("expand_ids") or []) != sorted(first.get("expand_ids") or []):
        return {"status": "fail", "message": "expand_ids ordering is not deterministic lexical order"}

    return {"status": "pass", "message": "transition selection determinism check passed"}
