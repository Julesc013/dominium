"""FAST test: supervisor log merge ordering is stable by the canonical key."""

from __future__ import annotations


TEST_ID = "test_log_merge_order_stable"
TEST_TAGS = ["fast", "appshell", "supervisor", "logging"]


def _sort_key(row):
    row_map = dict(row or {})
    return (
        str(row_map.get("source_product_id", "")).strip(),
        str(row_map.get("channel_id", "")).strip(),
        int(row_map.get("seq_no", 0) or 0),
        str(row_map.get("endpoint_id", "")).strip(),
        str(row_map.get("event_id", "")).strip(),
    )


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import run_probe

    report = run_probe(repo_root, suffix="supervisor_log_order")
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor probe failed while checking log merge order"}
    rows = [dict(row) for row in list(report.get("aggregated_logs") or [])]
    if rows != sorted(rows, key=_sort_key):
        return {"status": "fail", "message": "supervisor aggregated logs are not sorted by the canonical merge key"}
    return {"status": "pass", "message": "supervisor aggregated log ordering matches the canonical merge key"}
