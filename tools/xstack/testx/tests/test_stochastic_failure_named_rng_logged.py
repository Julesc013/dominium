"""FAST test: SYS-6 profile-gated stochastic reliability logs named RNG outcomes."""

from __future__ import annotations

import sys


TEST_ID = "test_stochastic_failure_named_rng_logged"
TEST_TAGS = ["fast", "system", "sys6", "reliability", "rng", "stochastic"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys6_testlib import (
        base_state,
        execute_health_tick,
        execute_reliability_tick,
    )

    state = base_state(
        system_id="system.reactor.stochastic",
        reliability_profile_id="reliability.reactor_stub",
        hazard_levels={
            "hazard.thermal.overheat": 520,
            "hazard.control.loss": 700,
        },
    )
    health_result = execute_health_tick(repo_root=repo_root, state=state)
    if str(health_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "health tick setup failed"}

    reliability_result = execute_reliability_tick(repo_root=repo_root, state=state)
    if str(reliability_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reliability tick failed"}

    rng_rows = [
        dict(row)
        for row in list(state.get("system_reliability_rng_outcome_rows") or [])
        if isinstance(row, dict)
    ]
    if not rng_rows:
        return {"status": "fail", "message": "stochastic profile did not emit named RNG outcome rows"}
    if not any(str(row.get("rng_stream_name", "")).strip() for row in rng_rows):
        return {"status": "fail", "message": "named RNG stream not recorded in stochastic reliability rows"}
    if not str(state.get("system_reliability_rng_hash_chain", "")).strip():
        return {"status": "fail", "message": "system_reliability_rng_hash_chain missing"}
    return {"status": "pass", "message": "SYS-6 stochastic reliability RNG outcomes are logged deterministically"}

