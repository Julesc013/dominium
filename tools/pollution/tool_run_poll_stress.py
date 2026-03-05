#!/usr/bin/env python3
"""POLL-3 deterministic stress harness."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Dict, List, Mapping

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from tools.pollution.tool_generate_poll_stress import (  # noqa: E402
    _as_int,
    _as_map,
    _sorted_tokens,
    _write_json,
    generate_poll_stress_scenario,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _read_json(path: str) -> dict:
    try:
        payload = json.load(open(path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _priority_rank(token: object) -> int:
    value = str(token or "").strip().lower()
    if value in {"critical", "high"}:
        return 0
    if value in {"normal", "medium"}:
        return 1
    return 2


def _chain(rows: object, key_fn) -> str:
    chain = "0" * 64
    for row in sorted((dict(item) for item in list(rows or []) if isinstance(item, Mapping)), key=key_fn):
        chain = canonical_sha256({"previous_hash": chain, "row_hash": canonical_sha256(row)})
    return chain


def _is_sorted(rows: object, key_fn) -> bool:
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    return normalized == sorted(normalized, key=key_fn)


def _seed_state(initial_snapshot: Mapping[str, object]) -> dict:
    state = copy.deepcopy(dict(initial_snapshot or {}))
    defaults = {
        "pollution_source_event_rows": [],
        "pollution_total_rows": [],
        "pollution_dispersion_step_rows": [],
        "pollution_deposition_rows": [],
        "pollution_exposure_state_rows": [],
        "pollution_exposure_increment_rows": [],
        "pollution_health_risk_event_rows": [],
        "pollution_hazard_hook_rows": [],
        "pollution_measurement_rows": [],
        "pollution_compliance_report_rows": [],
        "pollution_compliance_violation_rows": [],
        "pollution_dispersion_degrade_rows": [],
        "control_decision_log": [],
        "info_artifact_rows": [],
        "knowledge_artifacts": [],
        "knowledge_receipt_rows": [],
        "field_layers": [],
        "field_cells": [],
    }
    for key, value in defaults.items():
        state.setdefault(key, copy.deepcopy(value))
    state.setdefault(
        "simulation_time",
        {"tick": 0, "tick_rate": 1, "deterministic_clock": {"tick_duration_ms": 1000}},
    )
    return state


def _execute_process(
    *,
    state: dict,
    process_id: str,
    intent_id: str,
    inputs: Mapping[str, object],
    max_compute_units_per_tick: int,
) -> dict:
    from tools.xstack.sessionx.process_runtime import execute_intent
    from tools.xstack.testx.tests.construction_testlib import (
        authority_context as construction_authority_context,
        law_profile as construction_law_profile,
        policy_context as construction_policy_context,
    )

    allowed_processes = [
        "process.pollution_emit",
        "process.pollution_dispersion_tick",
        "process.pollution_measure",
        "process.pollution_compliance_tick",
    ]
    law = construction_law_profile(allowed_processes)
    authority = construction_authority_context(
        ["session.boot", "entitlement.control.admin", "entitlement.inspect", "entitlement.tool.use"],
        privilege_level="operator",
    )
    policy = construction_policy_context(max_compute_units_per_tick=int(max(1, int(max_compute_units_per_tick))))

    return execute_intent(
        state=state,
        intent={"intent_id": str(intent_id), "process_id": str(process_id), "inputs": dict(inputs or {})},
        law_profile=copy.deepcopy(law),
        authority_context=copy.deepcopy(authority),
        navigation_indices={},
        policy_context=copy.deepcopy(policy),
    )


def _append_decision(
    *,
    state: dict,
    tick: int,
    reason_code: str,
    result: str,
    target_id: str,
    details: Mapping[str, object] | None = None,
) -> None:
    rows = [dict(row) for row in list(state.get("control_decision_log") or []) if isinstance(row, Mapping)]
    seed = {
        "tick": int(max(0, _as_int(tick, 0))),
        "reason_code": str(reason_code),
        "result": str(result),
        "target_id": str(target_id),
        "details": dict(details or {}),
        "ordinal": int(len(rows)),
    }
    rows.append(
        {
            "decision_id": "decision.pollution.stress.{}".format(canonical_sha256(seed)[:16]),
            "tick": int(max(0, _as_int(tick, 0))),
            "process_id": "tool.run_poll_stress",
            "result": str(result),
            "reason_code": str(reason_code),
            "extensions": dict(details or {}),
        }
    )
    state["control_decision_log"] = sorted(
        rows,
        key=lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("decision_id", ""))),
    )


def _max_pollution_concentration(state: Mapping[str, object]) -> int:
    values = []
    for row in list(state.get("field_cells") or []):
        if not isinstance(row, Mapping):
            continue
        if not str(row.get("field_id", "")).startswith("field.pollution."):
            continue
        values.append(int(max(0, _as_int(row.get("value", 0), 0))))
    return int(max(values or [0]))


def _exposure_total(state: Mapping[str, object]) -> int:
    return int(
        sum(
            int(max(0, _as_int(row.get("accumulated_exposure", 0), 0)))
            for row in list(state.get("pollution_exposure_state_rows") or [])
            if isinstance(row, Mapping)
        )
    )


def _proof_hash_summary(state: Mapping[str, object]) -> dict:
    return {
        "pollution_emission_hash_chain": str(state.get("pollution_source_hash_chain", "")).strip(),
        "pollution_field_hash_chain": str(state.get("pollution_field_hash_chain", "")).strip(),
        "exposure_hash_chain": str(state.get("pollution_exposure_hash_chain", "")).strip(),
        "compliance_hash_chain": str(state.get("pollution_compliance_report_hash_chain", "")).strip(),
        "degradation_event_hash_chain": str(state.get("pollution_dispersion_degrade_hash_chain", "")).strip(),
    }


def _envelope_defaults(budget_envelope_id: str) -> dict:
    token = str(budget_envelope_id or "").strip().lower()
    if token == "poll.envelope.tight":
        return {
            "max_compute_units_per_tick": 820,
            "dispersion_tick_stride_base": 2,
            "max_cell_updates_per_tick": 36,
            "max_subject_updates_per_tick": 42,
            "max_compliance_reports_per_tick": 2,
            "max_measurements_per_tick": 6,
        }
    if token == "poll.envelope.rank_strict":
        return {
            "max_compute_units_per_tick": 1600,
            "dispersion_tick_stride_base": 1,
            "max_cell_updates_per_tick": 96,
            "max_subject_updates_per_tick": 96,
            "max_compliance_reports_per_tick": 8,
            "max_measurements_per_tick": 14,
        }
    return {
        "max_compute_units_per_tick": 1200,
        "dispersion_tick_stride_base": 1,
        "max_cell_updates_per_tick": 72,
        "max_subject_updates_per_tick": 72,
        "max_compliance_reports_per_tick": 6,
        "max_measurements_per_tick": 10,
    }

def run_poll_stress_scenario(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str,
    max_compute_units_per_tick: int,
    dispersion_tick_stride_base: int,
    max_cell_updates_per_tick: int,
    max_subject_updates_per_tick: int,
    max_compliance_reports_per_tick: int,
    max_measurements_per_tick: int,
) -> dict:
    scenario_row = copy.deepcopy(dict(scenario or {}))
    scenario_id = str(scenario_row.get("scenario_id", "")).strip() or "scenario.poll.unknown"
    horizon = int(max(1, _as_int(tick_count, _as_int(scenario_row.get("tick_horizon", 48), 48))))

    defaults = dict(_envelope_defaults(str(budget_envelope_id)))
    defaults.update(_as_map(scenario_row.get("budget_defaults")))

    compute_cap = int(max(1, _as_int(max_compute_units_per_tick, _as_int(defaults.get("max_compute_units_per_tick", 1200), 1200))))
    stride_base = int(max(1, _as_int(dispersion_tick_stride_base, _as_int(defaults.get("dispersion_tick_stride_base", 1), 1))))
    cell_cap_base = int(max(1, _as_int(max_cell_updates_per_tick, _as_int(defaults.get("max_cell_updates_per_tick", 72), 72))))
    subject_cap_base = int(max(1, _as_int(max_subject_updates_per_tick, _as_int(defaults.get("max_subject_updates_per_tick", 72), 72))))
    compliance_cap_base = int(max(1, _as_int(max_compliance_reports_per_tick, _as_int(defaults.get("max_compliance_reports_per_tick", 6), 6))))
    measurement_cap_base = int(max(1, _as_int(max_measurements_per_tick, _as_int(defaults.get("max_measurements_per_tick", 10), 10))))

    pollutant_ids = _sorted_tokens(list(scenario_row.get("pollutant_ids") or []))
    if not pollutant_ids:
        pollutant_ids = [
            "pollutant.smoke_particulate",
            "pollutant.co2_stub",
            "pollutant.toxic_gas_stub",
            "pollutant.oil_spill_stub",
        ]

    region_cell_map = dict(
        (
            str(region_id).strip(),
            [str(cell_id).strip() for cell_id in list(cell_ids or []) if str(cell_id).strip()],
        )
        for region_id, cell_ids in sorted(_as_map(scenario_row.get("region_cell_map")).items(), key=lambda item: str(item[0]))
        if str(region_id).strip()
    )
    all_cells = _sorted_tokens([cell_id for cell_ids in region_cell_map.values() for cell_id in list(cell_ids or [])])
    neighbor_map_by_cell = dict(
        (
            str(cell_id).strip(),
            [str(neighbor).strip() for neighbor in list(neighbors or []) if str(neighbor).strip()],
        )
        for cell_id, neighbors in sorted(_as_map(scenario_row.get("neighbor_map_by_cell")).items(), key=lambda item: str(item[0]))
        if str(cell_id).strip()
    )

    emission_rows_by_tick: Dict[int, List[dict]] = {}
    for row in [dict(item) for item in list(scenario_row.get("emission_schedule_rows") or []) if isinstance(item, Mapping)]:
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        emission_rows_by_tick.setdefault(tick, []).append(row)

    measurement_rows_by_tick: Dict[int, List[dict]] = {}
    for row in [dict(item) for item in list(scenario_row.get("measurement_schedule_rows") or []) if isinstance(item, Mapping)]:
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        measurement_rows_by_tick.setdefault(tick, []).append(row)

    compliance_rows_by_tick: Dict[int, List[dict]] = {}
    for row in [dict(item) for item in list(scenario_row.get("compliance_schedule_rows") or []) if isinstance(item, Mapping)]:
        tick = int(max(0, _as_int(row.get("tick", 0), 0)))
        compliance_rows_by_tick.setdefault(tick, []).append(row)

    subject_rows = [dict(row) for row in list(scenario_row.get("subject_rows") or []) if isinstance(row, Mapping)]
    pending_compliance_rows: List[dict] = []
    state = _seed_state(_as_map(scenario_row.get("initial_state_snapshot")))

    per_tick_field_workload: List[int] = []
    per_tick_degraded_cell_updates: List[int] = []
    per_tick_concentration_max: List[int] = []
    per_tick_exposure_totals: List[int] = []
    per_tick_threshold_events: List[int] = []
    per_tick_compliance_reports: List[int] = []
    per_tick_cost_units: List[int] = []

    total_measurement_refusals = 0
    total_compliance_delays = 0
    total_degraded_dispersion_ticks = 0

    deterministic_ordering_ok = True
    no_silent_field_writes = True
    all_events_logged = True
    bounded_execution = True

    for tick in range(horizon):
        tick_cost_units = 0

        scheduled_emissions = sorted(
            [dict(row) for row in list(emission_rows_by_tick.get(tick) or []) if isinstance(row, Mapping)],
            key=lambda row: (str(row.get("origin_id", "")), str(row.get("event_id", ""))),
        )
        if scheduled_emissions:
            emit_result = _execute_process(
                state=state,
                process_id="process.pollution_emit",
                intent_id="intent.poll.stress.emit.{}".format(str(tick).zfill(4)),
                inputs={"policy_id": "poll.policy.coarse_diffuse", "events": scheduled_emissions},
                max_compute_units_per_tick=compute_cap,
            )
            if str(emit_result.get("result", "")).strip() != "complete":
                return {
                    "schema_version": "1.0.0",
                    "result": "refused",
                    "scenario_id": scenario_id,
                    "errors": [{"code": "refusal.poll.stress.emit_failed", "message": str(emit_result)}],
                }
            tick_cost_units += int(len(scheduled_emissions))

        expected_cell_work = int(max(1, len(all_cells) * max(1, len(pollutant_ids))))
        expected_subject_work = int(max(1, len(subject_rows)))
        expected_measure_work = int(len(list(measurement_rows_by_tick.get(tick) or [])))
        expected_compliance_work = int(len(list(compliance_rows_by_tick.get(tick) or [])) + len(pending_compliance_rows))
        expected_total = int(expected_cell_work + expected_subject_work + expected_measure_work + expected_compliance_work)
        pressure_permille = int(max(0, ((expected_total - compute_cap) * 1000) // max(1, expected_total)))

        dispersion_stride = int(max(1, stride_base + (pressure_permille // 500)))
        dynamic_cell_cap = int(max(1, (cell_cap_base * max(250, 1000 - pressure_permille)) // 1000))
        dynamic_subject_cap = int(max(1, (subject_cap_base * max(250, 1000 - pressure_permille)) // 1000))
        dynamic_compliance_cap = int(max(1, (compliance_cap_base * max(350, 1000 - pressure_permille)) // 1000))
        dynamic_measurement_cap = int(max(1, (measurement_cap_base * max(300, 1000 - pressure_permille)) // 1000))

        dispersion_ran = bool((tick % dispersion_stride) == 0)
        if not dispersion_ran:
            total_degraded_dispersion_ticks += 1
            _append_decision(
                state=state,
                tick=tick,
                reason_code="degrade.pollution.dispersion_tick_bucket",
                target_id="pollution.global",
                result="degraded",
                details={"dispersion_tick_stride": int(dispersion_stride), "pressure_permille": int(pressure_permille)},
            )

        if dispersion_ran:
            before_dispersion_step_count = int(len(list(state.get("pollution_dispersion_step_rows") or [])))
            before_degrade_row_count = int(len(list(state.get("pollution_dispersion_degrade_rows") or [])))
            dispersion_result = _execute_process(
                state=state,
                process_id="process.pollution_dispersion_tick",
                intent_id="intent.poll.stress.dispersion.{}".format(str(tick).zfill(4)),
                inputs={
                    "field_layers": list(state.get("field_layers") or []),
                    "field_cells": list(state.get("field_cells") or []),
                    "neighbor_map_by_cell": dict(neighbor_map_by_cell),
                    "subjects": [dict(row) for row in subject_rows],
                    "max_cell_updates_per_tick": int(dynamic_cell_cap),
                    "max_subject_updates_per_tick": int(dynamic_subject_cap),
                    "wind_field_id": "field.wind",
                },
                max_compute_units_per_tick=compute_cap,
            )
            if str(dispersion_result.get("result", "")).strip() != "complete":
                return {
                    "schema_version": "1.0.0",
                    "result": "refused",
                    "scenario_id": scenario_id,
                    "errors": [{"code": "refusal.poll.stress.dispersion_failed", "message": str(dispersion_result)}],
                }

            metadata = _as_map(dispersion_result.get("result_metadata"))
            applied_updates = int(max(0, _as_int(metadata.get("applied_update_count", 0), 0)))
            per_tick_field_workload.append(int(applied_updates))
            deferred_cells = _sorted_tokens(list(metadata.get("deferred_cell_ids") or []))
            per_tick_degraded_cell_updates.append(int(len(deferred_cells)))
            tick_cost_units += int(applied_updates)

            if bool(metadata.get("degraded", False)):
                _append_decision(
                    state=state,
                    tick=tick,
                    reason_code="degrade.pollution.cell_budget",
                    target_id="pollution.dispersion",
                    result="degraded",
                    details={"deferred_cell_count": int(len(deferred_cells)), "max_cell_updates_per_tick": int(dynamic_cell_cap)},
                )
                all_events_logged = bool(all_events_logged and (int(len(list(state.get("pollution_dispersion_degrade_rows") or []))) > before_degrade_row_count))

            if int(max(0, _as_int(metadata.get("exposure_increment_count", 0), 0))) <= 0 and dynamic_subject_cap < len(subject_rows):
                _append_decision(
                    state=state,
                    tick=tick,
                    reason_code="degrade.pollution.exposure_subject_budget",
                    target_id="pollution.exposure",
                    result="degraded",
                    details={"max_subject_updates_per_tick": int(dynamic_subject_cap)},
                )

            after_dispersion_step_count = int(len(list(state.get("pollution_dispersion_step_rows") or [])))
            if applied_updates > 0 and after_dispersion_step_count <= before_dispersion_step_count:
                no_silent_field_writes = False
        else:
            per_tick_field_workload.append(0)
            per_tick_degraded_cell_updates.append(0)

        scheduled_measurements = sorted(
            [dict(row) for row in list(measurement_rows_by_tick.get(tick) or []) if isinstance(row, Mapping)],
            key=lambda row: (_priority_rank(row.get("priority_class")), str(row.get("measurement_task_id", ""))),
        )
        processed_measurements = 0
        for row in scheduled_measurements:
            priority = str(row.get("priority_class", "low")).strip().lower()
            if processed_measurements >= dynamic_measurement_cap:
                if priority in {"critical", "high"}:
                    deferred = dict(row)
                    deferred["tick"] = int(tick + 1)
                    measurement_rows_by_tick.setdefault(int(tick + 1), []).append(deferred)
                    _append_decision(
                        state=state,
                        tick=tick,
                        reason_code="degrade.pollution.measurement_delay",
                        target_id=str(row.get("measurement_task_id", "")),
                        result="degraded",
                        details={"priority_class": str(priority)},
                    )
                else:
                    total_measurement_refusals += 1
                    _append_decision(
                        state=state,
                        tick=tick,
                        reason_code="degrade.pollution.measurement_refusal",
                        target_id=str(row.get("measurement_task_id", "")),
                        result="refused",
                        details={"priority_class": str(priority)},
                    )
                continue
            measure_out = _execute_process(
                state=state,
                process_id="process.pollution_measure",
                intent_id="intent.poll.stress.measure.{}.{}".format(str(tick).zfill(4), str(processed_measurements + 1).zfill(3)),
                inputs={
                    "pollutant_id": str(row.get("pollutant_id", "")),
                    "spatial_scope_id": str(row.get("spatial_scope_id", "")),
                    "sensor_type_id": str(row.get("sensor_type_id", "")),
                    "instrument_id": str(row.get("instrument_id", "")),
                    "subject_id": str(row.get("subject_id", "subject.poll.stress.unknown")),
                },
                max_compute_units_per_tick=compute_cap,
            )
            if str(measure_out.get("result", "")).strip() != "complete":
                return {
                    "schema_version": "1.0.0",
                    "result": "refused",
                    "scenario_id": scenario_id,
                    "errors": [{"code": "refusal.poll.stress.measure_failed", "message": str(measure_out)}],
                }
            processed_measurements += 1
            tick_cost_units += 1

        pending_compliance_rows.extend([dict(row) for row in list(compliance_rows_by_tick.get(tick) or []) if isinstance(row, Mapping)])
        pending_compliance_rows = sorted(
            pending_compliance_rows,
            key=lambda row: (_priority_rank(row.get("priority_class")), int(max(0, _as_int(row.get("tick", tick), tick))), str(row.get("schedule_id", ""))),
        )
        compliance_rows_now = list(pending_compliance_rows[:dynamic_compliance_cap])
        deferred_compliance_rows = list(pending_compliance_rows[dynamic_compliance_cap:])
        pending_compliance_rows = [dict(row) for row in deferred_compliance_rows]

        if deferred_compliance_rows:
            total_compliance_delays += len(deferred_compliance_rows)
            _append_decision(
                state=state,
                tick=tick,
                reason_code="degrade.pollution.compliance_delay",
                target_id="pollution.compliance",
                result="degraded",
                details={"deferred_report_count": int(len(deferred_compliance_rows)), "max_compliance_reports_per_tick": int(dynamic_compliance_cap)},
            )

        processed_compliance = 0
        for row in compliance_rows_now:
            region_id = str(row.get("region_id", "")).strip()
            if not region_id:
                continue
            compliance_out = _execute_process(
                state=state,
                process_id="process.pollution_compliance_tick",
                intent_id="intent.poll.stress.compliance.{}.{}".format(str(tick).zfill(4), str(processed_compliance + 1).zfill(3)),
                inputs={
                    "observed_statistic": str(row.get("observed_statistic", "avg")),
                    "region_cell_map": {region_id: list(region_cell_map.get(region_id) or [])},
                    "channel_id": str(row.get("channel_id", "channel.pollution.missing")),
                    "institution_id": str(row.get("institution_id", "institution.pollution.default")),
                },
                max_compute_units_per_tick=compute_cap,
            )
            if str(compliance_out.get("result", "")).strip() != "complete":
                return {
                    "schema_version": "1.0.0",
                    "result": "refused",
                    "scenario_id": scenario_id,
                    "errors": [{"code": "refusal.poll.stress.compliance_failed", "message": str(compliance_out)}],
                }
            processed_compliance += 1
            tick_cost_units += 1

        concentration_max = _max_pollution_concentration(state)
        exposure_total = _exposure_total(state)
        threshold_event_count = int(
            len(
                [
                    row
                    for row in list(state.get("pollution_health_risk_event_rows") or [])
                    if isinstance(row, Mapping) and int(max(0, _as_int(row.get("tick", -1), -1))) == int(tick)
                ]
            )
        )
        compliance_count = int(
            len(
                [
                    row
                    for row in list(state.get("pollution_compliance_report_rows") or [])
                    if isinstance(row, Mapping)
                    and int(max(0, _as_int(_as_map(row.get("tick_range")).get("start_tick", -1), -1))) == int(tick)
                ]
            )
        )

        per_tick_concentration_max.append(int(concentration_max))
        per_tick_exposure_totals.append(int(exposure_total))
        per_tick_threshold_events.append(int(threshold_event_count))
        per_tick_compliance_reports.append(int(compliance_count))
        per_tick_cost_units.append(int(max(0, tick_cost_units)))

        if tick_cost_units > compute_cap:
            bounded_execution = False

        deterministic_ordering_ok = bool(
            deterministic_ordering_ok
            and _is_sorted(
                state.get("control_decision_log") or [],
                lambda row: (
                    int(max(0, _as_int(row.get("tick", 0), 0))),
                    str(row.get("decision_id", "")),
                ),
            )
        )

    decision_log_rows = [dict(row) for row in list(state.get("control_decision_log") or []) if isinstance(row, Mapping)]
    degrade_reason_codes = [
        str(row.get("reason_code", "")).strip()
        for row in decision_log_rows
        if str(row.get("reason_code", "")).strip().startswith("degrade.pollution")
    ]
    proof_hash_summary = _proof_hash_summary(state)
    proof_hash_summary["decision_log_hash_chain"] = _chain(
        decision_log_rows,
        lambda row: (int(max(0, _as_int(row.get("tick", 0), 0))), str(row.get("decision_id", ""))),
    )

    assertions = {
        "bounded_execution": bool(bounded_execution),
        "deterministic_ordering": bool(deterministic_ordering_ok),
        "no_silent_field_writes": bool(no_silent_field_writes),
        "all_events_logged": bool(all_events_logged),
    }

    result = {
        "schema_version": "1.0.0",
        "result": "complete" if all(bool(flag) for flag in assertions.values()) else "refused",
        "scenario_id": str(scenario_id),
        "budget_envelope_id": str(budget_envelope_id or "poll.envelope.standard") or "poll.envelope.standard",
        "tick_count": int(horizon),
        "metrics": {
            "field_update_workload_per_tick": list(per_tick_field_workload),
            "degraded_cell_updates_per_tick": list(per_tick_degraded_cell_updates),
            "concentration_max_per_tick": list(per_tick_concentration_max),
            "exposure_total_per_tick": list(per_tick_exposure_totals),
            "threshold_events_per_tick": list(per_tick_threshold_events),
            "compliance_reports_per_tick": list(per_tick_compliance_reports),
            "cost_units_per_tick": list(per_tick_cost_units),
            "max_concentration_observed": int(max(per_tick_concentration_max or [0])),
            "total_threshold_events": int(sum(per_tick_threshold_events)),
            "total_compliance_reports": int(sum(per_tick_compliance_reports)),
            "total_measurement_refusals": int(total_measurement_refusals),
            "total_compliance_delays": int(total_compliance_delays),
            "total_degraded_dispersion_ticks": int(total_degraded_dispersion_ticks),
            "proof_hash_summary": dict(proof_hash_summary),
            "degradation_policy_order": [
                "degrade.pollution.dispersion_tick_bucket",
                "degrade.pollution.cell_budget",
                "degrade.pollution.exposure_subject_budget",
                "degrade.pollution.compliance_delay",
                "degrade.pollution.measurement_refusal",
            ],
        },
        "assertions": dict(assertions),
        "extensions": {
            "degrade_reason_codes": list(_sorted_tokens(degrade_reason_codes)),
            "control_decision_log": [dict(row) for row in decision_log_rows],
            "pollution_degradation_event_rows": [
                {
                    "tick": int(max(0, _as_int(row.get("tick", 0), 0))),
                    "decision_id": str(row.get("decision_id", "")),
                    "reason_code": str(row.get("reason_code", "")),
                    "target_id": str(_as_map(row.get("extensions")).get("target_id", row.get("process_id", "pollution"))),
                }
                for row in decision_log_rows
                if str(row.get("reason_code", "")).strip().startswith("degrade.pollution")
            ],
            "final_state_snapshot": {
                "pollutant_ids": list(_sorted_tokens(pollutant_ids)),
                "field_cells": [dict(row) for row in list(state.get("field_cells") or []) if isinstance(row, Mapping)],
                "pollution_source_event_rows": [dict(row) for row in list(state.get("pollution_source_event_rows") or []) if isinstance(row, Mapping)],
                "pollution_total_rows": [dict(row) for row in list(state.get("pollution_total_rows") or []) if isinstance(row, Mapping)],
                "pollution_dispersion_step_rows": [dict(row) for row in list(state.get("pollution_dispersion_step_rows") or []) if isinstance(row, Mapping)],
                "pollution_deposition_rows": [dict(row) for row in list(state.get("pollution_deposition_rows") or []) if isinstance(row, Mapping)],
                "pollution_exposure_state_rows": [dict(row) for row in list(state.get("pollution_exposure_state_rows") or []) if isinstance(row, Mapping)],
                "pollution_health_risk_event_rows": [dict(row) for row in list(state.get("pollution_health_risk_event_rows") or []) if isinstance(row, Mapping)],
                "pollution_measurement_rows": [dict(row) for row in list(state.get("pollution_measurement_rows") or []) if isinstance(row, Mapping)],
                "pollution_compliance_report_rows": [dict(row) for row in list(state.get("pollution_compliance_report_rows") or []) if isinstance(row, Mapping)],
                "pollution_dispersion_degrade_rows": [dict(row) for row in list(state.get("pollution_dispersion_degrade_rows") or []) if isinstance(row, Mapping)],
                "pollution_source_hash_chain": str(state.get("pollution_source_hash_chain", "")).strip(),
                "pollution_field_hash_chain": str(state.get("pollution_field_hash_chain", "")).strip(),
                "pollution_exposure_hash_chain": str(state.get("pollution_exposure_hash_chain", "")).strip(),
                "pollution_compliance_report_hash_chain": str(state.get("pollution_compliance_report_hash_chain", "")).strip(),
                "pollution_dispersion_degrade_hash_chain": str(state.get("pollution_dispersion_degrade_hash_chain", "")).strip(),
            },
        },
        "deterministic_fingerprint": "",
    }
    seed_payload = dict(result)
    seed_payload["deterministic_fingerprint"] = ""
    result["deterministic_fingerprint"] = canonical_sha256(seed_payload)
    if str(result.get("result", "")).strip() == "complete":
        return result
    return {
        **result,
        "errors": [{"code": "refusal.poll.stress.assertion_failed", "message": "POLL stress assertions failed", "path": "$.assertions"}],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic POLL-3 stress scenario.")
    parser.add_argument("--scenario", default="build/pollution/poll3_stress_scenario.json")
    parser.add_argument("--seed", type=int, default=9301)
    parser.add_argument("--region-count", type=int, default=3)
    parser.add_argument("--cells-per-region", type=int, default=9)
    parser.add_argument("--subject-count", type=int, default=36)
    parser.add_argument("--tick-count", type=int, default=24)
    parser.add_argument("--emissions-per-tick", type=int, default=3)
    parser.add_argument("--measurements-per-tick", type=int, default=1)
    parser.add_argument("--compliance-interval-ticks", type=int, default=4)
    parser.add_argument("--include-wind-field", action="store_true")
    parser.add_argument("--budget-envelope-id", default="poll.envelope.standard")
    parser.add_argument("--max-compute-units-per-tick", type=int, default=0)
    parser.add_argument("--dispersion-tick-stride-base", type=int, default=0)
    parser.add_argument("--max-cell-updates-per-tick", type=int, default=0)
    parser.add_argument("--max-subject-updates-per-tick", type=int, default=0)
    parser.add_argument("--max-compliance-reports-per-tick", type=int, default=0)
    parser.add_argument("--max-measurements-per-tick", type=int, default=0)
    parser.add_argument("--output", default="build/pollution/poll3_stress_report.json")
    return parser


def main() -> int:
    args = _parser().parse_args()
    scenario = _read_json(os.path.normpath(os.path.abspath(str(args.scenario))))
    if not scenario:
        scenario = generate_poll_stress_scenario(
            seed=int(args.seed),
            region_count=int(args.region_count),
            cells_per_region=int(args.cells_per_region),
            subject_count=int(args.subject_count),
            tick_horizon=int(args.tick_count),
            emissions_per_tick=int(args.emissions_per_tick),
            measurements_per_tick=int(args.measurements_per_tick),
            compliance_interval_ticks=int(args.compliance_interval_ticks),
            include_wind_field=bool(args.include_wind_field),
            repo_root=REPO_ROOT_HINT,
        )

    defaults = _envelope_defaults(str(args.budget_envelope_id))
    max_compute_units_per_tick = int(args.max_compute_units_per_tick) if int(args.max_compute_units_per_tick) > 0 else int(defaults["max_compute_units_per_tick"])
    dispersion_tick_stride_base = int(args.dispersion_tick_stride_base) if int(args.dispersion_tick_stride_base) > 0 else int(defaults["dispersion_tick_stride_base"])
    max_cell_updates_per_tick = int(args.max_cell_updates_per_tick) if int(args.max_cell_updates_per_tick) > 0 else int(defaults["max_cell_updates_per_tick"])
    max_subject_updates_per_tick = int(args.max_subject_updates_per_tick) if int(args.max_subject_updates_per_tick) > 0 else int(defaults["max_subject_updates_per_tick"])
    max_compliance_reports_per_tick = int(args.max_compliance_reports_per_tick) if int(args.max_compliance_reports_per_tick) > 0 else int(defaults["max_compliance_reports_per_tick"])
    max_measurements_per_tick = int(args.max_measurements_per_tick) if int(args.max_measurements_per_tick) > 0 else int(defaults["max_measurements_per_tick"])

    report = run_poll_stress_scenario(
        scenario=scenario,
        tick_count=int(args.tick_count),
        budget_envelope_id=str(args.budget_envelope_id),
        max_compute_units_per_tick=max_compute_units_per_tick,
        dispersion_tick_stride_base=dispersion_tick_stride_base,
        max_cell_updates_per_tick=max_cell_updates_per_tick,
        max_subject_updates_per_tick=max_subject_updates_per_tick,
        max_compliance_reports_per_tick=max_compliance_reports_per_tick,
        max_measurements_per_tick=max_measurements_per_tick,
    )

    output_abs = os.path.normpath(os.path.abspath(str(args.output)))
    _write_json(output_abs, report)
    print(
        json.dumps(
            {
                "output_path": output_abs,
                "result": str(report.get("result", "")),
                "scenario_id": str(report.get("scenario_id", "")),
                "deterministic_fingerprint": str(report.get("deterministic_fingerprint", "")),
                "assertions": dict(report.get("assertions") or {}),
                "metrics": {
                    "max_concentration_observed": int(max(0, _as_int(dict(report.get("metrics") or {}).get("max_concentration_observed", 0), 0))),
                    "total_threshold_events": int(max(0, _as_int(dict(report.get("metrics") or {}).get("total_threshold_events", 0), 0))),
                    "total_compliance_reports": int(max(0, _as_int(dict(report.get("metrics") or {}).get("total_compliance_reports", 0), 0))),
                    "total_measurement_refusals": int(max(0, _as_int(dict(report.get("metrics") or {}).get("total_measurement_refusals", 0), 0))),
                    "total_compliance_delays": int(max(0, _as_int(dict(report.get("metrics") or {}).get("total_compliance_delays", 0), 0))),
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if str(report.get("result", "")).strip() == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
