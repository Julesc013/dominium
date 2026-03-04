"""FAST test: CHEM-4 replay-window verification matches baseline hashes."""

from __future__ import annotations

import sys


TEST_ID = "test_chem4_replay_window_hash_match"
TEST_TAGS = ["fast", "chem", "replay", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.chem.tool_replay_chem_window import verify_chem_replay_window
    from tools.xstack.testx.tests.chem4_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(
        repo_root=repo_root,
        seed=9121,
        species_pools=24,
        reactions=18,
        process_runs=24,
        ticks=36,
    )
    baseline = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        tick_count=36,
        budget_envelope_id="chem.envelope.standard",
    )
    if str(baseline.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "CHEM baseline stress run failed for replay fixture"}

    replay = verify_chem_replay_window(
        scenario=dict(scenario),
        baseline_report=dict(baseline),
        tick_start=0,
        tick_end=20,
        budget_envelope_id="chem.envelope.standard",
    )
    if str(replay.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "CHEM replay-window verification failed"}

    matches = dict(replay.get("matches") or {})
    required = (
        "proof_window_match",
        "reaction_window_match",
        "energy_window_match",
        "emission_window_match",
        "degradation_window_match",
        "cost_window_match",
        "full_proof_summary_match",
        "replay_completed",
    )
    for key in required:
        if bool(matches.get(key, False)):
            continue
        return {"status": "fail", "message": "CHEM replay-window mismatch for '{}'".format(key)}
    return {"status": "pass", "message": "CHEM replay window hash verification stable"}

