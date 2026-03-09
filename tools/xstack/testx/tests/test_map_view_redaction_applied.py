"""FAST test: UX-0 map/minimap views preserve lens redaction and profile gating."""

from __future__ import annotations

import sys


TEST_ID = "test_map_view_redaction_applied"
TEST_TAGS = ["fast", "ux", "viewer", "map", "redaction"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.ux0_testlib import redacted_map_fixture

    fixture = redacted_map_fixture(repo_root)
    view_set = dict(fixture.get("view_set") or {})
    map_view = dict(view_set.get("map_view") or {})
    if str(map_view.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "UX-0 redaction map view did not complete"}
    hidden_reasons = set()
    rendered_cells = list(dict(dict(map_view.get("projected_view_artifact") or {})).get("rendered_cells") or [])
    for row in rendered_cells:
        for layer_value in dict(dict(row).get("layers") or {}).values():
            layer = dict(layer_value or {})
            if str(layer.get("state", "")).strip() == "hidden":
                hidden_reasons.add(str(layer.get("hidden_reason", "")).strip())
    for required_reason in ("channel_required", "entitlement_required", "map_instrument_required"):
        if required_reason not in hidden_reasons:
            return {"status": "fail", "message": "UX-0 redaction map view missing hidden reason '{}'".format(required_reason)}
    if str(dict(map_view.get("display") or {}).get("preferred_presentation", "")).strip() != "ascii":
        return {"status": "fail", "message": "UX-0 CLI/TUI map view should prefer ASCII presentation"}
    return {"status": "pass", "message": "UX-0 map/minimap views preserve lens redaction and profile gating"}
