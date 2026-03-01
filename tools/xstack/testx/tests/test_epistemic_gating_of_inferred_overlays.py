"""FAST test: FORM-1 inferred overlays are epistemic-gated."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.infrastructure.formalization.epistemic_gating_of_inferred_overlays"
TEST_TAGS = ["fast", "infrastructure", "formalization", "epistemic", "overlay"]


def _state():
    return {
        "formalization_states": [
            {
                "schema_version": "1.0.0",
                "formalization_id": "formalization.overlay.alpha",
                "target_kind": "track",
                "target_context_id": "assembly.structure_instance.alpha",
                "state": "inferred",
                "raw_sources": ["part.a", "part.b", "part.c"],
                "inferred_artifact_ref": "inference.candidate_set.alpha",
                "formal_artifact_ref": None,
                "network_graph_ref": None,
                "spec_id": None,
                "created_tick": 10,
                "deterministic_fingerprint": "0" * 64,
                "extensions": {},
            }
        ],
        "formalization_inference_candidates": [],
        "formalization_events": [],
        "network_graphs": [],
        "material_commitments": [],
        "construction_commitments": [],
        "shipment_commitments": [],
        "maintenance_commitments": [],
        "spec_compliance_results": [],
        "reenactment_requests": [],
        "reenactment_artifacts": [],
    }


def _request():
    return {
        "schema_version": "1.0.0",
        "request_id": "inspect.req.formalization.overlay.001",
        "requester_subject_id": "subject.player",
        "target_kind": "formalization",
        "target_id": "formalization.overlay.alpha",
        "desired_fidelity": "meso",
        "tick": 10,
        "max_cost_units": 128,
        "extensions": {},
    }


def _target_payload():
    return {
        "target_id": "formalization.overlay.alpha",
        "exists": True,
        "collection": "formalization_states",
        "row": dict(_state()["formalization_states"][0]),
    }


def _perceived_model():
    return {
        "schema_version": "1.0.0",
        "time_state": {"tick": 10},
        "truth_overlay": {"state_hash_anchor": "a" * 64},
        "entities": {"entries": []},
        "populations": {"entries": []},
    }


def _candidate_row(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.infrastructure.formalization import build_inference_candidate

    return build_inference_candidate(
        formalization_id="formalization.overlay.alpha",
        candidate_kind="corridor",
        geometry_preview_ref="preview.formalization.overlay.alpha",
        confidence_score=920,
        suggested_spec_ids=["spec.track.standard_gauge.v1"],
        extensions={"target_kind": "track", "target_context_id": "assembly.structure_instance.alpha"},
    )


def _snapshot(
    *,
    repo_root: str,
    state: dict,
    visibility_level: str,
    allow_hidden_state: bool,
):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.inspection.inspection_engine import build_inspection_snapshot_artifact

    snapshot, _diag = build_inspection_snapshot_artifact(
        request_row=_request(),
        target_payload=_target_payload(),
        state=state,
        truth_hash_anchor="hash.truth.form1.overlay",
        ledger_hash="hash.ledger.form1.overlay",
        section_registry_payload={},
        policy_context={},
        law_profile={"epistemic_limits": {"allow_hidden_state_access": bool(allow_hidden_state)}},
        authority_context={
            "entitlements": ["entitlement.inspect"],
            "epistemic_scope": {"visibility_level": str(visibility_level)},
        },
        physics_profile_id="physics.test.form1",
        pack_lock_hash="b" * 64,
        cache_policy_id="cache.off",
        strict_budget=False,
    )
    return snapshot


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.inspection_overlays import build_inspection_overlays

    state = _state()
    state["formalization_inference_candidates"] = [_candidate_row(repo_root)]
    perceived = _perceived_model()

    diegetic_snapshot = _snapshot(
        repo_root=repo_root,
        state=copy.deepcopy(state),
        visibility_level="diegetic",
        allow_hidden_state=False,
    )
    lab_snapshot = _snapshot(
        repo_root=repo_root,
        state=copy.deepcopy(state),
        visibility_level="lab",
        allow_hidden_state=True,
    )

    diegetic_overlay = build_inspection_overlays(
        perceived_model=copy.deepcopy(perceived),
        target_semantic_id="formalization.overlay.alpha",
        authority_context={"entitlements": ["entitlement.inspect"]},
        inspection_snapshot=diegetic_snapshot,
        overlay_runtime={},
        requested_cost_units=1,
    )
    lab_overlay = build_inspection_overlays(
        perceived_model=copy.deepcopy(perceived),
        target_semantic_id="formalization.overlay.alpha",
        authority_context={"entitlements": ["entitlement.inspect", "lens.nondiegetic.access"]},
        inspection_snapshot=lab_snapshot,
        overlay_runtime={},
        requested_cost_units=1,
    )
    diegetic_rows = [
        dict(item)
        for item in list((dict(diegetic_overlay.get("inspection_overlays") or {})).get("renderables") or [])
        if isinstance(item, dict)
    ]
    lab_rows = [
        dict(item)
        for item in list((dict(lab_overlay.get("inspection_overlays") or {})).get("renderables") or [])
        if isinstance(item, dict)
    ]
    diegetic_candidates = [
        row
        for row in diegetic_rows
        if str((dict(row.get("extensions") or {})).get("overlay_kind", "")).strip() == "formalization_candidate"
    ]
    lab_candidates = [
        row
        for row in lab_rows
        if str((dict(row.get("extensions") or {})).get("overlay_kind", "")).strip() == "formalization_candidate"
    ]
    if diegetic_candidates:
        return {"status": "fail", "message": "diegetic overlay leaked inferred candidate rows"}
    if not lab_candidates:
        return {"status": "fail", "message": "lab overlay missing inferred candidate rows"}
    return {"status": "pass", "message": "inferred overlay candidate rows are epistemic-gated"}

