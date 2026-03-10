"""FAST test: extension registry rows must use namespaced keys and explicit legacy aliases."""

from __future__ import annotations


TEST_ID = "test_extension_keys_must_be_namespaced"
TEST_TAGS = ["fast", "compat", "extensions"]


def run(repo_root: str):
    from tools.xstack.testx.tests.compat_sem2_testlib import ensure_repo_on_path, load_extension_registry

    ensure_repo_on_path(repo_root)

    from src.meta_extensions_engine import legacy_alias_for_key

    payload = load_extension_registry(repo_root)
    rows = list(((payload.get("record") or {}).get("extension_interpretations")) or [])
    if not rows:
        return {"status": "fail", "message": "extension interpretation registry is empty"}
    for row in rows:
        if not isinstance(row, dict):
            return {"status": "fail", "message": "registry row must be an object"}
        extension_key = str(row.get("extension_key", "")).strip()
        legacy_alias = str(dict(row.get("extensions") or {}).get("legacy_alias_for", "")).strip()
        if not extension_key.startswith(("official.", "dev.", "mod.")):
            return {"status": "fail", "message": "registry row is not namespaced: {}".format(extension_key)}
        if legacy_alias and extension_key != legacy_alias_for_key(legacy_alias):
            return {"status": "fail", "message": "legacy alias mapping is not canonical for {}".format(extension_key)}
    return {"status": "pass", "message": "extension registry rows are namespaced and legacy aliases are explicit"}
