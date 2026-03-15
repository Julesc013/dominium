"""FAST test: COMPONENT-GRAPH-0 resolver is deterministic for identical inputs."""

from __future__ import annotations


TEST_ID = "test_resolver_deterministic"
TEST_TAGS = ["fast", "release", "dist", "component-graph", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.component_graph_testlib import load_default_plan

    first = load_default_plan(repo_root, platform_tag="win64")
    second = load_default_plan(repo_root, platform_tag="win64")
    first_plan = dict(first.get("install_plan") or {})
    second_plan = dict(second.get("install_plan") or {})
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "default component install plan must resolve successfully"}
    if str(first_plan.get("deterministic_fingerprint", "")).strip() != str(second_plan.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "component install plan fingerprint drifted across repeated identical runs"}
    if list(first_plan.get("selected_components") or []) != list(second_plan.get("selected_components") or []):
        return {"status": "fail", "message": "selected component ordering drifted across repeated identical runs"}
    return {"status": "pass", "message": "component graph resolver is deterministic"}
