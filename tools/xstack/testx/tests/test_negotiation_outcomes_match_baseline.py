"""FAST test: CAP-NEG-4 stress outcomes match the committed regression lock."""

from __future__ import annotations


TEST_ID = "test_negotiation_outcomes_match_baseline"
TEST_TAGS = ["fast", "compat", "cap_neg", "interop"]


def run(repo_root: str):
    from tools.xstack.testx.tests.cap_neg4_testlib import build_current_baseline, interop_baseline

    expected = interop_baseline(repo_root)
    actual = build_current_baseline(repo_root)
    if actual != expected:
        return {
            "status": "fail",
            "message": "CAP-NEG regression lock drifted (expected {}, got {})".format(
                str(expected.get("deterministic_fingerprint", "")),
                str(actual.get("deterministic_fingerprint", "")),
            ),
        }
    return {"status": "pass", "message": "negotiation outcomes match committed baseline"}
