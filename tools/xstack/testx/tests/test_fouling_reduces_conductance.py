"""FAST test: CHEM-3 fouling effects reduce THERM effective conductance deterministically."""

from __future__ import annotations

import sys


TEST_ID = "test_fouling_reduces_conductance"
TEST_TAGS = ["fast", "chem", "thermal", "degradation", "coupling"]


def _edge_row(result: dict) -> dict:
    rows = [dict(row) for row in list(result.get("edge_status_rows") or []) if isinstance(row, dict)]
    return rows[0] if rows else {}


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.thermal.network.thermal_network_engine import solve_thermal_network_t1
    from tools.xstack.testx.tests.chem_degradation_testlib import (
        execute_process,
        load_registry_payload,
        seed_degradation_state,
    )
    from tools.xstack.testx.tests.thermal_testlib import build_thermal_graph

    state = seed_degradation_state()
    tick = execute_process(
        repo_root=repo_root,
        state=state,
        process_id="process.degradation_tick",
        inputs={
            "target_id": "edge.therm.main",
            "profile_id": "profile.heat_exchanger_basic",
            "target_kind": "edge",
            "parameters": {
                "mass_flow": 920,
                "temperature": 38815,
                "contaminant_tags": ["tag.chem.scale", "tag.chem.fouling"],
            },
        },
    )
    if str(tick.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "degradation_tick refused for fouling fixture"}

    effect_rows = [
        dict(row)
        for row in list(state.get("effect_rows") or [])
        if isinstance(row, dict)
        and str(row.get("target_id", "")).strip() == "edge.therm.main"
        and str(row.get("effect_type_id", "")).strip() == "effect.conductance_reduction"
    ]
    if not effect_rows:
        return {"status": "fail", "message": "missing effect.conductance_reduction rows for target edge.therm.main"}

    effect_type_registry = load_registry_payload(repo_root, "data/registries/effect_type_registry.json")
    stacking_policy_registry = load_registry_payload(repo_root, "data/registries/stacking_policy_registry.json")
    graph = build_thermal_graph(source_energy=5000, sink_energy=100, source_capacity=100, sink_capacity=100, conductance_value=140)

    # Degradation effects are one-tick; evaluate at the same tick they are applied.
    baseline = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=0,
        effect_rows=[],
        effect_type_registry=effect_type_registry,
        stacking_policy_registry=stacking_policy_registry,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    degraded = solve_thermal_network_t1(
        graph_row=graph,
        current_tick=0,
        effect_rows=effect_rows,
        effect_type_registry=effect_type_registry,
        stacking_policy_registry=stacking_policy_registry,
        max_processed_edges=128,
        max_cost_units=4096,
    )
    if str(baseline.get("mode", "")).strip() != "T1" or str(degraded.get("mode", "")).strip() != "T1":
        return {"status": "fail", "message": "expected T1 solve mode for fouling conductance test"}

    base_edge = _edge_row(baseline)
    degraded_edge = _edge_row(degraded)
    if not base_edge or not degraded_edge:
        return {"status": "fail", "message": "missing thermal edge rows for fouling test"}

    base_effective = int(base_edge.get("effective_conductance_value", 0) or 0)
    degraded_effective = int(degraded_edge.get("effective_conductance_value", 0) or 0)
    if base_effective <= 0:
        return {"status": "fail", "message": "baseline effective conductance should be positive"}
    if degraded_effective >= base_effective:
        return {
            "status": "fail",
            "message": "fouling should reduce effective conductance (baseline={}, degraded={})".format(
                base_effective,
                degraded_effective,
            ),
        }
    return {"status": "pass", "message": "fouling effect deterministically reduces thermal conductance"}
