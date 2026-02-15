"""STRICT test: unsupported solver transition yields refusal.contract_violation."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.domain.contract_violation_refusal"
TEST_TAGS = ["strict", "session", "repox"]


def _state_fixture() -> dict:
    return {
        "schema_version": "1.0.0",
        "simulation_time": {"tick": 0, "timestamp_utc": "1970-01-01T00:00:00Z"},
        "camera_assemblies": [
            {
                "assembly_id": "camera.main",
                "frame_id": "frame.sol.system",
                "position_mm": {"x": 0, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "velocity_mm_per_tick": {"x": 0, "y": 0, "z": 0},
            }
        ],
        "interest_regions": [],
        "macro_capsules": [],
        "micro_regions": [],
        "history_anchors": [],
    }


def _navigation_fixture() -> dict:
    return {
        "astronomy_catalog_index": {
            "entries": [
                {
                    "object_id": "object.earth",
                    "kind": "planet",
                    "frame_id": "frame.earth.body_fixed",
                    "bounds": {"sphere_radius_mm": 6371000000},
                }
            ]
        },
        "site_registry_index": {"sites": []},
    }


def _policy_fixture() -> dict:
    return {
        "activation_policy": {
            "policy_id": "policy.activation.test",
            "interest_radius_rules": [
                {
                    "kind": "*",
                    "priority": 1,
                    "activation_distance_mm": 999999999999,
                    "deactivation_distance_mm": 999999999999,
                    "anchor_spacing_mm": 1,
                }
            ],
            "hysteresis": {"enter_margin_mm": 0, "exit_margin_mm": 0},
        },
        "budget_policy": {
            "policy_id": "policy.budget.test",
            "max_compute_units_per_tick": 1000,
            "max_entities_micro": 1000,
            "max_regions_micro": 10,
            "fallback_behavior": "degrade_fidelity",
            "entity_compute_weight": 1,
            "tier_compute_weights": {"coarse": 1, "medium": 2, "fine": 3},
        },
        "fidelity_policy": {
            "policy_id": "policy.fidelity.test",
            "tiers": [
                {"tier_id": "coarse", "max_distance_mm": 999999999999, "target_entities": 1},
                {"tier_id": "medium", "max_distance_mm": 1000, "target_entities": 2},
                {"tier_id": "fine", "max_distance_mm": 10, "target_entities": 3},
            ],
            "switching_rules": {"degrade_order": ["fine", "medium", "coarse"]},
        },
        "solver_bindings": {
            "collapse_solver_id": "solver.collapse.macro_capsule",
            "expand_solver_id": "solver.expand.local_high_fidelity",
        },
        "solver_registry": {
            "schema_id": "dominium.registry.solver_registry",
            "schema_version": "1.0.0",
            "records": [
                {
                    "solver_id": "solver.expand.local_high_fidelity",
                    "domain_ids": ["dom.domain.orbital.mechanics"],
                    "contract_ids": ["dom.contract.deterministic_transition"],
                    "resolution_tags": ["micro"],
                    "cost_class": "high",
                    "transition_support": ["collapse"],
                    "refusal_codes": ["refusal.contract_violation"],
                    "resolution": "micro",
                    "guarantees": [],
                    "supports_transitions": ["collapse"],
                    "numeric_bounds": {"bounded": True},
                    "conformance_bundle_refs": []
                },
                {
                    "solver_id": "solver.collapse.macro_capsule",
                    "domain_ids": ["dom.domain.gravity.macro"],
                    "contract_ids": ["dom.contract.deterministic_transition"],
                    "resolution_tags": ["macro"],
                    "cost_class": "low",
                    "transition_support": ["collapse"],
                    "refusal_codes": ["refusal.contract_violation"],
                    "resolution": "macro",
                    "guarantees": [],
                    "supports_transitions": ["collapse"],
                    "numeric_bounds": {"bounded": True},
                    "conformance_bundle_refs": []
                }
            ]
        },
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx.process_runtime import execute_intent

    state = _state_fixture()
    law_profile = {
        "law_profile_id": "law.test",
        "allowed_processes": ["process.region_management_tick"],
        "forbidden_processes": [],
    }
    authority_context = {
        "authority_origin": "tool",
        "entitlements": ["session.boot"],
        "privilege_level": "observer",
    }
    intent = {
        "intent_id": "intent.test.contract_violation",
        "process_id": "process.region_management_tick",
        "inputs": {},
    }
    result = execute_intent(
        state=copy.deepcopy(state),
        intent=intent,
        law_profile=law_profile,
        authority_context=authority_context,
        navigation_indices=_navigation_fixture(),
        policy_context=_policy_fixture(),
    )
    if str(result.get("result", "")) != "refused":
        return {"status": "fail", "message": "expected refusal for unsupported expand transition"}
    reason_code = str((result.get("refusal") or {}).get("reason_code", ""))
    if reason_code != "refusal.contract_violation":
        return {"status": "fail", "message": "expected refusal.contract_violation, got '{}'".format(reason_code)}
    return {"status": "pass", "message": "contract violation refusal check passed"}
