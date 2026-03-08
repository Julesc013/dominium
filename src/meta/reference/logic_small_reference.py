"""Bounded LOGIC reference evaluator helpers for META-REF."""

from __future__ import annotations

from typing import Mapping

from src.logic.eval.common import active_signal_for_slot
from src.logic.signal import process_signal_set
from tools.xstack.compatx.canonical_json import canonical_sha256


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _as_list(value: object) -> list:
    return list(value) if isinstance(value, list) else []


def _token(value: object) -> str:
    return str(value or "").strip()


def _bool_from_signal(signal_row: Mapping[str, object] | None) -> int:
    value_ref = _as_map(_as_map(signal_row).get("value_ref"))
    kind = _token(value_ref.get("value_kind"))
    if kind == "scalar":
        return 1 if _as_int(value_ref.get("value_fixed"), 0) else 0
    if kind == "pulse":
        return 1 if _as_list(value_ref.get("edges")) else 0
    return 1 if _as_int(value_ref.get("value"), 0) else 0


def _signal_process_inputs(state: Mapping[str, object]) -> dict:
    return {
        "signal_type_registry_payload": state.get("signal_type_registry_payload") or {},
        "carrier_type_registry_payload": state.get("carrier_type_registry_payload") or {},
        "signal_delay_policy_registry_payload": state.get("signal_delay_policy_registry_payload") or {},
        "signal_noise_policy_registry_payload": state.get("signal_noise_policy_registry_payload") or {},
        "bus_encoding_registry_payload": state.get("bus_encoding_registry_payload") or {},
        "protocol_registry_payload": state.get("protocol_registry_payload") or {},
        "compute_budget_profile_registry_payload": state.get("compute_budget_profile_registry_payload") or {},
        "compute_degrade_policy_registry_payload": state.get("compute_degrade_policy_registry_payload") or {},
        "tolerance_policy_registry_payload": state.get("tolerance_policy_registry_payload") or {},
    }


def _active_slot_projection(*, signal_store_state: Mapping[str, object] | None, tick: int) -> list[dict]:
    signal_rows = [
        dict(row)
        for row in _as_list(_as_map(signal_store_state).get("signal_rows"))
        if isinstance(row, Mapping)
    ]
    slot_keys = sorted(
        {
            "|".join(
                (
                    _token(_as_map(_as_map(row.get("extensions")).get("slot")).get("network_id")),
                    _token(_as_map(_as_map(row.get("extensions")).get("slot")).get("element_id")),
                    _token(_as_map(_as_map(row.get("extensions")).get("slot")).get("port_id")),
                )
            )
            for row in signal_rows
        }
    )
    projection = []
    for slot_key in slot_keys:
        network_id, element_id, port_id = (slot_key.split("|", 2) + ["", "", ""])[:3]
        active = active_signal_for_slot(
            signal_store_state=signal_store_state,
            network_id=network_id,
            element_id=element_id,
            port_id=port_id,
            tick=tick,
        )
        if not active:
            continue
        value_ref = _as_map(active.get("value_ref"))
        item = {
            "slot_key": slot_key,
            "signal_type_id": _token(active.get("signal_type_id")),
            "value_kind": _token(value_ref.get("value_kind")),
        }
        if item["value_kind"] == "scalar":
            item["value"] = int(_as_int(value_ref.get("value_fixed"), 0))
        elif item["value_kind"] == "pulse":
            item["value"] = [
                {
                    "tick_offset": int(max(0, _as_int(edge.get("tick_offset"), 0))),
                    "edge_kind": _token(edge.get("edge_kind")),
                }
                for edge in _as_list(value_ref.get("edges"))
                if isinstance(edge, Mapping)
            ]
        elif item["value_kind"] == "message":
            item["value"] = {
                "artifact_id": _token(value_ref.get("artifact_id")),
                "receipt_id": _token(value_ref.get("receipt_id")),
            }
        else:
            item["value"] = int(_as_int(value_ref.get("value"), 0))
        projection.append(item)
    return projection


def _window_projection(signal_store_state: Mapping[str, object] | None) -> list[dict]:
    signal_rows = [
        dict(row)
        for row in _as_list(_as_map(signal_store_state).get("signal_rows"))
        if isinstance(row, Mapping)
    ]
    windows = []
    for row in sorted(
        signal_rows,
        key=lambda item: (
            _token(_as_map(_as_map(item.get("extensions")).get("slot")).get("network_id")),
            _token(_as_map(_as_map(item.get("extensions")).get("slot")).get("element_id")),
            _token(_as_map(_as_map(item.get("extensions")).get("slot")).get("port_id")),
            int(max(0, _as_int(item.get("valid_from_tick"), 0))),
            _token(item.get("signal_id")),
        ),
    ):
        slot = _as_map(_as_map(row.get("extensions")).get("slot"))
        value_ref = _as_map(row.get("value_ref"))
        item = {
            "slot_key": "|".join((_token(slot.get("network_id")), _token(slot.get("element_id")), _token(slot.get("port_id")))),
            "signal_type_id": _token(row.get("signal_type_id")),
            "valid_from_tick": int(max(0, _as_int(row.get("valid_from_tick"), 0))),
            "valid_until_tick": (None if row.get("valid_until_tick") is None else int(max(0, _as_int(row.get("valid_until_tick"), 0)))),
            "value_kind": _token(value_ref.get("value_kind")),
        }
        if item["value_kind"] == "scalar":
            item["value"] = int(_as_int(value_ref.get("value_fixed"), 0))
        else:
            item["value"] = int(_as_int(value_ref.get("value"), 0))
        windows.append(item)
    return windows


def _project_runtime_output(
    runtime_report: Mapping[str, object],
    fixture_kind: str,
    ticks: list[int],
) -> dict:
    signal_store_state = _as_map(runtime_report.get("final_signal_store_state"))
    projected = {
        "fixture_kind": _token(fixture_kind),
        "tick_reports": [
            {
                "tick": int(tick),
                "signals": _active_slot_projection(signal_store_state=signal_store_state, tick=tick),
            }
            for tick in ticks
        ],
        "signal_windows": _window_projection(signal_store_state),
    }
    projected["output_hash"] = canonical_sha256(projected)
    return projected


def evaluate_reference_logic_eval_small(
    *,
    state_payload: Mapping[str, object] | None,
    tick_start: int | None,
    tick_end: int | None,
) -> dict:
    state = _as_map(state_payload)
    fixture = _as_map(state.get("logic_reference_fixture_payload"))
    runtime_report = _as_map(
        state.get("logic_eval_small_runtime_report")
        or _as_map(state.get("record")).get("logic_eval_small_runtime_report")
    )
    fixture_kind = _token(fixture.get("fixture_kind"))
    scenario = _as_map(fixture.get("scenario_payload"))
    network_id = _token(fixture.get("network_id"))

    tick_min = int(max(0, _as_int(0 if tick_start is None else tick_start, 0)))
    tick_max = int(max(tick_min, _as_int(tick_min if tick_end is None else tick_end, tick_min)))
    runtime_ticks = [
        int(max(0, _as_int(row.get("tick"), 0)))
        for row in _as_list(_as_map(fixture.get("scenario_payload")).get("evaluation_requests"))
        if isinstance(row, Mapping) and tick_min <= int(max(0, _as_int(row.get("tick"), 0))) <= tick_max
    ]
    runtime_out = _project_runtime_output(runtime_report, fixture_kind, runtime_ticks)
    if _token(runtime_report.get("result")) != "complete":
        return {
            "runtime": runtime_out,
            "reference": {
                "fixture_kind": fixture_kind,
                "tick_reports": [],
                "signal_windows": [],
                "output_hash": canonical_sha256({"fixture_kind": fixture_kind, "status": "runtime_incomplete"}),
            },
            "match": False,
            "discrepancy_summary": "logic runtime fixture did not complete",
        }

    if fixture_kind != "fixture.logic.chain_and_not_sink_boolean.v1":
        reference_out = {
            "fixture_kind": fixture_kind,
            "tick_reports": [],
            "signal_windows": [],
            "output_hash": canonical_sha256({"fixture_kind": fixture_kind, "status": "unsupported"}),
        }
        return {
            "runtime": runtime_out,
            "reference": reference_out,
            "match": False,
            "discrepancy_summary": "unsupported logic reference fixture",
        }

    requests = [
        dict(row)
        for row in sorted(
            (dict(item) for item in _as_list(scenario.get("evaluation_requests")) if isinstance(item, Mapping)),
            key=lambda item: (int(max(0, _as_int(item.get("tick"), 0))), _token(item.get("network_id"))),
        )
    ]
    filtered_requests = [
        row
        for row in requests
        if tick_min <= int(max(0, _as_int(row.get("tick"), 0))) <= tick_max
    ]
    signal_store_state = _as_map(scenario.get("signal_store_state"))
    process_inputs = _signal_process_inputs(state)
    reference_tick_reports = []

    for request in filtered_requests:
        tick = int(max(0, _as_int(request.get("tick"), 0)))
        and_a = _bool_from_signal(
            active_signal_for_slot(
                signal_store_state=signal_store_state,
                network_id=network_id,
                element_id="inst.logic.and.1",
                port_id="in.a",
                tick=tick,
            )
        )
        and_b = _bool_from_signal(
            active_signal_for_slot(
                signal_store_state=signal_store_state,
                network_id=network_id,
                element_id="inst.logic.and.1",
                port_id="in.b",
                tick=tick,
            )
        )
        not_in = _bool_from_signal(
            active_signal_for_slot(
                signal_store_state=signal_store_state,
                network_id=network_id,
                element_id="inst.logic.not.1",
                port_id="in.a",
                tick=tick,
            )
        )
        and_out = 1 if (and_a and and_b) else 0
        not_out = 0 if not_in else 1
        for target_element_id, target_port_id, value in (
            ("inst.logic.not.1", "in.a", and_out),
            ("inst.logic.or.sink", "in.a", not_out),
        ):
            deliver_tick = int(tick + 1)
            if deliver_tick > tick_max:
                continue
            set_result = process_signal_set(
                current_tick=deliver_tick,
                signal_store_state=signal_store_state,
                signal_request={
                    "network_id": network_id,
                    "element_id": target_element_id,
                    "port_id": target_port_id,
                    "signal_type_id": "signal.boolean",
                    "carrier_type_id": "carrier.electrical",
                    "delay_policy_id": "delay.none",
                    "noise_policy_id": "noise.none",
                    "value_payload": {"value": int(value)},
                },
                **process_inputs,
            )
            if _token(set_result.get("result")) != "complete":
                reference_out = {
                    "fixture_kind": fixture_kind,
                    "tick_reports": reference_tick_reports,
                    "signal_windows": _window_projection(signal_store_state),
                    "output_hash": canonical_sha256({"fixture_kind": fixture_kind, "status": "signal_refused"}),
                }
                return {
                    "runtime": runtime_out,
                    "reference": reference_out,
                    "match": False,
                    "discrepancy_summary": "logic reference signal set refused",
                }
            signal_store_state = _as_map(set_result.get("signal_store_state"))
        reference_tick_reports.append(
            {
                "tick": int(tick),
                "signals": _active_slot_projection(signal_store_state=signal_store_state, tick=tick),
            }
        )

    reference_out = {
        "fixture_kind": fixture_kind,
        "tick_reports": reference_tick_reports,
        "signal_windows": _window_projection(signal_store_state),
    }
    reference_out["output_hash"] = canonical_sha256(reference_out)
    match = bool(
        _token(runtime_out.get("output_hash"))
        and _token(runtime_out.get("output_hash")) == _token(reference_out.get("output_hash"))
    )
    return {
        "runtime": runtime_out,
        "reference": reference_out,
        "match": match,
        "discrepancy_summary": "" if match else "logic small reference mismatch",
    }


__all__ = ["evaluate_reference_logic_eval_small"]
