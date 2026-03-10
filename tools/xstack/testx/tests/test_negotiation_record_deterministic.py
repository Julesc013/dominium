"""FAST test: CAP-NEG-2 negotiation records are stable for identical inputs."""

from __future__ import annotations


TEST_ID = "test_negotiation_record_deterministic"
TEST_TAGS = ["fast", "compat", "cap_neg"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg_testlib import build_default_pair, negotiate

    client, server = build_default_pair(repo_root)
    first = negotiate(repo_root, client, server)
    second = negotiate(repo_root, client, server)
    first_record = dict(first.get("negotiation_record") or {})
    second_record = dict(second.get("negotiation_record") or {})
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "negotiation did not complete for deterministic record check"}
    if first_record != second_record:
        return {"status": "fail", "message": "negotiation record drifted across repeated runs"}
    return {"status": "pass", "message": "negotiation record is deterministic"}
