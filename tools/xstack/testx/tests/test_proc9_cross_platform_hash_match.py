"""FAST test: PROC-9 proof hash summary remains stable across equivalent runs."""

from __future__ import annotations

import sys

from tools.xstack.compatx.canonical_json import canonical_sha256


TEST_ID = "test_cross_platform_hash_match_proc9"
TEST_TAGS = ["fast", "proc", "proc9", "hash", "cross_platform"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests import proc9_testlib

    scenario = proc9_testlib.make_stress_scenario(repo_root=repo_root, seed=99151)
    first = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    second = proc9_testlib.run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(first.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "first PROC-9 run failed"}
    if str(second.get("result", "")).strip() != "pass":
        return {"status": "fail", "message": "second PROC-9 run failed"}

    fp_first = canonical_sha256(dict(first.get("proof_hash_summary") or {}))
    fp_second = canonical_sha256(dict(second.get("proof_hash_summary") or {}))
    if fp_first != fp_second:
        return {"status": "fail", "message": "proof hash summary drifted across equivalent runs"}
    return {"status": "pass", "message": "PROC-9 cross-run proof hash summary stable"}
