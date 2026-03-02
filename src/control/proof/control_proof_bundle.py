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
        "signal_network_hash": str(signal_network_hash),
        "message_delivery_event_hash_chain": str(message_delivery_event_hash_chain),
        "receipt_hash_chain": str(receipt_hash_chain),
        "trust_update_hash_chain": str(trust_update_hash_chain),
        "jamming_event_hash_chain": str(jamming_event_hash_chain),
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
                    "signal_network_hash": str(payload.get("signal_network_hash", "")),
                    "message_delivery_event_hash_chain": str(payload.get("message_delivery_event_hash_chain", "")),
                    "receipt_hash_chain": str(payload.get("receipt_hash_chain", "")),
                    "trust_update_hash_chain": str(payload.get("trust_update_hash_chain", "")),
                    "jamming_event_hash_chain": str(payload.get("jamming_event_hash_chain", "")),
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
