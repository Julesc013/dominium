"""STRICT test: pause/resume transitions are deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.time.pause_resume_determinism"
TEST_TAGS = ["strict", "time", "determinism"]


def _run_sequence() -> dict:
    from engine.time.time_engine import advance_time, ensure_simulation_time, ensure_time_control
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.time_rs3_testlib import default_variable_dt_policy_context

    policy_context = default_variable_dt_policy_context()
    state: dict = {}
    ensure_simulation_time(state)
    control = ensure_time_control(state)

    advance_time(state, policy_context=policy_context, steps=1)
    control["paused"] = True
    advance_time(state, policy_context=policy_context, steps=3)
    paused_tick = int((state.get("simulation_time") or {}).get("tick", 0) or 0)
    control["paused"] = False
    advance_time(state, policy_context=policy_context, steps=2)

    time_tick_log = list(state.get("time_tick_log") or [])
    return {
        "paused_tick": int(paused_tick),
        "final_tick": int((state.get("simulation_time") or {}).get("tick", 0) or 0),
        "time_tick_log_hash": canonical_sha256(time_tick_log),
        "time_tick_log": time_tick_log,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    left = _run_sequence()
    right = _run_sequence()

    if int(left.get("paused_tick", -1)) != int(right.get("paused_tick", -1)):
        return {"status": "fail", "message": "pause tick diverged across identical pause/resume sequence"}
    if int(left.get("final_tick", -1)) != int(right.get("final_tick", -1)):
        return {"status": "fail", "message": "final tick diverged across identical pause/resume sequence"}
    if str(left.get("time_tick_log_hash", "")) != str(right.get("time_tick_log_hash", "")):
        return {"status": "fail", "message": "time_tick_log hash diverged across identical pause/resume sequence"}

    if int(left.get("paused_tick", -1)) != 1:
        return {"status": "fail", "message": "pause period unexpectedly advanced tick while paused"}
    if int(left.get("final_tick", -1)) != 3:
        return {"status": "fail", "message": "unexpected final tick for deterministic pause/resume schedule"}
    if len(list(left.get("time_tick_log") or [])) != 3:
        return {"status": "fail", "message": "unexpected time_tick_log length for deterministic pause/resume schedule"}
    return {"status": "pass", "message": "pause/resume sequence is deterministic and pause halts tick advance"}
