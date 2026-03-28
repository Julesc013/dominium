"""Shared GEO-2 frame graph fixtures for TestX."""

from __future__ import annotations

from geo import build_position_ref


def baseline_frame_nodes() -> list[dict]:
    return [
        {
            "frame_id": "frame.galaxy_root",
            "parent_frame_id": None,
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "chart_id": "chart.global.r3",
            "anchor_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global.r3",
                "index_tuple": [0, 0, 0],
                "refinement_level": 0,
            },
            "scale_class_id": "galaxy",
            "extensions": {"source": "GEO2-8"},
        },
        {
            "frame_id": "frame.system_root",
            "parent_frame_id": "frame.galaxy_root",
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "chart_id": "chart.global.r3",
            "anchor_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global.r3",
                "index_tuple": [100, -25, 4],
                "refinement_level": 1,
            },
            "scale_class_id": "system",
            "extensions": {"source": "GEO2-8"},
        },
        {
            "frame_id": "frame.planet_root",
            "parent_frame_id": "frame.system_root",
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "chart_id": "chart.global.r3",
            "anchor_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global.r3",
                "index_tuple": [7, 3, 1],
                "refinement_level": 2,
            },
            "scale_class_id": "planet",
            "extensions": {"source": "GEO2-8"},
        },
        {
            "frame_id": "frame.surface_local",
            "parent_frame_id": "frame.planet_root",
            "topology_profile_id": "geo.topology.r3_infinite",
            "metric_profile_id": "geo.metric.euclidean",
            "chart_id": "chart.global.r3",
            "anchor_cell_key": {
                "partition_profile_id": "geo.partition.grid_zd",
                "topology_profile_id": "geo.topology.r3_infinite",
                "chart_id": "chart.global.r3",
                "index_tuple": [0, 0, 0],
                "refinement_level": 3,
            },
            "scale_class_id": "local",
            "extensions": {"source": "GEO2-8"},
        },
    ]


def baseline_frame_transforms() -> list[dict]:
    return [
        {
            "from_frame_id": "frame.system_root",
            "to_frame_id": "frame.galaxy_root",
            "transform_kind": "translate",
            "parameters": {"translation": [4_000_000_000, -2_000_000_000, 500_000_000]},
            "extensions": {"source": "GEO2-8"},
        },
        {
            "from_frame_id": "frame.planet_root",
            "to_frame_id": "frame.system_root",
            "transform_kind": "translate",
            "parameters": {"translation": [1_200_000, -800_000, 250_000]},
            "extensions": {"source": "GEO2-8"},
        },
        {
            "from_frame_id": "frame.surface_local",
            "to_frame_id": "frame.planet_root",
            "transform_kind": "translate",
            "parameters": {"translation": [1500, -3000, 4500]},
            "extensions": {"source": "GEO2-8"},
        },
    ]


def large_scale_frame_transforms() -> list[dict]:
    return [
        {
            "from_frame_id": "frame.system_root",
            "to_frame_id": "frame.galaxy_root",
            "transform_kind": "translate",
            "parameters": {"translation": [9_000_000_000_000_000, -7_000_000_000_000_000, 1_000_000_000_000]},
            "extensions": {"source": "GEO2-8"},
        },
        {
            "from_frame_id": "frame.planet_root",
            "to_frame_id": "frame.system_root",
            "transform_kind": "translate",
            "parameters": {"translation": [123_456_789_000, -987_654_321_000, 456_789_000]},
            "extensions": {"source": "GEO2-8"},
        },
        {
            "from_frame_id": "frame.surface_local",
            "to_frame_id": "frame.planet_root",
            "transform_kind": "translate",
            "parameters": {"translation": [321, -654, 987]},
            "extensions": {"source": "GEO2-8"},
        },
    ]


def surface_position() -> dict:
    return build_position_ref(
        object_id="object.surface.sample",
        frame_id="frame.surface_local",
        local_position=[123, -456, 789],
        extensions={"source": "GEO2-8"},
    )


def poi_position() -> dict:
    return build_position_ref(
        object_id="object.poi.sample",
        frame_id="frame.planet_root",
        local_position=[5000, 2000, -7000],
        extensions={"source": "GEO2-8"},
    )
