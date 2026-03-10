"""FAST test: unknown capabilities are ignored deterministically."""

from __future__ import annotations


TEST_ID = "test_unknown_cap_ignored"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate

    client, server = build_default_pair(repo_root)
    client["feature_capabilities"] = list(client.get("feature_capabilities") or []) + ["cap.unknown.future_client"]
    server["feature_capabilities"] = list(server.get("feature_capabilities") or []) + ["cap.unknown.future_server"]
    result = negotiate(repo_root, client, server)
    record = dict(result.get("negotiation_record") or {})
    disabled = list(record.get("disabled_capabilities") or [])
    ignored = [row for row in disabled if str((row or {}).get("reason_code", "")) == "ignored.unknown_capability"]
    if not ignored:
        return {"status": "fail", "message": "unknown capability did not enter deterministic ignore set"}
    return {"status": "pass", "message": "unknown capabilities are ignored deterministically"}
