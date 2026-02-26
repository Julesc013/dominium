"""Deterministic transition controller for macro/meso/micro tier changes."""

from __future__ import annotations

from typing import Dict, List, Tuple


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _sorted_tokens(items: List[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(items or []) if str(item).strip()))


def _tier_tokens() -> List[str]:
    return ["coarse", "medium", "fine"]


def _degrade_one_tier(current_tier: str, degrade_order: List[str]) -> str:
    token = str(current_tier).strip()
    if token not in degrade_order:
        return token
    idx = degrade_order.index(token)
    if idx + 1 >= len(degrade_order):
        return token
    next_tier = str(degrade_order[idx + 1]).strip()
    return next_tier if next_tier in _tier_tokens() else token


def _quantize_distance(distance_mm: int, step_mm: int) -> int:
    value = max(0, int(distance_mm))
    step = max(1, int(step_mm))
    return int((value // step) * step)


def _candidate_sort_key(candidate: dict, arbitration_rule_id: str) -> Tuple[int, int, str, str]:
    distance_bucket = int(candidate.get("distance_bucket_mm", 0) or 0)
    priority = int(candidate.get("priority", 0) or 0)
    region_id = str(candidate.get("region_id", ""))
    peer_id = str(candidate.get("issuer_peer_id", ""))
    if arbitration_rule_id == "arb.equal_share":
        return (priority, distance_bucket, peer_id, region_id)
    if arbitration_rule_id == "arb.server_authoritative_weighted":
        weighted_priority = -int(candidate.get("server_weight", 0) or 0)
        return (weighted_priority, distance_bucket, peer_id, region_id)
    return (distance_bucket, priority, peer_id, region_id)


def _candidate_priority_score(candidate: dict, arbitration_rule_id: str) -> int:
    distance_bucket = int(candidate.get("distance_bucket_mm", 0) or 0)
    priority = int(candidate.get("priority", 0) or 0)
    server_weight = int(candidate.get("server_weight", 0) or 0)
    if arbitration_rule_id == "arb.equal_share":
        return int((priority * 1_000_000) + distance_bucket)
    if arbitration_rule_id == "arb.server_authoritative_weighted":
        return int((max(0, 1_000_000 - server_weight) * 1_000_000) + distance_bucket)
    return int((distance_bucket * 1_000) + priority)


def _budget_usage(
    selection: Dict[str, str],
    *,
    tier_weight_by_tier: Dict[str, int],
    tier_entity_target_by_tier: Dict[str, int],
    entity_compute_weight: int,
) -> Dict[str, int]:
    tier_sum = 0
    entity_sum = 0
    for region_id in sorted(selection.keys()):
        tier = str(selection.get(region_id, "coarse")).strip() or "coarse"
        tier_sum += int(tier_weight_by_tier.get(tier, 0))
        entity_sum += int(tier_entity_target_by_tier.get(tier, 0))
    return {
        "compute_units": int(tier_sum + (entity_sum * int(max(0, entity_compute_weight)))),
        "entity_count": int(entity_sum),
    }


def _legacy_arbitration_mode(arbitration_rule_id: str) -> str:
    token = str(arbitration_rule_id).strip()
    if token == "arb.equal_share":
        return "equal_share"
    if token == "arb.server_authoritative_weighted":
        return "weighted"
    return "server_authoritative_priority"


def _normalized_mode(token: str, fallback: str) -> str:
    mode = str(token).strip()
    if mode in ("equal_share", "weighted", "server_authoritative_priority"):
        return mode
    return str(fallback).strip() or "server_authoritative_priority"


def _normalized_arbitration_policy(arbitration_policy: dict | None, arbitration_rule_id: str) -> dict:
    row = dict(arbitration_policy or {})
    fallback_mode = _legacy_arbitration_mode(arbitration_rule_id)
    mode = _normalized_mode(str(row.get("mode", "")), fallback_mode)
    return {
        "arbitration_policy_id": str(row.get("arbitration_policy_id", "")).strip() or "arb.derived.from_transition_policy",
        "mode": mode,
        "weight_source": str(row.get("weight_source", "")).strip() or "derived",
        "tie_break_rule_id": str(row.get("tie_break_rule_id", "")).strip() or "tie.player_region_tick",
        "extensions": dict(row.get("extensions") or {}),
    }


def _select_rows_by_arbitration_mode(
    *,
    candidates: List[dict],
    max_regions: int,
    arbitration_mode: str,
    arbitration_rule_id: str,
    weight_overrides: dict,
) -> List[dict]:
    if max_regions <= 0:
        return []
    sorted_rows = sorted(
        (dict(row) for row in list(candidates or []) if isinstance(row, dict)),
        key=lambda row: _candidate_sort_key(row, arbitration_rule_id),
    )
    if arbitration_mode == "server_authoritative_priority":
        return list(sorted_rows[: max(0, int(max_regions))])

    rows_by_peer: Dict[str, List[dict]] = {}
    for row in sorted_rows:
        peer_id = str(row.get("issuer_peer_id", "")).strip() or "peer.system"
        rows_by_peer.setdefault(peer_id, []).append(dict(row))
    peer_ids = sorted(rows_by_peer.keys())
    offsets = dict((peer_id, 0) for peer_id in peer_ids)
    selected: List[dict] = []

    if arbitration_mode == "equal_share":
        while len(selected) < int(max_regions):
            progressed = False
            for peer_id in peer_ids:
                offset = int(offsets.get(peer_id, 0))
                rows = list(rows_by_peer.get(peer_id) or [])
                if offset >= len(rows):
                    continue
                selected.append(dict(rows[offset]))
                offsets[peer_id] = int(offset + 1)
                progressed = True
                if len(selected) >= int(max_regions):
                    break
            if not progressed:
                break
        return selected

    weights: Dict[str, int] = {}
    for peer_id in peer_ids:
        override = _as_int(dict(weight_overrides or {}).get(peer_id, 0), 0)
        if override > 0:
            weights[peer_id] = int(override)
            continue
        rows = list(rows_by_peer.get(peer_id) or [])
        if not rows:
            weights[peer_id] = 1
            continue
        max_weight = max(1, max(_as_int(row.get("server_weight", 1), 1) for row in rows))
        weights[peer_id] = int(max_weight)

    allocation = dict((peer_id, 0) for peer_id in peer_ids)
    while len(selected) < int(max_regions):
        eligible = [peer_id for peer_id in peer_ids if int(offsets.get(peer_id, 0)) < len(list(rows_by_peer.get(peer_id) or []))]
        if not eligible:
            break
        chosen_peer = sorted(
            eligible,
            key=lambda peer_id: (
                int(int(allocation.get(peer_id, 0)) * 1_000_000 // max(1, int(weights.get(peer_id, 1)))),
                -int(weights.get(peer_id, 1)),
                str(peer_id),
            ),
        )[0]
        offset = int(offsets.get(chosen_peer, 0))
        rows = list(rows_by_peer.get(chosen_peer) or [])
        selected.append(dict(rows[offset]))
        offsets[chosen_peer] = int(offset + 1)
        allocation[chosen_peer] = int(allocation.get(chosen_peer, 0)) + 1
    return selected


def compute_transition_plan(
    *,
    tick: int,
    transition_policy: dict | None,
    budget_policy: dict | None,
    interest_regions_by_id: Dict[str, dict],
    candidates: List[dict],
    current_active: Dict[str, str],
    forced_expand_region_ids: List[str] | None,
    forced_collapse_region_ids: List[str] | None,
    forced_expand_tiers: Dict[str, str] | None,
    tier_weight_by_tier: Dict[str, int],
    tier_entity_target_by_tier: Dict[str, int],
    entity_compute_weight: int,
    arbitration_policy: dict | None = None,
    inspection_cost_units: int = 0,
    max_inspection_cost_units_per_tick: int = 0,
) -> Dict[str, object]:
    transition_policy_row = dict(transition_policy or {})
    budget_policy_row = dict(budget_policy or {})
    arbitration_rule_id = str(transition_policy_row.get("arbitration_rule_id", "")).strip() or "arb.priority_by_distance"
    normalized_arbitration_policy = _normalized_arbitration_policy(arbitration_policy, arbitration_rule_id)
    arbitration_mode = str(normalized_arbitration_policy.get("mode", "server_authoritative_priority"))
    quantization_mm = max(1, _as_int((transition_policy_row.get("extensions") or {}).get("distance_quantization_mm", 1000), 1000))
    hysteresis_rules = dict(transition_policy_row.get("hysteresis_rules") or {})
    min_transition_interval_ticks = max(0, _as_int(hysteresis_rules.get("min_transition_interval_ticks", 0), 0))

    max_regions = max(0, _as_int(budget_policy_row.get("max_regions_micro", 0), 0))
    max_entities = max(0, _as_int(budget_policy_row.get("max_entities_micro", 0), 0))
    max_compute = max(0, _as_int(budget_policy_row.get("max_compute_units_per_tick", 0), 0))
    policy_max_regions = max(0, _as_int(transition_policy_row.get("max_micro_regions", 0), 0))
    policy_max_entities = max(0, _as_int(transition_policy_row.get("max_micro_entities", 0), 0))
    if policy_max_regions > 0:
        if max_regions > 0:
            max_regions = min(max_regions, policy_max_regions)
        else:
            max_regions = int(policy_max_regions)
    if policy_max_entities > 0:
        if max_entities > 0:
            max_entities = min(max_entities, policy_max_entities)
        else:
            max_entities = int(policy_max_entities)

    forced_expand_ids = _sorted_tokens(list(forced_expand_region_ids or []))
    forced_collapse_ids = _sorted_tokens(list(forced_collapse_region_ids or []))
    forced_tiers = dict(forced_expand_tiers or {})
    for region_id in forced_expand_ids + forced_collapse_ids:
        if region_id not in interest_regions_by_id:
            return {
                "result": "refused",
                "code": "refusal.control.target_invalid",
                "message": "region '{}' is not known to transition controller".format(region_id),
            }

    thresholds = dict(transition_policy_row.get("refuse_thresholds") or {})
    max_forced_micro_regions = _as_int(thresholds.get("max_forced_micro_regions", -1), -1)
    if max_forced_micro_regions >= 0 and len(forced_expand_ids) > int(max_forced_micro_regions):
        return {
            "result": "refused",
            "code": "refusal.transition.policy_threshold_exceeded",
            "message": "forced micro region count exceeds transition policy threshold",
            "details": {
                "forced_expand_count": len(forced_expand_ids),
                "max_forced_micro_regions": int(max_forced_micro_regions),
            },
        }

    normalized_candidates: List[dict] = []
    for row in list(candidates or []):
        if not isinstance(row, dict):
            continue
        region_id = str(row.get("region_id", "")).strip()
        if not region_id:
            continue
        desired_tier = str(row.get("tier", "coarse")).strip() or "coarse"
        if desired_tier not in _tier_tokens():
            desired_tier = "coarse"
        normalized_row = {
            "region_id": region_id,
            "issuer_peer_id": str(row.get("issuer_peer_id", "")).strip() or "peer.system",
            "priority": int(_as_int(row.get("priority", 0), 0)),
            "distance_mm": int(_as_int(row.get("distance_mm", 0), 0)),
            "distance_bucket_mm": _quantize_distance(_as_int(row.get("distance_mm", 0), 0), quantization_mm),
            "tier": desired_tier,
            "server_weight": int(_as_int(row.get("server_weight", row.get("priority", 0)), 0)),
        }
        normalized_row["priority_score"] = int(_candidate_priority_score(normalized_row, arbitration_rule_id))
        normalized_candidates.append(normalized_row)
    normalized_candidates = sorted(
        normalized_candidates,
        key=lambda row: _candidate_sort_key(row, arbitration_rule_id),
    )

    selected_rows = _select_rows_by_arbitration_mode(
        candidates=normalized_candidates,
        max_regions=int(max_regions),
        arbitration_mode=arbitration_mode,
        arbitration_rule_id=arbitration_rule_id,
        weight_overrides=dict((normalized_arbitration_policy.get("extensions") or {}).get("player_weights") or {}),
    )
    selected: Dict[str, str] = {}
    selected_priority: Dict[str, int] = {}
    selected_priority_score: Dict[str, int] = {}
    selected_player_by_region: Dict[str, str] = {}
    for row in selected_rows:
        region_id = str(row.get("region_id", ""))
        selected[region_id] = str(row.get("tier", "coarse"))
        selected_priority[region_id] = int(_as_int(row.get("priority", 0), 0))
        selected_priority_score[region_id] = int(_as_int(row.get("priority_score", 0), 0))
        selected_player_by_region[region_id] = str(row.get("issuer_peer_id", "")).strip() or "peer.system"

    desired_active = dict(selected)
    for region_id in forced_collapse_ids:
        desired_active.pop(region_id, None)
    for region_id in forced_expand_ids:
        forced_tier = str(forced_tiers.get(region_id, "")).strip()
        if forced_tier not in _tier_tokens():
            forced_tier = str(desired_active.get(region_id, "") or current_active.get(region_id, "")).strip() or "coarse"
        if forced_tier not in _tier_tokens():
            forced_tier = "coarse"
        desired_active[region_id] = forced_tier
        selected_priority.setdefault(region_id, int(_as_int(interest_regions_by_id.get(region_id, {}).get("priority", 0), 0)))
        selected_priority_score.setdefault(region_id, int(9_999_999_999))
        selected_player_by_region.setdefault(region_id, "peer.system")

    if min_transition_interval_ticks > 0:
        for region_id in sorted(set(list(current_active.keys()) + list(desired_active.keys()))):
            from_tier = str(current_active.get(region_id, "")).strip()
            to_tier = str(desired_active.get(region_id, "")).strip()
            if from_tier == to_tier:
                continue
            if region_id in set(forced_expand_ids + forced_collapse_ids):
                continue
            last_transition_tick = _as_int((interest_regions_by_id.get(region_id) or {}).get("last_transition_tick", 0), 0)
            if int(max(0, tick) - int(last_transition_tick)) < int(min_transition_interval_ticks):
                if from_tier:
                    desired_active[region_id] = from_tier
                else:
                    desired_active.pop(region_id, None)

    usage = _budget_usage(
        desired_active,
        tier_weight_by_tier=tier_weight_by_tier,
        tier_entity_target_by_tier=tier_entity_target_by_tier,
        entity_compute_weight=entity_compute_weight,
    )
    fallback = str(budget_policy_row.get("fallback_behavior", "degrade_fidelity")).strip() or "degrade_fidelity"
    if usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
        if fallback == "refuse":
            return {
                "result": "refused",
                "code": "BUDGET_EXCEEDED",
                "message": "transition selection exceeded deterministic budget envelope",
                "details": {
                    "compute_units_used": int(usage["compute_units"]),
                    "max_compute_units_per_tick": int(max_compute),
                    "entity_count_used": int(usage["entity_count"]),
                    "max_entities_micro": int(max_entities),
                },
            }

    degrade_order = [str(item).strip() for item in list(transition_policy_row.get("degrade_order") or []) if str(item).strip()]
    if degrade_order != ["fine", "medium", "coarse"]:
        degrade_order = ["fine", "medium", "coarse"]
    budget_outcome = "ok"

    changed = False
    while usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
        step_changed = False
        for region_id in sorted(
            desired_active.keys(),
            key=lambda rid: (
                int(selected_priority_score.get(rid, 9_999_999_999)),
                int(selected_priority.get(rid, 9_999_999)),
                str(rid),
            ),
            reverse=True,
        ):
            current_tier = str(desired_active.get(region_id, "coarse")).strip() or "coarse"
            next_tier = _degrade_one_tier(current_tier, degrade_order)
            if next_tier == current_tier:
                continue
            desired_active[region_id] = next_tier
            usage = _budget_usage(
                desired_active,
                tier_weight_by_tier=tier_weight_by_tier,
                tier_entity_target_by_tier=tier_entity_target_by_tier,
                entity_compute_weight=entity_compute_weight,
            )
            step_changed = True
            changed = True
            if usage["compute_units"] <= max_compute and usage["entity_count"] <= max_entities:
                break
        if not step_changed:
            break

    if changed:
        budget_outcome = "degraded"

    if usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
        for region_id in sorted(
            desired_active.keys(),
            key=lambda rid: (
                int(selected_priority_score.get(rid, 9_999_999_999)),
                int(selected_priority.get(rid, 9_999_999)),
                str(rid),
            ),
            reverse=True,
        ):
            if region_id in set(forced_expand_ids):
                continue
            del desired_active[region_id]
            usage = _budget_usage(
                desired_active,
                tier_weight_by_tier=tier_weight_by_tier,
                tier_entity_target_by_tier=tier_entity_target_by_tier,
                entity_compute_weight=entity_compute_weight,
            )
            if usage["compute_units"] <= max_compute and usage["entity_count"] <= max_entities:
                break
        budget_outcome = "capped"

    refused_forced_expand_ids: List[str] = []
    if usage["compute_units"] > max_compute or usage["entity_count"] > max_entities:
        for region_id in sorted(
            (rid for rid in forced_expand_ids if rid in desired_active),
            key=lambda rid: (
                int(selected_priority_score.get(rid, 9_999_999_999)),
                int(selected_priority.get(rid, 9_999_999)),
                str(rid),
            ),
            reverse=True,
        ):
            desired_active.pop(region_id, None)
            refused_forced_expand_ids.append(str(region_id))
            usage = _budget_usage(
                desired_active,
                tier_weight_by_tier=tier_weight_by_tier,
                tier_entity_target_by_tier=tier_entity_target_by_tier,
                entity_compute_weight=entity_compute_weight,
            )
            if usage["compute_units"] <= max_compute and usage["entity_count"] <= max_entities:
                break
        budget_outcome = "capped"

    inspection_units = max(0, _as_int(inspection_cost_units, 0))
    max_inspection_units = max(0, _as_int(max_inspection_cost_units_per_tick, 0))
    inspection_resolution_reduced = False
    if max_inspection_units > 0 and inspection_units > max_inspection_units:
        inspection_units = int(max_inspection_units)
        inspection_resolution_reduced = True
        if budget_outcome == "ok":
            budget_outcome = "degraded"

    collapse_ids = sorted(
        region_id
        for region_id in current_active.keys()
        if region_id not in desired_active or str(desired_active.get(region_id, "")) != str(current_active.get(region_id, ""))
    )
    expand_ids = sorted(
        region_id
        for region_id in desired_active.keys()
        if region_id not in current_active or str(desired_active.get(region_id, "")) != str(current_active.get(region_id, ""))
    )

    candidate_region_ids = sorted(
        set(str(row.get("region_id", "")).strip() for row in normalized_candidates if str(row.get("region_id", "")).strip())
    )
    refused_expand_ids = sorted(
        set(
            [region_id for region_id in candidate_region_ids if region_id not in set(desired_active.keys())]
            + [str(item) for item in refused_forced_expand_ids if str(item).strip()]
        )
    )
    selection_trace: List[dict] = []
    for row in normalized_candidates:
        region_id = str(row.get("region_id", "")).strip()
        if not region_id:
            continue
        action = "refused"
        if region_id in set(expand_ids):
            action = "expand"
        elif region_id in set(collapse_ids):
            action = "collapse"
        elif region_id in set(desired_active.keys()):
            action = "retain"
        selection_trace.append(
            {
                "region_id": region_id,
                "issuer_peer_id": str(row.get("issuer_peer_id", "")).strip() or "peer.system",
                "priority": int(_as_int(row.get("priority", 0), 0)),
                "priority_score": int(_as_int(row.get("priority_score", 0), 0)),
                "distance_bucket_mm": int(_as_int(row.get("distance_bucket_mm", 0), 0)),
                "action": action,
            }
        )
    selection_trace = sorted(
        selection_trace,
        key=lambda row: (
            str(row.get("issuer_peer_id", "")),
            str(row.get("region_id", "")),
            int(_as_int(row.get("priority_score", 0), 0)),
        ),
    )

    return {
        "result": "complete",
        "desired_active": dict((str(key), str(value)) for key, value in sorted(desired_active.items(), key=lambda item: str(item[0]))),
        "collapse_ids": collapse_ids,
        "expand_ids": expand_ids,
        "forced_expand_region_ids": forced_expand_ids,
        "forced_collapse_region_ids": forced_collapse_ids,
        "refused_expand_ids": refused_expand_ids,
        "usage": dict(usage),
        "budget_outcome": str(budget_outcome),
        "arbitration_rule_id": str(arbitration_rule_id),
        "arbitration_policy_id": str(normalized_arbitration_policy.get("arbitration_policy_id", "")),
        "arbitration_mode": str(arbitration_mode),
        "tie_break_rule_id": str(normalized_arbitration_policy.get("tie_break_rule_id", "")),
        "selected_priority": dict((str(key), int(value)) for key, value in sorted(selected_priority.items(), key=lambda item: str(item[0]))),
        "selected_priority_score": dict(
            (str(key), int(value)) for key, value in sorted(selected_priority_score.items(), key=lambda item: str(item[0]))
        ),
        "selected_player_by_region": dict(
            (str(key), str(value)) for key, value in sorted(selected_player_by_region.items(), key=lambda item: str(item[0]))
        ),
        "inspection_cost_units_used": int(inspection_units),
        "max_inspection_cost_units_per_tick": int(max_inspection_units),
        "inspection_resolution_reduced": bool(inspection_resolution_reduced),
        "selection_trace": selection_trace,
    }
