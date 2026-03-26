"""FAST test: XI-4b review artifacts regenerate deterministically."""

from __future__ import annotations


TEST_ID = "test_xi4b_review_bundle_deterministic"
TEST_TAGS = ["fast", "xi", "restructure", "determinism"]


def run(repo_root: str):
    from tools.review.xi4b_src_domain_mapping_common import TMP_BUNDLE_MANIFEST_REL, TMP_BUNDLE_REL, XI4B_REVIEW_MANIFEST_REL, SRC_DOMAIN_MAPPING_REL
    from tools.xstack.testx.tests.xi4b_src_domain_mapping_testlib import committed_review_manifest, committed_src_domain_mapping, fresh_hashes, fresh_snapshot

    committed_mapping = committed_src_domain_mapping(repo_root)
    committed_manifest = committed_review_manifest(repo_root)
    fresh = fresh_snapshot(repo_root)
    fresh_mapping = dict(dict(fresh.get("json_payloads") or {}).get(SRC_DOMAIN_MAPPING_REL) or {})
    fresh_review_manifest = dict(dict(fresh.get("json_payloads") or {}).get(XI4B_REVIEW_MANIFEST_REL) or {})
    if str(committed_mapping.get("deterministic_fingerprint", "")).strip() != str(fresh_mapping.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4b src-domain mapping fingerprint drifted on regeneration"}
    if str(committed_manifest.get("deterministic_fingerprint", "")).strip() != str(fresh_review_manifest.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "XI-4b review manifest fingerprint drifted on regeneration"}
    hashes = fresh_hashes(repo_root)
    if TMP_BUNDLE_REL not in hashes or TMP_BUNDLE_MANIFEST_REL not in hashes:
        return {"status": "fail", "message": "XI-4b fresh render must include the bundle zip and manifest"}
    return {"status": "pass", "message": "XI-4b review artifacts regenerate deterministically"}
