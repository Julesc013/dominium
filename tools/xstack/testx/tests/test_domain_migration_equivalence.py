"""STRICT test: MAT-7/MAT-8/MAT-9 fidelity migration preserves deterministic engine equivalence."""

from __future__ import annotations

import sys


TEST_ID = "test_domain_migration_equivalence"
TEST_TAGS = ["strict", "control", "fidelity", "materials", "inspection", "reenactment"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.fidelity import DEFAULT_FIDELITY_POLICY_ID, arbitrate_fidelity_requests
    from inspection import inspection_engine as inspect_engine
    from materials.commitments.commitment_engine import build_reenactment_artifact
    from materials.materialization.materialization_engine import materialize_structure_roi

    # MAT-9 equivalence: inspection fidelity resolver must match direct fidelity arbitration output.
    section_rows = {}
    for fidelity in ("macro", "meso", "micro"):
        for section_id in inspect_engine._section_ids_for_fidelity(fidelity=fidelity, target_kind="structure"):
            section_rows[section_id] = {
                "section_id": section_id,
                "extensions": {"cost_units": 1},
            }
    desired_fidelity = "micro"
    achieved, _, _, _, inspection_request, inspection_allocation, _ = inspect_engine._resolve_fidelity(
        desired_fidelity=desired_fidelity,
        target_kind="structure",
        max_cost_units=2,
        section_rows=section_rows,
        micro_allowed=True,
        micro_available=True,
        strict_budget=False,
        requester_subject_id="subject.inspect",
        tick=0,
        server_profile_id="server.profile.inspect",
        fidelity_policy_id=DEFAULT_FIDELITY_POLICY_ID,
    )
    direct_inspection = arbitrate_fidelity_requests(
        fidelity_requests=[dict(inspection_request)],
        rs5_budget_state={
            "tick": 0,
            "envelope_id": "budget.inspect",
            "fidelity_policy_id": DEFAULT_FIDELITY_POLICY_ID,
            "max_cost_units_per_tick": 2,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.inspect"],
        },
        server_profile={"server_profile_id": "server.profile.inspect"},
        fidelity_policy={"policy_id": DEFAULT_FIDELITY_POLICY_ID},
    )
    direct_inspection_allocations = [
        dict(row) for row in list(direct_inspection.get("fidelity_allocations") or []) if isinstance(row, dict)
    ]
    if not direct_inspection_allocations:
        return {"status": "fail", "message": "direct MAT-9 fidelity arbitration returned no allocations"}
    direct_fidelity = str(direct_inspection_allocations[0].get("resolved_level", "")).strip()
    if achieved != direct_fidelity:
        return {"status": "fail", "message": "MAT-9 fidelity resolution drifted from direct fidelity engine result"}
    if str(inspection_allocation.get("resolved_level", "")).strip() != direct_fidelity:
        return {"status": "fail", "message": "MAT-9 fidelity allocation row diverged from direct arbitration"}

    # MAT-7 equivalence: materialization fidelity allocation must match direct fidelity arbitration.
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
    authority = {
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
        authority_context=dict(authority),
        policy_context={"server_profile_id": "server.profile.private"},
    )
    mat_request = dict(materialized.get("fidelity_request") or {})
    mat_allocation = dict(materialized.get("fidelity_allocation") or {})
    mat_arbitration = dict(materialized.get("fidelity_arbitration") or {})
    direct_materialization = arbitrate_fidelity_requests(
        fidelity_requests=[dict(mat_request)],
        rs5_budget_state={
            "tick": 9,
            "envelope_id": str(mat_arbitration.get("envelope_id", "budget.unknown")),
            "fidelity_policy_id": str(mat_arbitration.get("policy_id", DEFAULT_FIDELITY_POLICY_ID)),
            "max_cost_units_per_tick": 2,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.materialize"],
        },
        server_profile={"server_profile_id": "server.profile.private"},
        fidelity_policy={"policy_id": str(mat_arbitration.get("policy_id", DEFAULT_FIDELITY_POLICY_ID))},
    )
    direct_materialization_allocations = [
        dict(row)
        for row in list(direct_materialization.get("fidelity_allocations") or [])
        if isinstance(row, dict)
    ]
    if not direct_materialization_allocations:
        return {"status": "fail", "message": "direct MAT-7 fidelity arbitration returned no allocations"}
    direct_mat_allocation = direct_materialization_allocations[0]
    if int(max(0, int(mat_allocation.get("cost_allocated", 0) or 0))) != int(max(0, int(direct_mat_allocation.get("cost_allocated", 0) or 0))):
        return {"status": "fail", "message": "MAT-7 allocated cost diverged from direct fidelity arbitration"}
    if str(mat_allocation.get("resolved_level", "")).strip() != str(direct_mat_allocation.get("resolved_level", "")).strip():
        return {"status": "fail", "message": "MAT-7 resolved fidelity diverged from direct fidelity arbitration"}
    expected_parts = min(
        int(max(0, int(mat_request.get("cost_estimate", 0) or 0))),
        int(max(0, int(mat_allocation.get("cost_allocated", 0) or 0))),
    )
    if int(len(list(materialized.get("micro_parts") or []))) != int(expected_parts):
        return {"status": "fail", "message": "MAT-7 micro part truncation diverged from fidelity allocation budget"}

    # MAT-8 equivalence: reenactment artifact fidelity allocation must align with direct fidelity arbitration.
    artifact_row, _timeline = build_reenactment_artifact(
        request_row={
            "schema_version": "1.0.0",
            "request_id": "reenactment.request.alpha",
            "target_id": "manifest.alpha",
            "tick_range": {"start_tick": 0, "end_tick": 4},
            "desired_fidelity": "micro",
            "max_cost_units": 4,
            "requester_subject_id": "subject.reenact",
            "created_tick": 4,
            "extensions": {},
        },
        event_stream_row={
            "stream_hash": "stream.hash.alpha",
            "event_ids": ["event.alpha.1", "event.alpha.2"],
            "event_rows": [
                {"event_id": "event.alpha.1", "tick": 1, "event_type_id": "event.test"},
                {"event_id": "event.alpha.2", "tick": 2, "event_type_id": "event.test"},
            ],
        },
        commitment_rows=[],
        batch_lineage_rows=[{"batch_id": "batch.alpha"}],
        max_cost_units=4,
        allow_micro_detail=True,
        fidelity_policy_id=DEFAULT_FIDELITY_POLICY_ID,
        server_profile_id="server.profile.private",
        envelope_id="budget.reenactment",
    )
    reenactment_ext = dict(artifact_row.get("extensions") or {})
    reenactment_request = dict(reenactment_ext.get("fidelity_request") or {})
    reenactment_allocation = dict(reenactment_ext.get("fidelity_allocation") or {})
    if not reenactment_request or not reenactment_allocation:
        return {"status": "fail", "message": "MAT-8 artifact missing embedded fidelity request/allocation"}
    direct_reenactment = arbitrate_fidelity_requests(
        fidelity_requests=[dict(reenactment_request)],
        rs5_budget_state={
            "tick": 4,
            "envelope_id": "budget.reenactment",
            "fidelity_policy_id": DEFAULT_FIDELITY_POLICY_ID,
            "max_cost_units_per_tick": 4,
            "runtime_budget_state": {},
            "fairness_state": {},
            "connected_subject_ids": ["subject.reenact"],
        },
        server_profile={"server_profile_id": "server.profile.private"},
        fidelity_policy={"policy_id": DEFAULT_FIDELITY_POLICY_ID},
    )
    direct_reenactment_allocations = [
        dict(row) for row in list(direct_reenactment.get("fidelity_allocations") or []) if isinstance(row, dict)
    ]
    if not direct_reenactment_allocations:
        return {"status": "fail", "message": "direct MAT-8 fidelity arbitration returned no allocations"}
    direct_reenactment_allocation = direct_reenactment_allocations[0]
    if str(reenactment_allocation.get("resolved_level", "")).strip() != str(direct_reenactment_allocation.get("resolved_level", "")).strip():
        return {"status": "fail", "message": "MAT-8 resolved fidelity diverged from direct fidelity arbitration"}
    if str(artifact_row.get("fidelity_achieved", "")).strip() != str(reenactment_allocation.get("resolved_level", "")).strip():
        return {"status": "fail", "message": "MAT-8 artifact fidelity_achieved is not aligned to fidelity allocation"}

    return {"status": "pass", "message": "domain migration fidelity equivalence checks passed"}
