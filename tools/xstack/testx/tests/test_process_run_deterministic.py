"""FAST test: CHEM-2 process run lifecycle is deterministic for equivalent inputs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_process_run_deterministic"
TEST_TAGS = ["fast", "chem", "process", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.chem_testlib import execute_process_run_lifecycle, seed_process_run_state

    state = seed_process_run_state()
    lifecycle = execute_process_run_lifecycle(repo_root=repo_root, state=state)
    return {"state": dict(state), "lifecycle": dict(lifecycle)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once(repo_root)
    second = _run_once(repo_root)

    for key in ("start", "tick", "end"):
        if str((dict(first.get("lifecycle") or {}).get(key, {}) or {}).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "first lifecycle {} failed".format(key)}
        if str((dict(second.get("lifecycle") or {}).get(key, {}) or {}).get("result", "")).strip() != "complete":
            return {"status": "fail", "message": "second lifecycle {} failed".format(key)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    for key in ("process_run_hash_chain", "batch_quality_hash_chain", "yield_model_hash_chain"):
        chain_a = str(first_state.get(key, "")).strip().lower()
        chain_b = str(second_state.get(key, "")).strip().lower()
        if (not _HASH64.fullmatch(chain_a)) or (not _HASH64.fullmatch(chain_b)):
            return {"status": "fail", "message": "{} missing/invalid".format(key)}
        if chain_a != chain_b:
            return {"status": "fail", "message": "{} drifted across equivalent runs".format(key)}

    events_a = [dict(row) for row in list(first_state.get("chem_process_run_events") or []) if isinstance(row, dict)]
    events_b = [dict(row) for row in list(second_state.get("chem_process_run_events") or []) if isinstance(row, dict)]
    if events_a != events_b:
        return {"status": "fail", "message": "process run event stream drifted across equivalent runs"}
    return {"status": "pass", "message": "CHEM-2 process run lifecycle is deterministic"}
