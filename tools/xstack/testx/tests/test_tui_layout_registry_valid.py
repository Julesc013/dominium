"""FAST test: APPSHELL-3 TUI layout registry is valid and internally consistent."""

from __future__ import annotations


TEST_ID = "test_tui_layout_registry_valid"
TEST_TAGS = ["fast", "appshell", "tui"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell3_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from src.appshell.tui import load_tui_layout_registry, load_tui_panel_registry

    panel_payload, panel_error = load_tui_panel_registry(repo_root)
    layout_payload, layout_error = load_tui_layout_registry(repo_root)
    if panel_error or layout_error:
        return {"status": "fail", "message": "tui registries failed to load"}
    panel_ids = {
        str(dict(row).get("panel_id", "")).strip()
        for row in list(dict(panel_payload.get("record") or {}).get("panels") or [])
    }
    layout_rows = list(dict(layout_payload.get("record") or {}).get("layouts") or [])
    required_layouts = {"layout.default", "layout.viewer", "layout.server"}
    discovered_layouts = {str(dict(row).get("layout_id", "")).strip() for row in layout_rows}
    if not required_layouts.issubset(discovered_layouts):
        return {"status": "fail", "message": "required layouts missing from registry"}
    for row in layout_rows:
        for panel_row in list(dict(row).get("panels") or []):
            panel_id = str(dict(panel_row).get("panel_id", "")).strip()
            if panel_id not in panel_ids:
                return {"status": "fail", "message": "layout references unknown panel {}".format(panel_id)}
    return {"status": "pass", "message": "tui layouts are valid and reference known panels"}
