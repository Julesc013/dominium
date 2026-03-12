"""FAST test: governed registries do not contain untagged entries after scope freeze."""

from __future__ import annotations


TEST_ID = "test_no_new_registries_without_stability"
TEST_TAGS = ["fast", "release", "scope_freeze", "stability"]


def run(repo_root: str):
    from tools.xstack.testx.tests.scope_freeze_testlib import load_validation_report, missing_stability_errors

    report = load_validation_report(repo_root)
    violations = missing_stability_errors(report)
    if violations:
        first = violations[0]
        return {
            "status": "fail",
            "message": "registry entry without stability marker detected in {} ({})".format(
                first["file_path"],
                first["path"],
            ),
        }
    return {"status": "pass", "message": "all governed registry entries remain stability-tagged after scope freeze"}
