"""FAST test: `compat-status` exposes negotiated mode and degrade information."""

from __future__ import annotations


TEST_ID = "test_compat_status_command"
TEST_TAGS = ["fast", "appshell", "compat"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell1_testlib import run_wrapper_json

    report, payload = run_wrapper_json(repo_root, "dominium_client", ["compat-status"])
    if int(report.get("returncode", 0)) != 0:
        return {"status": "fail", "message": "compat-status exited non-zero"}
    if str(payload.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "compat-status did not complete"}
    if str(payload.get("compatibility_mode_id", "")).strip() != "compat.full":
        return {"status": "fail", "message": "compat-status returned unexpected compatibility mode"}
    if not isinstance(payload.get("disabled_capabilities"), list):
        return {"status": "fail", "message": "compat-status missing disabled capability list"}
    if not isinstance(payload.get("substituted_capabilities"), list):
        return {"status": "fail", "message": "compat-status missing substituted capability list"}
    if not str(payload.get("negotiation_record_hash", "")).strip():
        return {"status": "fail", "message": "compat-status missing negotiation record hash"}
    return {"status": "pass", "message": "compat-status exposes deterministic negotiation state"}
