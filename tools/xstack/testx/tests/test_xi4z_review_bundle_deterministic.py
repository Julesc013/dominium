"""FAST test: XI-4z approval artifacts regenerate deterministically."""

from __future__ import annotations


TEST_ID = "test_xi4z_review_bundle_deterministic"
TEST_TAGS = ["fast", "xi", "restructure", "determinism"]


def run(repo_root: str):
    from tools.review.xi4z_structure_approval_common import TMP_BUNDLE_MANIFEST_REL, TMP_BUNDLE_REL, XI4Z_DECISION_MANIFEST_REL
    from tools.xstack.testx.tests.xi4z_structure_approval_testlib import committed_manifest, fresh_hashes, fresh_snapshot

    committed = committed_manifest(repo_root)
    fresh = fresh_snapshot(repo_root)
    fresh_manifest = dict(dict(fresh.get("json_payloads") or {}).get(XI4Z_DECISION_MANIFEST_REL) or {})
    if str(committed.get("deterministic_fingerprint", "")).strip() != str(fresh_manifest.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4z decision manifest fingerprint drifted on regeneration"}
    hashes = fresh_hashes(repo_root)
    if TMP_BUNDLE_REL not in hashes or TMP_BUNDLE_MANIFEST_REL not in hashes:
        return {"status": "fail", "message": "XI-4z fresh render must include the readiness bundle and manifest"}
    return {"status": "pass", "message": "XI-4z approval artifacts regenerate deterministically"}
