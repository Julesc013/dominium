"""FAST test: GEO-5 CCTV views are delivered as delayed SIG-derived artifacts."""

from __future__ import annotations

import sys


TEST_ID = "test_cctv_view_delayed_via_sig"
TEST_TAGS = ["fast", "geo", "lens", "sig"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.geo import (
        build_cctv_view_delivery,
        build_lens_request,
        build_position_ref,
        build_projected_view_artifact,
        build_projection_request,
        project_view_cells,
    )

    origin = build_position_ref(
        object_id="object.camera.geo5.cctv",
        frame_id="frame.surface_local",
        local_position=[0, 0, 0],
        extensions={"source": "GEO5-9"},
    )
    projection_request = build_projection_request(
        request_id="projection_request.geo5.cctv",
        projection_profile_id="geo.projection.ortho_2d",
        origin_position_ref=origin,
        extent_spec={"radius_cells": 1, "axis_order": ["x", "y"]},
        resolution_spec={"width": 3, "height": 3},
        extensions={
            "view_type_id": "view.cctv_stub",
            "topology_profile_id": "geo.topology.r3_infinite",
            "partition_profile_id": "geo.partition.grid_zd",
            "chart_id": "chart.global.r3",
        },
    )
    projection_result = project_view_cells(
        projection_request,
        topology_profile_id="geo.topology.r3_infinite",
        partition_profile_id="geo.partition.grid_zd",
        metric_profile_id="geo.metric.euclidean",
    )
    center_cell_key = dict((list(projection_result.get("projected_cells") or []))[4].get("geo_cell_key") or {})
    lens_request = build_lens_request(
        lens_request_id="lens_request.geo5.cctv",
        lens_profile_id="lens.diegetic.sensor",
        included_layers=["layer.temperature"],
        extensions={"quantization_step": 10},
    )
    artifact = build_projected_view_artifact(
        projection_result=projection_result,
        lens_request=lens_request,
        perceived_model={
            "lens_id": "lens.diegetic.sensor",
            "metadata": {"lens_type": "diegetic", "epistemic_policy_id": "epistemic.cctv"},
            "channels": ["ch.diegetic.map_local"],
            "truth_overlay": {"state_hash_anchor": "truth.anchor.geo5.cctv"},
        },
        layer_source_payloads={
            "layer.temperature": {
                "field_id": "field.temperature",
                "field_layer_rows": [
                    {
                        "field_id": "field.temperature",
                        "field_type_id": "field.temperature",
                        "spatial_scope_id": "scope.geo5.cctv",
                        "resolution_level": "macro",
                        "update_policy_id": "field.static_default",
                        "extensions": {
                            "topology_profile_id": "geo.topology.r3_infinite",
                            "partition_profile_id": "geo.partition.grid_zd",
                            "chart_id": "chart.global.r3",
                        },
                    }
                ],
                "field_cell_rows": [
                    {
                        "field_id": "field.temperature",
                        "cell_id": "cell.0.0.0",
                        "value": 37,
                        "last_updated_tick": 0,
                        "extensions": {"geo_cell_key": center_cell_key},
                    }
                ],
            }
        },
        truth_hash_anchor="truth.anchor.geo5.cctv",
    )
    delivery = build_cctv_view_delivery(
        projected_view_artifact=artifact,
        created_tick=10,
        sender_subject_id="subject.camera.geo5",
        recipient_subject_id="subject.viewer.geo5",
        recipient_address={"address_kind": "subject.direct", "subject_id": "subject.viewer.geo5"},
        base_delay_ticks=3,
    )
    queue_row = dict(delivery.get("message_queue_entry_row") or {})
    receipt_row = dict(delivery.get("knowledge_receipt_row") or {})
    observation = dict(delivery.get("observation_artifact") or {})
    if int(queue_row.get("scheduled_tick", -1)) != 13:
        return {"status": "fail", "message": "CCTV SIG queue delay was not applied deterministically"}
    if int(receipt_row.get("acquired_tick", -1)) != 13:
        return {"status": "fail", "message": "knowledge receipt tick does not match scheduled CCTV delivery"}
    if str(observation.get("payload_type", "")) != "geo.projected_view_artifact":
        return {"status": "fail", "message": "CCTV delivery did not carry projected view artifact payload"}
    return {"status": "pass", "message": "GEO-5 CCTV delivery remains delayed SIG-derived observation"}
