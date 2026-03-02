"""SIG-2 deterministic message aggregation engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

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


def aggregation_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("aggregation_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("aggregation_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("aggregation_policy_id", ""))):
        policy_id = str(row.get("aggregation_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "aggregation_policy_id": policy_id,
            "input_family_ids": _sorted_tokens(row.get("input_family_ids")),
            "output_family_id": str(row.get("output_family_id", "REPORT")).strip() or "REPORT",
            "schedule_id": str(row.get("schedule_id", "")).strip(),
            "summarization_rules": _as_map(row.get("summarization_rules")),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def normalize_schedule_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("schedule_id", ""))):
        schedule_id = str(row.get("schedule_id", "")).strip()
        if not schedule_id:
            continue
        out[schedule_id] = {
            "schedule_id": schedule_id,
            "next_due_tick": int(max(0, _as_int(row.get("next_due_tick", 0), 0))),
            "interval_ticks": int(max(1, _as_int(row.get("interval_ticks", 1), 1))),
            "extensions": _as_map(row.get("extensions")),
        }
    return [dict(out[key]) for key in sorted(out.keys())]


def _policy_due(*, policy_row: Mapping[str, object], current_tick: int, schedule_rows_by_id: Mapping[str, dict]) -> bool:
    if bool(_as_map(policy_row.get("extensions")).get("disabled", False)):
        return False
    schedule_id = str(policy_row.get("schedule_id", "")).strip()
    if not schedule_id:
        return True
    schedule_row = dict(schedule_rows_by_id.get(schedule_id) or {})
    if not schedule_row:
        return False
    next_due_tick = int(max(0, _as_int(schedule_row.get("next_due_tick", 0), 0)))
    return bool(current_tick >= next_due_tick)


def _artifact_subject_id(artifact_row: Mapping[str, object]) -> str:
    row = dict(artifact_row or {})
    ext = _as_map(row.get("extensions"))
    return str(ext.get("subject_id", "")).strip() or str(row.get("subject_ref", "")).strip()


def _collect_policy_inputs(*, policy_row: Mapping[str, object], current_tick: int, info_artifact_rows: object) -> List[dict]:
    rows = normalize_info_artifact_rows(info_artifact_rows)
    families = set(_sorted_tokens(policy_row.get("input_family_ids")))
    rules = _as_map(policy_row.get("summarization_rules"))
    window_ticks = int(max(0, _as_int(rules.get("window_ticks", 0), 0)))
    max_refs = int(max(1, _as_int(rules.get("max_source_refs", 256), 256)))
    window_start = int(max(0, int(current_tick) - window_ticks)) if window_ticks > 0 else 0
    selected = []
    for row in rows:
        item = dict(row)
        family_id = str(item.get("artifact_family_id", "")).strip()
        if families and family_id not in families:
            continue
        created_tick = int(max(0, _as_int(item.get("created_tick", 0), 0)))
        if window_ticks > 0 and created_tick < window_start:
            continue
        selected.append(item)
    return sorted(selected, key=lambda item: (_as_int(item.get("created_tick", 0), 0), str(item.get("artifact_id", ""))))[:max_refs]


def _summarize_artifacts(*, policy_row: Mapping[str, object], artifacts: List[dict]) -> dict:
    rules = _as_map(policy_row.get("summarization_rules"))
    method = str(rules.get("method", "count_by_family")).strip().lower() or "count_by_family"
    if method == "disabled":
        return {"method": "disabled", "artifact_count": 0, "family_counts": {}}
    if method == "latest_by_subject":
        latest_by_subject: Dict[str, dict] = {}
        for artifact in artifacts:
            subject_id = _artifact_subject_id(artifact)
            if not subject_id:
                continue
            key = str(subject_id)
            existing = dict(latest_by_subject.get(key) or {})
            candidate = dict(artifact)
            current_sort = (_as_int(candidate.get("created_tick", 0), 0), str(candidate.get("artifact_id", "")))
            existing_sort = (_as_int(existing.get("created_tick", 0), 0), str(existing.get("artifact_id", "")))
            if (not existing) or current_sort >= existing_sort:
                latest_by_subject[key] = candidate
        rows = [
            {
                "subject_id": key,
                "artifact_id": str(value.get("artifact_id", "")).strip(),
                "created_tick": int(max(0, _as_int(value.get("created_tick", 0), 0))),
            }
            for key, value in sorted(latest_by_subject.items(), key=lambda item: str(item[0]))
        ]
        return {
            "method": "latest_by_subject",
            "artifact_count": int(len(artifacts)),
            "subject_count": int(len(rows)),
            "rows": rows,
        }
    family_counts: Dict[str, int] = {}
    for artifact in artifacts:
        family_id = str(dict(artifact).get("artifact_family_id", "")).strip() or "UNKNOWN"
        family_counts[family_id] = _as_int(family_counts.get(family_id, 0), 0) + 1
    return {
        "method": "count_by_family",
        "artifact_count": int(len(artifacts)),
        "family_counts": dict((key, int(family_counts[key])) for key in sorted(family_counts.keys())),
    }


def process_signal_aggregation_tick(
    *,
    current_tick: int,
    aggregation_policy_registry: Mapping[str, object] | None,
    schedule_rows: object,
    info_artifact_rows: object,
    signal_channel_rows: object,
    signal_message_envelope_rows: object,
    signal_transport_queue_rows: object,
    group_membership_rows: object = None,
    broadcast_scope_rows: object = None,
    decision_log_rows: object = None,
) -> dict:
    tick = int(max(0, _as_int(current_tick, 0)))
    policies = aggregation_policy_rows_by_id(aggregation_policy_registry)
    schedules = normalize_schedule_rows(schedule_rows)
    schedule_by_id = dict((str(row.get("schedule_id", "")).strip(), dict(row)) for row in schedules if str(row.get("schedule_id", "")).strip())

    next_artifacts = [dict(row) for row in list(info_artifact_rows or []) if isinstance(row, Mapping)]
    next_envelopes = [dict(row) for row in list(signal_message_envelope_rows or []) if isinstance(row, Mapping)]
    next_queue = [dict(row) for row in list(signal_transport_queue_rows or []) if isinstance(row, Mapping)]
    next_decision_rows = [dict(row) for row in list(decision_log_rows or []) if isinstance(row, Mapping)]
    next_schedule_rows = [dict(row) for row in list(schedules)]

    created_report_artifacts: List[dict] = []
    dispatched_envelopes: List[dict] = []

    for policy_id in sorted(policies.keys()):
        policy_row = dict(policies.get(policy_id) or {})
        if not _policy_due(policy_row=policy_row, current_tick=tick, schedule_rows_by_id=schedule_by_id):
            continue
        selected = _collect_policy_inputs(policy_row=policy_row, current_tick=tick, info_artifact_rows=next_artifacts)
        summary = _summarize_artifacts(policy_row=policy_row, artifacts=selected)
        artifact_id = "artifact.report.{}".format(
            canonical_sha256(
                {
                    "policy_id": policy_id,
                    "tick": tick,
                    "source_artifact_ids": [str(row.get("artifact_id", "")).strip() for row in selected],
                }
            )[:16]
        )
        report_row = {
            "schema_version": "1.0.0",
            "artifact_id": artifact_id,
            "artifact_family_id": str(policy_row.get("output_family_id", "REPORT")).strip() or "REPORT",
            "created_tick": tick,
            "source_artifact_ids": [str(row.get("artifact_id", "")).strip() for row in selected],
            "summary": dict(summary),
            "deterministic_fingerprint": "",
            "extensions": {
                "aggregation_policy_id": policy_id,
                "input_count": int(len(selected)),
            },
        }
        report_row = _with_fingerprint(report_row)
        next_artifacts.append(dict(report_row))
        created_report_artifacts.append(dict(report_row))

        policy_ext = _as_map(policy_row.get("extensions"))
        channel_id = str(policy_ext.get("dispatch_channel_id", "")).strip()
        if channel_id:
            address_type = str(policy_ext.get("dispatch_address_type", "group")).strip().lower() or "group"
            target_id = str(policy_ext.get("dispatch_target_id", "")).strip()
            if address_type == "subject":
                recipient_address = {"kind": "single", "subject_id": target_id, "to_node_id": "node.unknown"}
            elif address_type == "broadcast":
                recipient_address = {"kind": "broadcast", "broadcast_scope": target_id, "to_node_id": "node.unknown"}
            else:
                recipient_address = {"kind": "group", "group_id": target_id, "to_node_id": "node.unknown"}
            sent = process_signal_send(
                current_tick=tick,
                channel_id=channel_id,
                from_node_id=str(policy_ext.get("dispatch_from_node_id", "node.unknown")).strip() or "node.unknown",
                artifact_id=artifact_id,
                sender_subject_id=str(policy_ext.get("dispatch_sender_subject_id", "subject.system.aggregation")).strip() or "subject.system.aggregation",
                recipient_address=recipient_address,
                signal_channel_rows=signal_channel_rows,
                signal_message_envelope_rows=next_envelopes,
                signal_transport_queue_rows=next_queue,
                info_artifact_rows=next_artifacts,
                group_membership_rows=group_membership_rows,
                broadcast_scope_rows=broadcast_scope_rows,
                decision_log_rows=next_decision_rows,
                envelope_extensions={
                    "aggregation_policy_id": policy_id,
                },
            )
            next_envelopes = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or []) if isinstance(row, Mapping)]
            next_queue = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or []) if isinstance(row, Mapping)]
            next_decision_rows = [dict(row) for row in list(sent.get("decision_log_rows") or []) if isinstance(row, Mapping)]
            dispatched_envelopes.append(dict(sent.get("envelope_row") or {}))

        schedule_id = str(policy_row.get("schedule_id", "")).strip()
        if schedule_id:
            for row in next_schedule_rows:
                if str(row.get("schedule_id", "")).strip() != schedule_id:
                    continue
                interval = int(max(1, _as_int(row.get("interval_ticks", 1), 1)))
                row["next_due_tick"] = int(tick + interval)
                break

    return {
        "info_artifact_rows": sorted(
            (dict(row) for row in next_artifacts if isinstance(row, Mapping)),
            key=lambda row: (_as_int(row.get("created_tick", 0), 0), str(row.get("artifact_id", ""))),
        ),
        "signal_message_envelope_rows": next_envelopes,
        "signal_transport_queue_rows": next_queue,
        "decision_log_rows": next_decision_rows,
        "schedule_rows": sorted(
            (dict(row) for row in next_schedule_rows if isinstance(row, Mapping)),
            key=lambda row: str(row.get("schedule_id", "")),
        ),
        "created_report_artifacts": sorted(
            (dict(row) for row in created_report_artifacts if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "dispatched_envelopes": sorted(
            (dict(row) for row in dispatched_envelopes if isinstance(row, Mapping)),
            key=lambda row: str(row.get("envelope_id", "")),
        ),
    }


__all__ = [
    "aggregation_policy_rows_by_id",
    "normalize_schedule_rows",
    "process_signal_aggregation_tick",
]
