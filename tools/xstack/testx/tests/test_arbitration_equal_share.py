"""STRICT test: equal-share arbitration distributes micro slots deterministically."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.performance.arbitration_equal_share"
TEST_TAGS = ["strict", "performance", "arbitration", "determinism"]


def _transition_policy() -> dict:
    return {
        "transition_policy_id": "transition.policy.test.equal_share",
        "description": "equal-share arbitration fixture",
        "max_micro_regions": 6,
        "max_micro_entities": 60,
        "hysteresis_rules": {"min_transition_interval_ticks": 0},
        "arbitration_rule_id": "arb.priority_by_distance",
        "degrade_order": ["fine", "medium", "coarse"],
        "refuse_thresholds": {},
        "extensions": {"distance_quantization_mm": 1000},
    }


def _budget_policy() -> dict:
    return {
        "policy_id": "policy.budget.test.equal_share",
        "max_regions_micro": 6,
        "max_entities_micro": 60,
        "max_compute_units_per_tick": 400,
        "entity_compute_weight": 1,
        "fallback_behavior": "degrade_fidelity",
        "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 4},
    }


def _arbitration_policy() -> dict:
    return {
        "arbitration_policy_id": "arb.equal_share",
        "mode": "equal_share",
        "weight_source": "none",
        "tie_break_rule_id": "tie.player_region_tick",
        "extensions": {},
    }


def _candidates() -> list:
    rows = []
    for peer_id in ("peer.alpha", "peer.beta", "peer.gamma"):
        peer_token = peer_id.replace(".", "_")
        for idx in range(4):
            rows.append(
                {
                    "region_id": "region.{}.{}".format(peer_token, str(idx + 1).zfill(2)),
                    "issuer_peer_id": peer_id,
                    "priority": idx,
                    "distance_mm": 1000 + (idx * 1000),
                    "tier": "fine",
                    "server_weight": 10 - idx,
                }
            )
    return rows


def _interest_regions(rows: list) -> dict:
    out = {}
    for row in rows:
        region_id = str((row or {}).get("region_id", "")).strip()
        if region_id:
            out[region_id] = {"last_transition_tick": 0}
    return out


def _run_once(candidates: list) -> dict:
    from reality.transitions.transition_controller import compute_transition_plan

    return compute_transition_plan(
        tick=10,
        transition_policy=_transition_policy(),
        budget_policy=_budget_policy(),
        interest_regions_by_id=_interest_regions(candidates),
        candidates=list(candidates),
        current_active={},
        forced_expand_region_ids=[],
        forced_collapse_region_ids=[],
        forced_expand_tiers={},
        tier_weight_by_tier={"coarse": 1, "medium": 2, "fine": 4},
        tier_entity_target_by_tier={"coarse": 0, "medium": 4, "fine": 8},
        entity_compute_weight=1,
        arbitration_policy=_arbitration_policy(),
    )


def _share_counts(result: dict) -> dict:
    out = {}
    rows = dict(result.get("selected_player_by_region") or {})
    for peer_id in rows.values():
        token = str(peer_id).strip()
        if not token:
            continue
        out[token] = int(out.get(token, 0)) + 1
    return dict((key, out[key]) for key in sorted(out.keys()))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    rows = _candidates()
    first = _run_once(rows)
    second = _run_once(list(reversed(copy.deepcopy(rows))))
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "equal-share arbitration fixture refused unexpectedly"}
    if dict(first.get("desired_active") or {}) != dict(second.get("desired_active") or {}):
        return {"status": "fail", "message": "equal-share arbitration selection drifted by candidate order"}
    counts = _share_counts(first)
    if sorted(counts.keys()) != ["peer.alpha", "peer.beta", "peer.gamma"]:
        return {"status": "fail", "message": "equal-share arbitration did not allocate slots across all peers"}
    max_count = max(counts.values())
    min_count = min(counts.values())
    if int(max_count - min_count) > 1:
        return {"status": "fail", "message": "equal-share arbitration allocation imbalance exceeded deterministic tolerance"}
    return {"status": "pass", "message": "equal-share arbitration distribution is deterministic and balanced"}

