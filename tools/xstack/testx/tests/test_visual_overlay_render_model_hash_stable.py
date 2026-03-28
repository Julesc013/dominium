"""FAST test: logistics inspection overlay RenderModel hash is stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.materials.visual_overlay_render_model_hash_stable"
TEST_TAGS = ["fast", "materials", "logistics", "render", "determinism"]


def _build_overlay_payload(repo_root: str) -> dict:
    from client.interaction.inspection_overlays import build_inspection_overlays
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.logistics_testlib import (
        authority_context,
        base_state,
        law_profile,
        logistics_graph,
        policy_context,
        with_inventory,
    )

    state = with_inventory(
        base_state(),
        node_id="node.alpha",
        material_id="material.steel_basic",
        mass=1_200,
        batch_id="batch.overlay",
    )
    law = law_profile(["process.manifest_create"])
    authority = authority_context(["entitlement.control.admin"], privilege_level="operator")
    graph = logistics_graph(delay_ticks=2, loss_fraction=0)
    policy = policy_context(graph_rows=[graph], max_compute_units_per_tick=128)

    created = execute_intent(
        state=state,
        intent={
            "intent_id": "intent.logistics.overlay.create",
            "process_id": "process.manifest_create",
            "inputs": {
                "graph_id": "graph.logistics.test",
                "from_node_id": "node.alpha",
                "to_node_id": "node.beta",
                "batch_id": "batch.overlay",
                "material_id": "material.steel_basic",
                "quantity_mass": 300,
                "earliest_depart_tick": 0,
            },
        },
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )
    if str(created.get("result", "")) != "complete":
        return {}

    manifests = sorted(
        (dict(row) for row in list(state.get("logistics_manifests") or []) if isinstance(row, dict)),
        key=lambda row: str(row.get("manifest_id", "")),
    )
    if not manifests:
        return {}
    manifest_row = dict(manifests[0])
    manifest_id = str(manifest_row.get("manifest_id", ""))
    snapshot = {
        "target_payload": {
            "target_id": manifest_id,
            "exists": True,
            "collection": "logistics_manifests",
            "row": manifest_row,
        }
    }
    overlay_runtime = copy.deepcopy(policy)
    overlay_runtime["repo_root"] = str(repo_root)
    overlay = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 9}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id=manifest_id,
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
        return {"status": "fail", "message": "failed to build logistics inspection overlay payload"}

    perceived = {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.logistics",
        "time_state": {"tick": 9},
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
        pack_lock_hash="f" * 64,
        physics_profile_id="physics.test.logistics",
    )
    second = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="f" * 64,
        physics_profile_id="physics.test.logistics",
    )
    first_hash = str(first.get("render_model_hash", ""))
    second_hash = str(second.get("render_model_hash", ""))
    if not first_hash or first_hash != second_hash:
        return {"status": "fail", "message": "logistics inspection overlay render hash is unstable"}
    return {"status": "pass", "message": "logistics inspection overlay render hash stable"}
