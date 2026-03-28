"""FAST test: strict extension policy refuses unknown namespaced keys."""

from __future__ import annotations


TEST_ID = "test_unknown_extensions_refused_strict"
TEST_TAGS = ["fast", "compat", "extensions"]


def run(repo_root: str):
    from tools.xstack.testx.tests.compat_sem2_testlib import ensure_repo_on_path, load_extension_registry

    ensure_repo_on_path(repo_root)

    from meta_extensions_engine import STRICT_EXTENSION_POLICY_ID, validate_extensions_map

    report = validate_extensions_map(
        owner_schema_id="test.owner",
        extensions={"official.test.future_flag": True},
        registry_payload=load_extension_registry(repo_root),
        policy_mode=STRICT_EXTENSION_POLICY_ID,
    )
    codes = sorted(str(row.get("code", "")) for row in list(report.get("errors") or []))
    if "extension.unknown_key" not in codes:
        return {"status": "fail", "message": "strict policy did not refuse unknown namespaced extension keys"}
    return {"status": "pass", "message": "strict extension policy refuses unknown namespaced keys"}
