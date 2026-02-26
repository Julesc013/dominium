"""STRICT test: variable dt selection stays deterministic for identical rate changes."""

from __future__ import annotations

import sys


TEST_ID = "testx.time.variable_dt_determinism"
TEST_TAGS = ["strict", "time", "determinism"]


def _run_sequence() -> dict:
    from src.time.time_engine import advance_time, ensure_simulation_time, ensure_time_control
    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.testx.tests.time_rs3_testlib import default_variable_dt_policy_context

    policy_context = default_variable_dt_policy_context()
    state: dict = {}
    ensure_simulation_time(state)
    control = ensure_time_control(state)

    advance_time(state, policy_context=policy_context, steps=1)
    control["rate_permille"] = 2000
    advance_time(state, policy_context=policy_context, steps=1)
    control["rate_permille"] = 500
    advance_time(state, policy_context=policy_context, steps=1)
    control["rate_permille"] = 3333
    advance_time(state, policy_context=policy_context, steps=2)

    time_tick_log = list(state.get("time_tick_log") or [])
    dt_sequence = [int(row.get("dt_sim_permille", 0) or 0) for row in time_tick_log]
    return {
        "dt_sequence": dt_sequence,
        "time_tick_log_hash": canonical_sha256(time_tick_log),
        "tick": int((state.get("simulation_time") or {}).get("tick", 0) or 0),
        "sim_time_permille": int((state.get("simulation_time") or {}).get("sim_time_permille", 0) or 0),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    left = _run_sequence()
    right = _run_sequence()

    if list(left.get("dt_sequence") or []) != list(right.get("dt_sequence") or []):
        return {"status": "fail", "message": "dt sequence diverged for identical variable rate schedule"}
    if str(left.get("time_tick_log_hash", "")) != str(right.get("time_tick_log_hash", "")):
        return {"status": "fail", "message": "time_tick_log hash diverged for identical variable rate schedule"}
    if int(left.get("tick", 0)) != int(right.get("tick", 0)):
        return {"status": "fail", "message": "tick count diverged for identical variable rate schedule"}
    if int(left.get("sim_time_permille", 0)) != int(right.get("sim_time_permille", 0)):
        return {"status": "fail", "message": "sim_time accumulation diverged for identical variable rate schedule"}

    dt_sequence = list(left.get("dt_sequence") or [])
    if len(set(dt_sequence)) < 2:
        return {"status": "fail", "message": "variable dt schedule did not produce multiple quantized dt values"}
    if int(left.get("tick", 0)) != len(dt_sequence):
        return {"status": "fail", "message": "tick count does not match deterministic dt log length"}
    return {"status": "pass", "message": "variable dt sequence and hashes are deterministic"}
