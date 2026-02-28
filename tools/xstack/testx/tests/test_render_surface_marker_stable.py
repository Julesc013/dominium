"""STRICT test: selection overlay surface markers are stable and deterministically ordered."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_render_surface_marker_stable"
TEST_TAGS = ["strict", "interaction", "render", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.client.interaction.interaction_panel import build_selection_overlay
    from tools.xstack.compatx.canonical_json import canonical_sha256

    action_surfaces = [
        {
            "surface_id": "surface.zzz",
            "surface_type_id": "surface.port",
            "local_transform": {
                "position_mm": {"x": 120, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 300,
            },
            "tool_compatible": False,
        },
        {
            "surface_id": "surface.aaa",
            "surface_type_id": "surface.handle",
            "local_transform": {
                "position_mm": {"x": 60, "y": 0, "z": 0},
                "orientation_mdeg": {"yaw": 0, "pitch": 0, "roll": 0},
                "scale_permille": 300,
            },
            "tool_compatible": True,
        },
    ]
    first = build_selection_overlay("assembly.test.epsilon", action_surfaces=copy.deepcopy(action_surfaces))
    second = build_selection_overlay("assembly.test.epsilon", action_surfaces=list(reversed(copy.deepcopy(action_surfaces))))
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "selection overlay hash is unstable across equivalent surface sets"}
    action_rows = list(first.get("action_surfaces") or [])
    if [str((dict(row)).get("surface_id", "")) for row in action_rows] != sorted(
        [str((dict(row)).get("surface_id", "")) for row in action_rows]
    ):
        return {"status": "fail", "message": "action_surfaces payload is not sorted by surface_id"}
    renderables = [
        dict(row)
        for row in list(first.get("renderables") or [])
        if str((dict(row.get("extensions") or {})).get("overlay_kind", "")) == "action_surface_marker"
    ]
    if len(renderables) != 2:
        return {"status": "fail", "message": "expected deterministic marker renderables for each surface"}
    return {"status": "pass", "message": "surface marker overlay deterministic and stable"}

