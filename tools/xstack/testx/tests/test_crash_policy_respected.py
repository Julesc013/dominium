"""FAST test: supervisor crash policy backoff and restart behavior are deterministic."""

from __future__ import annotations


TEST_ID = "test_crash_policy_respected"
TEST_TAGS = ["fast", "appshell", "supervisor", "restart_policy"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import build_hardening_report

    report = build_hardening_report(repo_root)
    crash_policy = dict(report.get("crash_policy_probe") or {})
    if str(crash_policy.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor crash policy probe did not complete"}
    lab_policy = dict(crash_policy.get("lab_policy") or {})
    default_policy = dict(crash_policy.get("default_policy") or {})
    if str(lab_policy.get("after_second_refresh_status", "")).strip() != "restart_pending":
        return {"status": "fail", "message": "lab supervisor policy did not apply deterministic restart backoff"}
    if int(lab_policy.get("restart_count", 0) or 0) < 1 or str(lab_policy.get("after_third_refresh_status", "")).strip() != "running":
        return {"status": "fail", "message": "lab supervisor policy did not restart deterministically after backoff"}
    if int(default_policy.get("restart_count", 0) or 0) != 0 or str(default_policy.get("status", "")).strip() == "running":
        return {"status": "fail", "message": "default supervisor policy restarted a child despite max_restarts=0"}
    return {"status": "pass", "message": "supervisor crash policy remains deterministic and policy-bound"}
