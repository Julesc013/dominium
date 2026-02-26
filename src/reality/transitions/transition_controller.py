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


def _candidate_sort_key(candidate: dict, arbitration_rule_id: str) -> Tuple[int, int, str]:
    distance_bucket = int(candidate.get("distance_bucket_mm", 0) or 0)
    priority = int(candidate.get("priority", 0) or 0)
    region_id = str(candidate.get("region_id", ""))
    if arbitration_rule_id == "arb.equal_share":
        return (priority, distance_bucket, region_id)
    if arbitration_rule_id == "arb.server_authoritative_weighted":
        weighted_priority = int(candidate.get("server_weight", 0) or 0)
        return (weighted_priority, distance_bucket, region_id)
    return (distance_bucket, priority, region_id)


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
) -> Dict[str, object]:
    transition_policy_row = dict(transition_policy or {})
    budget_policy_row = dict(budget_policy or {})
    arbitration_rule_id = str(transition_policy_row.get("arbitration_rule_id", "")).strip() or "arb.priority_by_distance"
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
        normalized_candidates.append(
            {
                "region_id": region_id,
                "priority": int(_as_int(row.get("priority", 0), 0)),
                "distance_mm": int(_as_int(row.get("distance_mm", 0), 0)),
                "distance_bucket_mm": _quantize_distance(_as_int(row.get("distance_mm", 0), 0), quantization_mm),
                "tier": desired_tier,
                "server_weight": int(_as_int(row.get("server_weight", row.get("priority", 0)), 0)),
            }
        )
    normalized_candidates = sorted(
        normalized_candidates,
        key=lambda row: _candidate_sort_key(row, arbitration_rule_id),
    )

    selected: Dict[str, str] = {}
    selected_priority: Dict[str, int] = {}
    for row in normalized_candidates[: max(0, int(max_regions))]:
        region_id = str(row.get("region_id", ""))
        selected[region_id] = str(row.get("tier", "coarse"))
        selected_priority[region_id] = int(_as_int(row.get("priority", 0), 0))

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
        for region_id in sorted(desired_active.keys(), key=lambda rid: (int(selected_priority.get(rid, 0)), str(rid)), reverse=True):
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
        for region_id in sorted(desired_active.keys(), key=lambda rid: (int(selected_priority.get(rid, 0)), str(rid)), reverse=True):
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

    return {
        "result": "complete",
        "desired_active": dict((str(key), str(value)) for key, value in sorted(desired_active.items(), key=lambda item: str(item[0]))),
        "collapse_ids": collapse_ids,
        "expand_ids": expand_ids,
        "forced_expand_region_ids": forced_expand_ids,
        "forced_collapse_region_ids": forced_collapse_ids,
        "usage": dict(usage),
        "budget_outcome": str(budget_outcome),
        "arbitration_rule_id": str(arbitration_rule_id),
        "selected_priority": dict((str(key), int(value)) for key, value in sorted(selected_priority.items(), key=lambda item: str(item[0]))),
    }

