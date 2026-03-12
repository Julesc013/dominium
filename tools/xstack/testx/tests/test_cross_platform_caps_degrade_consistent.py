"""FAST test: explicit rendered-mode fallback degrades consistently across full platforms."""

from __future__ import annotations


TEST_ID = "test_cross_platform_caps_degrade_consistent"
TEST_TAGS = ["fast", "platform", "appshell", "compat"]


def run(repo_root: str):
    from tools.xstack.testx.tests.platform_formalize_testlib import mode_selection, probe

    for platform_id in ("platform.winnt", "platform.macos_cocoa", "platform.linux_gtk"):
        selection = mode_selection(
            repo_root,
            product_id="client",
            requested_mode_id="rendered",
            probe_payload=probe(
                repo_root,
                product_id="client",
                platform_id=platform_id,
                tty=True,
                gui=False,
                tui=True,
            ),
        )
        if str(selection.get("selected_mode_id", "")).strip() != "tui":
            return {
                "status": "fail",
                "message": "explicit rendered fallback on '{}' did not degrade to tui".format(platform_id),
            }
        if str(selection.get("compatibility_mode_id", "")).strip() != "compat.degraded":
            return {
                "status": "fail",
                "message": "explicit rendered fallback on '{}' did not report compat.degraded".format(platform_id),
            }
    return {"status": "pass", "message": "explicit rendered fallback degrades consistently across governed full platforms"}
