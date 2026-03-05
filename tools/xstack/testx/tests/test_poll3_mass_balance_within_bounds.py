"""FAST test: POLL-3 mass balance verifier remains within declared proxy bounds."""

from __future__ import annotations

import copy
import sys


TEST_ID = "test_poll3_mass_balance_within_bounds"
TEST_TAGS = ["fast", "pollution", "poll3", "mass_balance"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.pollution.tool_verify_poll_mass_balance import verify_poll_mass_balance
    from tools.xstack.testx.tests.poll3_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=9301)
    report = run_stress_report(
        repo_root=repo_root,
        scenario=scenario,
        budget_envelope_id="poll.envelope.standard",
    )
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "POLL-3 stress run failed for mass-balance fixture"}

    verify = verify_poll_mass_balance(
        state_payload=copy.deepcopy(report),
        proxy_error_permille=500,
    )
    if str(verify.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "POLL mass balance verifier returned violation"}
    if int(dict(verify.get("summary") or {}).get("violation_count", 0) or 0) != 0:
        return {"status": "fail", "message": "POLL mass balance summary violation_count != 0"}
    return {"status": "pass", "message": "POLL-3 mass balance is within declared bounds"}

