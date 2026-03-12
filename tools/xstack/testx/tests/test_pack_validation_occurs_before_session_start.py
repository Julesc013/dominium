"""FAST test: AppShell bootstrap plans keep pack validation ahead of session start."""

from __future__ import annotations


TEST_ID = "test_pack_validation_occurs_before_session_start"
TEST_TAGS = ["fast", "appshell", "pack", "bootstrap"]


def _index_of(steps: list[str], token: str) -> int:
    try:
        return steps.index(token)
    except ValueError:
        return -1


def run(repo_root: str):
    from tools.xstack.testx.tests.entrypoint_unify_testlib import context_for_product

    launcher = context_for_product(repo_root, "launcher")
    launcher_steps = list(launcher.get("bootstrap_steps") or [])
    if _index_of(launcher_steps, "pack_validate") < 0 or _index_of(launcher_steps, "session_start") < 0:
        return {"status": "fail", "message": "launcher bootstrap plan is missing pack/session phases"}
    if _index_of(launcher_steps, "pack_validate") > _index_of(launcher_steps, "session_start"):
        return {"status": "fail", "message": "launcher pack validation occurs after session start"}

    server = context_for_product(repo_root, "server")
    server_steps = list(server.get("bootstrap_steps") or [])
    if _index_of(server_steps, "contract_validate") < 0 or _index_of(server_steps, "pack_validate") < 0:
        return {"status": "fail", "message": "server bootstrap plan is missing contract or pack validation"}
    if _index_of(server_steps, "pack_validate") > _index_of(server_steps, "session_start"):
        return {"status": "fail", "message": "server pack validation occurs after session start"}
    return {"status": "pass", "message": "AppShell bootstrap plans validate packs before session start"}
