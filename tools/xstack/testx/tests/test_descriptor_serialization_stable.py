"""FAST test: CAP-NEG-1 descriptor serialization is stable for the same product/build."""

from __future__ import annotations


TEST_ID = "test_descriptor_serialization_stable"
TEST_TAGS = ["fast", "compat", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg1_testlib import emit_descriptor
    from src.compat import descriptor_json_text

    first = emit_descriptor(repo_root, "client")
    second = emit_descriptor(repo_root, "client")
    if descriptor_json_text(first) != descriptor_json_text(second):
        return {"status": "fail", "message": "descriptor JSON drifted across repeated emissions"}
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "descriptor fingerprint drifted across repeated emissions"}
    return {"status": "pass", "message": "descriptor serialization is stable for the same product/build"}
