"""FAST test: UX-0 canonical viewer shell surface hash stays fixed across platforms."""

from __future__ import annotations

import sys


TEST_ID = "test_cross_platform_ui_hash_match"
TEST_TAGS = ["fast", "ux", "viewer", "determinism", "cross_platform"]

EXPECTED_UI_HASH = "b8d0bc61be5a8f3cebbcf27395941fba48419c030e091c5cf9962d1eef25227f"


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.ux0_testlib import viewer_shell_fixture, viewer_shell_surface_hash

    fixture = viewer_shell_fixture(repo_root)
    shell_state = dict(fixture.get("shell_state") or {})
    if str(shell_state.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "UX-0 canonical viewer shell fixture did not complete"}
    observed_hash = viewer_shell_surface_hash(shell_state)
    if observed_hash != EXPECTED_UI_HASH:
        return {
            "status": "fail",
            "message": "UX-0 viewer shell surface hash drifted (expected {}, got {})".format(
                EXPECTED_UI_HASH,
                observed_hash or "<missing>",
            ),
        }
    return {"status": "pass", "message": "UX-0 canonical viewer shell surface hash matches expected cross-platform fixture"}
