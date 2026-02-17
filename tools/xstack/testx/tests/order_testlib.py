"""Shared CIV-3 order/institution fixtures."""

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
    return state


def with_cohort(state: dict, cohort_id: str, *, size: int = 5, faction_id: str | None = "faction.alpha", location_ref: str = "region.alpha") -> dict:
    out = copy.deepcopy(state)
    cohort_rows = list(out.get("cohort_assemblies") or [])
    cohort_rows.append(
        {
            "cohort_id": str(cohort_id),
            "size": int(size),
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
    faction_rows = list(out.get("faction_assemblies") or [])
    if faction_id and not any(str(row.get("faction_id", "")).strip() == str(faction_id).strip() for row in faction_rows if isinstance(row, dict)):
        faction_rows.append(
            {
                "faction_id": str(faction_id),
                "human_name": str(faction_id),
                "description": "",
                "created_tick": 0,
                "founder_agent_id": None,
                "governance_type_id": "gov.band",
                "territory_ids": [],
                "diplomatic_relations": {},
                "status": "active",
                "extensions": {},
            }
        )
    out["faction_assemblies"] = sorted(
        (dict(row) for row in faction_rows if isinstance(row, dict)),
        key=lambda row: str(row.get("faction_id", "")),
    )
    return out


def with_agent(state: dict, agent_id: str, *, location_ref: str = "region.alpha") -> dict:
    out = copy.deepcopy(state)
    agent_rows = list(out.get("agent_states") or [])
    agent_rows.append(
        {
            "agent_id": str(agent_id),
            "state_hash": "agent.hash.stub",
            "body_id": None,
            "owner_peer_id": "peer.test.order",
            "controller_id": "controller.test.order",
            "shard_id": "shard.0",
            "intent_scope_id": None,
            "parent_cohort_id": "",
            "location_ref": str(location_ref),
            "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
        }
    )
    out["agent_states"] = sorted(
        (dict(row) for row in agent_rows if isinstance(row, dict)),
        key=lambda row: str(row.get("agent_id", "")),
    )
    return out


def order_type_registry() -> dict:
    return {
        "order_types": [
            {
                "order_type_id": "order.move",
                "description": "move",
                "payload_schema_id": "dominium.schema.civilisation.order_move",
                "allowed_target_kinds": ["agent", "cohort", "faction"],
                "default_priority": 60,
                "required_capabilities": ["entitlement.civ.order"],
                "extensions": {},
            },
            {
                "order_type_id": "order.migrate",
                "description": "migrate",
                "payload_schema_id": "dominium.schema.civilisation.order_move",
                "allowed_target_kinds": ["cohort", "faction"],
                "default_priority": 70,
                "required_capabilities": ["entitlement.civ.order"],
                "extensions": {},
            },
            {
                "order_type_id": "order.assimilate",
                "description": "assimilate",
                "payload_schema_id": "dominium.schema.civilisation.order_assimilate",
                "allowed_target_kinds": ["agent", "cohort", "faction"],
                "default_priority": 80,
                "required_capabilities": ["entitlement.civ.order", "entitlement.civ.assimilate"],
                "extensions": {},
            },
            {
                "order_type_id": "order.patrol",
                "description": "patrol",
                "payload_schema_id": "dominium.schema.civilisation.order_move",
                "allowed_target_kinds": ["agent", "cohort"],
                "default_priority": 40,
                "required_capabilities": ["entitlement.civ.order"],
                "extensions": {},
            },
            {
                "order_type_id": "order.build_plan",
                "description": "build_plan",
                "payload_schema_id": "dominium.schema.civilisation.order_build_plan",
                "allowed_target_kinds": ["cohort", "faction", "territory"],
                "default_priority": 20,
                "required_capabilities": ["entitlement.civ.order"],
                "extensions": {},
            },
            {
                "order_type_id": "order.communicate",
                "description": "communicate",
                "payload_schema_id": "dominium.schema.diegetics.message",
                "allowed_target_kinds": ["agent", "cohort", "faction"],
                "default_priority": 50,
                "required_capabilities": ["entitlement.civ.order"],
                "extensions": {},
            },
        ]
    }


def role_registry() -> dict:
    return {
        "roles": [
            {
                "role_id": "role.leader",
                "description": "leader",
                "granted_entitlements": [
                    "entitlement.civ.order",
                    "entitlement.civ.assimilate",
                    "entitlement.civ.view_orders",
                    "entitlement.civ.role_assign",
                ],
                "extensions": {},
            },
            {
                "role_id": "role.envoy",
                "description": "envoy",
                "granted_entitlements": ["entitlement.civ.order", "entitlement.civ.view_orders"],
                "extensions": {},
            },
            {
                "role_id": "role.worker",
                "description": "worker",
                "granted_entitlements": ["entitlement.civ.order"],
                "extensions": {},
            },
            {
                "role_id": "role.guard",
                "description": "guard",
                "granted_entitlements": ["entitlement.civ.order"],
                "extensions": {},
            },
        ]
    }


def institution_type_registry() -> dict:
    return {
        "institution_types": [
            {
                "institution_type_id": "inst.band_council",
                "description": "band",
                "allowed_role_ids": ["role.leader", "role.envoy", "role.worker", "role.guard"],
                "extensions": {},
            },
            {
                "institution_type_id": "inst.tribe_council",
                "description": "tribe",
                "allowed_role_ids": ["role.leader", "role.envoy", "role.worker", "role.guard"],
                "extensions": {},
            },
            {
                "institution_type_id": "inst.city_admin",
                "description": "city",
                "allowed_role_ids": ["role.leader", "role.envoy", "role.worker", "role.guard"],
                "extensions": {},
            },
        ]
    }


def law_profile(allowed_processes: List[str], *, allow_role_delegation: bool = True) -> dict:
    unique_processes = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    entitlement_map: Dict[str, str] = {}
    privilege_map: Dict[str, str] = {}
    for process_id in unique_processes:
        if process_id in ("process.order_create", "process.order_cancel", "process.order_tick", "process.cohort_relocate"):
            entitlement_map[process_id] = "entitlement.civ.order"
            privilege_map[process_id] = "operator"
        elif process_id in ("process.role_assign", "process.role_revoke"):
            entitlement_map[process_id] = "entitlement.civ.role_assign"
            privilege_map[process_id] = "operator"
        else:
            entitlement_map[process_id] = "session.boot"
            privilege_map[process_id] = "observer"
    return {
        "law_profile_id": "law.test.order",
        "allowed_processes": unique_processes,
        "forbidden_processes": [],
        "process_entitlement_requirements": entitlement_map,
        "process_privilege_requirements": privilege_map,
        "allowed_lenses": ["lens.diegetic.sensor", "lens.nondiegetic.debug"],
        "epistemic_limits": {"max_view_radius_km": 1000000, "allow_hidden_state_access": True},
        "epistemic_policy_id": "ep.policy.lab_broad",
        "allow_role_delegation": bool(allow_role_delegation),
        "delegable_entitlements": [
            "entitlement.civ.order",
            "entitlement.civ.assimilate",
            "entitlement.civ.view_orders",
            "entitlement.civ.role_assign",
        ],
    }


def authority_context(entitlements: List[str] | None = None, privilege_level: str = "operator") -> dict:
    rows = sorted(set(str(item).strip() for item in list(entitlements or []) if str(item).strip()))
    return {
        "authority_origin": "tool",
        "peer_id": "peer.test.order",
        "experience_id": "profile.test.order",
        "law_profile_id": "law.test.order",
        "entitlements": rows,
        "epistemic_scope": {
            "scope_id": "scope.test.order",
            "visibility_level": "nondiegetic",
        },
        "privilege_level": str(privilege_level),
    }


def policy_context(*, active_shard_id: str = "", shard_map: dict | None = None) -> dict:
    return {
        "cohort_mapping_policy_registry": mapping_policy_registry(max_micro_agents_per_cohort=16),
        "order_type_registry": order_type_registry(),
        "role_registry": role_registry(),
        "institution_type_registry": institution_type_registry(),
        "pack_lock_hash": "a" * 64,
        "active_shard_id": str(active_shard_id).strip(),
        "shard_map": dict(shard_map or {}),
    }

