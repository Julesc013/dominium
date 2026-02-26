"""STRICT test: distributed-player transition arbitration is deterministic under budget limits."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.reality.multiplayer_distributed_players_arbitration"
TEST_TAGS = ["strict", "reality", "transition", "multiplayer", "determinism"]


def _transition_policy() -> dict:
    return {
        "transition_policy_id": "transition.policy.rank_strict",
        "description": "deterministic weighted arbitration fixture",
        "max_micro_regions": 20,
        "max_micro_entities": 220,
        "hysteresis_rules": {"min_transition_interval_ticks": 2},
        "arbitration_rule_id": "arb.server_authoritative_weighted",
        "degrade_order": ["fine", "medium", "coarse"],
        "refuse_thresholds": {},
        "extensions": {"distance_quantization_mm": 5000},
    }


def _budget_policy() -> dict:
    return {
        "policy_id": "policy.budget.distributed_arbitration",
        "max_regions_micro": 20,
        "max_entities_micro": 220,
        "max_compute_units_per_tick": 260,
        "entity_compute_weight": 1,
        "fallback_behavior": "degrade_fidelity",
        "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 4},
    }


def _candidate_rows() -> list:
    rows = []
    peers = ("peer.alpha", "peer.beta", "peer.gamma", "peer.delta")
    for peer_index, peer_id in enumerate(peers):
        peer_token = str(peer_id).replace(".", "_")
        for idx in range(1, 25):
            identity_code = int((peer_index * 100) + idx)
            rows.append(
                {
                    "region_id": "region.{}.{}".format(peer_token, str(idx).zfill(3)),
                    "priority": int(identity_code % 9),
                    "distance_mm": int(((identity_code % 20) + 1) * 8000),
                    "tier": "fine" if int(identity_code % 4) == 0 else "medium",
                    "server_weight": int(200 - ((identity_code * 7) % 37)),
                    "issuer_peer_id": str(peer_id),
                }
            )
    return rows


def _interest_regions(candidates: list) -> dict:
    rows = {}
    for item in list(candidates):
        if not isinstance(item, dict):
            continue
        region_id = str(item.get("region_id", "")).strip()
        if region_id:
            rows[region_id] = {"last_transition_tick": 0}
    return rows


def _run_once(candidates: list) -> dict:
    from src.reality.transitions.transition_controller import compute_transition_plan

    return compute_transition_plan(
        tick=20,
        transition_policy=_transition_policy(),
        budget_policy=_budget_policy(),
        interest_regions_by_id=_interest_regions(candidates),
        candidates=list(candidates),
        current_active={},
        forced_expand_region_ids=[],
        forced_collapse_region_ids=[],
        forced_expand_tiers={},
        tier_weight_by_tier={"coarse": 1, "medium": 2, "fine": 4},
        tier_entity_target_by_tier={"coarse": 0, "medium": 6, "fine": 12},
        entity_compute_weight=1,
    )


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    candidates = _candidate_rows()
    first = _run_once(candidates)
    second = _run_once(list(reversed(copy.deepcopy(candidates))))
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "distributed-player arbitration fixture refused unexpectedly"}
    if dict(first.get("desired_active") or {}) != dict(second.get("desired_active") or {}):
        return {"status": "fail", "message": "arbitration desired_active differs for equivalent distributed candidate sets"}
    if list(first.get("expand_ids") or []) != list(second.get("expand_ids") or []):
        return {"status": "fail", "message": "arbitration expand_ids differs for equivalent distributed candidate sets"}
    if list(first.get("collapse_ids") or []) != list(second.get("collapse_ids") or []):
        return {"status": "fail", "message": "arbitration collapse_ids differs for equivalent distributed candidate sets"}

    usage = dict(first.get("usage") or {})
    max_compute = int(_budget_policy().get("max_compute_units_per_tick", 0) or 0)
    max_entities = int(_budget_policy().get("max_entities_micro", 0) or 0)
    max_regions = int(_transition_policy().get("max_micro_regions", 0) or 0)
    if int(usage.get("compute_units", 0) or 0) > max_compute:
        return {"status": "fail", "message": "arbitration exceeded max_compute_units_per_tick abstract budget"}
    if int(usage.get("entity_count", 0) or 0) > max_entities:
        return {"status": "fail", "message": "arbitration exceeded max_entities_micro budget"}
    if len(dict(first.get("desired_active") or {})) > max_regions:
        return {"status": "fail", "message": "arbitration activated more micro regions than transition policy allows"}
    if list(first.get("expand_ids") or []) != sorted(first.get("expand_ids") or []):
        return {"status": "fail", "message": "arbitration expand_ids ordering is not deterministic lexical order"}

    return {"status": "pass", "message": "distributed-player arbitration determinism and budget check passed"}
