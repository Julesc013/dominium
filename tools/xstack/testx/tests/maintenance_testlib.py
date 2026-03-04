"""Shared MAT-6 decay/failure/maintenance test fixtures."""

from __future__ import annotations

import copy
from typing import List

from tools.xstack.testx.tests.construction_testlib import (
    authority_context as construction_authority_context,
    base_state as construction_base_state,
    law_profile as construction_law_profile,
    policy_context as construction_policy_context,
)


def base_state() -> dict:
    state = copy.deepcopy(construction_base_state())
    state.setdefault("asset_health_states", [])
    state.setdefault("failure_events", [])
    state.setdefault("maintenance_commitments", [])
    state.setdefault("maintenance_provenance_events", [])
    state.setdefault(
        "maintenance_runtime_state",
        {
            "next_event_sequence": 0,
            "last_decay_tick": 0,
            "last_schedule_tick": 0,
            "last_inspection_tick": 0,
            "last_maintenance_tick": 0,
            "last_budget_outcome": "none",
            "extensions": {},
        },
    )
    return state


def with_asset_health(
    state: dict,
    *,
    asset_id: str,
    failure_mode_ids: List[str] | None = None,
    maintenance_policy_id: str = "maint.policy.default_realistic",
    maintenance_backlog: int = 0,
    wear_by_mode: dict | None = None,
) -> dict:
    out = copy.deepcopy(state)
    rows = [dict(row) for row in list(out.get("asset_health_states") or []) if isinstance(row, dict)]
    rows.append(
        {
            "schema_version": "1.0.0",
            "asset_id": str(asset_id),
            "failure_mode_ids": sorted(set(str(item).strip() for item in list(failure_mode_ids or ["failure.wear.general"]) if str(item).strip())),
            "accumulated_wear": dict(
                (str(key).strip(), int(max(0, int(value))))
                for key, value in sorted((dict(wear_by_mode or {})).items(), key=lambda item: str(item[0]))
                if str(key).strip()
            ),
            "hazard_state": {"failed_mode_ids": []},
            "maintenance_backlog": int(max(0, int(maintenance_backlog))),
            "last_inspection_tick": 0,
            "last_maintenance_tick": 0,
            "extensions": {"maintenance_policy_id": str(maintenance_policy_id)},
        }
    )
    out["asset_health_states"] = rows
    return out


def failure_mode_registry(*, threshold_raw: int = 10_000, base_rate_raw: int = 2_000) -> dict:
    return {
        "failure_modes": [
            {
                "schema_version": "1.0.0",
                "failure_mode_id": "failure.wear.general",
                "description": "Generic deterministic wear mode for tests.",
                "applies_to_part_classes": ["partclass.beam.generic"],
                "hazard_inputs": ["ch.load.utilization"],
                "base_hazard_rate_per_tick": int(max(0, int(base_rate_raw))),
                "modifiers": {"failure_threshold": int(max(1, int(threshold_raw)))},
                "failure_event_type_id": "event.failure.triggered",
                "maintenance_effect_model_id": "maint.effect.partial_reset",
                "extensions": {},
            }
        ]
    }


def maintenance_policy_registry(
    *,
    inspection_interval_ticks: int = 5,
    maintenance_interval_ticks: int = 8,
    max_backlog: int = 1_000_000,
) -> dict:
    return {
        "policies": [
            {
                "schema_version": "1.0.0",
                "maintenance_policy_id": "maint.policy.default_realistic",
                "description": "Default deterministic maintenance policy for tests.",
                "inspection_interval_ticks": int(max(0, int(inspection_interval_ticks))),
                "maintenance_interval_ticks": int(max(0, int(maintenance_interval_ticks))),
                "backlog_growth_rule_id": "backlog.linear_stub",
                "max_backlog": int(max(0, int(max_backlog))),
                "extensions": {"risk_quantization_step": 50},
            },
            {
                "schema_version": "1.0.0",
                "maintenance_policy_id": "maint.policy.rank_strict",
                "description": "Rank strict deterministic maintenance policy for tests.",
                "inspection_interval_ticks": int(max(0, int(max(1, inspection_interval_ticks // 2)))),
                "maintenance_interval_ticks": int(max(0, int(max(1, maintenance_interval_ticks // 2)))),
                "backlog_growth_rule_id": "backlog.stepwise_stub",
                "max_backlog": int(max(0, int(max_backlog))),
                "extensions": {"risk_quantization_step": 25, "rank_profile": True},
            },
            {
                "schema_version": "1.0.0",
                "maintenance_policy_id": "maint.policy.none",
                "description": "No maintenance schedule test policy.",
                "inspection_interval_ticks": 0,
                "maintenance_interval_ticks": 0,
                "backlog_growth_rule_id": "backlog.linear_stub",
                "max_backlog": int(max(0, int(max_backlog))),
                "extensions": {"maintenance_disabled": True},
            },
        ]
    }


def backlog_growth_rule_registry() -> dict:
    return {
        "rules": [
            {
                "schema_version": "1.0.0",
                "rule_id": "backlog.linear_stub",
                "description": "Linear backlog growth for tests.",
                "model_kind": "linear",
                "base_increment_per_tick": 100,
                "thresholds": [],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "rule_id": "backlog.stepwise_stub",
                "description": "Stepwise backlog growth for tests.",
                "model_kind": "stepwise",
                "base_increment_per_tick": 20,
                "thresholds": [
                    {"at_backlog": 1_000, "increment_per_tick": 50},
                    {"at_backlog": 5_000, "increment_per_tick": 75},
                ],
                "extensions": {},
            },
        ]
    }


def law_profile(allowed_processes: List[str], *, allow_maintenance: bool = True) -> dict:
    unique = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    base = dict(construction_law_profile(unique))
    entitlement_map = dict(base.get("process_entitlement_requirements") or {})
    privilege_map = dict(base.get("process_privilege_requirements") or {})
    for process_id in unique:
        if process_id == "process.decay_tick":
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
        elif process_id in ("process.maintenance_schedule", "process.inspection_perform", "process.maintenance_perform"):
            entitlement_map[process_id] = "entitlement.control.admin"
            privilege_map[process_id] = "operator"
    base["process_entitlement_requirements"] = entitlement_map
    base["process_privilege_requirements"] = privilege_map
    base["allow_maintenance"] = bool(allow_maintenance)
    return base


def authority_context(
    entitlements: List[str] | None = None,
    *,
    privilege_level: str = "operator",
    visibility_level: str = "nondiegetic",
) -> dict:
    base = dict(construction_authority_context(entitlements or [], privilege_level=privilege_level))
    scope = dict(base.get("epistemic_scope") or {})
    scope["visibility_level"] = str(visibility_level).strip() or "nondiegetic"
    base["epistemic_scope"] = scope
    return base


def policy_context(
    *,
    max_compute_units_per_tick: int = 4096,
    failure_threshold_raw: int = 10_000,
    failure_base_rate_raw: int = 2_000,
    inspection_interval_ticks: int = 5,
    maintenance_interval_ticks: int = 8,
) -> dict:
    policy = copy.deepcopy(
        construction_policy_context(
            max_compute_units_per_tick=max_compute_units_per_tick,
            construction_max_projects_per_tick=32,
            construction_cost_units_per_active_step=1,
        )
    )
    policy["failure_mode_registry"] = failure_mode_registry(
        threshold_raw=int(failure_threshold_raw),
        base_rate_raw=int(failure_base_rate_raw),
    )
    policy["maintenance_policy_registry"] = maintenance_policy_registry(
        inspection_interval_ticks=int(inspection_interval_ticks),
        maintenance_interval_ticks=int(maintenance_interval_ticks),
    )
    policy["backlog_growth_rule_registry"] = backlog_growth_rule_registry()
    policy["maintenance_policy_id"] = "maint.policy.default_realistic"
    quantity_types = [
        dict(row)
        for row in list((dict(policy.get("quantity_type_registry") or {}).get("quantity_types") or []))
        if isinstance(row, dict)
    ]
    quantity_ids = set(str(row.get("quantity_id", "")).strip() for row in quantity_types)
    if "quantity.entropy_metric" not in quantity_ids:
        quantity_types.append({"quantity_id": "quantity.entropy_metric", "dimension_id": "dim.energy"})
    if "quantity.entropy_index" not in quantity_ids:
        quantity_types.append({"quantity_id": "quantity.entropy_index", "dimension_id": "dim.entropy"})
    policy["quantity_type_registry"] = {"quantity_types": quantity_types}
    quantities = [
        dict(row)
        for row in list((dict(policy.get("quantity_registry") or {}).get("quantities") or []))
        if isinstance(row, dict)
    ]
    quantity_ids = set(str(row.get("quantity_id", "")).strip() for row in quantities)
    if "quantity.entropy_metric" not in quantity_ids:
        quantities.append({"quantity_id": "quantity.entropy_metric", "dimension_id": "dim.energy"})
    if "quantity.entropy_index" not in quantity_ids:
        quantities.append({"quantity_id": "quantity.entropy_index", "dimension_id": "dim.entropy"})
    policy["quantity_registry"] = {"quantities": quantities}
    return policy
