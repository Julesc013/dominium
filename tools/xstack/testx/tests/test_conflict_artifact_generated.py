"""FAST test: overlay conflict artifacts are generated and surfaced through explain tooling."""

from __future__ import annotations

import sys


TEST_ID = "test_conflict_artifact_generated"
TEST_TAGS = ["fast", "geo", "overlay", "compat", "explain"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.geo.tool_explain_property_origin import explain_property_origin_report
    from tools.xstack.testx.tests.geo9_testlib import OBJECT_ID_EARTH, overlay_fixture_merge_result

    merge = dict(
        overlay_fixture_merge_result(include_mods=True, overlay_conflict_policy_id="overlay.conflict.last_wins").get(
            "merge_result"
        )
        or {}
    )
    artifacts = list(merge.get("overlay_conflict_artifacts") or [])
    if not artifacts:
        return {"status": "fail", "message": "last_wins merge did not emit conflict artifacts"}
    artifact = dict(artifacts[0])
    if str(artifact.get("object_id", "")).strip() != OBJECT_ID_EARTH:
        return {"status": "fail", "message": "conflict artifact targeted the wrong object"}
    if str(artifact.get("property_path", "")).strip() != "display_name":
        return {"status": "fail", "message": "conflict artifact targeted the wrong property"}
    report = explain_property_origin_report(object_id=OBJECT_ID_EARTH, property_path="display_name", merge_result=merge)
    inner = dict(report.get("report") or {})
    if str(inner.get("conflict_note", "")).strip() != "explain.overlay_conflict":
        return {"status": "fail", "message": "property-origin explain report omitted the overlay conflict note"}
    if int(inner.get("overlay_conflict_count", 0)) < 1:
        return {"status": "fail", "message": "property-origin explain report omitted overlay conflicts"}
    return {"status": "pass", "message": "overlay conflict artifacts are generated and surfaced through explain tooling"}
