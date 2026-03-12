"""FAST test: endpoint descriptors embed canonical platform metadata."""

from __future__ import annotations


TEST_ID = "test_endpoint_descriptor_includes_platform_caps"
TEST_TAGS = ["fast", "platform", "cap_neg", "descriptor"]


def run(repo_root: str):
    from tools.xstack.testx.tests.platform_formalize_testlib import default_descriptor, probe

    platform_probe = probe(
        repo_root,
        product_id="client",
        platform_id="platform.posix_min",
        tty=True,
        gui=False,
        tui=True,
    )
    descriptor = default_descriptor(
        repo_root,
        product_id="client",
        product_version="0.0.0+platform.test",
        platform_id="platform.posix_min",
        platform_probe=platform_probe,
    )
    extensions = dict(descriptor.get("extensions") or {})
    if str(extensions.get("official.platform_id", "")).strip() != "platform.posix_min":
        return {"status": "fail", "message": "descriptor missing canonical platform_id"}
    if not str(extensions.get("official.platform_descriptor_hash", "")).strip():
        return {"status": "fail", "message": "descriptor missing platform descriptor hash"}
    if "official.platform_descriptor" not in extensions:
        return {"status": "fail", "message": "descriptor missing embedded platform descriptor"}
    feature_caps = set(str(item).strip() for item in list(descriptor.get("feature_capabilities") or []) if str(item).strip())
    if "cap.ui.rendered" in feature_caps:
        return {"status": "fail", "message": "descriptor still claims rendered UI on platform.posix_min"}
    if "cap.ui.tui" not in feature_caps or "cap.ui.cli" not in feature_caps:
        return {"status": "fail", "message": "descriptor lost expected portable UI capabilities"}
    return {"status": "pass", "message": "endpoint descriptors include platform metadata and truthful UI capabilities"}
