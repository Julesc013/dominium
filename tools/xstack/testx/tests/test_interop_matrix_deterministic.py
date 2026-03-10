"""FAST test: CAP-NEG-4 interop matrix generation is deterministic."""

from __future__ import annotations


TEST_ID = "test_interop_matrix_deterministic"
TEST_TAGS = ["fast", "compat", "cap_neg", "interop"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg4_testlib import interop_matrix

    first = interop_matrix(repo_root)
    second = interop_matrix(repo_root)
    if str(first.get("deterministic_fingerprint", "")) != str(second.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "interop matrix fingerprint drifted across repeated runs"}
    if int(first.get("scenario_count", 0) or 0) < 10:
        return {"status": "fail", "message": "interop matrix omitted canonical CAP-NEG-4 scenarios"}
    return {"status": "pass", "message": "interop matrix generation is deterministic"}
