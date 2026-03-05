#!/usr/bin/env python3
"""POLL-3 deterministic stress scenario generator."""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
from typing import Dict, Iterable, List, Mapping, Tuple


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.fields import build_field_cell, build_field_layer  # noqa: E402
from src.pollution.dispersion_engine import concentration_field_id_for_pollutant  # noqa: E402
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


_FALLBACK_POLLUTANTS = [
    "pollutant.smoke_particulate",
    "pollutant.co2_stub",
    "pollutant.toxic_gas_stub",
    "pollutant.oil_spill_stub",
]

_DEGRADATION_POLICY_ORDER = [
    "degrade.pollution.dispersion_tick_bucket",
    "degrade.pollution.cell_budget",
    "degrade.pollution.exposure_subject_budget",
    "degrade.pollution.compliance_delay",
    "degrade.pollution.measurement_refusal",
]


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


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


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_json(path: str, payload: Mapping[str, object]) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")


def _pollutant_ids(repo_root: str) -> List[str]:
    rel = "data/registries/pollutant_type_registry.json"
    payload = _read_json(os.path.join(repo_root, rel.replace("/", os.sep)))
    record = _as_map(payload.get("record"))
    rows = list(record.get("pollutant_types") or [])
    out = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        token = str(row.get("pollutant_id", "")).strip()
        if token:
            out.append(token)
    tokens = _sorted_tokens(out)
    if tokens:
        return tokens
    return list(_FALLBACK_POLLUTANTS)


def _region_ids(region_count: int) -> List[str]:
    return ["region.poll.stress.{}".format(str(idx + 1).zfill(3)) for idx in range(max(1, int(region_count)))]


def _cells_by_region(*, region_ids: List[str], cells_per_region: int) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], List[str]]:
    cell_map: Dict[str, List[str]] = {}
    neighbor_map: Dict[str, List[str]] = {}
    all_cells: List[str] = []

    for region_index, region_id in enumerate(region_ids):
        rows = int(max(2, math.sqrt(max(1, int(cells_per_region)))))
        cols = int(max(2, (int(cells_per_region) + rows - 1) // rows))
        cell_ids: List[str] = []
        for row in range(rows):
            for col in range(cols):
                if len(cell_ids) >= int(cells_per_region):
                    break
                cell_id = "cell.poll.r{}.n{}".format(
                    str(region_index + 1).zfill(3),
                    str(len(cell_ids) + 1).zfill(4),
                )
                cell_ids.append(cell_id)
            if len(cell_ids) >= int(cells_per_region):
                break

        for idx, cell_id in enumerate(cell_ids):
            neighbors = []
            if idx > 0:
                neighbors.append(cell_ids[idx - 1])
            if idx + 1 < len(cell_ids):
                neighbors.append(cell_ids[idx + 1])
            if idx >= cols:
                neighbors.append(cell_ids[idx - cols])
            if idx + cols < len(cell_ids):
                neighbors.append(cell_ids[idx + cols])
            neighbor_map[cell_id] = _sorted_tokens(neighbors)

        cell_map[region_id] = list(cell_ids)
        all_cells.extend(cell_ids)

    return (
        dict((key, list(cell_map[key])) for key in sorted(cell_map.keys())),
        dict((key, list(neighbor_map[key])) for key in sorted(neighbor_map.keys())),
        _sorted_tokens(all_cells),
    )


def _field_snapshot(
    *,
    seed: int,
    pollutant_ids: List[str],
    cell_ids: List[str],
    include_wind: bool,
) -> Tuple[List[dict], List[dict]]:
    layers: List[dict] = []
    cells: List[dict] = []

    for pollutant_id in pollutant_ids:
        field_id = concentration_field_id_for_pollutant(pollutant_id)
        if not field_id:
            continue
        layers.append(
            build_field_layer(
                field_id=field_id,
                field_type_id=field_id,
                spatial_scope_id="spatial.pollution.stress",
                resolution_level="macro",
                update_policy_id="field.pollution_profile_defined",
                extensions={"pollutant_id": pollutant_id},
            )
        )
        for cell_id in cell_ids:
            cells.append(
                build_field_cell(
                    field_id=field_id,
                    cell_id=cell_id,
                    value=0,
                    last_updated_tick=0,
                    value_kind="scalar",
                )
            )

    if include_wind:
        layers.append(
            build_field_layer(
                field_id="field.wind",
                field_type_id="field.wind",
                spatial_scope_id="spatial.pollution.stress",
                resolution_level="macro",
                update_policy_id="field.static",
                extensions={"source": "poll3.stress_generator"},
            )
        )
        for idx, cell_id in enumerate(cell_ids):
            wind_x = int(_pick(seed, "wind.x", idx, 5, offset=-2))
            wind_y = int(_pick(seed, "wind.y", idx, 5, offset=-2))
            cells.append(
                build_field_cell(
                    field_id="field.wind",
                    cell_id=cell_id,
                    value={"x": wind_x, "y": wind_y, "z": 0},
                    last_updated_tick=0,
                    value_kind="vector",
                )
            )

    return (
        [dict(row) for row in sorted(layers, key=lambda row: str(row.get("field_id", "")))],
        [
            dict(row)
            for row in sorted(
                cells,
                key=lambda row: (str(row.get("field_id", "")), str(row.get("cell_id", ""))),
            )
        ],
    )


def _source_catalog(*, seed: int, region_cell_map: Mapping[str, object]) -> List[dict]:
    catalog: List[dict] = []
    for region_index, region_id in enumerate(sorted(str(key).strip() for key in region_cell_map.keys() if str(key).strip())):
        cells = [str(cell).strip() for cell in list(region_cell_map.get(region_id) or []) if str(cell).strip()]
        if not cells:
            continue
        factory_count = 2
        for idx in range(factory_count):
            cell_id = cells[_pick(seed, "source.factory.cell", region_index * 100 + idx, len(cells))]
            catalog.append(
                {
                    "source_id": "source.factory.{}.{}".format(str(region_index + 1).zfill(3), str(idx + 1).zfill(2)),
                    "region_id": region_id,
                    "cell_id": cell_id,
                    "origin_kind": "reaction",
                    "source_class": "factory",
                    "pollutant_ids": ["pollutant.co2_stub", "pollutant.toxic_gas_stub"],
                    "source_domain_id": "CHEM",
                }
            )

        fire_cell = cells[_pick(seed, "source.fire.cell", region_index, len(cells))]
        catalog.append(
            {
                "source_id": "source.fire.{}".format(str(region_index + 1).zfill(3)),
                "region_id": region_id,
                "cell_id": fire_cell,
                "origin_kind": "fire",
                "source_class": "fire",
                "pollutant_ids": ["pollutant.smoke_particulate", "pollutant.toxic_gas_stub"],
                "source_domain_id": "THERM",
            }
        )

        spill_cell = cells[_pick(seed, "source.spill.cell", region_index, len(cells))]
        catalog.append(
            {
                "source_id": "source.spill.{}".format(str(region_index + 1).zfill(3)),
                "region_id": region_id,
                "cell_id": spill_cell,
                "origin_kind": "leak",
                "source_class": "spill",
                "pollutant_ids": ["pollutant.oil_spill_stub", "pollutant.toxic_gas_stub"],
                "source_domain_id": "FLUID",
            }
        )

        stack_cell = cells[_pick(seed, "source.stack.cell", region_index, len(cells))]
        catalog.append(
            {
                "source_id": "source.stack.{}".format(str(region_index + 1).zfill(3)),
                "region_id": region_id,
                "cell_id": stack_cell,
                "origin_kind": "industrial",
                "source_class": "plant_stack",
                "pollutant_ids": ["pollutant.co2_stub", "pollutant.smoke_particulate"],
                "source_domain_id": "ELEC",
            }
        )

    return sorted(catalog, key=lambda row: str(row.get("source_id", "")))


def _mass_bounds_for_source(source_class: str) -> Tuple[int, int]:
    token = str(source_class or "").strip().lower()
    if token == "factory":
        return 24, 88
    if token == "fire":
        return 30, 96
    if token == "spill":
        return 18, 72
    return 22, 84


def _emission_schedule(
    *,
    seed: int,
    tick_horizon: int,
    emissions_per_tick: int,
    source_catalog: List[dict],
    pollutant_ids: List[str],
) -> List[dict]:
    rows: List[dict] = []
    if not source_catalog:
        return rows
    active_pollutants = set(_sorted_tokens(pollutant_ids))
    for tick in range(max(1, int(tick_horizon))):
        event_count = max(1, int(emissions_per_tick))
        for event_index in range(event_count):
            source_idx = _pick(seed, "schedule.source", tick * 1000 + event_index, len(source_catalog))
            source_row = dict(source_catalog[source_idx])
            candidates = [
                token
                for token in _sorted_tokens(list(source_row.get("pollutant_ids") or []))
                if token in active_pollutants
            ]
            if not candidates:
                candidates = [token for token in _sorted_tokens(active_pollutants)]
            if not candidates:
                continue
            pollutant_id = candidates[_pick(seed, "schedule.pollutant", tick * 1000 + event_index, len(candidates))]
            mass_min, mass_max = _mass_bounds_for_source(str(source_row.get("source_class", "")))
            emitted_mass = int(mass_min + _pick(seed, "schedule.mass", tick * 1000 + event_index, max(1, mass_max - mass_min + 1)))
            event_seed = {
                "tick": int(tick),
                "source_id": str(source_row.get("source_id", "")),
                "pollutant_id": str(pollutant_id),
                "event_index": int(event_index),
            }
            rows.append(
                {
                    "schema_version": "1.0.0",
                    "event_id": "event.pollution.stress.emit.{}".format(canonical_sha256(event_seed)[:16]),
                    "tick": int(tick),
                    "origin_kind": str(source_row.get("origin_kind", "industrial")),
                    "origin_id": str(source_row.get("source_id", "")),
                    "pollutant_id": str(pollutant_id),
                    "emitted_mass": int(max(0, emitted_mass)),
                    "spatial_scope_id": str(source_row.get("cell_id", "")),
                    "region_id": str(source_row.get("region_id", "")),
                    "extensions": {
                        "source_class": str(source_row.get("source_class", "")),
                        "source_domain_id": str(source_row.get("source_domain_id", "")),
                    },
                }
            )
    return sorted(
        rows,
        key=lambda row: (
            int(_as_int(row.get("tick", 0), 0)),
            str(row.get("origin_id", "")),
            str(row.get("event_id", "")),
        ),
    )


def _subject_rows(*, seed: int, cell_ids: List[str], subject_count: int) -> List[dict]:
    rows: List[dict] = []
    if not cell_ids:
        return rows
    for idx in range(max(1, int(subject_count))):
        cell_id = cell_ids[_pick(seed, "subject.cell", idx, len(cell_ids))]
        susceptibility = int(700 + _pick(seed, "subject.factor", idx, 901))
        rows.append(
            {
                "subject_id": "subject.poll.stress.{}".format(str(idx + 1).zfill(5)),
                "spatial_scope_id": str(cell_id),
                "exposure_factor_permille": int(susceptibility),
                "priority_class": "critical" if _pick(seed, "subject.priority", idx, 7) == 0 else "background",
                "extensions": {
                    "susceptibility_stub": int(susceptibility),
                    "source": "poll3.stress_generator",
                },
            }
        )
    return sorted(rows, key=lambda row: str(row.get("subject_id", "")))


def _measurement_schedule(
    *,
    seed: int,
    tick_horizon: int,
    subject_rows: List[dict],
    pollutant_ids: List[str],
    measurements_per_tick: int,
) -> List[dict]:
    rows: List[dict] = []
    if (not subject_rows) or (not pollutant_ids):
        return rows
    for tick in range(max(1, int(tick_horizon))):
        for idx in range(max(1, int(measurements_per_tick))):
            subject_row = dict(subject_rows[_pick(seed, "measure.subject", tick * 100 + idx, len(subject_rows))])
            pollutant_id = pollutant_ids[_pick(seed, "measure.pollutant", tick * 100 + idx, len(pollutant_ids))]
            priority = "low" if _pick(seed, "measure.priority", tick * 100 + idx, 5) else "high"
            rows.append(
                {
                    "measurement_task_id": "task.poll.measure.{}.{}".format(str(tick).zfill(4), str(idx + 1).zfill(3)),
                    "tick": int(tick),
                    "subject_id": str(subject_row.get("subject_id", "")),
                    "spatial_scope_id": str(subject_row.get("spatial_scope_id", "")),
                    "pollutant_id": str(pollutant_id),
                    "sensor_type_id": "sensor.water_quality_basic"
                    if str(pollutant_id) == "pollutant.oil_spill_stub"
                    else "sensor.air_quality_basic",
                    "instrument_id": "instrument.poll.sensor.{}".format(str(idx + 1).zfill(4)),
                    "priority_class": str(priority),
                    "extensions": {"task_type_id": "task.measure_pollution"},
                }
            )
    return sorted(rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("measurement_task_id", ""))))


def _compliance_schedule(
    *,
    tick_horizon: int,
    region_ids: List[str],
    interval_ticks: int,
) -> List[dict]:
    rows: List[dict] = []
    interval = int(max(1, int(interval_ticks)))
    for tick in range(0, max(1, int(tick_horizon)), interval):
        for region_index, region_id in enumerate(region_ids):
            rows.append(
                {
                    "schedule_id": "sched.poll.compliance.{}.{}".format(str(region_index + 1).zfill(3), str(tick).zfill(4)),
                    "tick": int(tick),
                    "region_id": str(region_id),
                    "observed_statistic": "max" if ((tick // interval) + region_index) % 2 == 0 else "avg",
                    "priority_class": "high" if region_index == 0 else "normal",
                    "institution_id": "institution.pollution.default",
                    "channel_id": "channel.pollution.missing",
                }
            )
    return sorted(rows, key=lambda row: (int(_as_int(row.get("tick", 0), 0)), str(row.get("region_id", ""))))


def generate_poll_stress_scenario(
    *,
    seed: int,
    region_count: int,
    cells_per_region: int,
    subject_count: int,
    tick_horizon: int,
    emissions_per_tick: int,
    measurements_per_tick: int,
    compliance_interval_ticks: int,
    include_wind_field: bool,
    repo_root: str | None = None,
) -> dict:
    root = os.path.normpath(os.path.abspath(str(repo_root or REPO_ROOT_HINT)))

    seed_i = int(max(1, _as_int(seed, 1)))
    region_count_i = int(max(1, _as_int(region_count, 4)))
    cells_per_region_i = int(max(4, _as_int(cells_per_region, 16)))
    subject_count_i = int(max(1, _as_int(subject_count, 96)))
    tick_horizon_i = int(max(8, _as_int(tick_horizon, 64)))
    emissions_per_tick_i = int(max(1, _as_int(emissions_per_tick, 8)))
    measurements_per_tick_i = int(max(0, _as_int(measurements_per_tick, 4)))
    compliance_interval_i = int(max(1, _as_int(compliance_interval_ticks, 6)))

    pollutant_ids = _pollutant_ids(root)
    region_ids = _region_ids(region_count_i)
    region_cell_map, neighbor_map_by_cell, all_cells = _cells_by_region(
        region_ids=region_ids,
        cells_per_region=cells_per_region_i,
    )
    field_layers, field_cells = _field_snapshot(
        seed=seed_i,
        pollutant_ids=pollutant_ids,
        cell_ids=all_cells,
        include_wind=bool(include_wind_field),
    )
    source_catalog = _source_catalog(seed=seed_i, region_cell_map=region_cell_map)
    emission_schedule_rows = _emission_schedule(
        seed=seed_i,
        tick_horizon=tick_horizon_i,
        emissions_per_tick=emissions_per_tick_i,
        source_catalog=source_catalog,
        pollutant_ids=pollutant_ids,
    )
    subjects = _subject_rows(seed=seed_i, cell_ids=all_cells, subject_count=subject_count_i)
    measurement_schedule_rows = _measurement_schedule(
        seed=seed_i,
        tick_horizon=tick_horizon_i,
        subject_rows=subjects,
        pollutant_ids=pollutant_ids,
        measurements_per_tick=measurements_per_tick_i,
    )
    compliance_schedule_rows = _compliance_schedule(
        tick_horizon=tick_horizon_i,
        region_ids=region_ids,
        interval_ticks=compliance_interval_i,
    )

    scenario_id = "scenario.poll.stress.{}".format(
        canonical_sha256(
            {
                "seed": int(seed_i),
                "region_count": int(region_count_i),
                "cells_per_region": int(cells_per_region_i),
                "subject_count": int(subject_count_i),
                "tick_horizon": int(tick_horizon_i),
                "emissions_per_tick": int(emissions_per_tick_i),
                "measurements_per_tick": int(measurements_per_tick_i),
                "compliance_interval_ticks": int(compliance_interval_i),
                "include_wind_field": bool(include_wind_field),
            }
        )[:12]
    )

    scenario = {
        "schema_version": "1.0.0",
        "scenario_id": str(scenario_id),
        "scenario_seed": int(seed_i),
        "tick_horizon": int(tick_horizon_i),
        "pollutant_ids": list(_sorted_tokens(pollutant_ids)),
        "region_cell_map": dict((key, list(region_cell_map[key])) for key in sorted(region_cell_map.keys())),
        "neighbor_map_by_cell": dict((key, list(neighbor_map_by_cell[key])) for key in sorted(neighbor_map_by_cell.keys())),
        "source_catalog": [dict(row) for row in source_catalog],
        "emission_schedule_rows": [dict(row) for row in emission_schedule_rows],
        "subject_rows": [dict(row) for row in subjects],
        "measurement_schedule_rows": [dict(row) for row in measurement_schedule_rows],
        "compliance_schedule_rows": [dict(row) for row in compliance_schedule_rows],
        "degradation_policy_order": list(_DEGRADATION_POLICY_ORDER),
        "budget_defaults": {
            "max_compute_units_per_tick": 4096,
            "dispersion_tick_stride_base": 1,
            "max_cell_updates_per_tick": int(max(16, min(512, cells_per_region_i * max(1, region_count_i) // 2))),
            "max_subject_updates_per_tick": int(max(16, min(512, subject_count_i // 2))),
            "max_compliance_reports_per_tick": int(max(1, min(64, region_count_i // 2 + 1))),
            "max_measurements_per_tick": int(max(1, min(128, measurements_per_tick_i * max(1, region_count_i)))),
        },
        "initial_state_snapshot": {
            "schema_version": "1.0.0",
            "field_layers": [dict(row) for row in field_layers],
            "field_cells": [dict(row) for row in field_cells],
            "pollution_subject_rows": [dict(row) for row in subjects],
            "pollution_source_event_rows": [],
            "pollution_total_rows": [],
            "pollution_dispersion_step_rows": [],
            "pollution_deposition_rows": [],
            "pollution_exposure_state_rows": [],
            "pollution_exposure_increment_rows": [],
            "pollution_health_risk_event_rows": [],
            "pollution_measurement_rows": [],
            "pollution_compliance_report_rows": [],
            "pollution_compliance_violation_rows": [],
            "pollution_dispersion_degrade_rows": [],
            "control_decision_log": [],
            "simulation_time": {
                "tick": 0,
                "tick_rate": 1,
                "deterministic_clock": {
                    "tick_duration_ms": 1000,
                },
            },
        },
        "deterministic_fingerprint": "",
        "extensions": {
            "include_wind_field": bool(include_wind_field),
            "region_count": int(region_count_i),
            "cells_per_region": int(cells_per_region_i),
            "subject_count": int(subject_count_i),
            "generator": "tools/pollution/tool_generate_poll_stress.py",
        },
    }
    scenario_seed = dict(scenario)
    scenario_seed["deterministic_fingerprint"] = ""
    scenario["deterministic_fingerprint"] = canonical_sha256(scenario_seed)
    return scenario


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic POLL-3 stress scenario.")
    parser.add_argument("--seed", type=int, default=9301)
    parser.add_argument("--region-count", type=int, default=3)
    parser.add_argument("--cells-per-region", type=int, default=9)
    parser.add_argument("--subject-count", type=int, default=36)
    parser.add_argument("--tick-horizon", type=int, default=24)
    parser.add_argument("--emissions-per-tick", type=int, default=3)
    parser.add_argument("--measurements-per-tick", type=int, default=1)
    parser.add_argument("--compliance-interval-ticks", type=int, default=4)
    parser.add_argument("--include-wind-field", action="store_true")
    parser.add_argument("--output", default="build/pollution/poll3_stress_scenario.json")
    return parser


def main() -> int:
    args = _parser().parse_args()
    scenario = generate_poll_stress_scenario(
        seed=int(args.seed),
        region_count=int(args.region_count),
        cells_per_region=int(args.cells_per_region),
        subject_count=int(args.subject_count),
        tick_horizon=int(args.tick_horizon),
        emissions_per_tick=int(args.emissions_per_tick),
        measurements_per_tick=int(args.measurements_per_tick),
        compliance_interval_ticks=int(args.compliance_interval_ticks),
        include_wind_field=bool(args.include_wind_field),
        repo_root=REPO_ROOT_HINT,
    )
    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, scenario)
    report = copy.deepcopy(dict(scenario))
    report["output_path"] = output_abs
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
