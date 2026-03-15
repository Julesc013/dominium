"""FAST test: observability redaction removes secret-like values from logs."""

from __future__ import annotations


TEST_ID = "test_redaction_applies"
TEST_TAGS = ["fast", "observability", "redaction"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell2_testlib import ensure_repo_on_path

    ensure_repo_on_path(repo_root)
    from src.appshell.logging import build_log_event

    payload = build_log_event(
        product_id="setup",
        build_id="build.test",
        event_index=1,
        category="update",
        severity="info",
        message_key="update.plan.generated",
        params={
            "install_root": "bundle/root",
            "auth_token": "top-secret-token",
            "nested": {"password": "should-not-leak"},
        },
        repo_root=repo_root,
    )
    params = dict(payload.get("params") or {})
    nested = dict(params.get("nested") or {})
    if str(params.get("auth_token", "")) != "[redacted]":
        return {"status": "fail", "message": "top-level secret field was not redacted"}
    if str(nested.get("password", "")) != "[redacted]":
        return {"status": "fail", "message": "nested secret field was not redacted"}
    observability_meta = dict(dict(payload.get("extensions") or {}).get("observability") or {})
    if int(observability_meta.get("redacted_field_count", 0) or 0) < 2:
        return {"status": "fail", "message": "redacted_field_count did not reflect the secret fields"}
    return {"status": "pass", "message": "observability redaction applies deterministically"}
