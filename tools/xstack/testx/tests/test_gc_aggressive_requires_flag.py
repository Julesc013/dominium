"""FAST test: gc.aggressive refuses without the explicit destructive flag."""

from __future__ import annotations


TEST_ID = "test_gc_aggressive_requires_flag"
TEST_TAGS = ["fast", "lib", "store", "gc", "safety"]


def run(repo_root: str):
    from tools.xstack.testx.tests.store_gc_testlib import REFUSAL_GC_EXPLICIT_FLAG, gc_aggressive_refusal

    result = gc_aggressive_refusal(repo_root)
    if str(result.get("refusal_code", "")).strip() != REFUSAL_GC_EXPLICIT_FLAG:
        return {"status": "fail", "message": "gc.aggressive did not refuse with the explicit-flag refusal code"}
    return {"status": "pass", "message": "gc.aggressive requires an explicit destructive flag"}
