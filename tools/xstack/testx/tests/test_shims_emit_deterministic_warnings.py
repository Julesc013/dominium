"""FAST test: shim deprecation warnings are deterministic."""

from __future__ import annotations


TEST_ID = "test_shims_emit_deterministic_warnings"
TEST_TAGS = ["fast", "warnings", "shims", "determinism"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.repo_layout1_testlib import warning_payload

    first = warning_payload()
    second = warning_payload()
    if first != second:
        return {"status": "fail", "message": "shim warning payloads are not deterministic across identical inputs"}
    fingerprint = str(first.get("deterministic_fingerprint", "")).strip()
    if len(fingerprint) != 64:
        return {"status": "fail", "message": "shim warning payload is missing a canonical fingerprint"}
    return {"status": "pass", "message": "shim deprecation warnings are deterministic"}
