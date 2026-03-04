"""STRICT test: CHEM-1 combustion hash chains are stable across equivalent ordering variants."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_cross_platform_hash_match"
TEST_TAGS = ["strict", "chem", "combustion", "cross_platform", "determinism", "hash"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _variant_state(*, reverse_seed_order: bool) -> dict:
    from tools.xstack.testx.tests.chem_testlib import seed_combustion_state

    state = seed_combustion_state(initial_fuel=1400, material_id="material.fuel_oil_stub")
    prior_combustion = [
        {
            "schema_version": "1.0.0",
            "event_id": "event.combustion.seed.aa",
            "tick": 0,
            "target_id": "node.therm.source",
            "reaction_id": "reaction.combustion_fuel_basic",
            "fuel_consumed": 1,
            "oxidizer_consumed": 3,
            "chemical_energy_in": 10,
            "thermal_energy_out": 8,
            "electrical_energy_out": 0,
            "irreversibility_loss": 2,
            "efficiency_permille": 800,
            "pollutant_emission": 1,
            "extensions": {},
        },
        {
            "schema_version": "1.0.0",
            "event_id": "event.combustion.seed.bb",
            "tick": 0,
            "target_id": "node.therm.source",
            "reaction_id": "reaction.combustion_rich_mixture_stub",
            "fuel_consumed": 2,
            "oxidizer_consumed": 2,
            "chemical_energy_in": 12,
            "thermal_energy_out": 9,
            "electrical_energy_out": 0,
            "irreversibility_loss": 3,
            "efficiency_permille": 750,
            "pollutant_emission": 2,
            "extensions": {},
        },
    ]
    prior_emission = [
        {
            "schema_version": "1.0.0",
            "event_id": "event.combustion.emission.seed.aa",
            "tick": 0,
            "target_id": "node.therm.source",
            "material_id": "material.pollutant_coarse_stub",
            "mass_value": 1,
            "source_reaction_id": "reaction.combustion_fuel_basic",
            "extensions": {},
        }
    ]
    prior_impulse = [
        {
            "schema_version": "1.0.0",
            "event_id": "event.combustion.impulse.seed.aa",
            "tick": 0,
            "target_id": "node.therm.source",
            "target_assembly_id": "body.vehicle.mob.free.alpha",
            "impulse_magnitude": 4,
            "reaction_id": "reaction.explosive_stub",
            "process_id": "process.apply_impulse",
            "extensions": {},
        }
    ]
    if bool(reverse_seed_order):
        prior_combustion = list(reversed(prior_combustion))
        prior_emission = list(reversed(prior_emission))
        prior_impulse = list(reversed(prior_impulse))
    state["combustion_event_rows"] = list(prior_combustion)
    state["combustion_emission_rows"] = list(prior_emission)
    state["combustion_impulse_rows"] = list(prior_impulse)
    return state


def _run_variant(repo_root: str, *, reverse_seed_order: bool) -> dict:
    from tools.xstack.testx.tests.chem_testlib import execute_combustion_tick

    state = _variant_state(reverse_seed_order=bool(reverse_seed_order))
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

    first = _run_variant(repo_root=repo_root, reverse_seed_order=False)
    second = _run_variant(repo_root=repo_root, reverse_seed_order=True)
    first_result = dict(first.get("result") or {})
    second_result = dict(second.get("result") or {})
    if str(first_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "baseline combustion hash fixture failed: {}".format(first_result)}
    if str(second_result.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "reordered combustion hash fixture failed: {}".format(second_result)}

    first_state = dict(first.get("state") or {})
    second_state = dict(second.get("state") or {})
    for key in ("combustion_hash_chain", "emission_hash_chain", "impulse_hash_chain"):
        a = str(first_state.get(key, "")).strip().lower()
        b = str(second_state.get(key, "")).strip().lower()
        if (not _HASH64.fullmatch(a)) or (not _HASH64.fullmatch(b)):
            return {"status": "fail", "message": "{} missing/invalid".format(key)}
        if a != b:
            return {"status": "fail", "message": "{} drifted across equivalent ordering variants".format(key)}

    if list(first_state.get("combustion_event_rows") or []) != list(second_state.get("combustion_event_rows") or []):
        return {"status": "fail", "message": "combustion_event_rows drifted across ordering variants"}
    if list(first_state.get("combustion_emission_rows") or []) != list(second_state.get("combustion_emission_rows") or []):
        return {"status": "fail", "message": "combustion_emission_rows drifted across ordering variants"}
    if list(first_state.get("combustion_impulse_rows") or []) != list(second_state.get("combustion_impulse_rows") or []):
        return {"status": "fail", "message": "combustion_impulse_rows drifted across ordering variants"}
    return {"status": "pass", "message": "combustion hash chains stable across equivalent ordering variants"}
