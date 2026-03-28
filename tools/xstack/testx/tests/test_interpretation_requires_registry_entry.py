"""FAST test: extension interpretation requires a registry declaration."""

from __future__ import annotations


TEST_ID = "test_interpretation_requires_registry_entry"
TEST_TAGS = ["fast", "compat", "extensions"]


def run(repo_root: str):
    from tools.xstack.testx.tests.compat_sem2_testlib import ensure_repo_on_path, load_extension_registry

    ensure_repo_on_path(repo_root)

    from meta_extensions_engine import extensions_get

    registry_payload = load_extension_registry(repo_root)
    allowed = extensions_get(
        repo_root=repo_root,
        owner_schema_id="test.owner",
        extensions={"age_bucket": "mature"},
        key="age_bucket",
        registry_payload=registry_payload,
        default=None,
    )
    refused = extensions_get(
        repo_root=repo_root,
        owner_schema_id="test.owner",
        extensions={"official.test.future_flag": True},
        key="official.test.future_flag",
        registry_payload=registry_payload,
        default=None,
    )
    if allowed != "mature":
        return {"status": "fail", "message": "registered legacy alias did not resolve through registry-backed access"}
    if refused is not None:
        return {"status": "fail", "message": "unregistered extension key was interpreted without registry entry"}
    return {"status": "pass", "message": "extension interpretation remains registry-gated"}
