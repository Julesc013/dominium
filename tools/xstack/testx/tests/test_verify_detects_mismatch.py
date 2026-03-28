"""FAST test: release manifest verification detects artifact mismatches."""

from __future__ import annotations

import os


TEST_ID = "test_verify_detects_mismatch"
TEST_TAGS = ["fast", "release", "verification"]


def run(repo_root: str):
    del repo_root
    from tools.xstack.testx.tests.release1_testlib import build_manifest_payload, release_fixture
    from release import verify_release_manifest, write_release_manifest

    with release_fixture() as dist_root:
        payload = build_manifest_payload(dist_root)
        manifest_path = os.path.join(dist_root, "manifests", "release_manifest.json")
        write_release_manifest(dist_root, payload, manifest_path=manifest_path)
        with open(os.path.join(dist_root, "profiles", "bundle.test.json"), "a", encoding="utf-8", newline="\n") as handle:
            handle.write("mismatch\n")
        report = verify_release_manifest(dist_root, manifest_path)
    codes = {str(dict(row or {}).get("code", "")).strip() for row in list(report.get("errors") or [])}
    if str(report.get("result", "")).strip() != "refused":
        return {"status": "fail", "message": "verification did not refuse after an artifact mismatch"}
    if "refusal.release_manifest.content_hash_mismatch" not in codes:
        return {"status": "fail", "message": "verification refused, but not with content_hash_mismatch evidence"}
    return {"status": "pass", "message": "verification detects content hash mismatches"}
