"""FAST test: release artifact naming is deterministic from canonical hashes and build IDs."""

from __future__ import annotations


TEST_ID = "test_artifact_naming_deterministic_from_hash"
TEST_TAGS = ["fast", "release", "identity"]


def run(repo_root: str):
    del repo_root
    from tools.release.release_identity_common import (
        binary_artifact_name,
        build_artifact_identity,
        bundle_artifact_name,
        lock_artifact_name,
        manifest_artifact_name,
        pack_artifact_name,
    )
    from tools.xstack.testx.tests.release0_testlib import SAMPLE_CONTENT_HASH

    binary_name = binary_artifact_name("client", "0.0.0", "build.test1234", "platform.posix_min")
    pack_name = pack_artifact_name("pack.base", "1.0.0", SAMPLE_CONTENT_HASH)
    lock_name = lock_artifact_name(SAMPLE_CONTENT_HASH)
    bundle_name = bundle_artifact_name("bundle", "bundle.mvp_default", SAMPLE_CONTENT_HASH)
    manifest_name = manifest_artifact_name("install", SAMPLE_CONTENT_HASH)
    identity = build_artifact_identity(
        artifact_kind="artifact.bundle",
        content_hash=SAMPLE_CONTENT_HASH,
        build_id="build.test1234",
        platform_tag="platform.posix_min",
    )
    expected = {
        "binary": "client-0.0.0+build.test1234-platform.posix_min",
        "pack": "pack.base-1.0.0-0123456789ab",
        "lock": "pack_lock-0123456789ab",
        "bundle": "bundle-bundle.mvp_default-0123456789ab",
        "manifest": "manifest-install-0123456789ab",
    }
    actual = {
        "binary": binary_name,
        "pack": pack_name,
        "lock": lock_name,
        "bundle": bundle_name,
        "manifest": manifest_name,
    }
    if actual != expected:
        return {"status": "fail", "message": "artifact naming drifted from deterministic templates"}
    if not str(identity.get("artifact_id", "")).strip() or not str(identity.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "artifact identity payload is incomplete"}
    return {"status": "pass", "message": "artifact naming is deterministic from content hashes and build IDs"}
