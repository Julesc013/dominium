"""FAST test: GEO-9 overlay layer precedence is respected deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_layer_precedence_respected"
TEST_TAGS = ["fast", "geo", "overlay", "precedence"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.geo import explain_property_origin
    from tools.xstack.testx.tests.geo9_testlib import OBJECT_ID_EARTH, overlay_fixture_merge_result

    fixture = overlay_fixture_merge_result(include_mods=True, include_save=True)
    merge_result = dict(fixture.get("merge_result") or {})
    if str(merge_result.get("result", "")) != "complete":
        return {"status": "fail", "message": "overlay merge did not complete"}
    views = list(merge_result.get("effective_object_views") or [])
    earth = next((dict(row) for row in views if str(dict(row).get("object_id", "")).strip() == OBJECT_ID_EARTH), {})
    display_name = str((dict(earth.get("properties") or {})).get("display_name", "")).strip()
    if display_name != "New Earth":
        return {"status": "fail", "message": "save layer did not win precedence for display_name"}
    origin = explain_property_origin(merge_result=merge_result, object_id=OBJECT_ID_EARTH, property_path="display_name")
    if str(origin.get("result", "")) != "complete":
        return {"status": "fail", "message": "property origin explanation did not complete"}
    if str(origin.get("current_layer_id", "")).strip() != "save.patch":
        return {"status": "fail", "message": "current property origin layer was not save.patch"}
    return {"status": "pass", "message": "GEO-9 overlay precedence resolves base/official/mod/save deterministically"}
