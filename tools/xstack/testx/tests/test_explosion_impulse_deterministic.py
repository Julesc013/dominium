"""FAST test: CHEM-1 explosive combustion impulse hooks are deterministic and logged."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_explosion_impulse_deterministic"
TEST_TAGS = ["fast", "chem", "combustion", "impulse", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _run_once(repo_root: str) -> dict:
    from tools.xstack.testx.tests.chem_testlib import execute_combustion_tick, seed_combustion_state

    state = seed_combustion_state(initial_fuel=1300, material_id="material.fuel_oil_stub")
    result = execute_combustion_tick(
        repo_root=repo_root,
        state=state,
        inputs={
            "target_id": "node.therm.source",
            "material_id": "material.fuel_oil_stub",
            "reaction_id": "reaction.explosive_stub",
            "explosive_profile": True,
            "explosion_target_assembly_id": "body.vehicle.mob.free.alpha",
            "impulse_energy_ratio_permille": 320,
        },
    )
    return {"result": dict(result), "state": dict(state)}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once(repo_root)
    second = _run_once(repo_root)

    if str((first.get("result") or {}).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "first explosive combustion tick failed"}
    if str((second.get("result") or {}).get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "second explosive combustion tick failed"}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    impulse_rows_a = [dict(row) for row in list(first_state.get("combustion_impulse_rows") or []) if isinstance(row, dict)]
    impulse_rows_b = [dict(row) for row in list(second_state.get("combustion_impulse_rows") or []) if isinstance(row, dict)]
    if not impulse_rows_a:
        return {"status": "fail", "message": "expected combustion_impulse_rows for explosive combustion"}
    if impulse_rows_a != impulse_rows_b:
        return {"status": "fail", "message": "combustion_impulse_rows drifted across equivalent runs"}

    latest = dict(impulse_rows_a[-1])
    if str(latest.get("reaction_id", "")).strip() != "reaction.explosive_stub":
        return {"status": "fail", "message": "impulse row reaction_id mismatch for explosive profile"}
    if int(max(0, int(latest.get("impulse_magnitude", 0) or 0))) <= 0:
        return {"status": "fail", "message": "impulse magnitude not emitted for explosive combustion"}
    if str(latest.get("process_id", "")).strip() != "process.apply_impulse":
        return {"status": "fail", "message": "impulse hook not tagged to process.apply_impulse"}
    if str(latest.get("target_assembly_id", "")).strip() != "body.vehicle.mob.free.alpha":
        return {"status": "fail", "message": "impulse target assembly mismatch"}

    chain_a = str(first_state.get("impulse_hash_chain", "")).strip().lower()
    chain_b = str(second_state.get("impulse_hash_chain", "")).strip().lower()
    if (not _HASH64.fullmatch(chain_a)) or (not _HASH64.fullmatch(chain_b)):
        return {"status": "fail", "message": "impulse_hash_chain missing/invalid"}
    if chain_a != chain_b:
        return {"status": "fail", "message": "impulse_hash_chain drifted across equivalent runs"}
    return {"status": "pass", "message": "explosive combustion impulse hooks are deterministic"}
