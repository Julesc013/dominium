"""Shared CIV-4 demography test fixtures."""

from __future__ import annotations

import copy
from typing import Dict, List

from tools.xstack.testx.tests.cohort_testlib import base_state as cohort_base_state
from tools.xstack.testx.tests.cohort_testlib import mapping_policy_registry


def base_state() -> dict:
    state = copy.deepcopy(cohort_base_state())
    state.setdefault("order_assemblies", [])
    state.setdefault("order_queue_assemblies", [])
    state.setdefault("institution_assemblies", [])
    state.setdefault("role_assignment_assemblies", [])
    state.setdefault("instrument_assemblies", [])
    return state


def with_cohort(
    state: dict,
    cohort_id: str,
    *,
    size: int = 1000,
    faction_id: str | None = "faction.alpha",
    location_ref: str = "region.alpha",
) -> dict:
    out = copy.deepcopy(state)
    cohort_rows = list(out.get("cohort_assemblies") or [])
    cohort_rows.append(
        {
            "cohort_id": str(cohort_id),
            "size": int(max(0, size)),
            "faction_id": faction_id,
            "territory_id": None,
            "location_ref": str(location_ref),
            "demographic_tags": {},
            "skill_distribution": {},
            "refinement_state": "macro",
            "created_tick": 0,
            "extensions": {
                "mapping_policy_id": "cohort.map.default",
                "expanded_micro_count": 0,
            },
        }
    )
    out["cohort_assemblies"] = sorted(
        (dict(row) for row in cohort_rows if isinstance(row, dict)),
        key=lambda row: str(row.get("cohort_id", "")),
    )
    return out


def demography_policy_registry(*, include_overkill: bool = False) -> dict:
    policies = [
        {
            "demography_policy_id": "demo.policy.none",
            "births_enabled": False,
            "death_model_id": "demo.death.none",
            "birth_model_id": "demo.birth.none",
            "migration_model_id": "demo.migration.instant",
            "tick_rate": 1,
            "deterministic_tie_break_id": "tie.cohort_id.asc",
            "extensions": {},
        },
        {
            "demography_policy_id": "demo.policy.stable_no_birth",
            "births_enabled": False,
            "death_model_id": "demo.death.low",
            "birth_model_id": "demo.birth.none",
            "migration_model_id": "demo.migration.banded",
            "tick_rate": 1,
            "deterministic_tie_break_id": "tie.cohort_id.asc",
            "extensions": {},
        },
        {
            "demography_policy_id": "demo.policy.basic_births",
            "births_enabled": True,
            "death_model_id": "demo.death.basic",
            "birth_model_id": "demo.birth.basic",
            "migration_model_id": "demo.migration.banded",
            "tick_rate": 1,
            "deterministic_tie_break_id": "tie.cohort_id.asc",
            "extensions": {},
        },
    ]
    if bool(include_overkill):
        policies.append(
            {
                "demography_policy_id": "demo.policy.overkill",
                "births_enabled": False,
                "death_model_id": "demo.death.overkill",
                "birth_model_id": "demo.birth.none",
                "migration_model_id": "demo.migration.instant",
                "tick_rate": 1,
                "deterministic_tie_break_id": "tie.cohort_id.asc",
                "extensions": {},
            }
        )
    return {"policies": policies}


def death_model_registry(*, include_overkill: bool = False) -> dict:
    rows = [
        {
            "death_model_id": "demo.death.none",
            "description": "none",
            "base_death_rate_per_tick": 0.0,
            "modifiers": {},
            "extensions": {},
        },
        {
            "death_model_id": "demo.death.low",
            "description": "low",
            "base_death_rate_per_tick": 0.001,
            "modifiers": {},
            "extensions": {},
        },
        {
            "death_model_id": "demo.death.basic",
            "description": "basic",
            "base_death_rate_per_tick": 0.002,
            "modifiers": {},
            "extensions": {},
        },
    ]
    if bool(include_overkill):
        rows.append(
            {
                "death_model_id": "demo.death.overkill",
                "description": "overkill",
                "base_death_rate_per_tick": 2.0,
                "modifiers": {},
                "extensions": {},
            }
        )
    return {"death_models": rows}


def birth_model_registry() -> dict:
    return {
        "birth_models": [
            {
                "birth_model_id": "demo.birth.none",
                "description": "none",
                "base_birth_rate_per_tick": 0.0,
                "modifiers": {},
                "extensions": {},
            },
            {
                "birth_model_id": "demo.birth.basic",
                "description": "basic",
                "base_birth_rate_per_tick": 0.003,
                "modifiers": {},
                "extensions": {},
            },
        ]
    }


def migration_model_registry() -> dict:
    return {
        "migration_models": [
            {
                "migration_model_id": "demo.migration.instant",
                "description": "instant",
                "travel_time_policy_id": "travel.instant",
                "capacity_limits": {},
                "extensions": {"instant": True},
            },
            {
                "migration_model_id": "demo.migration.banded",
                "description": "banded",
                "travel_time_policy_id": "travel.band.default",
                "capacity_limits": {"max_transit_per_tick": 1000000},
                "extensions": {
                    "distance_bands_mm": [
                        {"max_distance_mm": 0, "travel_ticks": 0},
                        {"max_distance_mm": 5000, "travel_ticks": 1},
                        {"max_distance_mm": 20000, "travel_ticks": 4},
                        {"max_distance_mm": 100000, "travel_ticks": 12},
                    ]
                },
            },
        ]
    }


def law_profile(
    allowed_processes: List[str],
    *,
    births_allowed: bool = True,
    migration_allowed: bool = True,
    allow_hidden_state_access: bool = False,
) -> dict:
    unique_processes = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    entitlement_map: Dict[str, str] = {}
    privilege_map: Dict[str, str] = {}
    for process_id in unique_processes:
        if process_id == "process.cohort_relocate":
            entitlement_map[process_id] = "entitlement.civ.order"
            privilege_map[process_id] = "operator"
        elif process_id in ("process.cohort_expand_to_micro", "process.cohort_collapse_from_micro"):
            entitlement_map[process_id] = "entitlement.civ.admin"
            privilege_map[process_id] = "operator"
        else:
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
    return {
        "law_profile_id": "law.test.demography",
        "allowed_processes": unique_processes,
        "forbidden_processes": [],
        "process_entitlement_requirements": entitlement_map,
        "process_privilege_requirements": privilege_map,
        "allowed_lenses": ["lens.test.demography", "lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {
            "max_view_radius_km": 1000000,
            "allow_hidden_state_access": bool(allow_hidden_state_access),
        },
        "epistemic_policy_id": "ep.policy.test.demography",
        "births_allowed": bool(births_allowed),
        "demography_births_allowed": bool(births_allowed),
        "migration_allowed": bool(migration_allowed),
    }


def authority_context(entitlements: List[str] | None = None, privilege_level: str = "observer") -> dict:
    rows = sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip()))
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.demography",
        "experience_id": "profile.test.demography",
        "law_profile_id": "law.test.demography",
        "entitlements": rows,
        "epistemic_scope": {
            "scope_id": "scope.test.demography",
            "visibility_level": "diegetic",
        },
        "privilege_level": str(privilege_level),
    }


def policy_context(
    *,
    parameter_bundle_id: str = "",
    active_shard_id: str = "",
    shard_map: dict | None = None,
    include_overkill: bool = False,
) -> dict:
    payload = {
        "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=16),
        "demography_policy_registry": demography_policy_registry(include_overkill=bool(include_overkill)),
        "death_model_registry": death_model_registry(include_overkill=bool(include_overkill)),
        "birth_model_registry": birth_model_registry(),
        "migration_model_registry": migration_model_registry(),
        "pack_lock_hash": "a" * 64,
        "active_shard_id": str(active_shard_id).strip(),
        "shard_map": dict(shard_map or {}),
    }
    if str(parameter_bundle_id).strip():
        payload["parameter_bundle_id"] = str(parameter_bundle_id).strip()
    return payload

