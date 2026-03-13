"""FAST test: DIST-2 verifier report ordering is deterministic."""

from __future__ import annotations


TEST_ID = "test_verify_outputs_deterministic_order"
TEST_TAGS = ["fast", "dist", "release", "determinism"]


def run(repo_root: str):
    from tools.dist.dist_verify_common import build_distribution_verify_report
    from tools.xstack.testx.tests.dist2_testlib import bundle_root

    root = bundle_root(repo_root)
    first = build_distribution_verify_report(root, platform_tag="win64", repo_root=repo_root)
    second = build_distribution_verify_report(root, platform_tag="win64", repo_root=repo_root)
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "DIST-2 report fingerprint drifted across repeated verification"}
    if list((first.get("mode_selection_sanity") or {}).get("rows") or []) != list((second.get("mode_selection_sanity") or {}).get("rows") or []):
        return {"status": "fail", "message": "DIST-2 mode sanity rows are not deterministically ordered"}
    return {"status": "pass", "message": "DIST-2 verifier output ordering is deterministic"}
