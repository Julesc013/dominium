"""FAST test: MVP cross-platform bundle hashes stay aligned across operating systems."""

from __future__ import annotations


TEST_ID = "test_bundle_hash_same_across_os"
TEST_TAGS = ["fast", "mvp", "cross-platform", "bundles"]


def run(repo_root: str):
    from tools.mvp.cross_platform_gate_common import build_mvp_cross_platform_baseline
    from tools.xstack.testx.tests.mvp_cross_platform_testlib import first_mismatch, load_baseline, load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    platform_rows = [dict(item) for item in list(report.get("platform_rows") or [])]
    bundle_hashes = {
        str(item.get("platform_id", "")).strip(): str(item.get("bundle_hash_fingerprint", "")).strip() for item in platform_rows
    }
    if len(set(value for value in bundle_hashes.values() if value)) != 1:
        return {"status": "fail", "message": "MVP cross-platform bundle hash fingerprints diverged across operating systems"}
    baseline = load_baseline(repo_root)
    if not baseline:
        return {"status": "fail", "message": "missing MVP cross-platform regression baseline"}
    expected_baseline = build_mvp_cross_platform_baseline(report)
    mismatch = first_mismatch(expected_baseline.get("bundle_hash_fingerprints"), baseline.get("bundle_hash_fingerprints"))
    if mismatch:
        return {"status": "fail", "message": "MVP cross-platform baseline bundle hashes drifted: {}".format(mismatch)}
    return {"status": "pass", "message": "MVP cross-platform bundle hashes stay aligned across operating systems"}
