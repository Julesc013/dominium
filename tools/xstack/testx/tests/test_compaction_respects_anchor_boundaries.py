"""FAST test: compaction boundaries are anchored to epoch anchors."""

from __future__ import annotations


TEST_ID = "test_compaction_respects_anchor_boundaries"
TEST_TAGS = ["fast", "time", "compaction", "anchor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.time_anchor_testlib import load_compaction_report

    report, error = load_compaction_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    checks = dict(report.get("checks") or {})
    for key in (
        "save_compaction_complete",
        "save_compaction_has_anchor_ids",
        "merged_log_has_anchor_ids",
        "provenance_compaction_complete",
        "provenance_marker_has_anchor_ids",
        "provenance_non_anchor_window_refused",
    ):
        if bool(checks.get(key, False)):
            continue
        return {"status": "fail", "message": "compaction report check '{}' failed".format(key)}
    save_fixture = dict(report.get("save_fixture") or {})
    compaction_result = dict(save_fixture.get("compaction_result") or {})
    merged_ext = dict(save_fixture.get("merged_payload_extensions") or {})
    if str(compaction_result.get("lower_epoch_anchor_id", "")).strip() != str(merged_ext.get("lower_epoch_anchor_id", "")).strip():
        return {"status": "fail", "message": "merged intent log lower anchor id mismatch"}
    if str(compaction_result.get("upper_epoch_anchor_id", "")).strip() != str(merged_ext.get("upper_epoch_anchor_id", "")).strip():
        return {"status": "fail", "message": "merged intent log upper anchor id mismatch"}
    return {"status": "pass", "message": "compaction boundaries respect epoch anchors"}
