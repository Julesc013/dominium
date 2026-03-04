"""FAST test: CHEM-1 burn increments entropy deterministically via entropy engine hooks."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_entropy_increment_on_burn"
TEST_TAGS = ["fast", "chem", "entropy", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.chem_testlib import execute_combustion_tick, seed_combustion_state

    state = seed_combustion_state(initial_fuel=1000, material_id="material.fuel_oil_stub", entropy_value=0)
    result = execute_combustion_tick(
        repo_root=repo_root,
        state=state,
        inputs={"target_id": "node.therm.source", "material_id": "material.fuel_oil_stub", "mixture_ratio_permille": 1200},
    )
    return {"result": dict(result), "state": dict(state)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once(repo_root)
    second = _run_once(repo_root)

    if str((first.get("result") or {}).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first combustion tick failed"}
    if str((second.get("result") or {}).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second combustion tick failed"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    event_rows_a = [dict(row) for row in list(first_state.get("entropy_event_rows") or []) if isinstance(row, dict)]
    event_rows_b = [dict(row) for row in list(second_state.get("entropy_event_rows") or []) if isinstance(row, dict)]
    if not event_rows_a:
        return {"status": "fail", "message": "expected entropy_event_rows after combustion"}
    if event_rows_a != event_rows_b:
        return {"status": "fail", "message": "entropy_event_rows drifted across equivalent combustion runs"}

    chain_a = str(first_state.get("entropy_hash_chain", "")).strip().lower()
    chain_b = str(second_state.get("entropy_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(chain_a)) or (not _HASH64.fullmatch(chain_b)):
        return {"status": "fail", "message": "entropy_hash_chain missing/invalid"}
    if chain_a != chain_b:
        return {"status": "fail", "message": "entropy_hash_chain drifted across equivalent combustion runs"}

    entropy_rows = [dict(row) for row in list(first_state.get("entropy_state_rows") or []) if isinstance(row, dict)]
    if not entropy_rows:
        entropy_rows = [dict(row) for row in list(first_state.get("entropy_states") or []) if isinstance(row, dict)]
    target_rows = [row for row in entropy_rows if str(row.get("target_id", "")).strip() == "node.therm.source"]
    if target_rows and int(max(0, int(target_rows[-1].get("entropy_value", 0) or 0))) > 0:
        return {"status": "pass", "message": "combustion entropy increments are deterministic and logged"}

    if not any(int(max(0, int(row.get("entropy_delta", 0) or 0))) > 0 for row in event_rows_a):
        return {"status": "fail", "message": "entropy event rows did not include positive delta after combustion"}

    return {"status": "pass", "message": "combustion entropy event deltas are deterministic and logged"}
