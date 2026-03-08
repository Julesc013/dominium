"""FAST test: GEO-10 projection views preserve lens redaction on derived artifacts."""

from __future__ import annotations


TEST_ID = "test_projection_view_redaction"
TEST_TAGS = ["fast", "geo", "projection", "lens"]


def run(repo_root: str):
    from tools.xstack.testx.tests.geo10_testlib import geo10_projection_redaction_fixture

    fixture = geo10_projection_redaction_fixture(repo_root)
    view_data = dict(fixture.get("view_data") or {})
    if bool(view_data.get("deferred", False)):
        return {"status": "fail", "message": "redaction fixture unexpectedly deferred derived views"}
    if int(view_data.get("redaction_count", 0)) <= 0:
        return {"status": "fail", "message": "redaction fixture produced no redacted layers"}
    hidden_reasons = set()
    rendered_cells = list((dict(view_data.get("view_artifact") or {})).get("rendered_cells") or [])
    for row in rendered_cells:
        for layer_value in dict(dict(row).get("layers") or {}).values():
            layer_map = dict(layer_value or {})
            if str(layer_map.get("state", "")).strip() == "hidden":
                hidden_reasons.add(str(layer_map.get("hidden_reason", "")).strip())
    for required_reason in ("channel_required", "entitlement_required"):
        if required_reason not in hidden_reasons:
            return {"status": "fail", "message": "projection redaction missing hidden reason '{}'".format(required_reason)}
    return {"status": "pass", "message": "GEO-10 projection views preserve epistemic redaction"}
