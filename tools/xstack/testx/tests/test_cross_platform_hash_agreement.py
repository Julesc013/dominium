"""FAST test: MVP cross-platform canonical hashes agree across the platform matrix."""

from __future__ import annotations


TEST_ID = "test_cross_platform_hash_agreement"
TEST_TAGS = ["fast", "mvp", "cross-platform", "hashes"]


def run(repo_root: str):
    from tools.mvp.cross_platform_gate_common import PLATFORM_ORDER
    from tools.xstack.testx.tests.mvp_cross_platform_testlib import load_report

    report, error = load_report(repo_root)
    if error:
        return {"status": "fail", "message": error}
    platform_rows = [dict(item) for item in list(report.get("platform_rows") or [])]
    platform_order = [str(item.get("platform_id", "")).strip() for item in platform_rows]
    if platform_order != list(PLATFORM_ORDER):
        return {"status": "fail", "message": "MVP cross-platform platform order drifted"}
    canonical_fingerprints = {
        str(item.get("platform_id", "")).strip(): str(item.get("canonical_artifact_fingerprint", "")).strip()
        for item in platform_rows
    }
    if len(set(value for value in canonical_fingerprints.values() if value)) != 1:
        return {"status": "fail", "message": "MVP cross-platform canonical artifact fingerprints diverged"}
    comparison = dict(report.get("comparison") or {})
    if not bool(dict(comparison.get("assertions") or {}).get("hashes_match_across_platforms", False)):
        return {"status": "fail", "message": "MVP cross-platform report did not record hashes_match_across_platforms=true"}
    if list(comparison.get("mismatches") or []):
        return {"status": "fail", "message": "MVP cross-platform report recorded mismatches"}
    return {"status": "pass", "message": "MVP cross-platform canonical hashes agree across the platform matrix"}
