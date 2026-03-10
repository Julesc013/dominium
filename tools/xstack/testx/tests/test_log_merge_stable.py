"""FAST test: APPSHELL-6 aggregated log ordering is deterministic."""

from __future__ import annotations


TEST_ID = "test_log_merge_stable"
TEST_TAGS = ["fast", "appshell", "supervisor", "logging"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import run_probe

    first = run_probe(repo_root, suffix="log_merge_one")
    second = run_probe(repo_root, suffix="log_merge_two")
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor probe failed while checking aggregated log stability"}
    first_ids = [str(dict(row).get("event_id", "")).strip() for row in list(first.get("aggregated_logs") or [])]
    second_ids = [str(dict(row).get("event_id", "")).strip() for row in list(second.get("aggregated_logs") or [])]
    if first_ids != second_ids:
        return {"status": "fail", "message": "aggregated log event ordering drifted across repeated runs"}
    return {"status": "pass", "message": "aggregated supervisor log ordering remains stable"}
