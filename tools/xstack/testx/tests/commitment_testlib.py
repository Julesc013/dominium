"""Shared MAT-8 commitment/reenactment test fixtures."""

from __future__ import annotations

import copy
from typing import List

from tools.xstack.testx.tests.logistics_testlib import (
    logistics_graph,
    logistics_graph_registry,
    logistics_routing_rule_registry,
)
from tools.xstack.testx.tests.maintenance_testlib import (
    authority_context as maintenance_authority_context,
    base_state as maintenance_base_state,
    law_profile as maintenance_law_profile,
    policy_context as maintenance_policy_context,
)


def base_state() -> dict:
    state = copy.deepcopy(maintenance_base_state())
    state.setdefault("material_commitments", [])
    state.setdefault("event_stream_indices", [])
    state.setdefault("reenactment_requests", [])
    state.setdefault("reenactment_artifacts", [])
    return state


def commitment_type_registry() -> dict:
    return {
        "commitment_types": [
            {
                "schema_version": "1.0.0",
                "commitment_type_id": "commit.construction.project",
                "description": "construction project commitment",
                "required_entitlements": ["entitlement.control.admin"],
                "produces_event_type_ids": ["event.construct_project_created"],
                "strictness_requirements": ["causality.C1", "causality.C2"],
                "extensions": {"major_change": True},
            },
            {
                "schema_version": "1.0.0",
                "commitment_type_id": "commit.construction.step",
                "description": "construction step commitment",
                "required_entitlements": ["entitlement.control.admin"],
                "produces_event_type_ids": ["event.construct_step_started", "event.construct_step_completed"],
                "strictness_requirements": ["causality.C1", "causality.C2"],
                "extensions": {"major_change": True},
            },
            {
                "schema_version": "1.0.0",
                "commitment_type_id": "commit.logistics.shipment",
                "description": "shipment commitment",
                "required_entitlements": ["entitlement.control.admin"],
                "produces_event_type_ids": ["event.shipment_depart", "event.shipment_arrive", "event.shipment_lost"],
                "strictness_requirements": ["causality.C1", "causality.C2"],
                "extensions": {"major_change": True},
            },
            {
                "schema_version": "1.0.0",
                "commitment_type_id": "commit.maintenance.inspect",
                "description": "maintenance inspection commitment",
                "required_entitlements": ["entitlement.control.admin"],
                "produces_event_type_ids": ["event.inspection_performed"],
                "strictness_requirements": ["causality.C1", "causality.C2"],
                "extensions": {"major_change": True},
            },
            {
                "schema_version": "1.0.0",
                "commitment_type_id": "commit.maintenance.repair",
                "description": "maintenance repair commitment",
                "required_entitlements": ["entitlement.control.admin"],
                "produces_event_type_ids": ["event.maintenance_performed"],
                "strictness_requirements": ["causality.C1", "causality.C2"],
                "extensions": {"major_change": True},
            },
            {
                "schema_version": "1.0.0",
                "commitment_type_id": "commit.custom",
                "description": "custom commitment",
                "required_entitlements": [],
                "produces_event_type_ids": [],
                "strictness_requirements": ["causality.C0", "causality.C1", "causality.C2"],
                "extensions": {"stub": True},
            },
        ]
    }


def causality_strictness_registry() -> dict:
    return {
        "strictness_levels": [
            {
                "schema_version": "1.0.0",
                "causality_strictness_id": "causality.C0",
                "level": "C0",
                "description": "events mandatory, commitments optional",
                "major_change_requires_commitment": False,
                "event_required_for_macro_change": True,
                "extensions": {"default": True},
            },
            {
                "schema_version": "1.0.0",
                "causality_strictness_id": "causality.C1",
                "level": "C1",
                "description": "major macro changes require commitments",
                "major_change_requires_commitment": True,
                "event_required_for_macro_change": True,
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "causality_strictness_id": "causality.C2",
                "level": "C2",
                "description": "reserved strict mode",
                "major_change_requires_commitment": True,
                "event_required_for_macro_change": True,
                "extensions": {"reserved": True},
            },
        ]
    }


def law_profile(allowed_processes: List[str], *, allow_maintenance: bool = True) -> dict:
    unique = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    base = dict(maintenance_law_profile(unique, allow_maintenance=allow_maintenance))
    entitlement_map = dict(base.get("process_entitlement_requirements") or {})
    privilege_map = dict(base.get("process_privilege_requirements") or {})
    for process_id in unique:
        if process_id == "process.commitment_create":
            entitlement_map[process_id] = "entitlement.control.admin"
            privilege_map[process_id] = "operator"
        elif process_id in ("process.event_stream_index_rebuild", "process.reenactment_generate", "process.reenactment_play"):
            entitlement_map[process_id] = "entitlement.inspect"
            privilege_map[process_id] = "observer"
    base["process_entitlement_requirements"] = entitlement_map
    base["process_privilege_requirements"] = privilege_map
    return base


def authority_context(
    entitlements: List[str] | None = None,
    *,
    privilege_level: str = "operator",
    visibility_level: str = "nondiegetic",
) -> dict:
    return maintenance_authority_context(
        entitlements or [],
        privilege_level=privilege_level,
        visibility_level=visibility_level,
    )


def policy_context(
    *,
    strictness_id: str = "causality.C0",
    max_compute_units_per_tick: int = 4096,
) -> dict:
    policy = copy.deepcopy(
        maintenance_policy_context(
            max_compute_units_per_tick=max_compute_units_per_tick,
            failure_threshold_raw=20_000,
            failure_base_rate_raw=800,
            inspection_interval_ticks=5,
            maintenance_interval_ticks=8,
        )
    )
    policy["commitment_type_registry"] = commitment_type_registry()
    policy["causality_strictness_registry"] = causality_strictness_registry()
    policy["causality_strictness_id"] = str(strictness_id).strip() or "causality.C0"
    policy["logistics_graph_registry"] = logistics_graph_registry([logistics_graph(delay_ticks=1, loss_fraction=0)])
    policy["logistics_routing_rule_registry"] = logistics_routing_rule_registry()
    return policy
