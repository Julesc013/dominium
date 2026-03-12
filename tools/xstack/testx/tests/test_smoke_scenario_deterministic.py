"""FAST test: MVP smoke scenario generation is deterministic for the canonical seed."""

from __future__ import annotations


TEST_ID = "test_smoke_scenario_deterministic"
TEST_TAGS = ["fast", "mvp", "smoke", "determinism"]


def run(repo_root: str):
    from tools.mvp.mvp_smoke_common import DEFAULT_MVP_SMOKE_SEED, generate_mvp_smoke_scenario
    from tools.xstack.testx.tests.mvp_smoke_testlib import load_scenario

    recorded = load_scenario(repo_root)
    regenerated = generate_mvp_smoke_scenario(repo_root, seed=DEFAULT_MVP_SMOKE_SEED)
    if str(recorded.get("scenario_id", "")).strip() != str(regenerated.get("scenario_id", "")).strip():
        return {"status": "fail", "message": "scenario_id drifted for canonical MVP smoke seed"}
    if str(recorded.get("deterministic_fingerprint", "")).strip() != str(regenerated.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "scenario fingerprint drifted for canonical MVP smoke seed"}
    if list(recorded.get("teleport_chain") or []) != list(regenerated.get("teleport_chain") or []):
        return {"status": "fail", "message": "teleport chain drifted for canonical MVP smoke seed"}
    return {"status": "pass", "message": "MVP smoke scenario is deterministic for seed 456"}
