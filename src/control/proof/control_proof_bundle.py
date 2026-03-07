"""Deterministic CTRL-10 control proof bundle builders."""

from __future__ import annotations

from typing import Iterable, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


def _to_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _is_hash64(value: object) -> bool:
    token = str(value or "").strip()
    return len(token) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in token)


def _hash64(value: object, fallback_seed: object) -> str:
    token = str(value or "").strip()
    if _is_hash64(token):
        return token.lower()
    if token:
        return canonical_sha256({"raw": token, "fallback_seed": fallback_seed})
    return canonical_sha256({"fallback_seed": fallback_seed})


def _sorted_unique_strings(values: Iterable[object]) -> List[str]:
    return sorted(set(str(item).strip() for item in list(values or []) if str(item).strip()))


def _marker_hash_list(decision_markers: List[dict], key: str) -> List[str]:
    out: List[str] = []
    for marker in list(decision_markers or []):
        if not isinstance(marker, Mapping):
            continue
        token = str(marker.get(str(key), "")).strip()
        if not token:
            continue
        out.append(_hash64(token, {"key": str(key), "marker": dict(marker)}))
    return _sorted_unique_strings(out)


def _mobility_surface_hash(
    *,
    key: str,
    surface: Mapping[str, object] | None,
    tick_start: int,
    tick_end: int,
    decision_log_hashes: List[str],
) -> str:
    payload = dict(surface or {})
    return _hash64(
        payload.get(str(key), ""),
        {
            "key": str(key),
            "tick_start": int(max(0, _to_int(tick_start, 0))),
            "tick_end": int(max(0, _to_int(tick_end, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )


def _signal_surface_hash(
    *,
    key: str,
    surface: Mapping[str, object] | None,
    tick_start: int,
    tick_end: int,
    decision_log_hashes: List[str],
) -> str:
    payload = dict(surface or {})
    return _hash64(
        payload.get(str(key), ""),
        {
            "key": str(key),
            "tick_start": int(max(0, _to_int(tick_start, 0))),
            "tick_end": int(max(0, _to_int(tick_end, 0))),
            "decision_log_hashes": list(decision_log_hashes),
            "surface_kind": "signals",
        },
    )


def collect_control_decision_markers(envelopes: Iterable[Mapping[str, object]]) -> List[dict]:
    """Extract deterministic control-decision proof markers from intent envelopes."""

    out: List[dict] = []
    for envelope in list(envelopes or []):
        row = dict(envelope or {}) if isinstance(envelope, Mapping) else {}
        ext = dict(row.get("extensions") or {})
        decision_hash = str(ext.get("control_decision_log_hash", "")).strip()
        if not decision_hash:
            continue
        out.append(
            {
                "envelope_id": str(row.get("envelope_id", "")).strip(),
                "control_decision_id": str(ext.get("control_decision_id", "")).strip(),
                "control_decision_log_hash": _hash64(
                    decision_hash,
                    {"envelope_id": str(row.get("envelope_id", ""))},
                ),
                "control_fidelity_allocation_hash": _hash64(
                    ext.get("control_fidelity_allocation_hash", ""),
                    {"decision_hash": decision_hash, "axis": "fidelity"},
                ),
                "control_abstraction_downgrade_hash": _hash64(
                    ext.get("control_abstraction_downgrade_hash", ""),
                    {"decision_hash": decision_hash, "axis": "abstraction"},
                ),
                "control_view_policy_changes_hash": _hash64(
                    ext.get("control_view_policy_changes_hash", ""),
                    {"decision_hash": decision_hash, "axis": "view"},
                ),
                "control_meta_override_hash": _hash64(
                    ext.get("control_meta_override_hash", ""),
                    {"decision_hash": decision_hash, "axis": "meta"},
                ),
            }
        )
    return sorted(
        out,
        key=lambda item: (
            str(item.get("control_decision_log_hash", "")),
            str(item.get("control_decision_id", "")),
            str(item.get("envelope_id", "")),
        ),
    )


def _marker_from_decision_log(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    decision_id = str(payload.get("decision_id", "")).strip()
    decision_hash = _hash64(
        payload.get("deterministic_fingerprint", ""),
        {"decision_id": decision_id, "payload": payload},
    )
    input_vector = dict(payload.get("input_vector") or {})
    resolved_vector = dict(payload.get("resolved_vector") or {})
    ext = dict(payload.get("extensions") or {})
    downgrade_entries = [
        dict(item)
        for item in list(ext.get("downgrade_entries") or [])
        if isinstance(item, Mapping)
    ]
    abstraction_entries = sorted(
        (
            {
                "decision_id": decision_id,
                "downgrade_id": str(item.get("downgrade_id", "")).strip(),
                "from": str(item.get("from_value", "")).strip(),
                "to": str(item.get("to_value", "")).strip(),
                "reason": str(item.get("reason_code", "")).strip(),
            }
            for item in downgrade_entries
            if str(item.get("axis", "")).strip() == "abstraction"
        ),
        key=lambda item: (
            str(item.get("downgrade_id", "")),
            str(item.get("from", "")),
            str(item.get("to", "")),
            str(item.get("reason", "")),
        ),
    )
    view_change_payload = {
        "decision_id": decision_id,
        "requested_view": str(input_vector.get("view_requested", "")).strip(),
        "resolved_view": str(resolved_vector.get("view_resolved", "")).strip(),
        "view_downgrade_ids": sorted(
            str(item.get("downgrade_id", "")).strip()
            for item in downgrade_entries
            if str(item.get("axis", "")).strip() == "view" and str(item.get("downgrade_id", "")).strip()
        ),
    }
    fidelity_payload = {
        "decision_id": decision_id,
        "fidelity_resolved": str(resolved_vector.get("fidelity_resolved", "")).strip(),
        "budget_allocated": int(max(0, _to_int(payload.get("budget_allocated", 0), 0))),
    }
    policy_ids = _sorted_unique_strings(payload.get("policy_ids_applied"))
    control_action_id = str(ext.get("control_action_id", "")).strip()
    control_policy_id = str(ext.get("control_policy_id", "")).strip()
    meta_payload = {
        "decision_id": decision_id,
        "meta": bool(
            control_action_id == "action.admin.meta_override"
            or control_policy_id == "ctrl.policy.admin.meta"
            or "ctrl.policy.admin.meta" in set(policy_ids)
        ),
        "control_action_id": control_action_id,
        "control_policy_id": control_policy_id,
        "policy_ids_applied": policy_ids,
    }
    return {
        "control_decision_id": decision_id,
        "control_decision_log_hash": decision_hash,
        "control_fidelity_allocation_hash": canonical_sha256(fidelity_payload),
        "control_abstraction_downgrade_hash": canonical_sha256(abstraction_entries),
        "control_view_policy_changes_hash": canonical_sha256(view_change_payload),
        "control_meta_override_hash": canonical_sha256(meta_payload),
    }


def build_control_proof_bundle_from_markers(
    *,
    tick_start: int,
    tick_end: int,
    decision_markers: Iterable[Mapping[str, object]],
    proof_id: str = "",
    mobility_proof_surface: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    """Build deterministic control proof bundle from pre-computed decision markers."""

    markers = sorted(
        (dict(row) for row in list(decision_markers or []) if isinstance(row, Mapping)),
        key=lambda item: (
            str(item.get("control_decision_log_hash", "")),
            str(item.get("control_decision_id", "")),
        ),
    )
    start_tick = int(max(0, _to_int(tick_start, 0)))
    end_tick = int(max(start_tick, _to_int(tick_end, start_tick)))

    decision_log_hashes = _marker_hash_list(markers, "control_decision_log_hash")
    fidelity_hashes = _marker_hash_list(markers, "control_fidelity_allocation_hash")
    abstraction_hashes = _marker_hash_list(markers, "control_abstraction_downgrade_hash")
    view_hashes = _marker_hash_list(markers, "control_view_policy_changes_hash")
    meta_hashes = _marker_hash_list(markers, "control_meta_override_hash")
    mobility_event_hash = _mobility_surface_hash(
        key="mobility_event_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    congestion_hash = _mobility_surface_hash(
        key="congestion_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    signal_state_hash = _mobility_surface_hash(
        key="signal_state_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    derailment_hash = _mobility_surface_hash(
        key="derailment_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    power_flow_hash = _mobility_surface_hash(
        key="power_flow_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    power_flow_hash_chain = _mobility_surface_hash(
        key="power_flow_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    fault_state_hash_chain = _mobility_surface_hash(
        key="fault_state_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    protection_state_hash_chain = _mobility_surface_hash(
        key="protection_state_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    degradation_event_hash_chain = _mobility_surface_hash(
        key="degradation_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    degradation_hash_chain = _mobility_surface_hash(
        key="degradation_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    maintenance_action_hash_chain = _mobility_surface_hash(
        key="maintenance_action_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    trip_event_hash_chain = _mobility_surface_hash(
        key="trip_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    trip_explanation_hash_chain = _mobility_surface_hash(
        key="trip_explanation_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    thermal_network_hash = _mobility_surface_hash(
        key="thermal_network_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    thermal_network_state_hash_chain = _mobility_surface_hash(
        key="thermal_network_state_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    heat_input_hash_chain = _mobility_surface_hash(
        key="heat_input_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    overheat_event_hash_chain = _mobility_surface_hash(
        key="overheat_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    ambient_exchange_hash = _mobility_surface_hash(
        key="ambient_exchange_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    fire_state_hash_chain = _mobility_surface_hash(
        key="fire_state_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    ignition_event_hash_chain = _mobility_surface_hash(
        key="ignition_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    fire_spread_hash_chain = _mobility_surface_hash(
        key="fire_spread_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    fire_cascade_hash_chain = _mobility_surface_hash(
        key="fire_cascade_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    runaway_event_hash_chain = _mobility_surface_hash(
        key="runaway_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    signal_network_hash = _signal_surface_hash(
        key="signal_network_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    message_delivery_event_hash_chain = _signal_surface_hash(
        key="message_delivery_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    receipt_hash_chain = _signal_surface_hash(
        key="receipt_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    trust_update_hash_chain = _signal_surface_hash(
        key="trust_update_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    jamming_event_hash_chain = _signal_surface_hash(
        key="jamming_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    momentum_hash_chain = _mobility_surface_hash(
        key="momentum_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    impulse_event_hash_chain = _mobility_surface_hash(
        key="impulse_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    energy_ledger_hash_chain = _mobility_surface_hash(
        key="energy_ledger_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    boundary_flux_hash_chain = _mobility_surface_hash(
        key="boundary_flux_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    combustion_hash_chain = _mobility_surface_hash(
        key="combustion_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    reaction_hash_chain = _mobility_surface_hash(
        key="reaction_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    emission_hash_chain = _mobility_surface_hash(
        key="emission_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    impulse_hash_chain = _mobility_surface_hash(
        key="impulse_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    process_run_hash_chain = _mobility_surface_hash(
        key="process_run_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    process_quality_hash_chain = _mobility_surface_hash(
        key="process_quality_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    batch_quality_hash_chain = _mobility_surface_hash(
        key="batch_quality_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    qc_result_hash_chain = _mobility_surface_hash(
        key="qc_result_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    sampling_decision_hash_chain = _mobility_surface_hash(
        key="sampling_decision_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    process_maturity_hash_chain = _mobility_surface_hash(
        key="process_maturity_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    metrics_state_hash_chain = _mobility_surface_hash(
        key="metrics_state_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    process_cert_hash_chain = _mobility_surface_hash(
        key="process_cert_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    drift_state_hash_chain = _mobility_surface_hash(
        key="drift_state_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    drift_event_hash_chain = _mobility_surface_hash(
        key="drift_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    qc_policy_change_hash_chain = _mobility_surface_hash(
        key="qc_policy_change_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    revalidation_run_hash_chain = _mobility_surface_hash(
        key="revalidation_run_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    yield_model_hash_chain = _mobility_surface_hash(
        key="yield_model_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    quantity_tolerance_registry_hash = _mobility_surface_hash(
        key="quantity_tolerance_registry_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    rounding_mode_policy_hash = _mobility_surface_hash(
        key="rounding_mode_policy_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    entropy_hash_chain = _mobility_surface_hash(
        key="entropy_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    entropy_reset_events_hash_chain = _mobility_surface_hash(
        key="entropy_reset_events_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    fluid_flow_hash_chain = _mobility_surface_hash(
        key="fluid_flow_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    leak_hash_chain = _mobility_surface_hash(
        key="leak_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    burst_hash_chain = _mobility_surface_hash(
        key="burst_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    relief_event_hash_chain = _mobility_surface_hash(
        key="relief_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    field_update_hash_chain = _mobility_surface_hash(
        key="field_update_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    field_sample_hash_chain = _mobility_surface_hash(
        key="field_sample_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    boundary_field_exchange_hash_chain = _mobility_surface_hash(
        key="boundary_field_exchange_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    time_mapping_hash_chain = _mobility_surface_hash(
        key="time_mapping_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    schedule_domain_evaluation_hash = _mobility_surface_hash(
        key="schedule_domain_evaluation_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    time_adjust_event_hash_chain = _mobility_surface_hash(
        key="time_adjust_event_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    compaction_marker_hash_chain = _mobility_surface_hash(
        key="compaction_marker_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    compaction_pre_anchor_hash = _mobility_surface_hash(
        key="compaction_pre_anchor_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    compaction_post_anchor_hash = _mobility_surface_hash(
        key="compaction_post_anchor_hash",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    pollution_field_hash_chain = _mobility_surface_hash(
        key="pollution_field_hash_chain",
        surface=mobility_proof_surface,
        tick_start=int(start_tick),
        tick_end=int(end_tick),
        decision_log_hashes=decision_log_hashes,
    )
    surface_payload = dict(mobility_proof_surface or {})
    pollution_emission_hash_chain = _hash64(
        str(
            surface_payload.get(
                "pollution_emission_hash_chain",
                surface_payload.get("pollution_source_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "pollution_emission_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    pollution_exposure_hash_chain = _hash64(
        str(
            surface_payload.get(
                "pollution_exposure_hash_chain",
                surface_payload.get("exposure_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "pollution_exposure_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    pollution_compliance_hash_chain = _hash64(
        str(
            surface_payload.get(
                "pollution_compliance_hash_chain",
                surface_payload.get("pollution_compliance_report_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "pollution_compliance_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    pollution_degradation_event_hash_chain = _hash64(
        str(
            surface_payload.get(
                "pollution_degradation_event_hash_chain",
                surface_payload.get("pollution_dispersion_degrade_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "pollution_degradation_event_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    deposition_hash_chain = _hash64(
        str(
            surface_payload.get(
                "deposition_hash_chain",
                surface_payload.get("pollution_deposition_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "deposition_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    compiled_model_hash_chain = _hash64(
        str(surface_payload.get("compiled_model_hash_chain", "")).strip(),
        {
            "key": "compiled_model_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    equivalence_proof_hash_chain = _hash64(
        str(surface_payload.get("equivalence_proof_hash_chain", "")).strip(),
        {
            "key": "equivalence_proof_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    compile_result_hash_chain = _hash64(
        str(surface_payload.get("compile_result_hash_chain", "")).strip(),
        {
            "key": "compile_result_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_compile_policy_hash_chain = _hash64(
        str(surface_payload.get("logic_compile_policy_hash_chain", "")).strip(),
        {
            "key": "logic_compile_policy_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    forced_expand_event_hash_chain = _hash64(
        str(surface_payload.get("forced_expand_event_hash_chain", "")).strip(),
        {
            "key": "forced_expand_event_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    process_capsule_generation_hash_chain = _hash64(
        str(
            surface_payload.get(
                "process_capsule_generation_hash_chain",
                surface_payload.get("capsule_generation_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "process_capsule_generation_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    process_capsule_execution_hash_chain = _hash64(
        str(
            surface_payload.get(
                "process_capsule_execution_hash_chain",
                surface_payload.get("capsule_execution_hash_chain", ""),
            )
        ).strip(),
        {
            "key": "process_capsule_execution_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_throttle_event_hash_chain = _hash64(
        str(surface_payload.get("logic_throttle_event_hash_chain", "")).strip(),
        {
            "key": "logic_throttle_event_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_state_update_hash_chain = _hash64(
        str(surface_payload.get("logic_state_update_hash_chain", "")).strip(),
        {
            "key": "logic_state_update_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_output_signal_hash_chain = _hash64(
        str(surface_payload.get("logic_output_signal_hash_chain", "")).strip(),
        {
            "key": "logic_output_signal_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_oscillation_record_hash_chain = _hash64(
        str(surface_payload.get("logic_oscillation_record_hash_chain", "")).strip(),
        {
            "key": "logic_oscillation_record_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_timing_violation_hash_chain = _hash64(
        str(surface_payload.get("logic_timing_violation_hash_chain", "")).strip(),
        {
            "key": "logic_timing_violation_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    logic_watchdog_timeout_hash_chain = _hash64(
        str(surface_payload.get("logic_watchdog_timeout_hash_chain", "")).strip(),
        {
            "key": "logic_watchdog_timeout_hash_chain",
            "tick_start": int(max(0, _to_int(start_tick, 0))),
            "tick_end": int(max(0, _to_int(end_tick, 0))),
            "decision_log_hashes": list(decision_log_hashes),
        },
    )
    drift_policy_id = str((dict(mobility_proof_surface or {})).get("drift_policy_id", "drift.none")).strip() or "drift.none"

    payload = {
        "schema_version": "1.0.0",
        "proof_id": str(proof_id).strip(),
        "tick_range": {
            "start_tick": int(start_tick),
            "end_tick": int(end_tick),
        },
        "decision_log_hashes": list(decision_log_hashes),
        "fidelity_allocations_hash": canonical_sha256(list(fidelity_hashes)),
        "abstraction_downgrade_hash": canonical_sha256(list(abstraction_hashes)),
        "view_policy_changes_hash": canonical_sha256(list(view_hashes)),
        "meta_override_hash": canonical_sha256(list(meta_hashes)),
        "mobility_event_hash": str(mobility_event_hash),
        "congestion_hash": str(congestion_hash),
        "signal_state_hash": str(signal_state_hash),
        "derailment_hash": str(derailment_hash),
        "power_flow_hash": str(power_flow_hash),
        "power_flow_hash_chain": str(power_flow_hash_chain),
        "fault_state_hash_chain": str(fault_state_hash_chain),
        "protection_state_hash_chain": str(protection_state_hash_chain),
        "degradation_event_hash_chain": str(degradation_event_hash_chain),
        "degradation_hash_chain": str(degradation_hash_chain),
        "maintenance_action_hash_chain": str(maintenance_action_hash_chain),
        "trip_event_hash_chain": str(trip_event_hash_chain),
        "trip_explanation_hash_chain": str(trip_explanation_hash_chain),
        "thermal_network_hash": str(thermal_network_hash),
        "thermal_network_state_hash_chain": str(thermal_network_state_hash_chain),
        "heat_input_hash_chain": str(heat_input_hash_chain),
        "overheat_event_hash_chain": str(overheat_event_hash_chain),
        "ambient_exchange_hash": str(ambient_exchange_hash),
        "fire_state_hash_chain": str(fire_state_hash_chain),
        "ignition_event_hash_chain": str(ignition_event_hash_chain),
        "fire_spread_hash_chain": str(fire_spread_hash_chain),
        "fire_cascade_hash_chain": str(fire_cascade_hash_chain),
        "runaway_event_hash_chain": str(runaway_event_hash_chain),
        "signal_network_hash": str(signal_network_hash),
        "message_delivery_event_hash_chain": str(message_delivery_event_hash_chain),
        "receipt_hash_chain": str(receipt_hash_chain),
        "trust_update_hash_chain": str(trust_update_hash_chain),
        "jamming_event_hash_chain": str(jamming_event_hash_chain),
        "momentum_hash_chain": str(momentum_hash_chain),
        "impulse_event_hash_chain": str(impulse_event_hash_chain),
        "energy_ledger_hash_chain": str(energy_ledger_hash_chain),
        "boundary_flux_hash_chain": str(boundary_flux_hash_chain),
        "combustion_hash_chain": str(combustion_hash_chain),
        "reaction_hash_chain": str(reaction_hash_chain),
        "emission_hash_chain": str(emission_hash_chain),
        "impulse_hash_chain": str(impulse_hash_chain),
        "process_run_hash_chain": str(process_run_hash_chain),
        "process_quality_hash_chain": str(process_quality_hash_chain),
        "batch_quality_hash_chain": str(batch_quality_hash_chain),
        "qc_result_hash_chain": str(qc_result_hash_chain),
        "sampling_decision_hash_chain": str(sampling_decision_hash_chain),
        "process_maturity_hash_chain": str(process_maturity_hash_chain),
        "metrics_state_hash_chain": str(metrics_state_hash_chain),
        "process_cert_hash_chain": str(process_cert_hash_chain),
        "drift_state_hash_chain": str(drift_state_hash_chain),
        "drift_event_hash_chain": str(drift_event_hash_chain),
        "qc_policy_change_hash_chain": str(qc_policy_change_hash_chain),
        "revalidation_run_hash_chain": str(revalidation_run_hash_chain),
        "yield_model_hash_chain": str(yield_model_hash_chain),
        "quantity_tolerance_registry_hash": str(quantity_tolerance_registry_hash),
        "rounding_mode_policy_hash": str(rounding_mode_policy_hash),
        "entropy_hash_chain": str(entropy_hash_chain),
        "entropy_reset_events_hash_chain": str(entropy_reset_events_hash_chain),
        "fluid_flow_hash_chain": str(fluid_flow_hash_chain),
        "leak_hash_chain": str(leak_hash_chain),
        "burst_hash_chain": str(burst_hash_chain),
        "relief_event_hash_chain": str(relief_event_hash_chain),
        "field_update_hash_chain": str(field_update_hash_chain),
        "field_sample_hash_chain": str(field_sample_hash_chain),
        "boundary_field_exchange_hash_chain": str(boundary_field_exchange_hash_chain),
        "time_mapping_hash_chain": str(time_mapping_hash_chain),
        "schedule_domain_evaluation_hash": str(schedule_domain_evaluation_hash),
        "time_adjust_event_hash_chain": str(time_adjust_event_hash_chain),
        "compaction_marker_hash_chain": str(compaction_marker_hash_chain),
        "compaction_pre_anchor_hash": str(compaction_pre_anchor_hash),
        "compaction_post_anchor_hash": str(compaction_post_anchor_hash),
        "pollution_field_hash_chain": str(pollution_field_hash_chain),
        "pollution_emission_hash_chain": str(pollution_emission_hash_chain),
        "pollution_exposure_hash_chain": str(pollution_exposure_hash_chain),
        "pollution_compliance_hash_chain": str(pollution_compliance_hash_chain),
        "pollution_degradation_event_hash_chain": str(
            pollution_degradation_event_hash_chain
        ),
        "deposition_hash_chain": str(deposition_hash_chain),
        "compiled_model_hash_chain": str(compiled_model_hash_chain),
        "equivalence_proof_hash_chain": str(equivalence_proof_hash_chain),
        "compile_result_hash_chain": str(compile_result_hash_chain),
        "logic_compile_policy_hash_chain": str(logic_compile_policy_hash_chain),
        "forced_expand_event_hash_chain": str(forced_expand_event_hash_chain),
        "process_capsule_generation_hash_chain": str(
            process_capsule_generation_hash_chain
        ),
        "process_capsule_execution_hash_chain": str(
            process_capsule_execution_hash_chain
        ),
        "logic_throttle_event_hash_chain": str(logic_throttle_event_hash_chain),
        "logic_state_update_hash_chain": str(logic_state_update_hash_chain),
        "logic_output_signal_hash_chain": str(logic_output_signal_hash_chain),
        "logic_oscillation_record_hash_chain": str(logic_oscillation_record_hash_chain),
        "logic_timing_violation_hash_chain": str(logic_timing_violation_hash_chain),
        "logic_watchdog_timeout_hash_chain": str(logic_watchdog_timeout_hash_chain),
        "drift_policy_id": str(drift_policy_id),
        "deterministic_fingerprint": "",
        "extensions": dict(extensions or {}),
    }
    ext = dict(payload.get("extensions") or {})
    ext["decision_marker_count"] = int(len(markers))
    ext["decision_id_count"] = int(
        len(
            _sorted_unique_strings(
                str(row.get("control_decision_id", "")).strip()
                for row in markers
                if str(row.get("control_decision_id", "")).strip()
            )
        )
    )
    payload["extensions"] = ext
    if not str(payload.get("proof_id", "")).strip():
        payload["proof_id"] = "control.proof.{}".format(
            canonical_sha256(
                {
                    "tick_range": dict(payload.get("tick_range") or {}),
                    "decision_log_hashes": list(decision_log_hashes),
                    "fidelity_allocations_hash": str(payload.get("fidelity_allocations_hash", "")),
                    "abstraction_downgrade_hash": str(payload.get("abstraction_downgrade_hash", "")),
                    "view_policy_changes_hash": str(payload.get("view_policy_changes_hash", "")),
                    "meta_override_hash": str(payload.get("meta_override_hash", "")),
                    "mobility_event_hash": str(payload.get("mobility_event_hash", "")),
                    "congestion_hash": str(payload.get("congestion_hash", "")),
                    "signal_state_hash": str(payload.get("signal_state_hash", "")),
                    "derailment_hash": str(payload.get("derailment_hash", "")),
                    "power_flow_hash": str(payload.get("power_flow_hash", "")),
                    "power_flow_hash_chain": str(payload.get("power_flow_hash_chain", "")),
                    "fault_state_hash_chain": str(payload.get("fault_state_hash_chain", "")),
                    "protection_state_hash_chain": str(payload.get("protection_state_hash_chain", "")),
                    "degradation_event_hash_chain": str(payload.get("degradation_event_hash_chain", "")),
                    "degradation_hash_chain": str(payload.get("degradation_hash_chain", "")),
                    "maintenance_action_hash_chain": str(payload.get("maintenance_action_hash_chain", "")),
                    "trip_event_hash_chain": str(payload.get("trip_event_hash_chain", "")),
                    "trip_explanation_hash_chain": str(payload.get("trip_explanation_hash_chain", "")),
                    "thermal_network_hash": str(payload.get("thermal_network_hash", "")),
                    "thermal_network_state_hash_chain": str(payload.get("thermal_network_state_hash_chain", "")),
                    "heat_input_hash_chain": str(payload.get("heat_input_hash_chain", "")),
                    "overheat_event_hash_chain": str(payload.get("overheat_event_hash_chain", "")),
                    "ambient_exchange_hash": str(payload.get("ambient_exchange_hash", "")),
                    "fire_state_hash_chain": str(payload.get("fire_state_hash_chain", "")),
                    "ignition_event_hash_chain": str(payload.get("ignition_event_hash_chain", "")),
                    "fire_spread_hash_chain": str(payload.get("fire_spread_hash_chain", "")),
                    "fire_cascade_hash_chain": str(payload.get("fire_cascade_hash_chain", "")),
                    "runaway_event_hash_chain": str(payload.get("runaway_event_hash_chain", "")),
                    "signal_network_hash": str(payload.get("signal_network_hash", "")),
                    "message_delivery_event_hash_chain": str(payload.get("message_delivery_event_hash_chain", "")),
                    "receipt_hash_chain": str(payload.get("receipt_hash_chain", "")),
                    "trust_update_hash_chain": str(payload.get("trust_update_hash_chain", "")),
                    "jamming_event_hash_chain": str(payload.get("jamming_event_hash_chain", "")),
                    "momentum_hash_chain": str(payload.get("momentum_hash_chain", "")),
                    "impulse_event_hash_chain": str(payload.get("impulse_event_hash_chain", "")),
                    "energy_ledger_hash_chain": str(payload.get("energy_ledger_hash_chain", "")),
                    "boundary_flux_hash_chain": str(payload.get("boundary_flux_hash_chain", "")),
                    "combustion_hash_chain": str(payload.get("combustion_hash_chain", "")),
                    "reaction_hash_chain": str(payload.get("reaction_hash_chain", "")),
                    "emission_hash_chain": str(payload.get("emission_hash_chain", "")),
                    "impulse_hash_chain": str(payload.get("impulse_hash_chain", "")),
                    "process_run_hash_chain": str(payload.get("process_run_hash_chain", "")),
                    "process_quality_hash_chain": str(payload.get("process_quality_hash_chain", "")),
                    "batch_quality_hash_chain": str(payload.get("batch_quality_hash_chain", "")),
                    "qc_result_hash_chain": str(payload.get("qc_result_hash_chain", "")),
                    "sampling_decision_hash_chain": str(payload.get("sampling_decision_hash_chain", "")),
                    "process_maturity_hash_chain": str(payload.get("process_maturity_hash_chain", "")),
                    "metrics_state_hash_chain": str(payload.get("metrics_state_hash_chain", "")),
                    "process_cert_hash_chain": str(payload.get("process_cert_hash_chain", "")),
                    "drift_state_hash_chain": str(payload.get("drift_state_hash_chain", "")),
                    "drift_event_hash_chain": str(payload.get("drift_event_hash_chain", "")),
                    "qc_policy_change_hash_chain": str(
                        payload.get("qc_policy_change_hash_chain", "")
                    ),
                    "revalidation_run_hash_chain": str(
                        payload.get("revalidation_run_hash_chain", "")
                    ),
                    "yield_model_hash_chain": str(payload.get("yield_model_hash_chain", "")),
                    "quantity_tolerance_registry_hash": str(payload.get("quantity_tolerance_registry_hash", "")),
                    "rounding_mode_policy_hash": str(payload.get("rounding_mode_policy_hash", "")),
                    "entropy_hash_chain": str(payload.get("entropy_hash_chain", "")),
                    "entropy_reset_events_hash_chain": str(payload.get("entropy_reset_events_hash_chain", "")),
                    "fluid_flow_hash_chain": str(payload.get("fluid_flow_hash_chain", "")),
                    "leak_hash_chain": str(payload.get("leak_hash_chain", "")),
                    "burst_hash_chain": str(payload.get("burst_hash_chain", "")),
                    "relief_event_hash_chain": str(payload.get("relief_event_hash_chain", "")),
                    "field_update_hash_chain": str(payload.get("field_update_hash_chain", "")),
                    "field_sample_hash_chain": str(payload.get("field_sample_hash_chain", "")),
                    "boundary_field_exchange_hash_chain": str(payload.get("boundary_field_exchange_hash_chain", "")),
                    "time_mapping_hash_chain": str(payload.get("time_mapping_hash_chain", "")),
                    "schedule_domain_evaluation_hash": str(payload.get("schedule_domain_evaluation_hash", "")),
                    "time_adjust_event_hash_chain": str(payload.get("time_adjust_event_hash_chain", "")),
                    "compaction_marker_hash_chain": str(payload.get("compaction_marker_hash_chain", "")),
                    "compaction_pre_anchor_hash": str(payload.get("compaction_pre_anchor_hash", "")),
                    "compaction_post_anchor_hash": str(payload.get("compaction_post_anchor_hash", "")),
                    "pollution_field_hash_chain": str(payload.get("pollution_field_hash_chain", "")),
                    "pollution_emission_hash_chain": str(payload.get("pollution_emission_hash_chain", "")),
                    "pollution_exposure_hash_chain": str(payload.get("pollution_exposure_hash_chain", "")),
                    "pollution_compliance_hash_chain": str(payload.get("pollution_compliance_hash_chain", "")),
                    "pollution_degradation_event_hash_chain": str(payload.get("pollution_degradation_event_hash_chain", "")),
                    "deposition_hash_chain": str(payload.get("deposition_hash_chain", "")),
                    "compiled_model_hash_chain": str(payload.get("compiled_model_hash_chain", "")),
                    "equivalence_proof_hash_chain": str(payload.get("equivalence_proof_hash_chain", "")),
                    "compile_result_hash_chain": str(payload.get("compile_result_hash_chain", "")),
                    "logic_compile_policy_hash_chain": str(
                        payload.get("logic_compile_policy_hash_chain", "")
                    ),
                    "forced_expand_event_hash_chain": str(
                        payload.get("forced_expand_event_hash_chain", "")
                    ),
                    "process_capsule_generation_hash_chain": str(
                        payload.get("process_capsule_generation_hash_chain", "")
                    ),
                    "process_capsule_execution_hash_chain": str(
                        payload.get("process_capsule_execution_hash_chain", "")
                    ),
                    "logic_throttle_event_hash_chain": str(
                        payload.get("logic_throttle_event_hash_chain", "")
                    ),
                    "logic_state_update_hash_chain": str(
                        payload.get("logic_state_update_hash_chain", "")
                    ),
                    "logic_output_signal_hash_chain": str(
                        payload.get("logic_output_signal_hash_chain", "")
                    ),
                    "logic_oscillation_record_hash_chain": str(
                        payload.get("logic_oscillation_record_hash_chain", "")
                    ),
                    "logic_timing_violation_hash_chain": str(
                        payload.get("logic_timing_violation_hash_chain", "")
                    ),
                    "logic_watchdog_timeout_hash_chain": str(
                        payload.get("logic_watchdog_timeout_hash_chain", "")
                    ),
                    "drift_policy_id": str(payload.get("drift_policy_id", "")),
                }
            )[:16]
        )
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def build_control_proof_bundle_from_decision_logs(
    *,
    tick_start: int,
    tick_end: int,
    decision_log_rows: Iterable[Mapping[str, object]],
    proof_id: str = "",
    mobility_proof_surface: Mapping[str, object] | None = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    """Build deterministic control proof bundle directly from decision-log rows."""

    markers = [
        _marker_from_decision_log(dict(row))
        for row in list(decision_log_rows or [])
        if isinstance(row, Mapping)
    ]
    return build_control_proof_bundle_from_markers(
        tick_start=int(tick_start),
        tick_end=int(tick_end),
        decision_markers=markers,
        proof_id=str(proof_id),
        mobility_proof_surface=dict(mobility_proof_surface or {}),
        extensions=dict(extensions or {}),
    )


__all__ = [
    "build_control_proof_bundle_from_decision_logs",
    "build_control_proof_bundle_from_markers",
    "collect_control_decision_markers",
]
