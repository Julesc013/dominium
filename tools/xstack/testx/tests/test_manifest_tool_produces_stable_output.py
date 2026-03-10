"""FAST test: CAP-NEG-1 offline descriptor manifest output is stable."""

from __future__ import annotations


TEST_ID = "test_manifest_tool_produces_stable_output"
TEST_TAGS = ["fast", "compat", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg1_testlib import generate_manifest
    from tools.xstack.compatx.canonical_json import canonical_sha256

    first, first_path = generate_manifest(repo_root)
    second, second_path = generate_manifest(repo_root)
    if canonical_sha256(first) != canonical_sha256(second):
        return {"status": "fail", "message": "descriptor manifest fingerprint drifted across repeated runs"}
    first_text = open(first_path, "r", encoding="utf-8").read()
    second_text = open(second_path, "r", encoding="utf-8").read()
    if first_text != second_text:
        return {"status": "fail", "message": "descriptor manifest text drifted across repeated runs"}
    return {"status": "pass", "message": "descriptor manifest output is stable"}
