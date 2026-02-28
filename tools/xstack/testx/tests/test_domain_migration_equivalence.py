"""STRICT test: MAT-7/MAT-9 migration to negotiation kernel preserves deterministic equivalence."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_domain_migration_equivalence"
TEST_TAGS = ["strict", "control", "negotiation", "materials", "inspection"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.control.negotiation import negotiate_request
    from src.inspection import inspection_engine as inspect_engine
    from src.materials.materialization.materialization_engine import materialize_structure_roi

    # MAT-9 equivalence: inspection fidelity resolver must match direct kernel negotiation.
    section_rows = {}
    for fidelity in ("macro", "meso", "micro"):
        for section_id in inspect_engine._section_ids_for_fidelity(fidelity=fidelity, target_kind="structure"):
            section_rows[section_id] = {
                "section_id": section_id,
                "extensions": {"cost_units": 1},
            }
    desired_fidelity = "micro"
    achieved, _, _, _ = inspect_engine._resolve_fidelity(
        desired_fidelity=desired_fidelity,
        target_kind="structure",
        max_cost_units=2,
        section_rows=section_rows,
        micro_allowed=True,
        micro_available=True,
        strict_budget=False,
    )
    fidelity_cost_by_level = {}
    for fidelity in ("macro", "meso", "micro"):
        section_ids = inspect_engine._section_ids_for_fidelity(fidelity=fidelity, target_kind="structure")
        fidelity_cost_by_level[fidelity] = int(inspect_engine._section_cost(section_rows, section_ids))
    desired_cost = int(fidelity_cost_by_level.get(desired_fidelity, 0))
    direct_inspection = negotiate_request(
        negotiation_request={
            "schema_version": "1.0.0",
            "requester_subject_id": "subject.inspect",
            "request_vector": {
                "abstraction_level_requested": "AL0",
                "fidelity_requested": desired_fidelity,
                "view_requested": "view.mode.first_person",
                "epistemic_scope_requested": "ep.scope.default",
                "budget_requested": desired_cost,
            },
            "context": {"law_profile_id": "law.inspect", "server_profile_id": "server.profile.inspect"},
            "extensions": {
                "micro_allowed": True,
                "micro_available": True,
                "budget_refuse_on_shortfall": False,
                "budget_refusal_code": "refusal.inspect.budget_exceeded",
                "budget_zero_means_unbounded": True,
                "fidelity_cost_by_level": dict(fidelity_cost_by_level),
            },
        },
        rs5_budget_state={
            "tick": 0,
            "requested_cost_units": desired_cost,
            "max_cost_units_per_tick": 2,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.inspect"],
        },
        control_policy={
            "control_policy_id": "ctrl.policy.inspect",
            "allowed_abstraction_levels": ["AL0"],
            "allowed_view_policies": ["view.mode.first_person"],
            "allowed_fidelity_ranges": ["macro", "meso", "micro"],
            "extensions": {},
        },
        authority_context={"entitlements": []},
        law_profile={"allowed_processes": [], "forbidden_processes": []},
    )
    direct_fidelity = str((dict(direct_inspection.get("resolved_vector") or {})).get("fidelity_resolved", "")).strip()
    if achieved != direct_fidelity:
        return {"status": "fail", "message": "MAT-9 fidelity resolution drifted from direct negotiation kernel result"}

    # MAT-7 equivalence: materialization budget truncation must match direct kernel budget allocation.
    structure_id = "assembly.structure_instance.alpha"
    structure_row = {"instance_id": structure_id, "installed_node_states": ["ag.node.001"]}
    distribution_rows = [
        {
            "schema_version": "1.0.0",
            "structure_id": structure_id,
            "ag_node_id": "ag.node.001",
            "total_mass": 100,
            "defect_distribution_vector": {},
            "wear_distribution_vector": {},
            "extensions": {
                "batch_id": "batch.alpha",
                "material_id": "material.steel",
                "part_count": 5,
            },
        }
    ]
    authority_context = {
        "subject_id": "subject.materialize",
        "epistemic_scope": {"scope_id": "ep.scope.standard"},
        "entitlements": [],
    }
    materialized = materialize_structure_roi(
        structure_row=structure_row,
        roi_id="roi.alpha",
        current_tick=9,
        max_micro_parts=2,
        distribution_aggregates=distribution_rows,
        existing_micro_parts=[],
        existing_materialization_states=[],
        strict_budget=False,
        roi_node_ids=["ag.node.001"],
        law_profile={"law_profile_id": "law.materialize", "allowed_processes": [], "forbidden_processes": []},
        authority_context=copy.deepcopy(authority_context),
        policy_context={"server_profile_id": "server.profile.private"},
    )
    materialization_negotiation = dict(materialized.get("negotiation_result") or {})
    materialization_budget = int(
        max(0, int((dict(materialization_negotiation.get("resolved_vector") or {})).get("budget_allocated", 0)))
    )
    direct_materialization = negotiate_request(
        negotiation_request={
            "schema_version": "1.0.0",
            "requester_subject_id": "subject.materialize",
            "request_vector": {
                "abstraction_level_requested": "AL1",
                "fidelity_requested": "micro",
                "view_requested": "view.mode.first_person",
                "epistemic_scope_requested": "ep.scope.standard",
                "budget_requested": 5,
            },
            "context": {"law_profile_id": "law.materialize", "server_profile_id": "server.profile.private"},
            "extensions": {
                "required_process_id": "process.materialize_structure_roi",
                "budget_refuse_on_shortfall": False,
                "budget_refusal_code": "refusal.materialization.budget_exceeded",
                "budget_zero_means_unbounded": False,
                "fidelity_cost_by_level": {"micro": 5, "meso": 2, "macro": 1},
            },
        },
        rs5_budget_state={
            "tick": 9,
            "requested_cost_units": 5,
            "max_cost_units_per_tick": 2,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.materialize"],
        },
        control_policy={
            "control_policy_id": "ctrl.policy.materialization",
            "allowed_abstraction_levels": ["AL1", "AL2", "AL3", "AL4"],
            "allowed_view_policies": ["view.mode.first_person"],
            "allowed_fidelity_ranges": ["macro", "meso", "micro"],
            "extensions": {},
        },
        authority_context=copy.deepcopy(authority_context),
        law_profile={"law_profile_id": "law.materialize", "allowed_processes": [], "forbidden_processes": []},
    )
    direct_budget = int(max(0, int((dict(direct_materialization.get("resolved_vector") or {})).get("budget_allocated", 0))))
    if materialization_budget != direct_budget:
        return {"status": "fail", "message": "MAT-7 budget allocation drifted from direct negotiation kernel result"}
    if int(len(list(materialized.get("micro_parts") or []))) != int(min(2, materialization_budget)):
        return {"status": "fail", "message": "MAT-7 truncation does not match negotiated budget allocation"}

    return {"status": "pass", "message": "domain migration negotiation equivalence checks passed"}

