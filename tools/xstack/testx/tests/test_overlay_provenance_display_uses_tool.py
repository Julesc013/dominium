"""FAST test: UX-0 overlay provenance panels route through the canonical explain tool."""

from __future__ import annotations

import sys


TEST_ID = "test_overlay_provenance_display_uses_tool"
TEST_TAGS = ["fast", "ux", "viewer", "inspection", "provenance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from client.ui.inspect_panels import build_inspection_panel_set
    from tools.xstack.testx.tests.geo9_testlib import OBJECT_ID_EARTH, overlay_fixture_merge_result

    merge_fixture = overlay_fixture_merge_result(include_mods=True, include_save=True)
    panels = build_inspection_panel_set(
        perceived_model={"time_state": {"tick": 0}},
        target_semantic_id=OBJECT_ID_EARTH,
        inspection_snapshot={
            "target_payload": {
                "target_id": OBJECT_ID_EARTH,
                "exists": True,
                "collection": "entities.entries",
                "row": {"object_id": OBJECT_ID_EARTH},
            }
        },
        property_origin_request={
            "object_id": OBJECT_ID_EARTH,
            "property_path": "display_name",
            "merge_result": merge_fixture["merge_result"],
        },
    )
    used_tool_ids = list(panels.get("used_tool_ids") or [])
    if used_tool_ids != ["tool.geo.explain_property_origin"]:
        return {"status": "fail", "message": "UX-0 provenance panel did not declare the canonical explain tool"}
    provenance_panels = [
        dict(row)
        for row in list(panels.get("panels") or [])
        if str(dict(row).get("panel_kind", "")).strip() == "overlay_provenance"
    ]
    if len(provenance_panels) != 1:
        return {"status": "fail", "message": "UX-0 provenance panel was not materialized"}
    panel = provenance_panels[0]
    if str(dict(panel.get("extensions") or {}).get("tool_id", "")).strip() != "tool.geo.explain_property_origin":
        return {"status": "fail", "message": "UX-0 provenance panel did not expose the canonical explain tool id"}
    tool_result = dict(dict(panel.get("extensions") or {}).get("tool_result") or {})
    if str(tool_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "UX-0 provenance panel did not run the explain tool successfully"}
    if not any(
        str(dict(row).get("key", "")).strip() == "tool_id"
        and str(dict(row).get("value", "")).strip() == "tool.geo.explain_property_origin"
        for row in list(panel.get("rows") or [])
    ):
        return {"status": "fail", "message": "UX-0 provenance panel rows do not surface the explain tool origin"}
    return {"status": "pass", "message": "UX-0 overlay provenance panels use the canonical explain tool"}
