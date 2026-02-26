"""STRICT test: distributed players receive deterministic fair arbitration under budget limits."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.performance.multiplayer_fairness_under_spread_players"
TEST_TAGS = ["strict", "performance", "multiplayer", "arbitration", "determinism"]


def _transition_policy() -> dict:
    return {
        "transition_policy_id": "transition.policy.performance.fairness",
        "description": "distributed fairness fixture",
        "max_micro_regions": 16,
        "max_micro_entities": 192,
        "hysteresis_rules": {"min_transition_interval_ticks": 1},
        "arbitration_rule_id": "arb.priority_by_distance",
        "degrade_order": ["fine", "medium", "coarse"],
        "refuse_thresholds": {},
        "extensions": {"distance_quantization_mm": 5000},
    }


def _budget_policy() -> dict:
    return {
        "policy_id": "policy.budget.performance.fairness",
        "max_regions_micro": 16,
        "max_entities_micro": 192,
        "max_compute_units_per_tick": 220,
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


def _candidate_rows() -> list:
    rows = []
    peer_ids = ("peer.alpha", "peer.beta", "peer.gamma", "peer.delta", "peer.epsilon", "peer.zeta")
    for peer_index, peer_id in enumerate(peer_ids):
        peer_token = peer_id.replace(".", "_")
        for idx in range(1, 21):
            serial = (peer_index * 100) + idx
            rows.append(
                {
                    "region_id": "region.{}.{}".format(peer_token, str(idx).zfill(3)),
                    "issuer_peer_id": peer_id,
                    "priority": int(serial % 8),
                    "distance_mm": int(((serial % 30) + 1) * 3000),
                    "tier": "fine" if int(serial % 5) == 0 else "medium",
                    "server_weight": int(200 - ((serial * 11) % 57)),
                }
            )
    return rows


def _interest(rows: list) -> dict:
    out = {}
    for row in rows:
        region_id = str((row or {}).get("region_id", "")).strip()
        if region_id:
            out[region_id] = {"last_transition_tick": 0}
    return out


def _run_once(candidates: list) -> dict:
    from src.reality.transitions.transition_controller import compute_transition_plan

    return compute_transition_plan(
        tick=42,
        transition_policy=_transition_policy(),
        budget_policy=_budget_policy(),
        interest_regions_by_id=_interest(candidates),
        candidates=list(candidates),
        current_active={},
        forced_expand_region_ids=[],
        forced_collapse_region_ids=[],
        forced_expand_tiers={},
        tier_weight_by_tier={"coarse": 1, "medium": 2, "fine": 4},
        tier_entity_target_by_tier={"coarse": 0, "medium": 6, "fine": 12},
        entity_compute_weight=1,
        arbitration_policy=_arbitration_policy(),
    )


def _peer_counts(result: dict) -> dict:
    counts = {}
    for peer_id in dict(result.get("selected_player_by_region") or {}).values():
        token = str(peer_id).strip()
        if not token:
            continue
        counts[token] = int(counts.get(token, 0)) + 1
    return dict((key, counts[key]) for key in sorted(counts.keys()))


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    rows = _candidate_rows()
    first = _run_once(rows)
    second = _run_once(list(reversed(copy.deepcopy(rows))))
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "distributed fairness fixture refused unexpectedly"}
    if dict(first.get("desired_active") or {}) != dict(second.get("desired_active") or {}):
        return {"status": "fail", "message": "distributed fairness selection drifted across equivalent candidate ordering"}
    counts = _peer_counts(first)
    if len(counts) < 4:
        return {"status": "fail", "message": "distributed fairness arbitration failed to allocate across peers"}
    spread = int(max(counts.values()) - min(counts.values()))
    if spread > 1:
        return {"status": "fail", "message": "distributed fairness allocation skew exceeded deterministic equal-share bounds"}
    usage = dict(first.get("usage") or {})
    if int(usage.get("compute_units", 0) or 0) > int(_budget_policy().get("max_compute_units_per_tick", 0) or 0):
        return {"status": "fail", "message": "distributed fairness exceeded deterministic compute envelope"}
    return {"status": "pass", "message": "distributed-player fairness arbitration remained deterministic and balanced"}

