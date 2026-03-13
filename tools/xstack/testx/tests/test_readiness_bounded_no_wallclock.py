"""FAST test: supervisor readiness is bounded and free of wall-clock tokens."""

from __future__ import annotations


TEST_ID = "test_readiness_bounded_no_wallclock"
TEST_TAGS = ["fast", "appshell", "supervisor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import build_hardening_report

    report = build_hardening_report(repo_root)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor hardening report did not complete"}
    violations = [
        dict(row)
        for row in list(report.get("violations") or [])
        if str(dict(row).get("code", "")).strip() in {"wallclock_token", "runtime_probe_failed"}
    ]
    if violations:
        return {"status": "fail", "message": "supervisor readiness still exposes wall-clock or runtime probe violations"}
    runtime_probe = dict(report.get("runtime_probe") or {})
    if str(runtime_probe.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "supervisor runtime probe did not complete"}
    return {"status": "pass", "message": "supervisor readiness remains bounded and wallclock-free"}
