"""FAST test: legacy UI flags map to the canonical AppShell mode surface."""

from __future__ import annotations

import os
import tempfile


TEST_ID = "test_legacy_flags_map_correctly"
TEST_TAGS = ["fast", "appshell", "flags", "migration"]


def run(repo_root: str):
    from tools.xstack.testx.tests.install_discovery_testlib import seed_install_root
    from tools.xstack.testx.tests.repo_layout1_testlib import build_context

    expectations = (
        ("client", ["--ui", "gui"], "rendered", "--ui", "gui"),
        ("client", ["--ui", "cli"], "cli", "--ui", "cli"),
        ("server", ["--ui", "headless"], "headless", "--ui", "headless"),
    )
    for product_id, raw_args, expected_mode, legacy_flag, legacy_value in expectations:
        context = build_context(repo_root, product_id, raw_args)
        mode = dict(context.get("mode") or {})
        delegate = list(context.get("delegate_argv") or [])
        if str(mode.get("effective_mode_id", "")).strip() != expected_mode:
            return {
                "status": "fail",
                "message": "{} {} did not map to {}".format(product_id, " ".join(raw_args), expected_mode),
            }
        if delegate[:2] != [legacy_flag, legacy_value]:
            return {
                "status": "fail",
                "message": "{} {} did not preserve translated delegate args".format(product_id, " ".join(raw_args)),
            }
    no_gui_context = build_context(repo_root, "client", ["--no-gui"])
    no_gui_mode = str(dict(no_gui_context.get("mode") or {}).get("effective_mode_id", "")).strip()
    if no_gui_mode not in {"tui", "cli"}:
        return {"status": "fail", "message": "client --no-gui did not map to a deterministic non-GUI mode"}
    deprecated_flags = list(dict(no_gui_context.get("mode") or {}).get("deprecated_flags") or [])
    if not any(str(dict(row).get("legacy_flag", "")).strip() == "--no-gui" for row in deprecated_flags):
        return {"status": "fail", "message": "client --no-gui did not emit a legacy flag deprecation row"}
    with tempfile.TemporaryDirectory(prefix="dominium_shim_portable_") as temp_root:
        install_root = os.path.join(temp_root, "portable")
        seed_install_root(install_root, "install.test.portable", root_path=".")
        executable_path = os.path.join(install_root, "dominium_launcher")
        context = build_context(repo_root, "launcher", ["--portable"], executable_path=executable_path)
        if str(context.get("install_reference", "")).replace("\\", "/") != install_root.replace("\\", "/"):
            return {"status": "fail", "message": "--portable did not resolve to the adjacent install root"}
    return {"status": "pass", "message": "legacy flags map cleanly onto canonical AppShell mode resolution"}
