"""FAST test: supervisor arg canonicalization remains stable."""

from __future__ import annotations


TEST_ID = "test_args_canonicalization_stable"
TEST_TAGS = ["fast", "appshell", "supervisor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.appshell6_testlib import canonicalize_sample_args

    first = canonicalize_sample_args(repo_root)
    second = canonicalize_sample_args(repo_root)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "supervisor arg canonicalization drifted across repeated calls"}
    if not str(first.get("argv_text_hash", "")).strip() or not str(first.get("args_hash", "")).strip():
        return {"status": "fail", "message": "supervisor arg canonicalization did not emit stable hashes"}
    return {"status": "pass", "message": "supervisor arg canonicalization is stable"}
