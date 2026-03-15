"""FAST test: install.profile.full resolves the expected full MVP component set."""

from __future__ import annotations


TEST_ID = "test_full_profile_resolves_required_components"
TEST_TAGS = ["fast", "dist", "release", "install-profile"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_profile_testlib import resolve_profile

    result = resolve_profile(repo_root, "install.profile.full")
    install_plan = dict(result.get("install_plan") or {})
    selected = set(str(value).strip() for value in list(install_plan.get("selected_components") or []))
    required = {
        "binary.client",
        "binary.game",
        "binary.launcher",
        "binary.server",
        "binary.setup",
        "docs.release_notes",
        "manifest.instance.default",
        "manifest.release_manifest",
        "lock.pack_lock.mvp_default",
        "profile.bundle.mvp_default",
    }
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "full install profile did not resolve successfully"}
    if not required.issubset(selected):
        return {"status": "fail", "message": "full install profile is missing required components"}
    return {"status": "pass", "message": "full install profile resolves the required component set"}
