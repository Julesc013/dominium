"""STRICT test: manual placement updates are applied via incremental plan artifacts."""

from __future__ import annotations

import copy
import sys
import os
import shutil


TEST_ID = "testx.control.manual_placement_via_plan"
TEST_TAGS = ["strict", "control", "planning", "manual_placement"]


def _reset_control_decisions(repo_root: str) -> None:
    decisions_dir = os.path.join(repo_root, "run_meta", "control_decisions")
    shutil.rmtree(decisions_dir, ignore_errors=True)


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.sessionx import process_runtime
    from tools.xstack.testx.tests.plan_testlib import (
        authority_context,
        base_state,
        custom_plan_create_inputs,
        law_profile,
        policy_context,
    )

    state = base_state()
    law = law_profile()
    auth = authority_context()
    policy = policy_context(repo_root)
    _reset_control_decisions(repo_root)
    created = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.manual.create",
            "process_id": "process.plan_create",
            "inputs": copy.deepcopy(custom_plan_create_inputs()),
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {"status": "fail", "message": "manual precondition plan_create refused"}
    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    if len(plan_rows) != 1:
        return {"status": "fail", "message": "expected one plan artifact for manual placement test"}
    plan_id = str(plan_rows[0].get("plan_id", "")).strip()
    if not plan_id:
        return {"status": "fail", "message": "manual placement plan artifact missing plan_id"}

    update_payload = {
        "change_kind": "manual_placement",
        "add_renderables": [
            {
                "schema_version": "1.0.0",
                "renderable_id": "ghost.track.segment.0001",
                "semantic_id": "plan.segment.0001",
                "primitive_id": "prim.line.debug",
                "transform": {
                    "position_mm": {"x": 0, "y": 0, "z": 0},
                    "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                    "scale_permille": 1000,
                },
                "material_id": "mat.plan.track.0001",
                "layer_tags": ["overlay", "ghost"],
                "label": None,
                "lod_hint": "lod.band.mid",
                "flags": {"selectable": False, "highlighted": False},
                "extensions": {"part_class_id": "part.track.segment"},
            }
        ],
        "add_materials": [
            {
                "schema_version": "1.0.0",
                "material_id": "mat.plan.track.0001",
                "base_color": {"r": 180, "g": 140, "b": 96},
                "roughness": 320,
                "metallic": 0,
                "emission": None,
                "transparency": {"alpha_permille": 650},
                "pattern_id": None,
                "extensions": {"material_id_or_class": "material.steel"},
            }
        ],
        "material_mass_delta": {"material.steel": 1200},
        "part_count_delta": 3,
    }
    updated = process_runtime.execute_intent(
        state=state,
        intent={
            "intent_id": "intent.plan.manual.update",
            "process_id": "process.plan_update_incremental",
            "inputs": {"plan_id": plan_id, "update_payload": update_payload},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(auth),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(updated.get("result", "")) != "complete":
        return {"status": "fail", "message": "process.plan_update_incremental refused"}
    plan_rows = [dict(row) for row in list(state.get("plan_artifacts") or []) if isinstance(row, dict)]
    matched = [row for row in plan_rows if str(row.get("plan_id", "")).strip() == plan_id]
    if not matched:
        return {"status": "fail", "message": "updated plan artifact missing from state"}
    plan_row = dict(matched[0])
    preview = dict(plan_row.get("spatial_preview_data") or {})
    resources = dict(plan_row.get("required_resources_summary") or {})
    if len(list(preview.get("renderables") or [])) < 1:
        return {"status": "fail", "message": "manual placement did not update ghost renderables"}
    if int(resources.get("total_mass_raw", 0) or 0) < 1:
        return {"status": "fail", "message": "manual placement did not update resource summary mass"}
    if str(plan_row.get("status", "")).strip() != "draft":
        return {"status": "fail", "message": "manual incremental update must leave plan in draft state"}
    history = [dict(item) for item in list((dict(plan_row.get("extensions") or {})).get("update_history") or []) if isinstance(item, dict)]
    if not history:
        return {"status": "fail", "message": "manual placement update_history was not recorded"}
    return {"status": "pass", "message": "manual placement routed through incremental plan artifact update"}
