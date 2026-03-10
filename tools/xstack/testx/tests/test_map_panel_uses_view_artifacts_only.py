"""FAST test: APPSHELL-3 map/inspect panels are wired through derived view surfaces."""

from __future__ import annotations


TEST_ID = "test_map_panel_uses_view_artifacts_only"
TEST_TAGS = ["fast", "appshell", "tui", "observer"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell3_testlib import build_surface, tui_source_text

    surface = build_surface(repo_root, product_id="client", layout_id="layout.viewer", backend_override="lite")
    panels = {
        str(dict(row).get("panel_id", "")).strip(): dict(row)
        for row in list(surface.get("panels") or [])
    }
    if "panel.map" not in panels:
        return {"status": "fail", "message": "client viewer layout did not include map panel"}
    if not list(dict(panels["panel.map"]).get("lines") or []):
        return {"status": "fail", "message": "map panel emitted no derived lines"}
    text = tui_source_text(repo_root)
    required_tokens = ("build_map_view_set(", "build_inspection_panel_set(")
    if any(token not in text for token in required_tokens):
        return {"status": "fail", "message": "tui engine lost derived view helper usage"}
    forbidden_tokens = ("TruthModel", "truth_model", "authoritative_state")
    if any(token in text for token in forbidden_tokens):
        return {"status": "fail", "message": "tui engine references direct truth surfaces"}
    return {"status": "pass", "message": "map and inspect panels stay on derived view artifacts"}
