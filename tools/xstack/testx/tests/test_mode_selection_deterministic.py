"""FAST test: AppShell mode resolution is deterministic for governed entrypoints."""

from __future__ import annotations


TEST_ID = "test_mode_selection_deterministic"
TEST_TAGS = ["fast", "appshell", "mode_selection", "determinism"]


def run(repo_root: str):
    from tools.xstack.compatx.canonical_json import canonical_json_text
    from tools.xstack.testx.tests.entrypoint_unify_testlib import context_for_product

    first = context_for_product(repo_root, "client", ["--ui", "gui", "--seed", "123"])
    second = context_for_product(repo_root, "client", ["--ui", "gui", "--seed", "123"])
    if str(first.get("deterministic_fingerprint", "")).strip() != str(second.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "client mode-resolution context fingerprint drifted across repeated builds"}
    if canonical_json_text(first) != canonical_json_text(second):
        return {"status": "fail", "message": "client mode-resolution context JSON drifted across repeated builds"}
    mode = dict(first.get("mode") or {})
    if str(mode.get("effective_mode_id", "")).strip() != "rendered":
        return {"status": "fail", "message": "legacy --ui gui did not resolve to rendered mode"}
    if str(mode.get("mode_source", "")).strip() != "legacy_flag":
        return {"status": "fail", "message": "legacy mode resolution did not record the legacy_flag source"}
    return {"status": "pass", "message": "AppShell mode selection remains deterministic for legacy and canonical inputs"}
