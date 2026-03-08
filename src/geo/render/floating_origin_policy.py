"""Deterministic GEO-2 floating-origin policy for render-only rebasing."""

from __future__ import annotations

from typing import List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.geo.frame.frame_engine import (
    REFUSAL_GEO_FRAME_INVALID,
    REFUSAL_GEO_POSITION_INVALID,
    _as_int,
    _as_map,
    _normalize_vector,
    frame_graph_hash,
    normalize_position_ref,
    position_ref_hash,
    position_to_frame,
)


REFUSAL_GEO_RENDER_REBASE_INVALID = "refusal.geo.render_rebase_invalid"
REFUSAL_GEO_RENDER_TRUTH_MUTATION = "refusal.geo.render_truth_mutation"


def _refusal(*, refusal_code: str, message: str, details: Mapping[str, object] | None = None) -> dict:
    payload = {
        "result": "refused",
        "refusal_code": str(refusal_code),
        "message": str(message),
        "details": _as_map(details),
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _snap_offset(coords: List[int], quantum_mm: int) -> List[int]:
    quantum = max(1, int(_as_int(quantum_mm, 1000), 1000))
    return [int((int(value) // quantum) * quantum) for value in coords]


def choose_floating_origin_offset(
    camera_position_ref: Mapping[str, object] | None,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    target_frame_id: str = "",
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    rebase_quantum_mm: int = 1000,
) -> dict:
    camera_row = normalize_position_ref(
        camera_position_ref,
        frame_nodes=frame_nodes,
        topology_registry_payload=topology_registry_payload,
    )
    if camera_row is None:
        return _refusal(
            refusal_code=REFUSAL_GEO_POSITION_INVALID,
            message="camera_position_ref is invalid",
        )
    target_token = str(target_frame_id or "").strip() or str(camera_row.get("frame_id", "")).strip()
    version = str(graph_version or "").strip() or frame_graph_hash(
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        topology_registry_payload=topology_registry_payload,
    )
    camera_in_target = position_to_frame(
        camera_row,
        target_token,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=version,
        topology_registry_payload=topology_registry_payload,
    )
    if str(camera_in_target.get("result", "")) != "complete":
        return camera_in_target
    local_position = list((_as_map(camera_in_target.get("target_position_ref")).get("local_position") or []))
    offset = _snap_offset(_normalize_vector(local_position, max(1, len(local_position))), int(rebase_quantum_mm))
    payload = {
        "result": "complete",
        "graph_version": version,
        "target_frame_id": target_token,
        "rebase_quantum_mm": int(max(1, int(_as_int(rebase_quantum_mm, 1000), 1000))),
        "camera_position_ref": _as_map(camera_in_target.get("target_position_ref")),
        "rebase_offset": offset,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def apply_floating_origin(
    position_ref: Mapping[str, object] | None,
    camera_position_ref: Mapping[str, object] | None,
    *,
    frame_nodes: object,
    frame_transform_rows: object,
    target_frame_id: str = "",
    graph_version: str = "",
    topology_registry_payload: Mapping[str, object] | None = None,
    rebase_quantum_mm: int = 1000,
) -> dict:
    original_position_hash = position_ref_hash(position_ref)
    original_camera_hash = position_ref_hash(camera_position_ref)

    source_row = normalize_position_ref(
        position_ref,
        frame_nodes=frame_nodes,
        topology_registry_payload=topology_registry_payload,
    )
    camera_row = normalize_position_ref(
        camera_position_ref,
        frame_nodes=frame_nodes,
        topology_registry_payload=topology_registry_payload,
    )
    if source_row is None or camera_row is None:
        return _refusal(
            refusal_code=REFUSAL_GEO_POSITION_INVALID,
            message="position_ref or camera_position_ref is invalid",
        )

    target_token = str(target_frame_id or "").strip() or str(camera_row.get("frame_id", "")).strip()
    offset_payload = choose_floating_origin_offset(
        camera_row,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        target_frame_id=target_token,
        graph_version=graph_version,
        topology_registry_payload=topology_registry_payload,
        rebase_quantum_mm=rebase_quantum_mm,
    )
    if str(offset_payload.get("result", "")) != "complete":
        return offset_payload

    converted = position_to_frame(
        source_row,
        target_token,
        frame_nodes=frame_nodes,
        frame_transform_rows=frame_transform_rows,
        graph_version=str(offset_payload.get("graph_version", "")),
        topology_registry_payload=topology_registry_payload,
    )
    if str(converted.get("result", "")) != "complete":
        return converted

    camera_in_target = _as_map(offset_payload.get("camera_position_ref"))
    object_in_target = _as_map(converted.get("target_position_ref"))
    object_coords = _normalize_vector(object_in_target.get("local_position"), max(1, len(list(object_in_target.get("local_position") or []))))
    camera_coords = _normalize_vector(camera_in_target.get("local_position"), max(1, len(list(camera_in_target.get("local_position") or []))))
    rebase_offset = _normalize_vector(offset_payload.get("rebase_offset"), max(len(object_coords), len(camera_coords), 1))

    rebased_coords = [int(object_coords[idx]) - int(rebase_offset[idx]) for idx in range(len(rebase_offset))]
    camera_relative_coords = [int(object_coords[idx]) - int(camera_coords[idx]) for idx in range(len(camera_coords))]

    if position_ref_hash(position_ref) != original_position_hash or position_ref_hash(camera_position_ref) != original_camera_hash:
        return _refusal(
            refusal_code=REFUSAL_GEO_RENDER_TRUTH_MUTATION,
            message="render rebasing mutated truth position input",
            details={"target_frame_id": target_token},
        )

    payload = {
        "result": "complete",
        "graph_version": str(offset_payload.get("graph_version", "")),
        "target_frame_id": target_token,
        "rebase_quantum_mm": int(offset_payload.get("rebase_quantum_mm", 1000) or 1000),
        "rebase_offset": list(rebase_offset),
        "object_position_ref": object_in_target,
        "camera_position_ref": camera_in_target,
        "rebased_local_position": list(rebased_coords),
        "camera_relative_position": list(camera_relative_coords),
        "render_only": True,
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


__all__ = [
    "REFUSAL_GEO_RENDER_REBASE_INVALID",
    "REFUSAL_GEO_RENDER_TRUTH_MUTATION",
    "apply_floating_origin",
    "choose_floating_origin_offset",
]
