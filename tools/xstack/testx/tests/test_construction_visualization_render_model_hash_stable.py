"""FAST test: construction inspection overlay RenderModel hash is stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.construction_visualization_render_model_hash_stable"
TEST_TAGS = ["fast", "materials", "construction", "render", "determinism"]


def _build_overlay_payload(repo_root: str) -> dict:
    from client.interaction.inspection_overlays import build_inspection_overlays
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context,
        base_state,
        law_profile,
        policy_context,
        with_inventory,
    )

    state = with_inventory(
        with_inventory(
            base_state(),
            node_id="node.alpha",
            material_id="material.wood_basic",
            mass=10_000_000_000,
            batch_id="batch.wood.seed",
        ),
        node_id="node.alpha",
        material_id="material.stone_basic",
        mass=10_000_000_000,
        batch_id="batch.stone.seed",
    )
    law = law_profile(["process.construction_project_create", "process.construction_project_tick"])
    authority = authority_context(["entitlement.control.admin", "session.boot"], privilege_level="operator")
    policy = policy_context()

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.overlay.create",
            "process_id": "process.construction_project_create",
            "inputs": {
                "blueprint_id": "blueprint.house.basic",
                "site_ref": "site.alpha",
                "logistics_node_id": "node.alpha",
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {}

    ticked = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.construction.overlay.tick",
            "process_id": "process.construction_project_tick",
            "inputs": {"max_projects_per_tick": 8},
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(ticked.get("result", "")) != "complete":
        return {}

    project_rows = sorted(
        [dict(row) for row in list(state.get("construction_projects") or []) if isinstance(row, dict)],
        key=lambda row: str(row.get("project_id", "")),
    )
    if not project_rows:
        return {}
    project_row = dict(project_rows[0])
    project_id = str(project_row.get("project_id", ""))
    snapshot = {
        "target_payload": {
            "target_id": project_id,
            "exists": True,
            "collection": "construction_projects",
            "row": project_row,
        }
    }
    overlay_runtime = copy.deepcopy(policy)
    overlay_runtime["repo_root"] = str(repo_root)
    overlay_runtime["construction_projects"] = [dict(row) for row in list(state.get("construction_projects") or []) if isinstance(row, dict)]
    overlay_runtime["construction_steps"] = [dict(row) for row in list(state.get("construction_steps") or []) if isinstance(row, dict)]
    overlay_runtime["construction_commitments"] = [dict(row) for row in list(state.get("construction_commitments") or []) if isinstance(row, dict)]
    overlay_runtime["installed_structure_instances"] = [dict(row) for row in list(state.get("installed_structure_instances") or []) if isinstance(row, dict)]
    overlay_runtime["construction_provenance_events"] = [dict(row) for row in list(state.get("construction_provenance_events") or []) if isinstance(row, dict)]
    overlay = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 2}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id=project_id,
        authority_context={},
        inspection_snapshot=snapshot,
        overlay_runtime=overlay_runtime,
        requested_cost_units=1,
    )
    if str(overlay.get("result", "")) != "complete":
        return {}
    return dict(overlay.get("inspection_overlays") or {})


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.render import build_render_model

    overlay_payload = _build_overlay_payload(repo_root=repo_root)
    if not overlay_payload:
        return {"status": "fail", "message": "failed to build construction inspection overlay payload"}

    perceived = {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.construction",
        "time_state": {"tick": 2},
        "camera_viewpoint": {"view_mode_id": "view.follow.spectator"},
        "interaction": {
            "inspection_overlays": {
                "renderables": list(overlay_payload.get("renderables") or []),
                "materials": list(overlay_payload.get("materials") or []),
            }
        },
        "entities": {"entries": []},
    }

    first = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="e" * 64,
        physics_profile_id="physics.test.construction",
    )
    second = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="e" * 64,
        physics_profile_id="physics.test.construction",
    )
    first_hash = str(first.get("render_model_hash", ""))
    second_hash = str(second.get("render_model_hash", ""))
    if not first_hash or first_hash != second_hash:
        return {"status": "fail", "message": "construction inspection overlay render hash is unstable"}
    return {"status": "pass", "message": "construction inspection overlay render hash stable"}

