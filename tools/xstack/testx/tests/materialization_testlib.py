"""Shared MAT-7 macro/micro materialization test fixtures."""

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
    state.setdefault("micro_part_instances", [])
    state.setdefault("materialization_states", [])
    state.setdefault("distribution_aggregates", [])
    state.setdefault("materialization_reenactment_descriptors", [])
    return state


def with_structure_aggregate(
    state: dict,
    *,
    structure_id: str = "assembly.structure_instance.alpha",
    ag_node_id: str = "ag.node.alpha",
    total_mass: int = 1000,
    part_count: int = 4,
    batch_id: str = "batch.alpha",
    material_id: str = "material.steel_basic",
) -> dict:
    out = copy.deepcopy(state)
    structure_token = str(structure_id).strip()
    node_token = str(ag_node_id).strip()
    mass_raw = int(max(0, int(total_mass)))
    count_raw = int(max(1, int(part_count)))
    structures = [dict(row) for row in list(out.get("installed_structure_instances") or []) if isinstance(row, dict)]
    structures = [row for row in structures if str(row.get("instance_id", "")).strip() != structure_token]
    structures.append(
        {
            "schema_version": "1.0.0",
            "instance_id": structure_token,
            "project_id": "project.construction.seed.{}".format(structure_token.split(".")[-1]),
            "ag_id": "ag.seed.{}".format(structure_token.split(".")[-1]),
            "site_ref": "site.seed",
            "installed_node_states": [node_token],
            "maintenance_backlog": {},
            "extensions": {},
        }
    )
    out["installed_structure_instances"] = sorted(
        structures,
        key=lambda row: str(row.get("instance_id", "")),
    )

    aggregates = [dict(row) for row in list(out.get("distribution_aggregates") or []) if isinstance(row, dict)]
    aggregates = [
        row
        for row in aggregates
        if (
            str(row.get("structure_id", "")).strip() != structure_token
            or str(row.get("ag_node_id", "")).strip() != node_token
        )
    ]
    aggregates.append(
        {
            "schema_version": "1.0.0",
            "structure_id": structure_token,
            "ag_node_id": node_token,
            "total_mass": mass_raw,
            "defect_distribution_vector": {"defect.none": mass_raw},
            "wear_distribution_vector": {"failure.wear.general": 0},
            "extensions": {
                "part_count": count_raw,
                "batch_id": str(batch_id).strip() or "batch.alpha",
                "material_id": str(material_id).strip() or "material.unknown",
            },
        }
    )
    out["distribution_aggregates"] = sorted(
        aggregates,
        key=lambda row: (
            str(row.get("structure_id", "")),
            str(row.get("ag_node_id", "")),
        ),
    )
    return out


def law_profile(allowed_processes: List[str]) -> dict:
    unique = sorted(set(str(item).strip() for item in list(allowed_processes or []) if str(item).strip()))
    base = dict(construction_law_profile(unique))
    entitlement_map = dict(base.get("process_entitlement_requirements") or {})
    privilege_map = dict(base.get("process_privilege_requirements") or {})
    for process_id in unique:
        if process_id in ("process.materialize_structure_roi", "process.dematerialize_structure_roi"):
            entitlement_map[process_id] = "entitlement.control.admin"
            privilege_map[process_id] = "operator"
        elif process_id == "process.inspect_generate_snapshot":
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
    base = dict(construction_authority_context(entitlements or [], privilege_level=privilege_level))
    scope = dict(base.get("epistemic_scope") or {})
    scope["visibility_level"] = str(visibility_level).strip() or "nondiegetic"
    base["epistemic_scope"] = scope
    return base


def policy_context(
    *,
    max_micro_parts_per_roi: int = 1024,
    strict_contracts: bool = False,
    expand_tolerance: int = 0,
    collapse_tolerance: int = 0,
) -> dict:
    policy = copy.deepcopy(construction_policy_context())
    policy["strict_contracts"] = bool(strict_contracts)
    policy["materialization_max_micro_parts_per_roi"] = int(max(1, int(max_micro_parts_per_roi)))
    policy["active_shard_id"] = "shard.test.materialization"
    policy["expand_solver_id"] = "solver.expand.local_high_fidelity"
    policy["collapse_solver_id"] = "solver.collapse.macro_capsule"
    policy["transition_policy"] = {
        "policy_id": "policy.transition.test.materialization",
        "extensions": {
            "invariant_tolerances": {
                "expand_materialization": int(max(0, int(expand_tolerance))),
                "collapse_materialization": int(max(0, int(collapse_tolerance))),
            }
        },
    }
    return policy

