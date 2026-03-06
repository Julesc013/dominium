"""FAST test: PROC-9 stress scenario + report are deterministic for same seed."""

from __future__ import annotations

import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_stress_scenario_deterministic_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "determinism", "stress"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc9_testlib

    scenario = proc9_testlib.make_stress_scenario(repo_root=repo_root, seed=99101)
    first = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    second = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(first.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "first PROC-9 stress run did not pass"}
    if str(second.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "second PROC-9 stress run did not pass"}

    fp_first = canonical_sha256(
        {
            "metrics": dict(first.get("metrics") or {}),
            "assertions": dict(first.get("assertions") or {}),
            "proof_hash_summary": dict(first.get("proof_hash_summary") or {}),
            "trace": str(first.get("execution_trace_fingerprint", "")),
        }
    )
    fp_second = canonical_sha256(
        {
            "metrics": dict(second.get("metrics") or {}),
            "assertions": dict(second.get("assertions") or {}),
            "proof_hash_summary": dict(second.get("proof_hash_summary") or {}),
            "trace": str(second.get("execution_trace_fingerprint", "")),
        }
    )
    if fp_first != fp_second:
        return {"status": "fail", "message": "PROC-9 stress fingerprint drifted across equivalent runs"}
    return {"status": "pass", "message": "PROC-9 stress scenario deterministic"}
