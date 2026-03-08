"""FAST test: GEO-5 lens requests apply diegetic redaction and quantization rules."""

from __future__ import annotations

import sys


TEST_ID = "test_lens_redaction_policy_applied"
TEST_TAGS = ["fast", "geo", "lens", "epistemics"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.geo import (
        build_lens_request,
        build_position_ref,
        build_projected_view_artifact,
        build_projection_request,
        project_view_cells,
    )

    origin = build_position_ref(
        object_id="object.camera.geo5.redaction",
        frame_id="frame.surface_local",
        local_position=[0, 0, 0],
        extensions={"source": "GEO5-9"},
    )
    projection_request = build_projection_request(
        request_id="projection_request.geo5.redaction",
        projection_profile_id="geo.projection.ortho_2d",
        origin_position_ref=origin,
        extent_spec={"radius_cells": 1, "axis_order": ["x", "y"]},
        resolution_spec={"width": 3, "height": 3},
        extensions={
            "view_type_id": "view.map_ortho",
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
        lens_request_id="lens_request.geo5.redaction",
        lens_profile_id="lens.diegetic.sensor",
        included_layers=[
            "layer.temperature",
            "layer.terrain_stub",
            "layer.infrastructure_stub",
            "layer.entity_markers_stub",
        ],
        extensions={"quantization_step": 10},
    )
    artifact = build_projected_view_artifact(
        projection_result=projection_result,
        lens_request=lens_request,
        perceived_model={
            "lens_id": "lens.diegetic.sensor",
            "metadata": {"lens_type": "diegetic", "epistemic_policy_id": "epistemic.local_map"},
            "channels": [],
            "truth_overlay": {"state_hash_anchor": "truth.anchor.geo5.redaction"},
        },
        layer_source_payloads={
            "layer.temperature": {
                "field_id": "field.temperature",
                "field_layer_rows": [
                    {
                        "field_id": "field.temperature",
                        "field_type_id": "field.temperature",
                        "spatial_scope_id": "scope.geo5.redaction",
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
            },
            "layer.terrain_stub": {
                "source_kind": "terrain",
                "entries": [{"cell_key": "terrain.cell.ignored", "terrain_class": "ridge"}],
            },
            "layer.infrastructure_stub": {
                "source_kind": "infrastructure",
                "required_channels": ["ch.diegetic.infra"],
                "rows": [{"geo_cell_key": center_cell_key, "marker": "relay"}],
            },
            "layer.entity_markers_stub": {
                "source_kind": "entities",
                "required_entitlements": ["entitlement.inspect"],
                "rows": [{"geo_cell_key": center_cell_key, "entity_id": "entity.geo5"}],
            },
        },
        authority_context={"entitlements": []},
        truth_hash_anchor="truth.anchor.geo5.redaction",
    )
    center_layers = dict((list(artifact.get("rendered_cells") or []))[4].get("layers") or {})
    temperature = dict(center_layers.get("layer.temperature") or {})
    terrain = dict(center_layers.get("layer.terrain_stub") or {})
    infrastructure = dict(center_layers.get("layer.infrastructure_stub") or {})
    entities = dict(center_layers.get("layer.entity_markers_stub") or {})
    if temperature.get("state") != "visible" or int(temperature.get("value", -1)) != 30 or not bool(temperature.get("quantized")):
        return {"status": "fail", "message": "diegetic temperature layer was not quantized deterministically"}
    if terrain.get("hidden_reason") != "map_instrument_required":
        return {"status": "fail", "message": "terrain layer did not require diegetic map instrument"}
    if infrastructure.get("hidden_reason") != "channel_required":
        return {"status": "fail", "message": "infrastructure layer did not enforce channel gating"}
    if entities.get("hidden_reason") != "entitlement_required":
        return {"status": "fail", "message": "entity marker layer did not enforce entitlement gating"}
    return {"status": "pass", "message": "GEO-5 lens redaction and quantization applied deterministically"}
