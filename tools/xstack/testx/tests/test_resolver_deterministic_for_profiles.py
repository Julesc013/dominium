"""FAST test: install-profile resolution is deterministic for repeated identical inputs."""

from __future__ import annotations


TEST_ID = "test_resolver_deterministic_for_profiles"
TEST_TAGS = ["fast", "dist", "release", "install-profile", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_profile_testlib import resolve_profile

    first = resolve_profile(repo_root, "install.profile.client")
    second = resolve_profile(repo_root, "install.profile.client")
    first_plan = dict(first.get("install_plan") or {})
    second_plan = dict(second.get("install_plan") or {})
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "client install profile must resolve successfully for repeated identical inputs"}
    if str(first_plan.get("deterministic_fingerprint", "")).strip() != str(second_plan.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "install plan fingerprint drifted across repeated client profile resolution"}
    if list(dict(first_plan.get("extensions") or {}).get("selection_reasons") or []) != list(dict(second_plan.get("extensions") or {}).get("selection_reasons") or []):
        return {"status": "fail", "message": "selection reasons drifted across repeated client profile resolution"}
    return {"status": "pass", "message": "install-profile resolution is deterministic"}
