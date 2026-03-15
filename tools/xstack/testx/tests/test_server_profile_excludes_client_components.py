"""FAST test: install.profile.server excludes client-only runtime components."""

from __future__ import annotations


TEST_ID = "test_server_profile_excludes_client_components"
TEST_TAGS = ["fast", "dist", "release", "install-profile"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_profile_testlib import resolve_profile

    result = resolve_profile(repo_root, "install.profile.server")
    install_plan = dict(result.get("install_plan") or {})
    selected = set(str(value).strip() for value in list(install_plan.get("selected_components") or []))
    if str(result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "server install profile did not resolve successfully"}
    if "binary.server" not in selected:
        return {"status": "fail", "message": "server install profile must include the server binary"}
    if "binary.client" in selected:
        return {"status": "fail", "message": "server install profile must exclude the client binary"}
    return {"status": "pass", "message": "server install profile excludes client-only runtime components"}
