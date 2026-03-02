"""FAST test: GuideGeometry inspection overlay metadata/render hash is stable."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.mobility.guide_geometry.render_overlay_hash_stable"
TEST_TAGS = ["fast", "mobility", "geometry", "overlay", "render", "determinism"]


def _snapshot() -> dict:
    return {
        "target_payload": {
            "target_id": "geometry.overlay.alpha",
            "exists": True,
            "collection": "guide_geometries",
            "row": {
                "schema_version": "1.0.0",
                "geometry_id": "geometry.overlay.alpha",
                "geometry_type_id": "geo.corridor2D",
                "parent_spatial_id": "spatial.overlay.alpha",
                "spec_id": "spec.track.standard_gauge.v1",
                "parameters": {
                    "control_points_mm": [
                        {"x": 0, "y": 0, "z": 0},
                        {"x": 4000, "y": 600, "z": 0},
                        {"x": 9000, "y": 1200, "z": 0},
                    ],
                    "width_mm": 3500,
                    "gauge_mm": 1435,
                },
                "bounds": {
                    "min_mm": {"x": 0, "y": 0, "z": 0},
                    "max_mm": {"x": 9000, "y": 1200, "z": 0},
                },
                "junction_refs": ["junction.overlay.alpha"],
                "deterministic_fingerprint": "fixture",
                "extensions": {},
            },
        },
        "summary_sections": {},
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.inspection_overlays import build_inspection_overlays
    from src.client.render import build_render_model
    from tools.xstack.compatx.canonical_json import canonical_sha256

    snapshot = _snapshot()
    overlay_a = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 3}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id="geometry.overlay.alpha",
        authority_context={},
        inspection_snapshot=copy.deepcopy(snapshot),
        overlay_runtime={},
        requested_cost_units=1,
    )
    overlay_b = build_inspection_overlays(
        perceived_model={"time_state": {"tick": 3}, "entities": {"entries": []}, "populations": {"entries": []}},
        target_semantic_id="geometry.overlay.alpha",
        authority_context={},
        inspection_snapshot=copy.deepcopy(snapshot),
        overlay_runtime={},
        requested_cost_units=1,
    )
    if str(overlay_a.get("result", "")) != "complete" or str(overlay_b.get("result", "")) != "complete":
        return {"status": "fail", "message": "GuideGeometry overlay fixture failed"}
    payload_a = dict(overlay_a.get("inspection_overlays") or {})
    payload_b = dict(overlay_b.get("inspection_overlays") or {})
    if payload_a != payload_b:
        return {"status": "fail", "message": "GuideGeometry overlay payload drifted across equivalent invocations"}

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
        return {"status": "fail", "message": "GuideGeometry overlay metadata hash is unstable"}

    perceived = {
        "schema_version": "1.0.0",
        "viewpoint_id": "viewpoint.mob.geometry.overlay",
        "time_state": {"tick": 3},
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
        pack_lock_hash="d" * 64,
        physics_profile_id="physics.null",
    )
    render_b = build_render_model(
        perceived_model=copy.deepcopy(perceived),
        registry_payloads={},
        pack_lock_hash="d" * 64,
        physics_profile_id="physics.null",
    )
    hash_a = str(render_a.get("render_model_hash", "")).strip()
    hash_b = str(render_b.get("render_model_hash", "")).strip()
    if (not hash_a) or hash_a != hash_b:
        return {"status": "fail", "message": "GuideGeometry overlay render hash drifted"}
    return {"status": "pass", "message": "GuideGeometry overlay metadata/render hash stable"}
