"""FAST test: endpoint descriptors include deterministic build identity."""

from __future__ import annotations


TEST_ID = "test_descriptor_includes_build_id"
TEST_TAGS = ["fast", "release", "compat"]


def run(repo_root: str):
    from compat.descriptor import build_product_descriptor
    from release import build_product_build_metadata

    descriptor = build_product_descriptor(repo_root, product_id="client")
    build_meta = build_product_build_metadata(repo_root, "client")
    build_id = str(dict(descriptor.get("extensions") or {}).get("official.build_id", "")).strip()
    if not build_id:
        return {"status": "fail", "message": "descriptor missing extensions.official.build_id"}
    if build_id != str(build_meta.get("build_id", "")).strip():
        return {"status": "fail", "message": "descriptor build_id does not match release build metadata"}
    return {"status": "pass", "message": "descriptor includes canonical build_id"}
