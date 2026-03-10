"""FAST test: SERVER-MVP-1 local spawn args are deterministic."""

from __future__ import annotations


TEST_ID = "test_spawn_args_deterministic"
TEST_TAGS = ["fast", "server", "singleplayer"]


def run(repo_root: str):
    from tools.xstack.testx.tests.server_mvp1_testlib import launch_spec

    first = launch_spec(repo_root, suffix="spawn_args")
    second = launch_spec(repo_root, suffix="spawn_args")
    if str(first.get("result", "")) != "complete" or str(second.get("result", "")) != "complete":
        return {"status": "fail", "message": "local launch spec generation did not complete"}
    first_spec = dict(first.get("process_spec") or {})
    second_spec = dict(second.get("process_spec") or {})
    if list(first_spec.get("args") or []) != list(second_spec.get("args") or []):
        return {"status": "fail", "message": "spawn args drifted across repeated runs"}
    if str(first_spec.get("deterministic_fingerprint", "")) != str(second_spec.get("deterministic_fingerprint", "")):
        return {"status": "fail", "message": "spawn spec fingerprint drifted across repeated runs"}
    return {"status": "pass", "message": "SERVER-MVP-1 spawn args are deterministic"}
