"""FAST test: legacy UI flags map to the canonical AppShell mode surface."""

from __future__ import annotations


TEST_ID = "test_legacy_flags_map_correctly"
TEST_TAGS = ["fast", "appshell", "flags", "migration"]


def run(repo_root: str):
    from tools.xstack.testx.tests.entrypoint_unify_testlib import context_for_product

    expectations = (
        ("client", ["--ui", "gui"], "rendered", "--ui", "gui"),
        ("client", ["--ui", "cli"], "cli", "--ui", "cli"),
        ("server", ["--ui", "headless"], "headless", "--ui", "headless"),
    )
    for product_id, raw_args, expected_mode, legacy_flag, legacy_value in expectations:
        context = context_for_product(repo_root, product_id, raw_args)
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
    return {"status": "pass", "message": "legacy UI flags map cleanly onto canonical AppShell mode resolution"}
