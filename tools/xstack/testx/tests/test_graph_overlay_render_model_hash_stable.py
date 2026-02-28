"""FAST test: NetworkGraph inspection overlay RenderModel hash is stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.core.graph_overlay_render_model_hash_stable"
TEST_TAGS = ["fast", "core", "graph", "inspection", "render", "determinism"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.core.overlay",
        "node_type_schema_id": "core.node.payload",
        "edge_type_schema_id": "core.edge.payload",
        "payload_schema_versions": {
            "core.node.payload": "1.0.0",
            "core.edge.payload": "1.0.0",
        },
        "validation_mode": "strict",
        "nodes": [
            {"schema_version": "1.0.0", "node_id": "node.a", "node_type_id": "kind.node", "payload_ref": {}, "tags": [], "extensions": {}},
            {"schema_version": "1.0.0", "node_id": "node.b", "node_type_id": "kind.node", "payload_ref": {}, "tags": [], "extensions": {}},
        ],
        "edges": [
            {"schema_version": "1.0.0", "edge_id": "edge.a_b", "from_node_id": "node.a", "to_node_id": "node.b", "edge_type_id": "mode.road", "payload_ref": {}, "capacity": 100, "delay_ticks": 1, "loss_fraction": 0, "cost_units": 1, "extensions": {}},
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.inspection_overlays import build_inspection_overlays
    from src.client.render import build_render_model

    graph = _graph_payload()
    snapshot = {
        "target_payload": {
            "target_id": "graph.core.overlay",
            "exists": True,
            "collection": "network_graphs",
            "row": graph,
            "extensions": {
                "route_result": {
                    "path_node_ids": ["node.a", "node.b"],
                    "path_edge_ids": ["edge.a_b"],
                    "total_cost": 1,
                    "route_policy_id": "route.shortest_delay",
                }
            },
        },
        "summary_sections": {
            "section.networkgraph.route": {
                "section_id": "section.networkgraph.route",
                "data": {
                    "path_node_ids": ["node.a", "node.b"],
                    "path_edge_ids": ["edge.a_b"],
                    "total_cost": 1,
                    "route_policy_id": "route.shortest_delay",
                },
            }
        },
    }
    overlay_result = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 10}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id="graph.core.overlay",
        authority_context={},
        inspection_snapshot=snapshot,
        overlay_runtime={"network_graph_rows": [graph], "repo_root": str(repo_root)},
        requested_cost_units=1,
    )
    if str(overlay_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "failed to build network graph overlay payload"}
    overlay_payload = dict(overlay_result.get("inspection_overlays") or {})
    perceived = {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.test.graph.overlay",
        "time_state": {"tick": 10},
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
        pack_lock_hash="a" * 64,
        physics_profile_id="physics.null",
    )
    second = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="a" * 64,
        physics_profile_id="physics.null",
    )
    first_hash = str(first.get("render_model_hash", ""))
    second_hash = str(second.get("render_model_hash", ""))
    if not first_hash or first_hash != second_hash:
        return {"status": "fail", "message": "network graph overlay render hash is unstable"}
    return {"status": "pass", "message": "network graph overlay render hash stable"}

