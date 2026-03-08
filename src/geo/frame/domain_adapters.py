"""Deterministic GEO-2 domain adapter helpers for frame-based sampling and distance queries."""

from __future__ import annotations

from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.index.geo_index_engine import geo_cell_key_from_position

from .frame_engine import (
    _as_map,
    position_distance,
    position_to_frame,
)


def field_sampling_position(
    position_ref: Mapping[str, object] | None,
    target_frame_id: str,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    converted = position_to_frame(
        position_ref,
        str(target_frame_id or "").strip(),
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(converted.get("result", "")) != "complete":
        return converted
    target_position_ref = _as_map(converted.get("target_position_ref"))
    return {
        "result": "complete",
        "graph_version": str(converted.get("graph_version", "")),
        "target_frame_id": str(target_position_ref.get("frame_id", "")),
        "field_position": {
            "coords": list(target_position_ref.get("local_position") or []),
            "frame_id": str(target_position_ref.get("frame_id", "")),
        },
        "target_position_ref": target_position_ref,
        "deterministic_fingerprint": canonical_sha256(
            {
                "target_position_ref": target_position_ref,
                "graph_version": str(converted.get("graph_version", "")),
            }
        ),
    }


def field_sampling_cell_key(
    position_ref: Mapping[str, object] | None,
    target_frame_id: str,
    partition_profile_id: str,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    partition_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    converted = field_sampling_position(
        position_ref,
        target_frame_id,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(converted.get("result", "")) != "complete":
        return converted
    field_position = _as_map(converted.get("field_position"))
    target_position_ref = _as_map(converted.get("target_position_ref"))
    topology_profile_id = ""
    chart_id = "chart.global"
    for row in list(frame_nodes or []):
        if not isinstance(row, Mapping):
            continue
        if str(row.get("frame_id", "")).strip() != str(target_position_ref.get("frame_id", "")).strip():
            continue
        topology_profile_id = str(row.get("topology_profile_id", "")).strip()
        chart_id = str(row.get("chart_id", "")).strip() or chart_id
        break
    cell_payload = geo_cell_key_from_position(
        {"coords": list(field_position.get("coords") or [])},
        topology_profile_id,
        str(partition_profile_id or "").strip(),
        chart_id,
        topology_registry_payload=topology_registry_payload,
        partition_registry_payload=partition_registry_payload,
    )
    if str(cell_payload.get("result", "")) != "complete":
        return cell_payload
    return {
        "result": "complete",
        "graph_version": str(converted.get("graph_version", "")),
        "target_frame_id": str(target_position_ref.get("frame_id", "")),
        "field_position": field_position,
        "cell_key": _as_map(cell_payload.get("cell_key")),
        "deterministic_fingerprint": canonical_sha256(
            {
                "graph_version": str(converted.get("graph_version", "")),
                "target_frame_id": str(target_position_ref.get("frame_id", "")),
                "field_position": field_position,
                "cell_key": _as_map(cell_payload.get("cell_key")),
            }
        ),
    }


def roi_distance_mm(
    pos_a_ref: Mapping[str, object] | None,
    pos_b_ref: Mapping[str, object] | None,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    metric_registry_payload: Mapping[str, object] | None = None,
) -> dict:
    return position_distance(
        pos_a_ref,
        pos_b_ref,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        metric_registry_payload=metric_registry_payload,
    )


__all__ = [
    "field_sampling_cell_key",
    "field_sampling_position",
    "roi_distance_mm",
]
