#!/usr/bin/env python3
"""Verify GEO-2 frame graph and position transforms are stable across replay."""

from __future__ import annotations

import argparse
import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.geo import (  # noqa: E402
    build_position_ref,
    frame_get_transform,
    frame_graph_hash,
    position_distance,
    position_ref_hash,
    position_to_frame,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_FRAME_NODES = [
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
        "extensions": {"source": "GEO2-6"},
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
        "extensions": {"source": "GEO2-6"},
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
        "extensions": {"source": "GEO2-6"},
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
        "extensions": {"source": "GEO2-6"},
    },
]

_FRAME_TRANSFORMS = [
    {
        "from_frame_id": "frame.system_root",
        "to_frame_id": "frame.galaxy_root",
        "transform_kind": "translate",
        "parameters": {"translation": [4_000_000_000, -2_000_000_000, 500_000_000]},
        "extensions": {"source": "GEO2-6"},
    },
    {
        "from_frame_id": "frame.planet_root",
        "to_frame_id": "frame.system_root",
        "transform_kind": "translate",
        "parameters": {"translation": [1_200_000, -800_000, 250_000]},
        "extensions": {"source": "GEO2-6"},
    },
    {
        "from_frame_id": "frame.surface_local",
        "to_frame_id": "frame.planet_root",
        "transform_kind": "translate",
        "parameters": {"translation": [1500, -3000, 4500]},
        "extensions": {"source": "GEO2-6"},
    },
]

_POSITIONS = [
    build_position_ref(
        object_id="object.camera",
        frame_id="frame.surface_local",
        local_position=[123, -456, 789],
        extensions={"source": "GEO2-6"},
    ),
    build_position_ref(
        object_id="object.poi",
        frame_id="frame.planet_root",
        local_position=[5_000, 2_000, -7_000],
        extensions={"source": "GEO2-6"},
    ),
]


def _run_once() -> dict:
    graph_hash = frame_graph_hash(
        frame_nodes=_FRAME_NODES,
        frame_transform_rows=_FRAME_TRANSFORMS,
    )
    transform_payload = frame_get_transform(
        "frame.surface_local",
        "frame.galaxy_root",
        frame_nodes=_FRAME_NODES,
        frame_transform_rows=_FRAME_TRANSFORMS,
        graph_version=graph_hash,
    )
    converted_payload = position_to_frame(
        _POSITIONS[0],
        "frame.galaxy_root",
        frame_nodes=_FRAME_NODES,
        frame_transform_rows=_FRAME_TRANSFORMS,
        graph_version=graph_hash,
    )
    distance_payload = position_distance(
        _POSITIONS[0],
        _POSITIONS[1],
        frame_nodes=_FRAME_NODES,
        frame_transform_rows=_FRAME_TRANSFORMS,
        graph_version=graph_hash,
    )
    position_hash_chain = canonical_sha256([position_ref_hash(row) for row in _POSITIONS])
    return {
        "frame_graph_hash_chain": graph_hash,
        "position_ref_hash_chain": position_hash_chain,
        "transform_payload": transform_payload,
        "converted_payload": converted_payload,
        "distance_payload": distance_payload,
    }


def verify_frame_window() -> dict:
    first = _run_once()
    second = _run_once()
    stable = first == second
    report = {
        "result": "complete" if stable else "violation",
        "frame_graph_hash_chain": str(first.get("frame_graph_hash_chain", "")),
        "position_ref_hash_chain": str(first.get("position_ref_hash_chain", "")),
        "observed": first,
        "stable_across_repeated_runs": bool(stable),
        "deterministic_fingerprint": "",
    }
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify GEO-2 frame transform replay stability.")
    parser.add_argument("--output-path", default="")
    args = parser.parse_args()

    report = verify_frame_window()
    output_path = str(args.output_path or "").strip()
    if output_path:
        abs_path = os.path.normpath(os.path.abspath(output_path))
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")) == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
