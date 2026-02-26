"""Deterministic RS-5 cost accounting helpers."""

from __future__ import annotations

from typing import Dict


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def normalize_budget_envelope(*, envelope: dict | None, budget_policy: dict | None) -> dict:
    """Return deterministic envelope row with safe fallbacks when profile wiring is absent."""
    row = dict(envelope or {})
    if not row:
        policy = dict(budget_policy or {})
        row = {
            "envelope_id": "budget.derived.from_budget_policy",
            "max_micro_entities_per_shard": max(0, _as_int(policy.get("max_entities_micro", 0), 0)),
            "max_micro_regions_per_shard": max(0, _as_int(policy.get("max_regions_micro", 0), 0)),
            "max_solver_cost_units_per_tick": max(0, _as_int(policy.get("max_compute_units_per_tick", 0), 0)),
            "max_inspection_cost_units_per_tick": max(0, _as_int(policy.get("max_compute_units_per_tick", 0), 0)),
            "extensions": {},
        }
    return {
        "envelope_id": str(row.get("envelope_id", "budget.unknown")).strip() or "budget.unknown",
        "max_micro_entities_per_shard": max(0, _as_int(row.get("max_micro_entities_per_shard", 0), 0)),
        "max_micro_regions_per_shard": max(0, _as_int(row.get("max_micro_regions_per_shard", 0), 0)),
        "max_solver_cost_units_per_tick": max(0, _as_int(row.get("max_solver_cost_units_per_tick", 0), 0)),
        "max_inspection_cost_units_per_tick": max(0, _as_int(row.get("max_inspection_cost_units_per_tick", 0), 0)),
        "extensions": dict(row.get("extensions") or {}) if isinstance(row.get("extensions"), dict) else {},
    }


def compute_cost_snapshot(
    *,
    active_tiers_by_region: Dict[str, str],
    tier_weight_by_tier: Dict[str, int],
    tier_entity_target_by_tier: Dict[str, int],
    entity_compute_weight: int,
    inspection_cost_units: int,
) -> dict:
    micro_region_count = 0
    micro_entity_count = 0
    solver_cost_units = 0
    for region_id in sorted(active_tiers_by_region.keys()):
        tier = str(active_tiers_by_region.get(region_id, "coarse")).strip() or "coarse"
        micro_region_count += 1
        micro_entity_count += max(0, _as_int(tier_entity_target_by_tier.get(tier, 0), 0))
        solver_cost_units += max(0, _as_int(tier_weight_by_tier.get(tier, 0), 0))
    solver_cost_units += int(micro_entity_count * max(0, _as_int(entity_compute_weight, 0)))
    inspection_units = max(0, _as_int(inspection_cost_units, 0))
    return {
        "micro_entity_count": int(micro_entity_count),
        "micro_region_count": int(micro_region_count),
        "solver_cost_units": int(max(0, solver_cost_units)),
        "inspection_cost_units": int(inspection_units),
        "total_cost_units": int(max(0, solver_cost_units) + inspection_units),
    }


def evaluate_envelope(*, cost_snapshot: dict, envelope: dict) -> dict:
    row = normalize_budget_envelope(envelope=envelope, budget_policy={})
    entities = max(0, _as_int(cost_snapshot.get("micro_entity_count", 0), 0))
    regions = max(0, _as_int(cost_snapshot.get("micro_region_count", 0), 0))
    solver = max(0, _as_int(cost_snapshot.get("solver_cost_units", 0), 0))
    inspection = max(0, _as_int(cost_snapshot.get("inspection_cost_units", 0), 0))
    max_entities = max(0, _as_int(row.get("max_micro_entities_per_shard", 0), 0))
    max_regions = max(0, _as_int(row.get("max_micro_regions_per_shard", 0), 0))
    max_solver = max(0, _as_int(row.get("max_solver_cost_units_per_tick", 0), 0))
    max_inspection = max(0, _as_int(row.get("max_inspection_cost_units_per_tick", 0), 0))
    return {
        "envelope_id": str(row.get("envelope_id", "")),
        "max_micro_entities_per_shard": int(max_entities),
        "max_micro_regions_per_shard": int(max_regions),
        "max_solver_cost_units_per_tick": int(max_solver),
        "max_inspection_cost_units_per_tick": int(max_inspection),
        "micro_entities_exceeded": bool(entities > max_entities),
        "micro_regions_exceeded": bool(regions > max_regions),
        "solver_cost_exceeded": bool(solver > max_solver),
        "inspection_cost_exceeded": bool(inspection > max_inspection),
    }


def reserve_inspection_budget(
    *,
    runtime_budget_state: dict | None,
    tick: int,
    requested_cost_units: int,
    max_cost_units_per_tick: int,
) -> dict:
    state = dict(runtime_budget_state or {})
    used_by_tick = state.get("used_by_tick")
    if not isinstance(used_by_tick, dict):
        used_by_tick = {}
    tick_token = str(max(0, _as_int(tick, 0)))
    used_before = max(0, _as_int(used_by_tick.get(tick_token, 0), 0))
    requested = max(0, _as_int(requested_cost_units, 0))
    max_cost = max(0, _as_int(max_cost_units_per_tick, 0))
    if used_before + requested > max_cost:
        return {
            "result": "refused",
            "used_before": int(used_before),
            "requested_cost_units": int(requested),
            "max_cost_units_per_tick": int(max_cost),
            "used_after": int(used_before),
            "runtime_budget_state": {
                "used_by_tick": dict((str(key), max(0, _as_int(value, 0))) for key, value in sorted(used_by_tick.items()))
            },
        }
    used_after = used_before + requested
    used_by_tick[tick_token] = int(used_after)
    # Keep a deterministic bounded horizon of per-tick budget counters.
    tick_tokens_sorted = sorted((token for token in used_by_tick.keys() if str(token).isdigit()), key=lambda token: int(token))
    if len(tick_tokens_sorted) > 512:
        for token in tick_tokens_sorted[: len(tick_tokens_sorted) - 512]:
            used_by_tick.pop(token, None)
    out_state = {
        "used_by_tick": dict((str(key), max(0, _as_int(value, 0))) for key, value in sorted(used_by_tick.items()))
    }
    return {
        "result": "complete",
        "used_before": int(used_before),
        "requested_cost_units": int(requested),
        "max_cost_units_per_tick": int(max_cost),
        "used_after": int(used_after),
        "runtime_budget_state": out_state,
    }
