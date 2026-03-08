"""FAST test: GEO-9 property origin explain tool returns the correct provenance chain."""

from __future__ import annotations

import sys


TEST_ID = "test_property_origin_tool_correct"
TEST_TAGS = ["fast", "geo", "overlay", "explain"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.geo.tool_explain_property_origin import explain_property_origin_report
    from tools.xstack.testx.tests.geo9_testlib import OBJECT_ID_EARTH

    report = explain_property_origin_report(object_id=OBJECT_ID_EARTH, property_path="display_name")
    if str(report.get("result", "")) != "complete":
        return {"status": "fail", "message": "property origin explain tool did not complete"}
    if str(report.get("explain_contract_id", "")).strip() != "explain.property_origin":
        return {"status": "fail", "message": "property origin explain contract id missing"}
    if str(report.get("overlay_conflict_contract_id", "")).strip() != "explain.overlay_conflict":
        return {"status": "fail", "message": "overlay conflict explain contract id missing"}
    inner = dict(report.get("report") or {})
    if str(inner.get("current_layer_id", "")).strip() != "save.patch":
        return {"status": "fail", "message": "property origin tool did not resolve the save layer as current"}
    prior_chain = list(inner.get("prior_value_chain") or [])
    if not any(str(dict(row).get("layer_id", "")).strip() == "official.reality.earth" for row in prior_chain):
        return {"status": "fail", "message": "property origin chain omitted the official layer"}
    return {"status": "pass", "message": "GEO-9 property origin explain tool returns the correct provenance chain"}
