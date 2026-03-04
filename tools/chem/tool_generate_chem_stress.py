#!/usr/bin/env python3
"""CHEM-4 deterministic stress scenario generator."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping, Sequence, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_DEGRADE_ORDER = [
    "degrade.chem.tick_bucket",
    "degrade.chem.reaction_to_c0",
    "degrade.chem.defer_noncritical_yield",
    "degrade.chem.eval_cap",
]


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _pick(seed: int, stream: str, index: int, modulo: int, *, offset: int = 0) -> int:
    mod = int(modulo)
    if mod <= 0:
        return int(offset)
    digest = canonical_sha256(
        {
            "seed": int(seed),
            "stream": str(stream),
            "index": int(index),
            "modulo": int(mod),
        }
    )
    return int(int(offset) + (int(digest[:12], 16) % int(mod)))


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _reaction_rows(repo_root: str) -> List[dict]:
    rel = "data/registries/reaction_profile_registry.json"
    abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
    payload = _read_json(abs_path)
    rows = list((dict(payload.get("record") or {})).get("reaction_profiles") or [])
    out: List[dict] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        reaction_id = str(row.get("reaction_id", "")).strip()
        if not reaction_id:
            continue
        out.append(dict(row))
    return sorted(out, key=lambda row: str(row.get("reaction_id", "")))


def _species_catalog(reaction_rows: Sequence[Mapping[str, object]]) -> List[str]:
    out = set()
    for row in reaction_rows:
        inputs = dict(row.get("input_species") or {}) if isinstance(row.get("input_species"), Mapping) else {}
        outputs = dict(row.get("output_species") or {}) if isinstance(row.get("output_species"), Mapping) else {}
        emissions = dict(row.get("emission_species") or {}) if isinstance(row.get("emission_species"), Mapping) else {}
        for token in list(inputs.keys()) + list(outputs.keys()) + list(emissions.keys()):
            species_id = str(token or "").strip()
            if species_id.startswith("material."):
                out.add(species_id)
    if not out:
        out.update(
            [
                "material.fuel_basic",
                "material.oxidizer_air_stub",
                "material.exhaust_gas_stub",
                "material.residue_stub",
                "material.pollutant_coarse_stub",
            ]
        )
    return sorted(out)


def _species_pool_rows(*, seed: int, pool_count: int, species_ids: Sequence[str]) -> List[dict]:
    rows: List[dict] = []
    species = list(species_ids or [])
    for idx in range(max(1, int(pool_count))):
        target_id = "node.chem.pool.{}".format(str(idx + 1).zfill(4))
        species_id = species[_pick(seed, "pool.species", idx, max(1, len(species)))]
        mass_value = int(500 + _pick(seed, "pool.mass", idx, 5000))
        row = {
            "schema_version": "1.0.0",
            "target_id": str(target_id),
            "material_id": str(species_id),
            "mass_value": int(mass_value),
            "last_update_tick": 0,
            "deterministic_fingerprint": "",
            "extensions": {
                "pool_kind": "reactor" if (_pick(seed, "pool.kind", idx, 4) > 0) else "storage",
                "shard_id": "shard.{}".format(str((_pick(seed, "pool.shard", idx, 3) + 1)).zfill(2)),
            },
        }
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
        rows.append(row)
    return sorted(rows, key=lambda row: str(row.get("target_id", "")))


def _reaction_binding_rows(
    *,
    seed: int,
    reaction_rows: Sequence[Mapping[str, object]],
    pool_rows: Sequence[Mapping[str, object]],
    reaction_count: int,
) -> List[dict]:
    rows: List[dict] = []
    pools = [str(row.get("target_id", "")).strip() for row in pool_rows if str(row.get("target_id", "")).strip()]
    reactions = [dict(row) for row in reaction_rows if isinstance(row, Mapping)]
    if (not pools) or (not reactions):
        return []
    for idx in range(max(1, int(reaction_count))):
        reaction = dict(reactions[_pick(seed, "binding.reaction", idx, len(reactions))])
        reaction_id = str(reaction.get("reaction_id", "")).strip()
        if not reaction_id:
            continue
        primary_pool = pools[_pick(seed, "binding.pool.primary", idx, len(pools))]
        secondary_pool = pools[_pick(seed, "binding.pool.secondary", idx + 917, len(pools))]
        if secondary_pool == primary_pool and len(pools) > 1:
            secondary_pool = pools[(pools.index(primary_pool) + 1) % len(pools)]
        equipment_id = "equipment.chem.cell.{}".format(str(idx + 1).zfill(4))
        row = {
            "schema_version": "1.0.0",
            "binding_id": "binding.chem.stress.{}".format(str(idx + 1).zfill(5)),
            "reaction_id": reaction_id,
            "equipment_id": str(equipment_id),
            "node_id": str(primary_pool),
            "input_pool_ids": sorted({str(primary_pool), str(secondary_pool)}),
            "rate_model_id": str(reaction.get("rate_model_id", "")).strip() or "model.chem_rate_linear_stub",
            "rate_scale_permille": int(450 + _pick(seed, "binding.rate", idx, 801)),
            "priority": int(_pick(seed, "binding.priority", idx, 100)),
            "tier_mode": "C1" if (_pick(seed, "binding.tier", idx, 4) > 0) else "C0",
            "deterministic_fingerprint": "",
            "extensions": {
                "yield_model_id": str((dict(reaction.get("extensions") or {})).get("yield_model_id", "yield.basic_windowed")),
                "emission_enabled": bool(dict(reaction.get("emission_species") or {})),
                "catalyst_present": bool(_pick(seed, "binding.catalyst", idx, 2)),
            },
        }
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
        rows.append(row)
    return sorted(rows, key=lambda row: str(row.get("binding_id", "")))


def _process_run_schedule_rows(
    *,
    seed: int,
    binding_rows: Sequence[Mapping[str, object]],
    run_count: int,
    tick_horizon: int,
) -> List[dict]:
    rows: List[dict] = []
    bindings = [dict(row) for row in binding_rows if isinstance(row, Mapping)]
    if not bindings:
        return rows
    horizon = int(max(8, int(tick_horizon)))
    for idx in range(max(1, int(run_count))):
        binding = dict(bindings[_pick(seed, "run.binding", idx, len(bindings))])
        run_id = "run.chem.stress.{}".format(str(idx + 1).zfill(5))
        start_tick = int(_pick(seed, "run.start", idx, max(1, horizon // 2)))
        interval_ticks = int(1 + _pick(seed, "run.interval", idx, 8))
        stop_tick = int(max(start_tick, min(horizon - 1, start_tick + _pick(seed, "run.window", idx, max(2, horizon // 2)))))
        row = {
            "schema_version": "1.0.0",
            "run_id": str(run_id),
            "binding_id": str(binding.get("binding_id", "")),
            "reaction_id": str(binding.get("reaction_id", "")),
            "equipment_id": str(binding.get("equipment_id", "")),
            "input_pool_ids": list(binding.get("input_pool_ids") or []),
            "start_tick": int(start_tick),
            "interval_ticks": int(interval_ticks),
            "stop_tick": int(stop_tick),
            "priority": int(_pick(seed, "run.priority", idx, 100)),
            "deterministic_fingerprint": "",
            "extensions": {
                "burst_weight_permille": int(200 + _pick(seed, "run.burst_weight", idx, 700)),
            },
        }
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
        rows.append(row)
    return sorted(rows, key=lambda row: str(row.get("run_id", "")))


def _condition_pattern_rows(
    *,
    seed: int,
    equipment_ids: Sequence[str],
    tick_horizon: int,
) -> Tuple[List[dict], List[dict]]:
    temp_rows: List[dict] = []
    pressure_rows: List[dict] = []
    horizon = int(max(1, int(tick_horizon)))
    for idx, equipment_id in enumerate(sorted(_sorted_tokens(list(equipment_ids)))):
        cycle = int(3 + _pick(seed, "condition.cycle", idx, 9))
        temp_rows.append(
            {
                "equipment_id": str(equipment_id),
                "base_temperature": int(500 + _pick(seed, "condition.temp.base", idx, 260)),
                "amplitude": int(20 + _pick(seed, "condition.temp.amp", idx, 140)),
                "cycle_ticks": int(cycle),
                "phase_offset": int(_pick(seed, "condition.temp.phase", idx, cycle)),
                "start_tick": 0,
                "end_tick": int(max(0, horizon - 1)),
            }
        )
        pressure_rows.append(
            {
                "equipment_id": str(equipment_id),
                "base_pressure_head": int(90 + _pick(seed, "condition.press.base", idx, 320)),
                "amplitude": int(10 + _pick(seed, "condition.press.amp", idx, 120)),
                "cycle_ticks": int(max(2, cycle - 1)),
                "phase_offset": int(_pick(seed, "condition.press.phase", idx, max(2, cycle - 1))),
                "start_tick": 0,
                "end_tick": int(max(0, horizon - 1)),
            }
        )
    return (
        sorted(temp_rows, key=lambda row: str(row.get("equipment_id", ""))),
        sorted(pressure_rows, key=lambda row: str(row.get("equipment_id", ""))),
    )


def _emission_burst_rows(
    *,
    seed: int,
    schedule_rows: Sequence[Mapping[str, object]],
    tick_horizon: int,
) -> List[dict]:
    rows: List[dict] = []
    horizon = int(max(8, int(tick_horizon)))
    schedules = [dict(row) for row in schedule_rows if isinstance(row, Mapping)]
    if not schedules:
        return rows
    burst_count = int(max(2, min(len(schedules), horizon // 3)))
    for idx in range(burst_count):
        run_row = dict(schedules[_pick(seed, "burst.run", idx, len(schedules))])
        rows.append(
            {
                "burst_id": "burst.chem.{}".format(str(idx + 1).zfill(4)),
                "tick": int(1 + _pick(seed, "burst.tick", idx, max(2, horizon - 2))),
                "run_id": str(run_row.get("run_id", "")).strip(),
                "multiplier_permille": int(1100 + _pick(seed, "burst.multiplier", idx, 1800)),
                "reason_code": "chem.emission_burst_stub",
            }
        )
    return sorted(rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("burst_id", ""))))


def generate_chem_stress_scenario(
    *,
    seed: int = 12041,
    species_pools: int = 64,
    reactions: int = 96,
    process_runs: int = 128,
    ticks: int = 64,
    repo_root: str | None = None,
) -> dict:
    root = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))
    reaction_rows = _reaction_rows(root)
    species_ids = _species_catalog(reaction_rows)

    pool_rows = _species_pool_rows(
        seed=int(seed),
        pool_count=int(species_pools),
        species_ids=list(species_ids),
    )
    binding_rows = _reaction_binding_rows(
        seed=int(seed),
        reaction_rows=reaction_rows,
        pool_rows=pool_rows,
        reaction_count=int(reactions),
    )
    schedule_rows = _process_run_schedule_rows(
        seed=int(seed),
        binding_rows=binding_rows,
        run_count=int(process_runs),
        tick_horizon=int(ticks),
    )
    equipment_ids = [str(row.get("equipment_id", "")).strip() for row in binding_rows if str(row.get("equipment_id", "")).strip()]
    temperature_rows, pressure_rows = _condition_pattern_rows(
        seed=int(seed),
        equipment_ids=equipment_ids,
        tick_horizon=int(ticks),
    )
    emission_rows = _emission_burst_rows(
        seed=int(seed),
        schedule_rows=schedule_rows,
        tick_horizon=int(ticks),
    )

    scenario_id = "scenario.chem.stress.{}".format(
        canonical_sha256(
            {
                "seed": int(seed),
                "species_pools": int(species_pools),
                "reactions": int(reactions),
                "process_runs": int(process_runs),
                "ticks": int(ticks),
            }
        )[:12]
    )
    payload = {
        "schema_version": "1.0.0",
        "scenario_id": str(scenario_id),
        "scenario_seed": int(seed),
        "tick_horizon": int(max(1, int(ticks))),
        "degradation_policy_order": list(_DEGRADE_ORDER),
        "reaction_binding_rows": [dict(row) for row in binding_rows],
        "process_run_schedule_rows": [dict(row) for row in schedule_rows],
        "temperature_pattern_rows": [dict(row) for row in temperature_rows],
        "pressure_pattern_rows": [dict(row) for row in pressure_rows],
        "emission_burst_rows": [dict(row) for row in emission_rows],
        "initial_state_snapshot": {
            "chem_species_pool_rows": [dict(row) for row in pool_rows],
            "chem_degradation_state_rows": [],
            "chem_process_run_state_rows": [],
            "chem_process_run_events": [],
            "chem_process_emission_rows": [],
            "combustion_event_rows": [],
            "energy_ledger_entries": [],
            "entropy_event_rows": [],
            "entropy_reset_events": [],
        },
        "budget_defaults": {
            "max_reaction_evaluations_per_tick": int(max(1, min(4096, int(reactions) // 2 + 64))),
            "max_cost_units_per_tick": int(max(256, min(16384, int(reactions) * 8))),
            "max_model_cost_units_per_tick": int(max(256, min(16384, int(reactions) * 6))),
            "max_emission_events_per_tick": int(max(8, min(4096, int(process_runs) // 2 + 16))),
        },
        "extensions": {
            "generator": _norm(os.path.relpath(os.path.abspath(__file__), root)),
            "reaction_profile_count": int(len(reaction_rows)),
            "species_catalog_size": int(len(species_ids)),
        },
        "deterministic_fingerprint": "",
    }
    payload["deterministic_fingerprint"] = canonical_sha256(dict(payload, deterministic_fingerprint=""))
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic CHEM stress scenario.")
    parser.add_argument("--seed", type=int, default=12041)
    parser.add_argument("--species-pools", type=int, default=64)
    parser.add_argument("--reactions", type=int, default=96)
    parser.add_argument("--process-runs", type=int, default=128)
    parser.add_argument("--ticks", type=int, default=64)
    parser.add_argument("--output", default="build/chem/chem_stress_scenario.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    scenario = generate_chem_stress_scenario(
        seed=int(args.seed),
        species_pools=int(args.species_pools),
        reactions=int(args.reactions),
        process_runs=int(args.process_runs),
        ticks=int(args.ticks),
        repo_root=REPO_ROOT_HINT,
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, scenario)
    report = dict(scenario)
    report["output_path"] = output_abs
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
