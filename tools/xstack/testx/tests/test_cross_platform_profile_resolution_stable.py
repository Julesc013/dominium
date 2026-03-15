"""FAST test: install-profile resolution stays stable for repeated identical cross-platform inputs."""

from __future__ import annotations


TEST_ID = "test_cross_platform_profile_resolution_stable"
TEST_TAGS = ["fast", "dist", "release", "install-profile", "platform", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_profile_testlib import resolve_profile

    first = resolve_profile(repo_root, "install.profile.server", platform_tag="linux-x86_64")
    second = resolve_profile(repo_root, "install.profile.server", platform_tag="linux-x86_64")
    first_plan = dict(first.get("install_plan") or {})
    second_plan = dict(second.get("install_plan") or {})
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "server install profile must resolve successfully for repeated linux target inputs"}
    if list(first_plan.get("selected_components") or []) != list(second_plan.get("selected_components") or []):
        return {"status": "fail", "message": "selected component ordering drifted for repeated linux target inputs"}
    if str(first_plan.get("deterministic_fingerprint", "")).strip() != str(second_plan.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "install plan fingerprint drifted for repeated linux target inputs"}
    return {"status": "pass", "message": "install-profile resolution is stable for repeated cross-platform inputs"}
