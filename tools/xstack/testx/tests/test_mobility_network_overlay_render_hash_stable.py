"""FAST test: mobility network overlay metadata/render hash remains stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.network.overlay_render_hash_stable"
TEST_TAGS = ["fast", "mobility", "network", "overlay", "render", "determinism"]


def _graph_payload() -> dict:
    return {
        "schema_version": "1.0.0",
        "graph_id": "graph.mob.overlay.alpha",
        "node_type_schema_id": "dominium.schema.mobility.mobility_node_payload.v1",
        "edge_type_schema_id": "dominium.schema.mobility.mobility_edge_payload.v1",
        "payload_schema_versions": {
            "dominium.schema.mobility.mobility_node_payload.v1": "1.0.0",
            "dominium.schema.mobility.mobility_edge_payload.v1": "1.0.0",
        },
        "validation_mode": "strict",
        "nodes": [
            {
                "schema_version": "1.0.0",
                "node_id": "node.mob.switch",
                "node_type_id": "node.mobility.switch",
                "payload": {
                    "schema_version": "1.0.0",
                    "node_kind": "switch",
                    "parent_spatial_id": "spatial.mob.overlay",
                    "position_ref": None,
                    "junction_id": "junction.mob.switch",
                    "state_machine_id": "state_machine.mob.switch.overlay",
                    "tags": ["mobility", "switch"],
                    "extensions": {},
                },
                "tags": ["mobility", "switch"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "node_id": "node.mob.a",
                "node_type_id": "node.mobility.endpoint",
                "payload": {"schema_version": "1.0.0", "node_kind": "endpoint", "parent_spatial_id": "spatial.mob.overlay", "position_ref": None, "junction_id": None, "state_machine_id": None, "tags": ["mobility", "endpoint"], "extensions": {}},
                "tags": ["mobility", "endpoint"],
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "node_id": "node.mob.b",
                "node_type_id": "node.mobility.endpoint",
                "payload": {"schema_version": "1.0.0", "node_kind": "endpoint", "parent_spatial_id": "spatial.mob.overlay", "position_ref": None, "junction_id": None, "state_machine_id": None, "tags": ["mobility", "endpoint"], "extensions": {}},
                "tags": ["mobility", "endpoint"],
                "extensions": {},
            },
        ],
        "edges": [
            {
                "schema_version": "1.0.0",
                "edge_id": "edge.mob.switch_a",
                "from_node_id": "node.mob.switch",
                "to_node_id": "node.mob.a",
                "edge_type_id": "edge.mobility.track",
                "capacity": None,
                "delay_ticks": 1,
                "loss_fraction": 0,
                "cost_units": 1,
                "payload": {
                    "schema_version": "1.0.0",
                    "edge_kind": "track",
                    "guide_geometry_id": "geometry.mob.overlay.a",
                    "spec_id": "spec.track.standard_gauge.v1",
                    "capacity_units": None,
                    "max_speed_policy_id": "speed_policy.spec_based",
                    "tags": ["mobility", "track"],
                    "extensions": {},
                },
                "extensions": {},
            },
            {
                "schema_version": "1.0.0",
                "edge_id": "edge.mob.switch_b",
                "from_node_id": "node.mob.switch",
                "to_node_id": "node.mob.b",
                "edge_type_id": "edge.mobility.track",
                "capacity": None,
                "delay_ticks": 1,
                "loss_fraction": 0,
                "cost_units": 1,
                "payload": {
                    "schema_version": "1.0.0",
                    "edge_kind": "track",
                    "guide_geometry_id": "geometry.mob.overlay.b",
                    "spec_id": None,
                    "capacity_units": None,
                    "max_speed_policy_id": "speed_policy.spec_based",
                    "tags": ["mobility", "track"],
                    "extensions": {},
                },
                "extensions": {},
            },
        ],
        "deterministic_routing_policy_id": "route.shortest_delay",
        "extensions": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.interaction.inspection_overlays import build_inspection_overlays
    from client.render import build_render_model
    from tools.xstack.compatx.canonical_json import canonical_sha256

    graph = _graph_payload()
    snapshot = {
        "target_payload": {
            "target_id": "graph.mob.overlay.alpha",
            "exists": True,
            "collection": "network_graphs",
            "row": graph,
        },
        "summary_sections": {
            "section.mob.network_summary": {
                "section_id": "section.mob.network_summary",
                "data": {
                    "graph_id": "graph.mob.overlay.alpha",
                    "node_count": 3,
                    "edge_count": 2,
                    "switch_count": 1,
                    "switch_states": [
                        {
                            "node_id": "node.mob.switch",
                            "machine_id": "state_machine.mob.switch.overlay",
                            "active_edge_id": "edge.mob.switch_a",
                            "outgoing_edge_ids": ["edge.mob.switch_a", "edge.mob.switch_b"],
                        }
                    ],
                    "spec_missing_edge_count": 1,
                },
            },
            "section.mob.route_result": {
                "section_id": "section.mob.route_result",
                "data": {
                    "path_node_ids": ["node.mob.switch", "node.mob.a"],
                    "path_edge_ids": ["edge.mob.switch_a"],
                    "total_cost": 1,
                    "route_policy_id": "route.shortest_delay",
                },
            },
        },
    }

    overlay_a = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 11}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id="graph.mob.overlay.alpha",
        authority_context={},
        inspection_snapshot=copy.deepcopy(snapshot),
        overlay_runtime={"network_graph_rows": [graph]},
        requested_cost_units=1,
    )
    overlay_b = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 11}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id="graph.mob.overlay.alpha",
        authority_context={},
        inspection_snapshot=copy.deepcopy(snapshot),
        overlay_runtime={"network_graph_rows": [graph]},
        requested_cost_units=1,
    )
    if str(overlay_a.get("result", "")) != "complete" or str(overlay_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "mobility network overlay fixture failed"}

    payload_a = dict(overlay_a.get("inspection_overlays") or {})
    payload_b = dict(overlay_b.get("inspection_overlays") or {})
    if payload_a != payload_b:
        return {"status": "fail", "message": "mobility network overlay payload drifted across equivalent invocations"}

    metadata_hash_a = canonical_sha256(
        {
            "mode": str(payload_a.get("mode", "")).strip(),
            "summary": str(payload_a.get("summary", "")).strip(),
            "extensions": dict(payload_a.get("extensions") or {}),
        }
    )
    metadata_hash_b = canonical_sha256(
        {
            "mode": str(payload_b.get("mode", "")).strip(),
            "summary": str(payload_b.get("summary", "")).strip(),
            "extensions": dict(payload_b.get("extensions") or {}),
        }
    )
    if metadata_hash_a != metadata_hash_b:
        return {"status": "fail", "message": "mobility network overlay metadata hash is unstable"}

    perceived = {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.mob.network.overlay",
        "time_state": {"tick": 11},
        "camera_viewpoint": {"view_mode_id": "view.follow.spectator"},
        "interaction": {
            "inspection_overlays": {
                "renderables": list(payload_a.get("renderables") or []),
                "materials": list(payload_a.get("materials") or []),
            }
        },
        "entities": {"entries": []},
    }
    render_a = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="f" * 64,
        physics_profile_id="physics.null",
    )
    render_b = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="f" * 64,
        physics_profile_id="physics.null",
    )
    hash_a = str(render_a.get("render_model_hash", "")).strip()
    hash_b = str(render_b.get("render_model_hash", "")).strip()
    if (not hash_a) or hash_a != hash_b:
        return {"status": "fail", "message": "mobility network overlay render hash drifted"}
    return {"status": "pass", "message": "mobility network overlay metadata/render hash stable"}
