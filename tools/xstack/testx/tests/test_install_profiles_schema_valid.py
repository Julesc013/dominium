"""FAST test: DIST-REFINE-1 install profile registry and report are structurally valid."""

from __future__ import annotations


TEST_ID = "test_install_profiles_schema_valid"
TEST_TAGS = ["fast", "dist", "release", "install-profile"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_profile_testlib import build_report, current_violations, load_registry

    registry = load_registry(repo_root)
    report = build_report(repo_root)
    violations = current_violations(repo_root)
    profile_rows = list(dict(dict(registry).get("record") or {}).get("install_profiles") or [])
    profile_ids = {str(dict(row or {}).get("install_profile_id", "")).strip() for row in profile_rows}
    required_ids = {
        "install.profile.full",
        "install.profile.client",
        "install.profile.server",
        "install.profile.tools",
        "install.profile.sdk",
    }
    if str(registry.get("schema_version", "")).strip() != "1.0.0":
        return {"status": "fail", "message": "install profile registry schema_version must be 1.0.0"}
    if not required_ids.issubset(profile_ids):
        return {"status": "fail", "message": "install profile registry is missing required ids"}
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "install profile report did not complete successfully"}
    if violations:
        return {"status": "fail", "message": "install profile governance violations remain: {}".format(len(violations))}
    return {"status": "pass", "message": "install profile registry and report are valid"}
