"""FAST test: META-STABILITY-0 validator output is deterministic."""

from __future__ import annotations

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_validator_deterministic_output"
TEST_TAGS = ["fast", "meta", "stability", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.stability_classification_testlib import load_validation_report

    first = load_validation_report(repo_root)
    second = load_validation_report(repo_root)
    if first != second:
        return {"status": "fail", "message": "stability validator output drifted across identical runs"}
    expected = canonical_sha256(dict(first, deterministic_fingerprint=""))
    if str(first.get("deterministic_fingerprint", "")).strip() != expected:
        return {"status": "fail", "message": "stability validator deterministic_fingerprint is incorrect"}
    return {"status": "pass", "message": "stability validator output is deterministic"}
