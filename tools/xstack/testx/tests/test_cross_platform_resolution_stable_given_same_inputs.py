"""FAST test: COMPONENT-GRAPH-0 resolution stays stable for repeated identical target inputs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_resolution_stable_given_same_inputs"
TEST_TAGS = ["fast", "release", "dist", "component-graph", "platform", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.component_graph_testlib import load_default_plan

    first = load_default_plan(repo_root, platform_tag="linux-x86_64")
    second = load_default_plan(repo_root, platform_tag="linux-x86_64")
    first_plan = dict(first.get("install_plan") or {})
    second_plan = dict(second.get("install_plan") or {})
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "component graph must resolve successfully for repeated linux target inputs"}
    if str(first_plan.get("deterministic_fingerprint", "")).strip() != str(second_plan.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "cross-platform target resolution fingerprint drifted for repeated identical inputs"}
    if list(first_plan.get("verification_steps") or []) != list(second_plan.get("verification_steps") or []):
        return {"status": "fail", "message": "verification step ordering drifted for repeated identical target inputs"}
    return {"status": "pass", "message": "resolution is stable for repeated identical cross-platform target inputs"}
