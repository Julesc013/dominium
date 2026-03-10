"""FAST test: capability negotiation is deterministic for identical inputs."""

from __future__ import annotations


TEST_ID = "test_negotiation_deterministic"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate

    client, server = build_default_pair(repo_root)
    first = negotiate(repo_root, client, server)
    second = negotiate(repo_root, client, server)
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "deterministic negotiation did not complete"}
    if str(first.get("negotiation_record_hash", "")) != str(second.get("negotiation_record_hash", "")):
        return {"status": "fail", "message": "negotiation hash drifted across repeated runs"}
    return {"status": "pass", "message": "capability negotiation is deterministic"}
