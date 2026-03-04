"""FAST test: FLUID stress proof hash-chain summary is stable for equivalent runs."""

from __future__ import annotations

import sys


TEST_ID = "test_fluid_proof_hash_chain_stable"
TEST_TAGS = ["fast", "fluid", "proof", "determinism"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.fluid.tool_generate_fluid_stress import generate_fluid_stress_scenario
    from tools.fluid.tool_run_fluid_stress import run_fluid_stress_scenario

    scenario = generate_fluid_stress_scenario(
        seed=9703,
        tanks=8,
        vessels=3,
        pipes=44,
        pumps=4,
        valves=4,
        graphs=2,
        ticks=18,
        interior_compartment_count=6,
    )
    a = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=18,
        budget_envelope_id="fluid.envelope.standard",
        max_cost_units_per_tick=2400,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=860,
        base_f1_tick_stride=1,
        max_failure_events_per_tick=64,
        base_max_leak_evaluations_per_tick=64,
    )
    b = run_fluid_stress_scenario(
        scenario=scenario,
        tick_count=18,
        budget_envelope_id="fluid.envelope.standard",
        max_cost_units_per_tick=2400,
        max_processed_edges_per_network=4096,
        max_model_cost_units_per_network=860,
        base_f1_tick_stride=1,
        max_failure_events_per_tick=64,
        base_max_leak_evaluations_per_tick=64,
    )
    proof_a = dict(dict(a.get("metrics") or {}).get("proof_hash_summary") or {})
    proof_b = dict(dict(b.get("metrics") or {}).get("proof_hash_summary") or {})
    if not proof_a:
        return {"status": "fail", "message": "missing FLUID proof_hash_summary"}
    if proof_a != proof_b:
        return {"status": "fail", "message": "FLUID proof_hash_summary drifted across equivalent runs"}
    tick_a = list(dict(a.get("extensions") or {}).get("proof_hashes_per_tick") or [])
    tick_b = list(dict(b.get("extensions") or {}).get("proof_hashes_per_tick") or [])
    if tick_a != tick_b:
        return {"status": "fail", "message": "per-tick proof hashes drifted across equivalent runs"}
    for key in ("fluid_flow_hash_chain", "relief_event_hash_chain", "leak_hash_chain", "burst_hash_chain"):
        if not str(proof_a.get(key, "")).strip():
            return {"status": "fail", "message": "missing '{}' in FLUID proof hash summary".format(key)}
    return {"status": "pass", "message": "FLUID proof hash-chain summary stable"}
