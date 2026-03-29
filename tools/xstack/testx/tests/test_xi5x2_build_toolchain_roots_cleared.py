from __future__ import annotations

from tools.xstack.testx.tests.xi5x2_testlib import committed_postmove_report

TEST_ID = "test_xi5x2_build_toolchain_roots_cleared"
TEST_TAGS = ["fast", "xi5x2", "restructure"]


def run(repo_root: str):
    payload = committed_postmove_report(repo_root)
    remaining_counts = dict(payload.get("remaining_classification_counts") or {})
    root_counts = dict(payload.get("remaining_root_file_counts") or {})
    offenders = [
        name
        for name in (
            "legacy/launcher_core_launcher/launcher/core/source",
            "legacy/setup_core_setup/setup/core/source",
            "legacy/setup_core_setup/setup/adapters/macosx/gui/xcode/DominiumSetupMacApp/Sources",
        )
        if int(root_counts.get(name, 0) or 0) != 0
    ]
    if int(remaining_counts.get("HIGH_RISK_BUILD_OR_TOOLCHAIN", 0) or 0) != 0 or offenders:
        return {"status": "fail", "message": "Xi-5x2 still has build/toolchain source roots: {}".format(", ".join(offenders or ["HIGH_RISK_BUILD_OR_TOOLCHAIN"]))}
    return {"status": "pass", "message": "Xi-5x2 cleared the build/toolchain source-root blockers"}
