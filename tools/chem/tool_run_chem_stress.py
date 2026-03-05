#!/usr/bin/env python3
"""CHEM-4 deterministic stress harness."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List, Mapping, Sequence


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.chem.tool_generate_chem_stress import (  # noqa: E402
    _as_int,
    _read_json,
    _write_json,
    generate_chem_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_DEGRADE_ORDER = [
    "degrade.chem.tick_bucket",
    "degrade.chem.reaction_to_c0",
    "degrade.chem.defer_noncritical_yield",
    "degrade.chem.eval_cap",
]


def _envelope_defaults(budget_envelope_id: str) -> dict:
    token = str(budget_envelope_id or "").strip().lower()
    if token == "chem.envelope.tight":
        return {
            "max_reaction_evaluations_per_tick": 48,
            "max_cost_units_per_tick": 860,
            "max_model_cost_units_per_tick": 420,
            "base_tick_stride": 2,
            "max_emission_events_per_tick": 48,
            "max_residual_abs": 2,
        }
    if token == "chem.envelope.rank_strict":
        return {
            "max_reaction_evaluations_per_tick": 128,
            "max_cost_units_per_tick": 2400,
            "max_model_cost_units_per_tick": 1200,
            "base_tick_stride": 1,
            "max_emission_events_per_tick": 128,
            "max_residual_abs": 0,
        }
    return {
        "max_reaction_evaluations_per_tick": 96,
        "max_cost_units_per_tick": 1800,
        "max_model_cost_units_per_tick": 920,
        "base_tick_stride": 1,
        "max_emission_events_per_tick": 96,
        "max_residual_abs": 1,
    }


def _reaction_rows_by_id(repo_root: str) -> Dict[str, dict]:
    rel = "data/registries/reaction_profile_registry.json"
    abs_path = os.path.join(repo_root, rel.replace("/", os.sep))
    payload = _read_json(abs_path)
    rows = list((dict(payload.get("record") or {})).get("reaction_profiles") or [])
    out: Dict[str, dict] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        reaction_id = str(row.get("reaction_id", "")).strip()
        if not reaction_id:
            continue
        out[reaction_id] = dict(row)
    return dict((key, out[key]) for key in sorted(out.keys()))


def _chain(rows: object, key_fn) -> str:
    chain = "0" * 64
    for row in sorted((dict(item) for item in list(rows or []) if isinstance(item, Mapping)), key=key_fn):
        chain = canonical_sha256({"previous_hash": chain, "row_hash": canonical_sha256(row)})
    return chain


def _pattern_value(row: Mapping[str, object], tick: int, base_key: str) -> int:
    base = int(_as_int(row.get(base_key, 0), 0))
    amp = int(max(0, _as_int(row.get("amplitude", 0), 0)))
    cycle = int(max(1, _as_int(row.get("cycle_ticks", 1), 1)))
    offset = int(max(0, _as_int(row.get("phase_offset", 0), 0)))
    phase = int((int(tick) + offset) % cycle)
    # Deterministic sawtooth wave in [-amp, +amp].
    numerator = (phase * 2 * amp) - (amp * cycle)
    delta = int(numerator // cycle)
    return int(base + delta)


def _pool_key(target_id: str, material_id: str) -> str:
    return "{}::{}".format(str(target_id or "").strip(), str(material_id or "").strip())


def _get_mass(pool_by_key: Mapping[str, int], target_id: str, material_id: str) -> int:
    return int(max(0, _as_int(dict(pool_by_key or {}).get(_pool_key(target_id, material_id), 0), 0)))


def _set_mass(pool_by_key: Dict[str, int], target_id: str, material_id: str, mass_value: int) -> None:
    key = _pool_key(target_id, material_id)
    pool_by_key[key] = int(max(0, _as_int(mass_value, 0)))


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _active_runs(schedule_rows: Sequence[Mapping[str, object]], tick: int) -> List[dict]:
    out: List[dict] = []
    for row in sorted((dict(item) for item in schedule_rows if isinstance(item, Mapping)), key=lambda item: str(item.get("run_id", ""))):
        start_tick = int(max(0, _as_int(row.get("start_tick", 0), 0)))
        stop_tick = int(max(start_tick, _as_int(row.get("stop_tick", start_tick), start_tick)))
        interval_ticks = int(max(1, _as_int(row.get("interval_ticks", 1), 1)))
        if int(tick) < start_tick or int(tick) > stop_tick:
            continue
        if ((int(tick) - start_tick) % interval_ticks) != 0:
            continue
        out.append(dict(row))
    return out


def _burst_multiplier(run_id: str, tick: int, burst_rows: Sequence[Mapping[str, object]]) -> int:
    multiplier = 1000
    for row in sorted((dict(item) for item in burst_rows if isinstance(item, Mapping)), key=lambda item: (int(_as_int(item.get("tick", 0), 0)), str(item.get("burst_id", "")))):
        if int(_as_int(row.get("tick", 0), 0)) != int(tick):
            continue
        if str(row.get("run_id", "")).strip() != str(run_id).strip():
            continue
        multiplier = int(max(0, _as_int(row.get("multiplier_permille", 1000), 1000)))
    return int(multiplier)


def _summarize_residuals(values: Sequence[int]) -> dict:
    rows = [int(v) for v in values]
    if not rows:
        return {"count": 0, "max_abs": 0, "sum_abs": 0}
    return {
        "count": int(len(rows)),
        "max_abs": int(max(abs(v) for v in rows)),
        "sum_abs": int(sum(abs(v) for v in rows)),
    }


def _is_sorted(rows: object, key_fn) -> bool:
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    return normalized == sorted(normalized, key=key_fn)


def run_chem_stress_scenario(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str,
    max_reaction_evaluations_per_tick: int,
    max_cost_units_per_tick: int,
    max_model_cost_units_per_tick: int,
    base_tick_stride: int,
    max_emission_events_per_tick: int,
) -> dict:
    scenario_row = copy.deepcopy(dict(scenario or {}))
    scenario_id = str(scenario_row.get("scenario_id", "")).strip() or "scenario.chem.unknown"
    horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 64), 64))))
    budget_id = str(budget_envelope_id or "").strip() or "chem.envelope.standard"

    reaction_cap = int(max(1, _as_int(max_reaction_evaluations_per_tick, 96)))
    cost_cap = int(max(1, _as_int(max_cost_units_per_tick, 1800)))
    model_cost_cap = int(max(1, _as_int(max_model_cost_units_per_tick, 920)))
    tick_stride_base = int(max(1, _as_int(base_tick_stride, 1)))
    emission_cap = int(max(1, _as_int(max_emission_events_per_tick, 96)))

    reaction_rows_by_id = _reaction_rows_by_id(REPO_ROOT_HINT)
    binding_rows = [dict(row) for row in list(scenario_row.get("reaction_binding_rows") or []) if isinstance(row, Mapping)]
    binding_rows_by_id = dict(
        (str(row.get("binding_id", "")).strip(), dict(row))
        for row in sorted(binding_rows, key=lambda row: str(row.get("binding_id", "")))
        if str(row.get("binding_id", "")).strip()
    )
    schedule_rows = [dict(row) for row in list(scenario_row.get("process_run_schedule_rows") or []) if isinstance(row, Mapping)]
    temperature_rows = [dict(row) for row in list(scenario_row.get("temperature_pattern_rows") or []) if isinstance(row, Mapping)]
    pressure_rows = [dict(row) for row in list(scenario_row.get("pressure_pattern_rows") or []) if isinstance(row, Mapping)]
    burst_rows = [dict(row) for row in list(scenario_row.get("emission_burst_rows") or []) if isinstance(row, Mapping)]

    initial_snapshot = dict(scenario_row.get("initial_state_snapshot") or {})
    pool_rows = [dict(row) for row in list(initial_snapshot.get("chem_species_pool_rows") or []) if isinstance(row, Mapping)]
    pool_by_key: Dict[str, int] = {}
    for row in sorted(pool_rows, key=lambda item: (str(item.get("target_id", "")), str(item.get("material_id", "")))):
        target_id = str(row.get("target_id", "")).strip()
        material_id = str(row.get("material_id", "")).strip()
        if (not target_id) or (not material_id):
            continue
        _set_mass(pool_by_key, target_id, material_id, _as_int(row.get("mass_value", 0), 0))

    entropy_by_equipment: Dict[str, int] = {}
    process_run_rows: List[dict] = []
    reaction_event_rows: List[dict] = []
    emission_event_rows: List[dict] = []
    ledger_rows: List[dict] = []
    degradation_event_rows: List[dict] = []
    decision_log_rows: List[dict] = []

    per_tick_reactions: List[int] = []
    per_tick_degraded: List[int] = []
    per_tick_mass_residual: List[int] = []
    per_tick_energy_residual: List[int] = []
    per_tick_entropy_increment: List[int] = []
    per_tick_emission_total: List[int] = []
    per_tick_cost_units: List[int] = []
    per_tick_hashes: List[str] = []

    deterministic_ordering_ok = True
    bounded_evaluation_ok = True
    no_silent_mass_changes = True
    no_silent_energy_changes = True
    all_outputs_logged = True

    expected_total_cost = int(max(1, len(binding_rows_by_id) * 12))

    for tick in range(0, int(horizon)):
        active_rows = _active_runs(schedule_rows, int(tick))
        pressure_ratio_permille = int(max(0, ((expected_total_cost - cost_cap) * 1000) // expected_total_cost))
        dynamic_tick_stride = int(max(1, tick_stride_base + (pressure_ratio_permille // 380)))

        tick_reactions = 0
        tick_degraded = 0
        tick_mass_residual = 0
        tick_energy_residual = 0
        tick_entropy_increment = 0
        tick_emission_total = 0
        tick_cost_units = 0
        tick_model_cost = 0
        tick_emission_event_count = 0

        deferred_for_cap: List[str] = []
        deferred_for_stride: List[str] = []

        for idx, schedule_row in enumerate(active_rows):
            run_id = str(schedule_row.get("run_id", "")).strip()
            binding_id = str(schedule_row.get("binding_id", "")).strip()
            binding_row = dict(binding_rows_by_id.get(binding_id) or {})
            reaction_id = str(schedule_row.get("reaction_id", "")).strip() or str(binding_row.get("reaction_id", "")).strip()
            reaction_row = dict(reaction_rows_by_id.get(reaction_id) or {})
            if (not run_id) or (not binding_row) or (not reaction_row):
                continue

            if dynamic_tick_stride > 1 and (int((tick + idx) % dynamic_tick_stride) != 0):
                deferred_for_stride.append(run_id)
                decision_log_rows.append(
                    {
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "reason_code": "degrade.chem.tick_bucket",
                        "step_order": 1,
                        "details": {"dynamic_tick_stride": int(dynamic_tick_stride)},
                    }
                )
                degradation_event_rows.append(
                    {
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "event_kind": "degrade.chem.tick_bucket",
                        "binding_id": str(binding_id),
                        "step_order": 1,
                    }
                )
                continue

            if tick_reactions >= reaction_cap:
                deferred_for_cap.append(run_id)
                bounded_evaluation_ok = bool(bounded_evaluation_ok and tick_reactions <= reaction_cap)
                decision_log_rows.append(
                    {
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "reason_code": "degrade.chem.eval_cap",
                        "step_order": 4,
                        "details": {"max_reaction_evaluations_per_tick": int(reaction_cap)},
                    }
                )
                degradation_event_rows.append(
                    {
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "event_kind": "degrade.chem.eval_cap",
                        "binding_id": str(binding_id),
                        "step_order": 4,
                    }
                )
                continue

            input_species = dict(reaction_row.get("input_species") or {}) if isinstance(reaction_row.get("input_species"), Mapping) else {}
            output_species = dict(reaction_row.get("output_species") or {}) if isinstance(reaction_row.get("output_species"), Mapping) else {}
            emission_species = dict(reaction_row.get("emission_species") or {}) if isinstance(reaction_row.get("emission_species"), Mapping) else {}
            input_pool_ids = _sorted_tokens(list(schedule_row.get("input_pool_ids") or binding_row.get("input_pool_ids") or []))
            if not input_pool_ids:
                continue
            primary_pool_id = str(input_pool_ids[0])
            equipment_id = str(schedule_row.get("equipment_id", "")).strip() or str(binding_row.get("equipment_id", "")).strip()
            tier_mode = str(binding_row.get("tier_mode", "C1")).strip().upper() or "C1"

            temperature_row = next((row for row in temperature_rows if str(row.get("equipment_id", "")).strip() == equipment_id), {})
            pressure_row = next((row for row in pressure_rows if str(row.get("equipment_id", "")).strip() == equipment_id), {})
            temperature = _pattern_value(temperature_row, int(tick), "base_temperature") if temperature_row else 620
            pressure_head = _pattern_value(pressure_row, int(tick), "base_pressure_head") if pressure_row else 160
            entropy_value = int(max(0, _as_int(entropy_by_equipment.get(equipment_id, 0), 0)))

            rate_scale_permille = int(max(1, _as_int(binding_row.get("rate_scale_permille", 700), 700)))
            rate_permille = int(max(50, min(1800, rate_scale_permille + ((temperature - 620) // 2) + (pressure_head // 8))))
            base_units = int(max(1, rate_permille // (260 if tier_mode == "C1" else 520)))
            model_cost = int(2 + len(input_species) + len(output_species))
            run_cost = int(4 + (len(input_species) * 2) + (len(output_species) * 2))
            downgraded_to_c0 = False
            deferred_noncritical = False

            if (tick_cost_units + run_cost) > cost_cap:
                if tier_mode == "C1":
                    downgraded_to_c0 = True
                    tick_degraded += 1
                    tier_mode = "C0"
                    base_units = int(max(1, base_units // 2))
                    run_cost = int(max(2, run_cost // 2))
                    decision_log_rows.append(
                        {
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "reason_code": "degrade.chem.reaction_to_c0",
                            "step_order": 2,
                            "details": {"binding_id": str(binding_id), "mode": "C0"},
                        }
                    )
                    degradation_event_rows.append(
                        {
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "event_kind": "degrade.chem.reaction_to_c0",
                            "binding_id": str(binding_id),
                            "step_order": 2,
                        }
                    )
                if (tick_cost_units + run_cost) > cost_cap:
                    deferred_for_cap.append(run_id)
                    decision_log_rows.append(
                        {
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "reason_code": "degrade.chem.eval_cap",
                            "step_order": 4,
                            "details": {"max_cost_units_per_tick": int(cost_cap)},
                        }
                    )
                    degradation_event_rows.append(
                        {
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "event_kind": "degrade.chem.eval_cap",
                            "binding_id": str(binding_id),
                            "step_order": 4,
                        }
                    )
                    continue

            if (tick_model_cost + model_cost) > model_cost_cap:
                deferred_noncritical = True
                tick_degraded += 1
                decision_log_rows.append(
                    {
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "reason_code": "degrade.chem.defer_noncritical_yield",
                        "step_order": 3,
                        "details": {"max_model_cost_units_per_tick": int(model_cost_cap)},
                    }
                )
                degradation_event_rows.append(
                    {
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "event_kind": "degrade.chem.defer_noncritical_yield",
                        "binding_id": str(binding_id),
                        "step_order": 3,
                    }
                )
                model_cost = 0

            available_units = None
            for species_id, coeff in sorted(input_species.items(), key=lambda item: str(item[0])):
                coeff_value = int(max(1, _as_int(coeff, 1)))
                total_mass = 0
                for pool_id in input_pool_ids:
                    total_mass += _get_mass(pool_by_key, pool_id, str(species_id))
                units = int(total_mass // coeff_value)
                available_units = units if available_units is None else min(int(available_units), int(units))
            available_units = int(max(0, _as_int(available_units, 0)))
            if available_units <= 0:
                continue

            units = int(min(int(base_units), int(available_units)))
            if units <= 0:
                continue

            efficiency_permille = int(max(120, min(980, 900 - (entropy_value // 6) - (abs(temperature - 650) // 5))))
            if deferred_noncritical:
                yield_factor_permille = 1000
            else:
                catalyst_bonus = 120 if bool(dict(binding_row.get("extensions") or {}).get("catalyst_present", False)) else 0
                yield_factor_permille = int(max(200, min(1000, 820 + catalyst_bonus - (entropy_value // 12))))
            effective_units = int(max(1, (units * yield_factor_permille) // 1000))

            consumed_mass = 0
            for species_id, coeff in sorted(input_species.items(), key=lambda item: str(item[0])):
                coeff_value = int(max(1, _as_int(coeff, 1)))
                consume_mass = int(effective_units * coeff_value)
                remaining = int(consume_mass)
                for pool_id in input_pool_ids:
                    available_mass = _get_mass(pool_by_key, pool_id, str(species_id))
                    take = int(min(available_mass, remaining))
                    if take > 0:
                        _set_mass(pool_by_key, pool_id, str(species_id), available_mass - take)
                        remaining -= take
                        consumed_mass += take
                    if remaining <= 0:
                        break

            produced_mass = 0
            for species_id, coeff in sorted(output_species.items(), key=lambda item: str(item[0])):
                coeff_value = int(max(1, _as_int(coeff, 1)))
                mass_out = int(effective_units * coeff_value)
                if mass_out <= 0:
                    continue
                current_mass = _get_mass(pool_by_key, primary_pool_id, str(species_id))
                _set_mass(pool_by_key, primary_pool_id, str(species_id), current_mass + mass_out)
                produced_mass += mass_out

            multiplier = _burst_multiplier(run_id, int(tick), burst_rows)
            emission_mass_total = 0
            emitted_rows_for_run: List[dict] = []
            for species_id, coeff in sorted(emission_species.items(), key=lambda item: str(item[0])):
                coeff_value = int(max(1, _as_int(coeff, 1)))
                base_mass = int(effective_units * coeff_value)
                emission_mass = int((base_mass * multiplier) // 1000)
                if emission_mass <= 0:
                    continue
                emission_mass_total += emission_mass
                emitted_rows_for_run.append(
                    {
                        "schema_version": "1.0.0",
                        "event_id": "event.chem.stress.emission.{}".format(
                            canonical_sha256({"tick": int(tick), "run_id": run_id, "species_id": str(species_id)})[:16]
                        ),
                        "tick": int(tick),
                        "run_id": str(run_id),
                        "equipment_id": str(equipment_id),
                        "material_id": str(species_id),
                        "mass_value": int(emission_mass),
                        "deterministic_fingerprint": "",
                        "extensions": {"source": "tool_run_chem_stress"},
                    }
                )

            if emitted_rows_for_run:
                if (tick_emission_event_count + len(emitted_rows_for_run)) > emission_cap:
                    decision_log_rows.append(
                        {
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "reason_code": "degrade.chem.eval_cap",
                            "step_order": 4,
                            "details": {"max_emission_events_per_tick": int(emission_cap)},
                        }
                    )
                    degradation_event_rows.append(
                        {
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "event_kind": "degrade.chem.eval_cap",
                            "binding_id": str(binding_id),
                            "step_order": 4,
                        }
                    )
                    # Deterministic aggregation when cap is exceeded.
                    aggregate_mass = int(sum(int(_as_int(row.get("mass_value", 0), 0)) for row in emitted_rows_for_run))
                    emitted_rows_for_run = [
                        {
                            "schema_version": "1.0.0",
                            "event_id": "event.chem.stress.emission.aggregate.{}".format(
                                canonical_sha256({"tick": int(tick), "run_id": run_id})[:16]
                            ),
                            "tick": int(tick),
                            "run_id": str(run_id),
                            "equipment_id": str(equipment_id),
                            "material_id": "material.pollutant_coarse_stub",
                            "mass_value": int(aggregate_mass),
                            "deterministic_fingerprint": "",
                            "extensions": {
                                "source": "tool_run_chem_stress",
                                "aggregated_due_to_cap": True,
                            },
                        }
                    ]
                tick_emission_event_count += len(emitted_rows_for_run)
                for row in emitted_rows_for_run:
                    row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
                emission_event_rows.extend(emitted_rows_for_run)

            waste_mass = int(max(0, consumed_mass - produced_mass - emission_mass_total))
            mass_residual = int(consumed_mass - produced_mass - emission_mass_total - waste_mass)
            tick_mass_residual += mass_residual

            chemical_energy_in = int(consumed_mass * 5)
            thermal_out = int((chemical_energy_in * efficiency_permille) // 1000)
            entropy_loss = int(max(0, chemical_energy_in - thermal_out))
            energy_residual = int(chemical_energy_in - thermal_out - entropy_loss)
            tick_energy_residual += energy_residual

            entropy_increment = int(max(0, entropy_loss // 8))
            entropy_by_equipment[equipment_id] = int(max(0, entropy_value + entropy_increment))
            tick_entropy_increment += entropy_increment
            tick_emission_total += int(emission_mass_total)

            event_id = "event.chem.stress.reaction.{}".format(
                canonical_sha256({"tick": int(tick), "run_id": run_id, "reaction_id": reaction_id})[:16]
            )
            reaction_event_rows.append(
                {
                    "schema_version": "1.0.0",
                    "event_id": str(event_id),
                    "tick": int(tick),
                    "run_id": str(run_id),
                    "reaction_id": str(reaction_id),
                    "equipment_id": str(equipment_id),
                    "units": int(effective_units),
                    "consumed_mass": int(consumed_mass),
                    "produced_mass": int(produced_mass),
                    "emission_mass": int(emission_mass_total),
                    "mass_residual": int(mass_residual),
                    "tier_mode": str(tier_mode),
                    "downgraded_to_c0": bool(downgraded_to_c0),
                    "deterministic_fingerprint": "",
                    "extensions": {
                        "yield_factor_permille": int(yield_factor_permille),
                        "efficiency_permille": int(efficiency_permille),
                        "deferred_noncritical": bool(deferred_noncritical),
                    },
                }
            )
            reaction_event_rows[-1]["deterministic_fingerprint"] = canonical_sha256(
                dict(reaction_event_rows[-1], deterministic_fingerprint="")
            )

            ledger_rows.append(
                {
                    "schema_version": "1.0.0",
                    "entry_id": "entry.chem.stress.{}".format(
                        canonical_sha256({"tick": int(tick), "run_id": run_id, "reaction_id": reaction_id})[:16]
                    ),
                    "tick": int(tick),
                    "transformation_id": str(reaction_row.get("energy_transformation_id", "transform.chemical_to_thermal")).strip() or "transform.chemical_to_thermal",
                    "source_id": str(run_id),
                    "input_values": {"quantity.energy_chemical": int(chemical_energy_in)},
                    "output_values": {
                        "quantity.energy_thermal": int(thermal_out),
                        "quantity.heat_loss": int(entropy_loss),
                    },
                    "energy_total_delta": int(0),
                    "deterministic_fingerprint": "",
                    "extensions": {"source": "tool_run_chem_stress"},
                }
            )
            ledger_rows[-1]["deterministic_fingerprint"] = canonical_sha256(dict(ledger_rows[-1], deterministic_fingerprint=""))

            process_run_rows.append(
                {
                    "schema_version": "1.0.0",
                    "run_id": str(run_id),
                    "reaction_id": str(reaction_id),
                    "equipment_id": str(equipment_id),
                    "input_batch_ids": [],
                    "output_batch_ids": [],
                    "start_tick": int(max(0, _as_int(schedule_row.get("start_tick", tick), tick))),
                    "end_tick": int(tick),
                    "progress": int(min(1000, int(100 + (tick * 10)))),
                    "deterministic_fingerprint": "",
                    "extensions": {"status": "active"},
                }
            )
            process_run_rows[-1]["deterministic_fingerprint"] = canonical_sha256(dict(process_run_rows[-1], deterministic_fingerprint=""))

            tick_reactions += 1
            tick_cost_units += run_cost
            tick_model_cost += model_cost

        deterministic_ordering_ok = bool(
            deterministic_ordering_ok
            and _is_sorted(
                reaction_event_rows,
                key_fn=lambda row: (
                    int(_as_int(row.get("tick", 0), 0)),
                    str(row.get("run_id", "")),
                    str(row.get("reaction_id", "")),
                    str(row.get("event_id", "")),
                ),
            )
            and _is_sorted(
                emission_event_rows,
                key_fn=lambda row: (
                    int(_as_int(row.get("tick", 0), 0)),
                    str(row.get("run_id", "")),
                    str(row.get("material_id", "")),
                    str(row.get("event_id", "")),
                ),
            )
            and _is_sorted(
                ledger_rows,
                key_fn=lambda row: (
                    int(_as_int(row.get("tick", 0), 0)),
                    str(row.get("source_id", "")),
                    str(row.get("transformation_id", "")),
                    str(row.get("entry_id", "")),
                ),
            )
        )
        bounded_evaluation_ok = bool(
            bounded_evaluation_ok
            and tick_reactions <= reaction_cap
            and tick_cost_units <= cost_cap
            and tick_model_cost <= model_cost_cap
            and tick_emission_event_count <= emission_cap
        )

        per_tick_reactions.append(int(tick_reactions))
        per_tick_degraded.append(int(tick_degraded))
        per_tick_mass_residual.append(int(tick_mass_residual))
        per_tick_energy_residual.append(int(tick_energy_residual))
        per_tick_entropy_increment.append(int(tick_entropy_increment))
        per_tick_emission_total.append(int(tick_emission_total))
        per_tick_cost_units.append(int(tick_cost_units))
        per_tick_hashes.append(
            canonical_sha256(
                {
                    "tick": int(tick),
                    "reaction_rows": [
                        str(row.get("event_id", "")).strip()
                        for row in reaction_event_rows
                        if int(_as_int(row.get("tick", 0), 0)) == int(tick)
                    ],
                    "emission_rows": [
                        str(row.get("event_id", "")).strip()
                        for row in emission_event_rows
                        if int(_as_int(row.get("tick", 0), 0)) == int(tick)
                    ],
                    "ledger_rows": [
                        str(row.get("entry_id", "")).strip()
                        for row in ledger_rows
                        if int(_as_int(row.get("tick", 0), 0)) == int(tick)
                    ],
                    "deferred_for_stride": list(_sorted_tokens(deferred_for_stride)),
                    "deferred_for_cap": list(_sorted_tokens(deferred_for_cap)),
                }
            )
        )

    mass_summary = _summarize_residuals(per_tick_mass_residual)
    energy_summary = _summarize_residuals(per_tick_energy_residual)
    max_residual_abs = int(_envelope_defaults(budget_id).get("max_residual_abs", 1))
    no_silent_mass_changes = bool(mass_summary.get("max_abs", 0) <= max_residual_abs)
    no_silent_energy_changes = bool(energy_summary.get("max_abs", 0) <= max_residual_abs)
    all_outputs_logged = bool(len(ledger_rows) >= len(reaction_event_rows))
    degradation_rows_sorted = sorted(
        (dict(row) for row in degradation_event_rows if isinstance(row, Mapping)),
        key=lambda row: (
            int(_as_int(row.get("tick", 0), 0)),
            str(row.get("run_id", "")),
            int(_as_int(row.get("step_order", 99), 99)),
            str(row.get("event_kind", "")),
        ),
    )
    degradation_order_deterministic = degradation_rows_sorted == [
        dict(row) for row in list(degradation_event_rows or []) if isinstance(row, Mapping)
    ]

    reaction_hash_chain = _chain(
        reaction_event_rows,
        key_fn=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
    )
    energy_hash_chain = _chain(
        ledger_rows,
        key_fn=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("entry_id", ""))),
    )
    emission_hash_chain = _chain(
        emission_event_rows,
        key_fn=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))),
    )
    degradation_hash_chain = _chain(
        degradation_event_rows,
        key_fn=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_kind", "")), str(row.get("run_id", ""))),
    )
    proof_tick_hash_chain = canonical_sha256(list(per_tick_hashes))

    final_pool_rows: List[dict] = []
    for key in sorted(pool_by_key.keys()):
        parts = str(key).split("::", 1)
        if len(parts) != 2:
            continue
        target_id, material_id = parts
        row = {
            "schema_version": "1.0.0",
            "target_id": str(target_id),
            "material_id": str(material_id),
            "mass_value": int(max(0, _as_int(pool_by_key.get(key, 0), 0))),
            "last_update_tick": int(max(0, horizon - 1)),
            "deterministic_fingerprint": "",
            "extensions": {},
        }
        row["deterministic_fingerprint"] = canonical_sha256(dict(row, deterministic_fingerprint=""))
        final_pool_rows.append(row)

    report = {
        "schema_version": "1.0.0",
        "result": "complete"
        if (
            deterministic_ordering_ok
            and bounded_evaluation_ok
            and no_silent_mass_changes
            and no_silent_energy_changes
            and all_outputs_logged
        )
        else "violation",
        "scenario_id": str(scenario_id),
        "tick_count": int(horizon),
        "budget_envelope_id": str(budget_id),
        "degradation_policy_order": list(_DEGRADE_ORDER),
        "metrics": {
            "total_reactions_evaluated": int(sum(per_tick_reactions)),
            "degraded_evaluation_count": int(sum(per_tick_degraded)),
            "mass_residual_stats": dict(mass_summary),
            "energy_residual_stats": dict(energy_summary),
            "entropy_increment_total": int(sum(per_tick_entropy_increment)),
            "emission_total_mass": int(sum(per_tick_emission_total)),
            "max_cost_units_observed": int(max(per_tick_cost_units or [0])),
            "proof_hash_summary": {
                "reaction_hash_chain": str(reaction_hash_chain),
                "energy_ledger_hash_chain": str(energy_hash_chain),
                "emission_hash_chain": str(emission_hash_chain),
                "degradation_hash_chain": str(degradation_hash_chain),
                "proof_tick_hash_chain": str(proof_tick_hash_chain),
            },
            "per_tick_reactions": list(per_tick_reactions),
            "per_tick_degraded": list(per_tick_degraded),
            "per_tick_mass_residual": list(per_tick_mass_residual),
            "per_tick_energy_residual": list(per_tick_energy_residual),
            "per_tick_entropy_increment": list(per_tick_entropy_increment),
            "per_tick_emission_total": list(per_tick_emission_total),
            "per_tick_cost_units": list(per_tick_cost_units),
        },
        "assertions": {
            "bounded_evaluation": bool(bounded_evaluation_ok),
            "deterministic_ordering": bool(deterministic_ordering_ok),
            "no_silent_mass_changes": bool(no_silent_mass_changes),
            "no_silent_energy_changes": bool(no_silent_energy_changes),
            "all_outputs_logged": bool(all_outputs_logged),
            "degradation_order_deterministic": bool(
                list(scenario_row.get("degradation_policy_order") or _DEGRADE_ORDER) == list(_DEGRADE_ORDER)
                and bool(degradation_order_deterministic)
            ),
        },
        "extensions": {
            "reaction_event_rows": [dict(row) for row in sorted(reaction_event_rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))],
            "energy_ledger_rows": [dict(row) for row in sorted(ledger_rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("entry_id", ""))))],
            "emission_event_rows": [dict(row) for row in sorted(emission_event_rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("event_id", ""))))],
            "degradation_event_rows": [dict(row) for row in list(degradation_rows_sorted)],
            "decision_log_rows": [dict(row) for row in sorted(decision_log_rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), int(_as_int(row.get("step_order", 99), 99)), str(row.get("run_id", "")), str(row.get("reason_code", ""))))],
            "proof_hashes_per_tick": list(per_tick_hashes),
            "final_species_pool_rows": list(final_pool_rows),
            "process_run_rows": [dict(row) for row in sorted(process_run_rows, key=lambda row: (str(row.get("run_id", "")), int(_as_int(row.get("end_tick", 0), 0))))],
            "entropy_by_equipment": dict((key, int(entropy_by_equipment[key])) for key in sorted(entropy_by_equipment.keys())),
        },
        "deterministic_fingerprint": "",
    }
    if str(report.get("result", "")).strip() != "complete":
        report["errors"] = [
            {
                "code": "violation.chem.stress_assertions",
                "message": "one or more CHEM stress assertions failed",
                "path": "$.assertions",
            }
        ]
    report["deterministic_fingerprint"] = canonical_sha256(dict(report, deterministic_fingerprint=""))
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic CHEM stress scenario and emit metrics/proof summary.")
    parser.add_argument("--scenario", default="build/chem/chem_stress_scenario.json")
    parser.add_argument("--tick-count", type=int, default=0)
    parser.add_argument("--budget-envelope-id", default="chem.envelope.standard")
    parser.add_argument("--max-reaction-evaluations-per-tick", type=int, default=0)
    parser.add_argument("--max-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--max-model-cost-units-per-tick", type=int, default=0)
    parser.add_argument("--base-tick-stride", type=int, default=0)
    parser.add_argument("--max-emission-events-per-tick", type=int, default=0)
    parser.add_argument("--output", default="build/chem/chem_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_path = os.path.normpath(os.path.abspath(str(args.scenario)))
    scenario_payload = _read_json(scenario_path)
    if not scenario_payload:
        scenario_payload = generate_chem_stress_scenario(
            seed=12041,
            species_pools=64,
            reactions=96,
            process_runs=128,
            ticks=64,
            repo_root=REPO_ROOT_HINT,
        )

    defaults = _envelope_defaults(str(args.budget_envelope_id))
    report = run_chem_stress_scenario(
        scenario=scenario_payload,
        tick_count=int(args.tick_count) or int(max(1, _as_int(scenario_payload.get("tick_horizon", 64), 64))),
        budget_envelope_id=str(args.budget_envelope_id),
        max_reaction_evaluations_per_tick=int(args.max_reaction_evaluations_per_tick) or int(defaults["max_reaction_evaluations_per_tick"]),
        max_cost_units_per_tick=int(args.max_cost_units_per_tick) or int(defaults["max_cost_units_per_tick"]),
        max_model_cost_units_per_tick=int(args.max_model_cost_units_per_tick) or int(defaults["max_model_cost_units_per_tick"]),
        base_tick_stride=int(args.base_tick_stride) or int(defaults["base_tick_stride"]),
        max_emission_events_per_tick=int(args.max_emission_events_per_tick) or int(defaults["max_emission_events_per_tick"]),
    )
    report["scenario_path"] = scenario_path
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, report)
    report["output_path"] = output_abs
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
