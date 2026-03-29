from __future__ import annotations

from tools.xstack.testx.tests.xi6_testlib import build_single_engine_findings, committed_single_engine_registry

TEST_ID = "test_single_engine_registry_enforced"
TEST_TAGS = ["fast", "xi6", "architecture"]


def run(repo_root: str):
    payload = committed_single_engine_registry(repo_root)
    if not list(payload.get("engines") or []):
        return {"status": "fail", "message": "single engine registry is empty"}
    findings = build_single_engine_findings(repo_root)
    if findings:
        first = dict(findings[0] or {})
        return {"status": "fail", "message": str(first.get("message", "")).strip() or "single engine registry violation detected"}
    return {"status": "pass", "message": "single engine registry enforces canonical engine ownership"}
