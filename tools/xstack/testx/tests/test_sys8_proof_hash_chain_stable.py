"""FAST test: SYS-8 proof hash chains remain stable across equivalent runs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_proof_hash_chain_stable_sys8"
TEST_TAGS = ["fast", "system", "sys8", "proof", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.testx.tests.sys8_testlib import make_stress_scenario, run_stress_report

    scenario = make_stress_scenario(repo_root=repo_root, seed=88047)
    first = run_stress_report(repo_root=repo_root, scenario=scenario)
    second = run_stress_report(repo_root=repo_root, scenario=scenario)
    if str(first.get("result", "")).strip() != "complete" or str(second.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-8 stress report did not complete for proof-hash check"}

    proof_a = dict((dict(first.get("metrics") or {})).get("proof_hash_summary") or {})
    proof_b = dict((dict(second.get("metrics") or {})).get("proof_hash_summary") or {})
    if proof_a != proof_b:
        return {"status": "fail", "message": "SYS-8 proof hash summary drifted across equivalent runs"}

    for key in (
        "system_collapse_expand_hash_chain",
        "macro_output_record_hash_chain",
        "forced_expand_event_hash_chain",
        "certification_hash_chain",
        "system_health_hash_chain",
    ):
        value = str(proof_a.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(value):
            return {"status": "fail", "message": "SYS-8 proof hash missing/invalid for {}".format(key)}

    return {"status": "pass", "message": "SYS-8 proof hash chains stable across equivalent runs"}
