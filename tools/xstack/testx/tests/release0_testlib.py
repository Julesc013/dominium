"""Shared RELEASE-0 test helpers."""

from __future__ import annotations


SAMPLE_CONTENT_HASH = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def sample_build_metadata(repo_root: str, product_id: str, *, source_revision_id: str = "rev.test", feature_capability: str = "") -> dict:
    from release import build_product_build_metadata

    override = None
    if feature_capability:
        override = {
            "descriptor_schema_version": "1.0.0",
            "product_id": str(product_id).strip(),
            "runtime_family": "python.portable",
            "protocol_ids": ["protocol.loopback.control"],
            "feature_capabilities": [str(feature_capability).strip()],
            "source": "RELEASE0-TEST",
        }
    return build_product_build_metadata(
        repo_root,
        product_id,
        source_revision_id_override=str(source_revision_id).strip(),
        compilation_options_override=override,
    )


def sample_release_report(repo_root: str) -> dict:
    from tools.release.release_identity_common import build_release_identity_report

    return build_release_identity_report(repo_root)
