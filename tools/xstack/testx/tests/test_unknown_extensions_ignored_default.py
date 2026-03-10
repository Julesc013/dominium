"""FAST test: unknown namespaced extensions stay inert under default policy."""

from __future__ import annotations


TEST_ID = "test_unknown_extensions_ignored_default"
TEST_TAGS = ["fast", "compat", "extensions"]


def run(repo_root: str):
    from tools.xstack.testx.tests.compat_sem2_testlib import ensure_repo_on_path, load_extension_registry

    ensure_repo_on_path(repo_root)

    from src.meta_extensions_engine import DEFAULT_EXTENSION_POLICY_ID, validate_extensions_map

    report = validate_extensions_map(
        owner_schema_id="test.owner",
        extensions={"official.test.future_flag": True},
        registry_payload=load_extension_registry(repo_root),
        policy_mode=DEFAULT_EXTENSION_POLICY_ID,
    )
    if list(report.get("errors") or []):
        return {"status": "fail", "message": "default extension policy must not refuse unknown namespaced keys"}
    if list(report.get("warnings") or []):
        return {"status": "fail", "message": "default extension policy should ignore unknown namespaced keys deterministically"}
    normalized = dict(report.get("normalized_extensions") or {})
    if normalized.get("official.test.future_flag") is not True:
        return {"status": "fail", "message": "default normalization lost the unknown extension payload"}
    return {"status": "pass", "message": "unknown namespaced extensions are inert under default policy"}
