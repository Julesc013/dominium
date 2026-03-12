"""FAST test: UI fallback order remains consistent with the governed selector policies."""

from __future__ import annotations


TEST_ID = "test_ui_fallback_order_respected"
TEST_TAGS = ["fast", "ui", "appshell", "compat"]


def run(repo_root: str):
    from tools.release.ui_mode_resolution_common import build_test_probe, selection_for_product

    client_gui = selection_for_product(
        repo_root,
        product_id="client",
        probe=build_test_probe(
            repo_root,
            product_id="client",
            platform_id="linux",
            tty=False,
            gui=True,
            native=False,
            rendered=True,
            tui=True,
        ),
    )
    if str(client_gui.get("selected_mode_id", "")).strip() != "rendered":
        return {"status": "fail", "message": "client GUI context did not prefer rendered mode first"}
    launcher_tty = selection_for_product(
        repo_root,
        product_id="launcher",
        probe=build_test_probe(
            repo_root,
            product_id="launcher",
            platform_id="linux",
            tty=True,
            gui=False,
            native=False,
            rendered=False,
            tui=True,
        ),
    )
    if str(launcher_tty.get("selected_mode_id", "")).strip() != "tui":
        return {"status": "fail", "message": "launcher TTY context did not prefer TUI ahead of CLI"}
    setup_gui_no_native = selection_for_product(
        repo_root,
        product_id="setup",
        probe=build_test_probe(
            repo_root,
            product_id="setup",
            platform_id="windows",
            tty=False,
            gui=True,
            native=False,
            rendered=False,
            tui=True,
        ),
    )
    if str(setup_gui_no_native.get("selected_mode_id", "")).strip() != "cli":
        return {"status": "fail", "message": "setup GUI fallback did not degrade deterministically to CLI when native/TUI were unavailable"}
    return {"status": "pass", "message": "UI fallback order follows the governed selector policies"}

