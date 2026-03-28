"""SIG-6 deterministic institutional dispatch engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from control import build_control_intent
from signals.transport import normalize_info_artifact_rows, process_signal_send


REFUSAL_DISPATCH_POLICY_FORBIDDEN = "refusal.dispatch.policy_forbidden"


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


def dispatch_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("dispatch_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("dispatch_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("dispatch_policy_id", ""))):
        policy_id = str(row.get("dispatch_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "dispatch_policy_id": policy_id,
            "allowed_schedule_kinds": _sorted_tokens(row.get("allowed_schedule_kinds")),
            "priority_rules": _as_map(row.get("priority_rules")),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_dispatch_update_id(
    *,
    institution_id: str,
    schedule_id: str,
    vehicle_id: str,
    itinerary_id: str,
    schedule_kind: str,
    requested_tick: int,
) -> str:
    digest = canonical_sha256(
        {
            "institution_id": str(institution_id or "").strip(),
            "schedule_id": str(schedule_id or "").strip(),
            "vehicle_id": str(vehicle_id or "").strip(),
            "itinerary_id": str(itinerary_id or "").strip(),
            "schedule_kind": str(schedule_kind or "").strip(),
            "requested_tick": int(max(0, _as_int(requested_tick, 0))),
        }
    )
    return "dispatch.update.{}".format(digest[:16])


def build_dispatch_update(
    *,
    update_id: str,
    institution_id: str,
    schedule_id: str,
    vehicle_id: str,
    itinerary_id: str,
    schedule_kind: str,
    requested_tick: int,
    priority: str,
    notes: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "update_id": str(update_id or "").strip(),
        "institution_id": str(institution_id or "").strip(),
        "schedule_id": str(schedule_id or "").strip(),
        "vehicle_id": str(vehicle_id or "").strip(),
        "itinerary_id": str(itinerary_id or "").strip(),
        "schedule_kind": str(schedule_kind or "").strip() or "travel.departure",
        "requested_tick": int(max(0, _as_int(requested_tick, 0))),
        "priority": str(priority or "").strip() or "passenger",
        "notes": str(notes or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if not payload["update_id"]:
        return {}
    return _with_fingerprint(payload)


def normalize_dispatch_update_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("update_id", ""))):
        built = build_dispatch_update(
            update_id=str(row.get("update_id", "")).strip(),
            institution_id=str(row.get("institution_id", "")).strip(),
            schedule_id=str(row.get("schedule_id", "")).strip(),
            vehicle_id=str(row.get("vehicle_id", "")).strip(),
            itinerary_id=str(row.get("itinerary_id", "")).strip(),
            schedule_kind=str(row.get("schedule_kind", "travel.departure")).strip(),
            requested_tick=_as_int(row.get("requested_tick", 0), 0),
            priority=str(row.get("priority", "passenger")).strip(),
            notes=str(row.get("notes", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        update_id = str(built.get("update_id", "")).strip()
        if update_id:
            out[update_id] = dict(built)
    return [dict(out[key]) for key in sorted(out.keys())]


def _dispatch_report_row(
    *,
    institution_id: str,
    dispatch_policy_id: str,
    accepted_updates: List[dict],
    refused_updates: List[dict],
    current_tick: int,
) -> dict:
    report_id = "artifact.report.dispatch.{}".format(
        canonical_sha256(
            {
                "institution_id": institution_id,
                "dispatch_policy_id": dispatch_policy_id,
                "tick": int(max(0, _as_int(current_tick, 0))),
                "accepted_update_ids": [str(row.get("update_id", "")).strip() for row in accepted_updates],
                "refused_update_ids": [str(row.get("update_id", "")).strip() for row in refused_updates],
            }
        )[:16]
    )
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "artifact_id": report_id,
            "artifact_family_id": "REPORT",
            "created_tick": int(max(0, _as_int(current_tick, 0))),
            "source_artifact_ids": [],
            "summary": {
                "institution_id": institution_id,
                "dispatch_policy_id": dispatch_policy_id,
                "accepted_update_count": int(len(accepted_updates)),
                "refused_update_count": int(len(refused_updates)),
                "accepted_update_ids": [str(row.get("update_id", "")).strip() for row in accepted_updates],
                "refused_update_ids": [str(row.get("update_id", "")).strip() for row in refused_updates],
            },
            "deterministic_fingerprint": "",
            "extensions": {
                "institution_id": institution_id,
                "dispatch_policy_id": dispatch_policy_id,
            },
        }
    )


def _institution_sender_subject_id(*, institution_id: str, explicit_sender_subject_id: str) -> str:
    explicit = str(explicit_sender_subject_id or "").strip()
    if explicit:
        return explicit
    token = str(institution_id or "").strip()
    if token.startswith("institution."):
        token = token[len("institution.") :]
    token = token.strip() or "unknown"
    return "subject.institution.{}".format(token)


def process_dispatch_issue_updates(
    *,
    current_tick: int,
    institution_profile_row: Mapping[str, object],
    dispatch_policy_registry: Mapping[str, object] | None,
    dispatch_update_rows: object,
    requester_subject_id: str,
    signal_channel_rows: object,
    signal_message_envelope_rows: object,
    signal_transport_queue_rows: object,
    info_artifact_rows: object,
    decision_log_rows: object = None,
    group_membership_rows: object = None,
    broadcast_scope_rows: object = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    profile_row = dict(institution_profile_row or {})
    institution_id = str(profile_row.get("institution_id", "")).strip()
    dispatch_policy_id = str(profile_row.get("dispatch_policy_id", "")).strip()
    policy_rows = dispatch_policy_rows_by_id(dispatch_policy_registry)
    dispatch_policy_row = dict(policy_rows.get(dispatch_policy_id) or {})
    allowed_schedule_kinds = set(_sorted_tokens(dispatch_policy_row.get("allowed_schedule_kinds")))

    next_artifacts = [dict(row) for row in normalize_info_artifact_rows(info_artifact_rows)]
    next_envelopes = [dict(row) for row in list(signal_message_envelope_rows or []) if isinstance(row, Mapping)]
    next_queue = [dict(row) for row in list(signal_transport_queue_rows or []) if isinstance(row, Mapping)]
    next_decisions = [dict(row) for row in list(decision_log_rows or []) if isinstance(row, Mapping)]

    updates = normalize_dispatch_update_rows(dispatch_update_rows)
    accepted_updates: List[dict] = []
    refused_updates: List[dict] = []
    emitted_control_intents: List[dict] = []
    dispatch_ir_rows: List[dict] = []

    for row in updates:
        update = dict(row)
        if institution_id and str(update.get("institution_id", "")).strip() != institution_id:
            continue
        schedule_kind = str(update.get("schedule_kind", "travel.departure")).strip() or "travel.departure"
        if allowed_schedule_kinds and schedule_kind not in allowed_schedule_kinds:
            refused = {
                "update_id": str(update.get("update_id", "")).strip(),
                "reason_code": REFUSAL_DISPATCH_POLICY_FORBIDDEN,
                "schedule_kind": schedule_kind,
            }
            refused_updates.append(refused)
            next_decisions.append(
                {
                    "decision_id": "decision.dispatch.refusal.{}".format(
                        canonical_sha256(
                            {
                                "update_id": str(update.get("update_id", "")).strip(),
                                "reason_code": REFUSAL_DISPATCH_POLICY_FORBIDDEN,
                            }
                        )[:16]
                    ),
                    "tick": tick,
                    "process_id": "process.dispatch_schedule_issue",
                    "result": "refused",
                    "reason_code": REFUSAL_DISPATCH_POLICY_FORBIDDEN,
                    "extensions": {
                        "institution_id": institution_id,
                        "dispatch_policy_id": dispatch_policy_id,
                        "update_id": str(update.get("update_id", "")).strip(),
                        "schedule_kind": schedule_kind,
                    },
                }
            )
            continue

        control_intent = build_control_intent(
            requester_subject_id=str(requester_subject_id or "").strip() or "subject.dispatch.operator",
            requested_action_id="action.decide.dispatch_update",
            target_kind="schedule",
            target_id=str(update.get("schedule_id", "")).strip() or None,
            parameters={
                "process_id": "process.travel_schedule_set",
                "inputs": {
                    "schedule_id": str(update.get("schedule_id", "")).strip(),
                    "vehicle_id": str(update.get("vehicle_id", "")).strip(),
                    "itinerary_id": str(update.get("itinerary_id", "")).strip(),
                    "kind": schedule_kind,
                    "requested_tick": int(max(0, _as_int(update.get("requested_tick", tick), tick))),
                    "priority": str(update.get("priority", "passenger")).strip() or "passenger",
                    "notes": str(update.get("notes", "")).strip(),
                    "dispatch_update_id": str(update.get("update_id", "")).strip(),
                    "institution_id": institution_id or None,
                },
            },
            abstraction_level_requested="al1",
            fidelity_requested="macro",
            view_requested="view.dispatch",
            created_tick=tick,
        )
        emitted_control_intents.append(dict(control_intent))
        dispatch_ir_rows.append(
            {
                "program_id": "dispatch.ir.{}".format(
                    canonical_sha256(
                        {
                            "control_intent_id": str(control_intent.get("control_intent_id", "")).strip(),
                            "update_id": str(update.get("update_id", "")).strip(),
                        }
                    )[:16]
                ),
                "control_intent_id": str(control_intent.get("control_intent_id", "")).strip(),
                "op_sequence": [
                    "op.request_schedule_update",
                    "op.emit_dispatch_report",
                ],
                "extensions": {
                    "dispatch_update_id": str(update.get("update_id", "")).strip(),
                    "schedule_kind": schedule_kind,
                },
            }
        )
        accepted_updates.append(dict(update))
        next_decisions.append(
            {
                "decision_id": "decision.dispatch.accept.{}".format(
                    canonical_sha256(
                        {
                            "update_id": str(update.get("update_id", "")).strip(),
                            "control_intent_id": str(control_intent.get("control_intent_id", "")).strip(),
                        }
                    )[:16]
                ),
                "tick": tick,
                "process_id": "process.dispatch_schedule_issue",
                "result": "accepted",
                "extensions": {
                    "institution_id": institution_id,
                    "dispatch_policy_id": dispatch_policy_id,
                    "update_id": str(update.get("update_id", "")).strip(),
                    "control_intent_id": str(control_intent.get("control_intent_id", "")).strip(),
                    "schedule_kind": schedule_kind,
                },
            }
        )

    dispatch_report = _dispatch_report_row(
        institution_id=institution_id or "institution.unknown",
        dispatch_policy_id=dispatch_policy_id or "dispatch.policy.unknown",
        accepted_updates=accepted_updates,
        refused_updates=refused_updates,
        current_tick=tick,
    )
    next_artifacts.append(dict(dispatch_report))

    policy_ext = _as_map(dispatch_policy_row.get("extensions"))
    channel_id = str(policy_ext.get("dispatch_report_channel_id", "")).strip()
    if not channel_id:
        channels = _sorted_tokens(profile_row.get("channels_available"))
        channel_id = channels[0] if channels else "channel.local_institutional"
    recipient_address = {
        "kind": "group",
        "group_id": str(policy_ext.get("dispatch_report_group_id", "group.dispatch.default")).strip() or "group.dispatch.default",
        "to_node_id": str(policy_ext.get("dispatch_from_node_id", "node.unknown")).strip() or "node.unknown",
    }
    sent = process_signal_send(
        current_tick=tick,
        channel_id=channel_id,
        from_node_id=str(policy_ext.get("dispatch_from_node_id", "node.unknown")).strip() or "node.unknown",
        artifact_id=str(dispatch_report.get("artifact_id", "")).strip(),
        sender_subject_id=_institution_sender_subject_id(
            institution_id=institution_id,
            explicit_sender_subject_id=str(policy_ext.get("dispatch_sender_subject_id", "")).strip(),
        ),
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
            "dispatch_policy_id": dispatch_policy_id,
            "report_kind": "dispatch_update",
        },
    )
    next_envelopes = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or []) if isinstance(row, Mapping)]
    next_queue = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or []) if isinstance(row, Mapping)]
    next_decisions = [dict(row) for row in list(sent.get("decision_log_rows") or []) if isinstance(row, Mapping)]

    return {
        "control_intent_rows": sorted(
            (dict(row) for row in emitted_control_intents if isinstance(row, Mapping)),
            key=lambda row: str(row.get("control_intent_id", "")),
        ),
        "dispatch_ir_rows": sorted(
            (dict(row) for row in dispatch_ir_rows if isinstance(row, Mapping)),
            key=lambda row: str(row.get("program_id", "")),
        ),
        "accepted_updates": sorted(
            (dict(row) for row in accepted_updates if isinstance(row, Mapping)),
            key=lambda row: str(row.get("update_id", "")),
        ),
        "refused_updates": sorted(
            (dict(row) for row in refused_updates if isinstance(row, Mapping)),
            key=lambda row: str(row.get("update_id", "")),
        ),
        "dispatch_report_artifact": dict(dispatch_report),
        "signal_message_envelope_rows": next_envelopes,
        "signal_transport_queue_rows": next_queue,
        "info_artifact_rows": sorted(
            (dict(row) for row in next_artifacts if isinstance(row, Mapping)),
            key=lambda row: (_as_int(row.get("created_tick", 0), 0), str(row.get("artifact_id", ""))),
        ),
        "decision_log_rows": next_decisions,
        "dispatched_envelope": dict(sent.get("envelope_row") or {}),
    }


__all__ = [
    "REFUSAL_DISPATCH_POLICY_FORBIDDEN",
    "build_dispatch_update",
    "deterministic_dispatch_update_id",
    "dispatch_policy_rows_by_id",
    "normalize_dispatch_update_rows",
    "process_dispatch_issue_updates",
]
