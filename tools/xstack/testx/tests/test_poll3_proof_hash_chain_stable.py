"""FAST test: POLL-3 proof hash summary is stable across equivalent runs."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_poll3_proof_hash_chain_stable"
TEST_TAGS = ["fast", "pollution", "poll3", "proof", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.poll3_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=9301)
    first = run_stress_report(
        repo_root=repo_root,
        scenario=copy.deepcopy(scenario),
        budget_envelope_id="poll.envelope.standard",
    )
    second = run_stress_report(
        repo_root=repo_root,
        scenario=copy.deepcopy(scenario),
        budget_envelope_id="poll.envelope.standard",
    )
    if str(first.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first POLL-3 run failed for proof-hash fixture"}
    if str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second POLL-3 run failed for proof-hash fixture"}

    first_summary = dict(dict(first.get("metrics") or {}).get("proof_hash_summary") or {})
    second_summary = dict(dict(second.get("metrics") or {}).get("proof_hash_summary") or {})
    if first_summary != second_summary:
        return {"status": "fail", "message": "POLL-3 proof hash summary drifted across equivalent runs"}

    required_keys = (
        "pollution_emission_hash_chain",
        "pollution_field_hash_chain",
        "exposure_hash_chain",
        "compliance_hash_chain",
        "degradation_event_hash_chain",
    )
    for key in required_keys:
        if str(first_summary.get(key, "")).strip():
            continue
        return {"status": "fail", "message": "missing POLL-3 proof hash key '{}'".format(key)}
    return {"status": "pass", "message": "POLL-3 proof hash summary stable across equivalent runs"}

