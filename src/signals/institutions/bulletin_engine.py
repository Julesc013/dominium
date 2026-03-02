"""SIG-6 deterministic institutional bulletin engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.signals.aggregation import normalize_schedule_rows
from src.signals.transport import normalize_info_artifact_rows, process_signal_send


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _with_fingerprint(row: Mapping[str, object]) -> dict:
    payload = dict(row or {})
    payload["deterministic_fingerprint"] = ""
    out = dict(payload)
    out["deterministic_fingerprint"] = canonical_sha256(payload)
    return out


def build_institution_profile(
    *,
    institution_id: str,
    bulletin_policy_id: str,
    dispatch_policy_id: str,
    standards_policy_id: str,
    channels_available: object,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "institution_id": str(institution_id or "").strip(),
        "bulletin_policy_id": str(bulletin_policy_id or "").strip(),
        "dispatch_policy_id": str(dispatch_policy_id or "").strip(),
        "standards_policy_id": str(standards_policy_id or "").strip(),
        "channels_available": _sorted_tokens(channels_available),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if (not payload["institution_id"]) or (not payload["bulletin_policy_id"]):
        return {}
    return _with_fingerprint(payload)


def normalize_institution_profile_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("institution_id", ""))):
        built = build_institution_profile(
            institution_id=str(row.get("institution_id", "")).strip(),
            bulletin_policy_id=str(row.get("bulletin_policy_id", "")).strip(),
            dispatch_policy_id=str(row.get("dispatch_policy_id", "")).strip(),
            standards_policy_id=str(row.get("standards_policy_id", "")).strip(),
            channels_available=row.get("channels_available"),
            extensions=_as_map(row.get("extensions")),
        )
        institution_id = str(built.get("institution_id", "")).strip()
        if institution_id:
            out[institution_id] = dict(built)
    return [dict(out[key]) for key in sorted(out.keys())]


def institution_profile_rows_by_id(rows: object) -> Dict[str, dict]:
    return dict(
        (str(row.get("institution_id", "")).strip(), dict(row))
        for row in normalize_institution_profile_rows(rows)
        if str(row.get("institution_id", "")).strip()
    )


def bulletin_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("bulletin_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("bulletin_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("bulletin_policy_id", ""))):
        policy_id = str(row.get("bulletin_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "bulletin_policy_id": policy_id,
            "schedule_id": str(row.get("schedule_id", "")).strip(),
            "aggregation_policy_id": str(row.get("aggregation_policy_id", "")).strip(),
            "audience_address": _as_map(row.get("audience_address")),
            "severity_rules": _as_map(row.get("severity_rules")),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _policy_due(*, policy_row: Mapping[str, object], current_tick: int, schedule_rows_by_id: Mapping[str, dict]) -> bool:
    schedule_id = str(policy_row.get("schedule_id", "")).strip()
    if not schedule_id:
        return True
    schedule_row = dict(schedule_rows_by_id.get(schedule_id) or {})
    if not schedule_row:
        return False
    next_due_tick = int(max(0, _as_int(schedule_row.get("next_due_tick", 0), 0)))
    return bool(int(current_tick) >= next_due_tick)


def _top_ids(rows: object, id_key: str, max_items: int) -> List[str]:
    values = [
        str(dict(item).get(id_key, "")).strip()
        for item in list(rows or [])
        if isinstance(item, Mapping) and str(dict(item).get(id_key, "")).strip()
    ]
    return sorted(set(values))[: int(max(1, _as_int(max_items, 16)))]


def _coarse_summary(
    *,
    institution_id: str,
    current_tick: int,
    mat_event_rows: object,
    mobility_travel_event_rows: object,
    maintenance_wear_rows: object,
    mobility_edge_occupancy_rows: object,
    spec_compliance_rows: object,
) -> dict:
    incident_count = len(
        [
            dict(item)
            for item in list(mobility_travel_event_rows or [])
            if isinstance(item, Mapping)
            and str(dict(item).get("kind", "")).strip() in {"incident_stub", "delay"}
        ]
    )
    congestion_hot_count = len(
        [
            dict(item)
            for item in list(mobility_edge_occupancy_rows or [])
            if isinstance(item, Mapping)
            and int(max(0, _as_int(dict(item).get("congestion_ratio", 0), 0))) > 1000
        ]
    )
    wear_critical_count = len(
        [
            dict(item)
            for item in list(maintenance_wear_rows or [])
            if isinstance(item, Mapping)
            and (
                bool(_as_map(dict(item).get("extensions")).get("critical", False))
                or int(max(0, _as_int(_as_map(dict(item).get("extensions")).get("wear_ratio_permille", 0), 0))) >= 1000
            )
        ]
    )
    compliance_fail_count = len(
        [
            dict(item)
            for item in list(spec_compliance_rows or [])
            if isinstance(item, Mapping)
            and str(dict(item).get("overall_grade", "")).strip() == "fail"
        ]
    )
    return {
        "institution_id": institution_id,
        "generated_tick": int(current_tick),
        "headline": {
            "event_count": int(len([item for item in list(mat_event_rows or []) if isinstance(item, Mapping)])),
            "incident_count": int(incident_count),
            "congestion_hot_edge_count": int(congestion_hot_count),
            "wear_critical_count": int(wear_critical_count),
            "compliance_fail_count": int(compliance_fail_count),
        },
    }


def _detailed_summary(
    *,
    institution_id: str,
    current_tick: int,
    mat_event_rows: object,
    mobility_travel_event_rows: object,
    maintenance_wear_rows: object,
    mobility_edge_occupancy_rows: object,
    spec_compliance_rows: object,
    max_items: int,
) -> dict:
    headline = _coarse_summary(
        institution_id=institution_id,
        current_tick=current_tick,
        mat_event_rows=mat_event_rows,
        mobility_travel_event_rows=mobility_travel_event_rows,
        maintenance_wear_rows=maintenance_wear_rows,
        mobility_edge_occupancy_rows=mobility_edge_occupancy_rows,
        spec_compliance_rows=spec_compliance_rows,
    )
    return {
        **headline,
        "sections": {
            "events": {
                "sample_event_ids": _top_ids(mat_event_rows, "event_id", max_items),
            },
            "mobility": {
                "sample_travel_event_ids": _top_ids(mobility_travel_event_rows, "event_id", max_items),
            },
            "maintenance": {
                "sample_wear_target_ids": _top_ids(maintenance_wear_rows, "target_id", max_items),
            },
            "congestion": {
                "sample_edge_ids": _top_ids(mobility_edge_occupancy_rows, "edge_id", max_items),
            },
            "compliance": {
                "sample_result_ids": _top_ids(spec_compliance_rows, "result_id", max_items),
            },
        },
    }


def _audience_to_recipient_address(audience_row: Mapping[str, object]) -> dict:
    row = _as_map(audience_row)
    address_type = str(row.get("address_type", "group")).strip().lower() or "group"
    target_id = str(row.get("target_id", "")).strip() or "group.dispatch.default"
    if address_type == "subject":
        return {"kind": "single", "subject_id": target_id, "to_node_id": str(row.get("to_node_id", "node.unknown")).strip() or "node.unknown"}
    if address_type == "broadcast":
        return {"kind": "broadcast", "broadcast_scope": target_id, "to_node_id": str(row.get("to_node_id", "node.unknown")).strip() or "node.unknown"}
    return {"kind": "group", "group_id": target_id, "to_node_id": str(row.get("to_node_id", "node.unknown")).strip() or "node.unknown"}


def process_institution_bulletin_tick(
    *,
    current_tick: int,
    institution_profile_rows: object,
    bulletin_policy_registry: Mapping[str, object] | None,
    schedule_rows: object,
    info_artifact_rows: object,
    signal_channel_rows: object,
    signal_message_envelope_rows: object,
    signal_transport_queue_rows: object,
    group_membership_rows: object = None,
    broadcast_scope_rows: object = None,
    decision_log_rows: object = None,
    mat_event_rows: object = None,
    mobility_travel_event_rows: object = None,
    maintenance_wear_rows: object = None,
    mobility_edge_occupancy_rows: object = None,
    spec_compliance_rows: object = None,
    max_cost_units: int = 0,
    cost_units_per_institution: int = 1,
    summary_max_items: int = 24,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    profile_rows = normalize_institution_profile_rows(institution_profile_rows)
    policy_rows = bulletin_policy_rows_by_id(bulletin_policy_registry)
    normalized_schedules = normalize_schedule_rows(schedule_rows)
    schedule_by_id = dict(
        (str(row.get("schedule_id", "")).strip(), dict(row))
        for row in normalized_schedules
        if str(row.get("schedule_id", "")).strip()
    )

    next_artifacts = [dict(row) for row in normalize_info_artifact_rows(info_artifact_rows)]
    next_envelopes = [dict(row) for row in list(signal_message_envelope_rows or []) if isinstance(row, Mapping)]
    next_queue = [dict(row) for row in list(signal_transport_queue_rows or []) if isinstance(row, Mapping)]
    next_decisions = [dict(row) for row in list(decision_log_rows or []) if isinstance(row, Mapping)]
    next_schedules = [dict(row) for row in list(normalized_schedules or []) if isinstance(row, Mapping)]

    unit_cost = int(max(1, _as_int(cost_units_per_institution, 1)))
    max_updates = 0 if int(max_cost_units) <= 0 else int(max(0, _as_int(max_cost_units, 0)) // unit_cost)
    updates = 0
    budget_outcome = "complete"
    processed_institutions: List[str] = []
    deferred_institutions: List[str] = []
    created_reports: List[dict] = []
    dispatched_envelopes: List[dict] = []

    for profile_row in profile_rows:
        institution_id = str(profile_row.get("institution_id", "")).strip()
        if not institution_id:
            continue
        policy_id = str(profile_row.get("bulletin_policy_id", "")).strip()
        policy_row = dict(policy_rows.get(policy_id) or {})
        if not policy_row:
            continue
        if not _policy_due(policy_row=policy_row, current_tick=tick, schedule_rows_by_id=schedule_by_id):
            continue
        if int(max_updates) > 0 and updates >= max_updates:
            deferred_institutions.append(institution_id)
            budget_outcome = "degraded"
            continue

        remaining = 0 if int(max_updates) <= 0 else int(max_updates - updates)
        coarse = bool(int(max_updates) > 0 and remaining <= 1 and len(profile_rows) > max_updates)
        summary_payload = (
            _coarse_summary(
                institution_id=institution_id,
                current_tick=tick,
                mat_event_rows=mat_event_rows,
                mobility_travel_event_rows=mobility_travel_event_rows,
                maintenance_wear_rows=maintenance_wear_rows,
                mobility_edge_occupancy_rows=mobility_edge_occupancy_rows,
                spec_compliance_rows=spec_compliance_rows,
            )
            if coarse
            else _detailed_summary(
                institution_id=institution_id,
                current_tick=tick,
                mat_event_rows=mat_event_rows,
                mobility_travel_event_rows=mobility_travel_event_rows,
                maintenance_wear_rows=maintenance_wear_rows,
                mobility_edge_occupancy_rows=mobility_edge_occupancy_rows,
                spec_compliance_rows=spec_compliance_rows,
                max_items=int(max(1, _as_int(summary_max_items, 24))),
            )
        )

        source_ids = sorted(
            set(
                _top_ids(mat_event_rows, "event_id", 256)
                + _top_ids(mobility_travel_event_rows, "event_id", 256)
                + _top_ids(spec_compliance_rows, "result_id", 256)
            )
        )
        artifact_id = "artifact.report.institution.{}".format(
            canonical_sha256(
                {
                    "institution_id": institution_id,
                    "policy_id": policy_id,
                    "tick": tick,
                    "source_ids": source_ids,
                    "coarse": bool(coarse),
                }
            )[:16]
        )
        report_row = _with_fingerprint(
            {
                "schema_version": "1.0.0",
                "artifact_id": artifact_id,
                "artifact_family_id": "REPORT",
                "created_tick": tick,
                "source_artifact_ids": source_ids,
                "summary": summary_payload,
                "deterministic_fingerprint": "",
                "extensions": {
                    "institution_id": institution_id,
                    "bulletin_policy_id": policy_id,
                    "aggregation_policy_id": str(policy_row.get("aggregation_policy_id", "")).strip() or None,
                    "coarse_summary": bool(coarse),
                },
            }
        )
        next_artifacts.append(dict(report_row))
        created_reports.append(dict(report_row))

        policy_ext = _as_map(policy_row.get("extensions"))
        channel_id = str(policy_ext.get("dispatch_channel_id", "")).strip()
        if not channel_id:
            channels_available = _sorted_tokens(profile_row.get("channels_available"))
            channel_id = channels_available[0] if channels_available else "channel.local_institutional"
        recipient_address = _audience_to_recipient_address(_as_map(policy_row.get("audience_address")))
        sent = process_signal_send(
            current_tick=tick,
            channel_id=channel_id,
            from_node_id=str(policy_ext.get("dispatch_from_node_id", "node.unknown")).strip() or "node.unknown",
            artifact_id=artifact_id,
            sender_subject_id=str(policy_ext.get("dispatch_sender_subject_id", "subject.system.institution")).strip()
            or "subject.system.institution",
            recipient_address=recipient_address,
            signal_channel_rows=signal_channel_rows,
            signal_message_envelope_rows=next_envelopes,
            signal_transport_queue_rows=next_queue,
            info_artifact_rows=next_artifacts,
            group_membership_rows=group_membership_rows,
            broadcast_scope_rows=broadcast_scope_rows,
            decision_log_rows=next_decisions,
            envelope_extensions={
                "institution_id": institution_id,
                "bulletin_policy_id": policy_id,
            },
        )
        next_envelopes = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or []) if isinstance(row, Mapping)]
        next_queue = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or []) if isinstance(row, Mapping)]
        next_decisions = [dict(row) for row in list(sent.get("decision_log_rows") or []) if isinstance(row, Mapping)]
        dispatched_envelopes.append(dict(sent.get("envelope_row") or {}))

        schedule_id = str(policy_row.get("schedule_id", "")).strip()
        if schedule_id:
            for row in next_schedules:
                if str(row.get("schedule_id", "")).strip() != schedule_id:
                    continue
                interval_ticks = int(max(1, _as_int(row.get("interval_ticks", 1), 1)))
                row["next_due_tick"] = int(tick + interval_ticks)
                break

        updates += 1
        processed_institutions.append(institution_id)

    return {
        "info_artifact_rows": sorted(
            (dict(row) for row in next_artifacts if isinstance(row, Mapping)),
            key=lambda row: (_as_int(row.get("created_tick", 0), 0), str(row.get("artifact_id", ""))),
        ),
        "signal_message_envelope_rows": list(next_envelopes),
        "signal_transport_queue_rows": list(next_queue),
        "decision_log_rows": list(next_decisions),
        "schedule_rows": sorted(
            (dict(row) for row in next_schedules if isinstance(row, Mapping)),
            key=lambda row: str(row.get("schedule_id", "")),
        ),
        "created_report_artifacts": sorted(
            (dict(row) for row in created_reports if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "dispatched_envelopes": sorted(
            (dict(row) for row in dispatched_envelopes if isinstance(row, Mapping)),
            key=lambda row: str(row.get("envelope_id", "")),
        ),
        "processed_institution_ids": sorted(set(processed_institutions)),
        "deferred_institution_ids": sorted(set(deferred_institutions)),
        "budget_outcome": str(budget_outcome),
        "cost_units": int(updates * unit_cost),
    }


__all__ = [
    "build_institution_profile",
    "bulletin_policy_rows_by_id",
    "institution_profile_rows_by_id",
    "normalize_institution_profile_rows",
    "process_institution_bulletin_tick",
]
