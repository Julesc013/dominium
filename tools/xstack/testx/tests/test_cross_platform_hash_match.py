"""FAST test: CHEM-2 process-run replay hashes are stable across equivalent runs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_cross_platform_hash_match"
TEST_TAGS = ["fast", "chem", "replay", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.chem_testlib import execute_process_run_lifecycle, seed_process_run_state

    state = seed_process_run_state()
    lifecycle = execute_process_run_lifecycle(repo_root=repo_root, state=state, catalyst_present=True)
    return {"state": dict(state), "lifecycle": dict(lifecycle)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.chem.tool_replay_process_run import verify_process_run_window

    first = _run_once(repo_root)
    second = _run_once(repo_root)
    for label, payload in (("first", first), ("second", second)):
        tick_result = str((dict(payload.get("lifecycle") or {}).get("tick", {}) or {}).get("result", "")).strip()
        if tick_result != "complete":
            return {"status": "fail", "message": "{} process_run_tick failed".format(label)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    report = verify_process_run_window(state_payload=first_state, expected_payload=second_state)
    if str(report.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "process-run replay verifier reported violations: {}".format(report.get("violations", []))}

    for key in ("process_run_hash_chain", "batch_quality_hash_chain", "yield_model_hash_chain"):
        chain = str((dict(report.get("observed") or {})).get(key, "")).strip().lower()
        if not _HASH64.fullmatch(chain):
            return {"status": "fail", "message": "observed {} missing/invalid".format(key)}
    return {"status": "pass", "message": "CHEM-2 replay hashes are stable across equivalent runs"}
