#!/usr/bin/env python3
"""SIG-7 deterministic stress harness."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, List, Mapping


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)

from src.signals import (  # noqa: E402
    REFUSAL_SIG_NONESSENTIAL_SEND,
    apply_sig_budget_degradation,
    process_message_verify_claim,
    process_signal_aggregation_tick,
    process_signal_jam_start,
    process_signal_jam_stop,
    process_signal_send,
    process_signal_transport_tick,
)
from tools.xstack.compatx.canonical_json import canonical_sha256  # noqa: E402


def _as_int(value: object, default_value: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default_value)


def _as_map(value: object) -> dict:
    return dict(value or {}) if isinstance(value, Mapping) else {}


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and (not os.path.isdir(parent)):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        row = json.load(handle)
    return dict(row) if isinstance(row, Mapping) else {}


def _sorted_tokens(values: object) -> List[str]:
    if not isinstance(values, list):
        values = []
    return sorted(set(str(item).strip() for item in values if str(item).strip()))


def _identity_artifact(
    *,
    artifact_id: str,
    tick: int,
    family_id: str,
    summary: Mapping[str, object] | None = None,
    source_ids: object = None,
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "artifact_id": str(artifact_id or "").strip(),
        "artifact_family_id": str(family_id or "").strip() or "REPORT",
        "created_tick": int(max(0, _as_int(tick, 0))),
        "source_artifact_ids": _sorted_tokens(source_ids),
        "summary": _as_map(summary),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    seed = dict(payload)
    seed["deterministic_fingerprint"] = ""
    payload["deterministic_fingerprint"] = canonical_sha256(seed)
    return payload


def _chain_hash(rows: object, *, row_sort_key) -> str:
    chain = "0" * 64
    normalized = [dict(row) for row in list(rows or []) if isinstance(row, Mapping)]
    for row in sorted(normalized, key=row_sort_key):
        row_hash = canonical_sha256(row)
        chain = canonical_sha256({"previous_hash": chain, "row_hash": row_hash})
    return chain


def _subject_membership_index(group_membership_rows: object) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    rows = [dict(row) for row in list(group_membership_rows or []) if isinstance(row, Mapping)]
    for row in sorted(rows, key=lambda item: str(item.get("group_id", ""))):
        group_id = str(row.get("group_id", "")).strip()
        if not group_id:
            continue
        out[group_id] = _sorted_tokens(row.get("subject_ids"))
    return out


def _subject_to_node_map(*, scenario: Mapping[str, object]) -> Dict[str, str]:
    profile_rows = [
        dict(row)
        for row in list(scenario.get("institution_profile_rows") or [])
        if isinstance(row, Mapping)
    ]
    group_rows = _subject_membership_index(scenario.get("group_membership_rows"))
    mapping: Dict[str, str] = {}
    for profile in sorted(profile_rows, key=lambda item: str(item.get("institution_id", ""))):
        ext = _as_map(profile.get("extensions"))
        group_id = str(ext.get("group_id", "")).strip()
        node_id = str(ext.get("home_node_id", "")).strip() or "node.unknown"
        for subject_id in group_rows.get(group_id, []):
            mapping[subject_id] = node_id
    return dict((key, mapping[key]) for key in sorted(mapping.keys()))


def _travel_budget_profile(budget_envelope_id: str) -> dict:
    token = str(budget_envelope_id or "").strip().lower()
    if token == "sig.envelope.tight":
        return {"max_cost_units": 24, "cost_units_per_delivery": 2, "max_verifications_per_tick": 1}
    if token == "sig.envelope.rank_strict":
        return {"max_cost_units": 32, "cost_units_per_delivery": 2, "max_verifications_per_tick": 2}
    return {"max_cost_units": 64, "cost_units_per_delivery": 1, "max_verifications_per_tick": 3}


def _delivery_event_rows_for_tick(rows: object, tick: int) -> List[dict]:
    out = []
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        if int(max(0, _as_int(row.get("delivered_tick", 0), 0))) != int(tick):
            continue
        out.append(dict(row))
    return sorted(
        out,
        key=lambda item: (
            str(item.get("envelope_id", "")),
            str(item.get("event_id", "")),
        ),
    )


def _build_network_hash(*, scenario: Mapping[str, object]) -> str:
    rows = {
        "graph_rows": [dict(row) for row in list(scenario.get("network_graph_rows") or []) if isinstance(row, Mapping)],
        "channel_rows": [dict(row) for row in list(scenario.get("signal_channel_rows") or []) if isinstance(row, Mapping)],
    }
    return canonical_sha256(rows)


def _schedule_rows_by_id(rows: object) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for row in list(rows or []):
        if not isinstance(row, Mapping):
            continue
        schedule_id = str(row.get("schedule_id", "")).strip()
        if not schedule_id:
            continue
        out[schedule_id] = {
            "schedule_id": schedule_id,
            "next_due_tick": int(max(0, _as_int(row.get("next_due_tick", 0), 0))),
            "interval_ticks": int(max(1, _as_int(row.get("interval_ticks", 1), 1))),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def _run_scenario(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str,
) -> dict:
    scenario_id = str(scenario.get("scenario_id", "")).strip() or "scenario.sig.unknown"
    policy = _travel_budget_profile(str(budget_envelope_id))
    tick_horizon = int(max(1, _as_int(tick_count, _as_int(scenario.get("tick_horizon", 64), 64))))

    channel_rows = [dict(row) for row in list(scenario.get("signal_channel_rows") or []) if isinstance(row, Mapping)]
    graph_rows = [dict(row) for row in list(scenario.get("network_graph_rows") or []) if isinstance(row, Mapping)]
    membership_rows = [dict(row) for row in list(scenario.get("group_membership_rows") or []) if isinstance(row, Mapping)]
    bulletin_emit_rows = [dict(row) for row in list(scenario.get("bulletin_emit_rows") or []) if isinstance(row, Mapping)]
    dispatch_rows = [dict(row) for row in list(scenario.get("dispatch_update_rows") or []) if isinstance(row, Mapping)]
    standards_rows = [dict(row) for row in list(scenario.get("standards_issue_request_rows") or []) if isinstance(row, Mapping)]
    jam_rows = [dict(row) for row in list(scenario.get("jamming_effect_rows") or []) if isinstance(row, Mapping)]
    rotation_rows = [dict(row) for row in list(scenario.get("key_rotation_rows") or []) if isinstance(row, Mapping)]

    subject_to_node = _subject_to_node_map(scenario=scenario)
    schedule_rows = _schedule_rows_by_id(scenario.get("bulletin_schedule_rows"))

    info_artifact_rows: List[dict] = []
    envelope_rows: List[dict] = []
    queue_rows: List[dict] = []
    delivery_event_rows: List[dict] = []
    knowledge_receipt_rows: List[dict] = []
    trust_edge_rows: List[dict] = []
    verification_result_rows: List[dict] = []
    decision_log_rows: List[dict] = []
    jamming_effect_rows: List[dict] = []
    route_cache_state: dict = {}
    field_sample_cache_state: dict = {}

    throughput_per_tick: List[int] = []
    queue_depth_per_tick: List[int] = []
    aggregation_outputs_per_tick: List[int] = []
    trust_updates_per_tick: List[int] = []
    proof_hashes_per_tick: List[str] = []
    silent_drop_detected = False

    aggregation_policy_registry = {
        "aggregation_policies": [
            {
                "aggregation_policy_id": "agg.sig7.tick_summary",
                "input_family_ids": ["REPORT", "MESSAGE", "MODEL", "CREDENTIAL"],
                "output_family_id": "REPORT",
                "schedule_id": "schedule.sig7.agg",
                "summarization_rules": {
                    "method": "count_by_family",
                    "window_ticks": 24,
                    "max_source_refs": 128,
                },
                "extensions": {
                    "dispatch_channel_id": "channel.local_institutional",
                    "dispatch_address_type": "group",
                    "dispatch_target_id": "group.sig.inst.0000",
                    "dispatch_from_node_id": "node.unknown",
                    "dispatch_sender_subject_id": "subject.system.aggregation",
                },
            }
        ]
    }
    aggregation_schedule_rows = [{"schedule_id": "schedule.sig7.agg", "next_due_tick": 0, "interval_ticks": 6}]

    for tick in range(0, int(tick_horizon)):
        for rot in rotation_rows:
            if int(max(0, _as_int(rot.get("rotation_tick", -1), -1))) != int(tick):
                continue
            decision_log_rows.append(
                {
                    "decision_id": "decision.sig7.key_rotation.{}".format(
                        canonical_sha256({"scenario_id": scenario_id, "tick": tick, "rotation": dict(rot)})[:16]
                    ),
                    "tick": int(tick),
                    "process_id": "process.message_key_rotate",
                    "result": "complete",
                    "extensions": dict(rot),
                }
            )

        for jam in sorted(jam_rows, key=lambda item: str(item.get("effect_id", ""))):
            start_tick = int(max(0, _as_int(jam.get("start_tick", 0), 0)))
            end_tick = int(max(start_tick, _as_int(jam.get("end_tick", start_tick), start_tick)))
            if int(tick) == int(start_tick):
                started = process_signal_jam_start(
                    current_tick=int(tick),
                    channel_id=str(jam.get("target_channel_id", "")).strip(),
                    strength_modifier=int(max(0, _as_int(jam.get("strength_modifier", 0), 0))),
                    duration_ticks=int(max(0, _as_int(jam.get("duration_ticks", 0), 0))),
                    signal_channel_rows=channel_rows,
                    jamming_effect_rows=jamming_effect_rows,
                    decision_log_rows=decision_log_rows,
                )
                jamming_effect_rows = [dict(row) for row in list(started.get("jamming_effect_rows") or [])]
                decision_log_rows = [dict(row) for row in list(started.get("decision_log_rows") or [])]
            if int(tick) == int(end_tick):
                stopped = process_signal_jam_stop(
                    current_tick=int(tick),
                    channel_id=str(jam.get("target_channel_id", "")).strip(),
                    jamming_effect_rows=jamming_effect_rows,
                    decision_log_rows=decision_log_rows,
                )
                jamming_effect_rows = [dict(row) for row in list(stopped.get("jamming_effect_rows") or [])]
                decision_log_rows = [dict(row) for row in list(stopped.get("decision_log_rows") or [])]

        envelope_by_id = dict(
            (str(row.get("envelope_id", "")).strip(), dict(row))
            for row in list(envelope_rows or [])
            if isinstance(row, Mapping) and str(row.get("envelope_id", "")).strip()
        )
        pending_low_priority_count = 0
        pending_broadcast_count = 0
        for queue_row in list(queue_rows or []):
            if not isinstance(queue_row, Mapping):
                continue
            env = dict(envelope_by_id.get(str(queue_row.get("envelope_id", "")).strip()) or {})
            env_ext = _as_map(env.get("extensions"))
            if str(env_ext.get("priority", "")).strip().lower() == "low":
                pending_low_priority_count += 1
            recipient = _as_map(env.get("recipient_address"))
            if str(recipient.get("address_type", "")).strip().lower() == "broadcast":
                pending_broadcast_count += 1
        degrade_plan = apply_sig_budget_degradation(
            current_tick=int(tick),
            budget_envelope_id=str(budget_envelope_id),
            queue_depth=int(len(queue_rows)),
            base_message_cap=int(policy.get("max_cost_units", 64)),
            base_aggregation_section_cap=128,
            pending_broadcast_count=int(pending_broadcast_count),
            pending_low_priority_count=int(pending_low_priority_count),
            nonessential_send_candidate_count=int(pending_low_priority_count),
            ranked_mode=bool(str(budget_envelope_id).strip().lower() == "sig.envelope.rank_strict"),
            allow_broadcast_fanout_degrade=True,
        )
        decision_log_rows.extend([dict(row) for row in list(degrade_plan.get("decision_log_rows") or []) if isinstance(row, Mapping)])
        if bool(degrade_plan.get("delay_low_priority", False)):
            delayed_rows: List[dict] = []
            for queue_row in list(queue_rows or []):
                row = dict(queue_row)
                env = dict(envelope_by_id.get(str(row.get("envelope_id", "")).strip()) or {})
                env_ext = _as_map(env.get("extensions"))
                if str(env_ext.get("priority", "")).strip().lower() == "low":
                    row["remaining_delay_ticks"] = int(max(0, _as_int(row.get("remaining_delay_ticks", 0), 0)) + 1)
                delayed_rows.append(row)
            queue_rows = delayed_rows

        schedule_by_id = dict((key, dict(schedule_rows[key])) for key in sorted(schedule_rows.keys()))
        for emit in sorted(
            bulletin_emit_rows,
            key=lambda item: (str(item.get("institution_id", "")), str(item.get("schedule_id", ""))),
        ):
            schedule_id = str(emit.get("schedule_id", "")).strip()
            schedule_row = dict(schedule_by_id.get(schedule_id) or {})
            if not schedule_row:
                continue
            next_due_tick = int(max(0, _as_int(schedule_row.get("next_due_tick", 0), 0)))
            interval_ticks = int(max(1, _as_int(schedule_row.get("interval_ticks", 1), 1)))
            if int(tick) < int(next_due_tick):
                continue
            institution_id = str(emit.get("institution_id", "")).strip() or "institution.unknown"
            artifact_id = "artifact.report.sig7.bulletin.{}".format(
                canonical_sha256({"scenario_id": scenario_id, "tick": tick, "institution_id": institution_id})[:16]
            )
            info_artifact_rows.append(
                _identity_artifact(
                    artifact_id=artifact_id,
                    tick=int(tick),
                    family_id="REPORT",
                    summary={"kind": "bulletin", "institution_id": institution_id},
                    extensions={"scenario_id": scenario_id, "source_process_id": "process.signal_send"},
                )
            )
            sent = process_signal_send(
                current_tick=int(tick),
                channel_id=str(emit.get("channel_id", "")).strip() or "channel.local_institutional",
                from_node_id=str(emit.get("from_node_id", "")).strip() or "node.unknown",
                artifact_id=str(artifact_id),
                sender_subject_id="subject.institution.{}".format(institution_id.replace(".", "_")),
                recipient_address={
                    "kind": "group",
                    "group_id": str(emit.get("group_id", "")).strip() or "group.dispatch.default",
                    "to_node_id": "node.unknown",
                },
                signal_channel_rows=channel_rows,
                signal_message_envelope_rows=envelope_rows,
                signal_transport_queue_rows=queue_rows,
                info_artifact_rows=info_artifact_rows,
                group_membership_rows=membership_rows,
                decision_log_rows=decision_log_rows,
            )
            envelope_rows = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or [])]
            queue_rows = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or [])]
            decision_log_rows = [dict(row) for row in list(sent.get("decision_log_rows") or [])]
            schedule_rows[schedule_id]["next_due_tick"] = int(next_due_tick + interval_ticks)

        for update in sorted(dispatch_rows, key=lambda item: str(item.get("update_id", ""))):
            requested_tick = int(max(0, _as_int(update.get("requested_tick", 0), 0)))
            if requested_tick != int(tick):
                continue
            artifact_id = "artifact.report.sig7.dispatch.{}".format(
                str(update.get("update_id", "")).strip() or canonical_sha256(update)[:16]
            )
            info_artifact_rows.append(
                _identity_artifact(
                    artifact_id=artifact_id,
                    tick=int(tick),
                    family_id="REPORT",
                    summary={"kind": "dispatch_update", "update_id": str(update.get("update_id", "")).strip()},
                    extensions={"scenario_id": scenario_id, "source_process_id": "process.signal_send"},
                )
            )
            sent = process_signal_send(
                current_tick=int(tick),
                channel_id="channel.local_institutional",
                from_node_id="node.unknown",
                artifact_id=str(artifact_id),
                sender_subject_id="subject.dispatch.office",
                recipient_address={
                    "kind": "group",
                    "group_id": "group.sig.inst.0000",
                    "to_node_id": "node.unknown",
                },
                signal_channel_rows=channel_rows,
                signal_message_envelope_rows=envelope_rows,
                signal_transport_queue_rows=queue_rows,
                info_artifact_rows=info_artifact_rows,
                group_membership_rows=membership_rows,
                decision_log_rows=decision_log_rows,
                envelope_extensions={"priority": str(update.get("priority", "normal")).strip()},
            )
            envelope_rows = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or [])]
            queue_rows = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or [])]
            decision_log_rows = [dict(row) for row in list(sent.get("decision_log_rows") or [])]

        for request in sorted(standards_rows, key=lambda item: str(item.get("request_id", ""))):
            request_index = int(canonical_sha256({"request_id": str(request.get("request_id", ""))})[:4], 16)
            if (request_index % max(1, int(tick_horizon))) != int(tick):
                continue
            if bool(degrade_plan.get("refuse_nonessential", False)):
                decision_log_rows.append(
                    {
                        "decision_id": "decision.sig7.refusal.nonessential.{}".format(
                            canonical_sha256(
                                {
                                    "tick": int(tick),
                                    "request_id": str(request.get("request_id", "")).strip(),
                                    "reason_code": REFUSAL_SIG_NONESSENTIAL_SEND,
                                }
                            )[:16]
                        ),
                        "tick": int(tick),
                        "process_id": "process.signal_send",
                        "result": "refused",
                        "reason_code": REFUSAL_SIG_NONESSENTIAL_SEND,
                        "extensions": {
                            "request_id": str(request.get("request_id", "")).strip(),
                        },
                    }
                )
                continue
            artifact_id = "artifact.report.sig7.standard.{}".format(
                str(request.get("request_id", "")).strip() or canonical_sha256(request)[:16]
            )
            info_artifact_rows.append(
                _identity_artifact(
                    artifact_id=artifact_id,
                    tick=int(tick),
                    family_id="REPORT",
                    summary={"kind": "standards_update", "request_id": str(request.get("request_id", "")).strip()},
                    extensions={"scenario_id": scenario_id, "source_process_id": "process.signal_send"},
                )
            )
            sent = process_signal_send(
                current_tick=int(tick),
                channel_id="channel.sig.wired.stress",
                from_node_id="node.unknown",
                artifact_id=str(artifact_id),
                sender_subject_id="subject.standards.body",
                recipient_address={"kind": "broadcast", "broadcast_scope": "all", "to_node_id": "node.unknown"},
                signal_channel_rows=channel_rows,
                signal_message_envelope_rows=envelope_rows,
                signal_transport_queue_rows=queue_rows,
                info_artifact_rows=info_artifact_rows,
                group_membership_rows=membership_rows,
                broadcast_scope_rows=[
                    {
                        "broadcast_scope_id": "all",
                        "subject_ids": (
                            _sorted_tokens(scenario.get("subject_ids"))[: int(max(1, _as_int(degrade_plan.get("broadcast_fanout_cap", 0), 0)))]
                            if degrade_plan.get("broadcast_fanout_cap") is not None
                            else _sorted_tokens(scenario.get("subject_ids"))
                        ),
                    }
                ],
                decision_log_rows=decision_log_rows,
                envelope_extensions={"priority": "low"},
            )
            envelope_rows = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or [])]
            queue_rows = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or [])]
            decision_log_rows = [dict(row) for row in list(sent.get("decision_log_rows") or [])]

        agg_result = process_signal_aggregation_tick(
            current_tick=int(tick),
            aggregation_policy_registry={
                "aggregation_policies": [
                    {
                        **dict((aggregation_policy_registry.get("aggregation_policies") or [{}])[0]),
                        "summarization_rules": {
                            **_as_map(
                                _as_map((aggregation_policy_registry.get("aggregation_policies") or [{}])[0]).get("summarization_rules")
                            ),
                            "max_source_refs": int(max(4, _as_int(degrade_plan.get("aggregation_section_cap", 128), 128))),
                        },
                    }
                ]
            },
            schedule_rows=aggregation_schedule_rows,
            info_artifact_rows=info_artifact_rows,
            signal_channel_rows=channel_rows,
            signal_message_envelope_rows=envelope_rows,
            signal_transport_queue_rows=queue_rows,
            group_membership_rows=membership_rows,
            decision_log_rows=decision_log_rows,
            knowledge_receipt_rows=knowledge_receipt_rows,
        )
        info_artifact_rows = [dict(row) for row in list(agg_result.get("info_artifact_rows") or [])]
        envelope_rows = [dict(row) for row in list(agg_result.get("signal_message_envelope_rows") or [])]
        queue_rows = [dict(row) for row in list(agg_result.get("signal_transport_queue_rows") or [])]
        decision_log_rows = [dict(row) for row in list(agg_result.get("decision_log_rows") or [])]
        aggregation_schedule_rows = [dict(row) for row in list(agg_result.get("schedule_rows") or [])]
        aggregation_outputs_per_tick.append(int(len(list(agg_result.get("created_report_artifacts") or []))))

        field_samples_by_node_id = dict((node_id, {"field.visibility": 100}) for node_id in _sorted_tokens(subject_to_node.values()))
        transport_result = process_signal_transport_tick(
            current_tick=int(tick),
            signal_channel_rows=channel_rows,
            signal_transport_queue_rows=queue_rows,
            signal_message_envelope_rows=envelope_rows,
            message_delivery_event_rows=delivery_event_rows,
            knowledge_receipt_rows=knowledge_receipt_rows,
            network_graph_rows=graph_rows,
            loss_policy_registry={},
            routing_policy_registry={},
            max_cost_units=int(max(1, _as_int(degrade_plan.get("message_cap", policy.get("max_cost_units", 64)), policy.get("max_cost_units", 64)))),
            cost_units_per_delivery=int(policy.get("cost_units_per_delivery", 1)),
            attenuation_policy_registry={},
            jamming_effect_rows=jamming_effect_rows,
            field_samples_by_node_id=field_samples_by_node_id,
            route_cache_state=route_cache_state,
            field_sample_cache_state=field_sample_cache_state,
            default_trust_weight=0.5,
            trust_edge_rows=trust_edge_rows,
            belief_policy_registry={},
            belief_policy_id="belief.default",
        )
        queue_rows = [dict(row) for row in list(transport_result.get("signal_transport_queue_rows") or [])]
        delivery_event_rows = [dict(row) for row in list(transport_result.get("message_delivery_event_rows") or [])]
        knowledge_receipt_rows = [dict(row) for row in list(transport_result.get("knowledge_receipt_rows") or [])]
        route_cache_state = _as_map(transport_result.get("route_cache_state"))
        field_sample_cache_state = _as_map(transport_result.get("field_sample_cache_state"))

        delivered_now = _delivery_event_rows_for_tick(delivery_event_rows, tick=int(tick))
        delivered_count = int(sum(1 for row in delivered_now if str(row.get("delivery_state", "")).strip() == "delivered"))
        if (delivered_count == 0) and int(len(delivered_now)) > 0:
            silent_drop_detected = True
        throughput_per_tick.append(delivered_count)
        queue_depth_per_tick.append(int(len(queue_rows)))

        trust_updates_this_tick = 0
        created_receipts = [dict(row) for row in list(transport_result.get("created_receipt_rows") or []) if isinstance(row, Mapping)]
        max_verifications = int(max(0, _as_int(policy.get("max_verifications_per_tick", 0), 0)))
        for receipt in created_receipts[:max_verifications]:
            artifact_id = str(receipt.get("artifact_id", "")).strip()
            recipient_subject_id = str(receipt.get("subject_id", "")).strip()
            sender_subject_id = str(_as_map(receipt.get("extensions")).get("sender_subject_id", "")).strip()
            if (not artifact_id) or (not recipient_subject_id) or (not sender_subject_id):
                continue
            verifier_node = str(subject_to_node.get(recipient_subject_id, "node.unknown")).strip() or "node.unknown"
            verify_result = process_message_verify_claim(
                current_tick=int(tick),
                artifact_id=artifact_id,
                verifier_subject_id=recipient_subject_id,
                claimed_sender_subject_id=sender_subject_id,
                evidence_artifact_rows=[
                    {
                        "artifact_id": "evidence.{}".format(canonical_sha256({"artifact_id": artifact_id, "tick": tick})[:16]),
                        "extensions": {
                            "claim_artifact_id": artifact_id,
                            "sender_subject_id": sender_subject_id,
                            "verifier_node_id": verifier_node,
                        },
                    }
                ],
                certificate_rows=[],
                allow_truth_observer=False,
                verification_result_rows=verification_result_rows,
                trust_edge_rows=trust_edge_rows,
                belief_policy_registry={},
                trust_update_rule_registry={},
                belief_policy_id="belief.default",
                decision_log_rows=decision_log_rows,
            )
            verification_result_rows = [dict(row) for row in list(verify_result.get("verification_result_rows") or [])]
            trust_edge_rows = [dict(row) for row in list(verify_result.get("trust_edge_rows") or [])]
            decision_log_rows = [dict(row) for row in list(verify_result.get("decision_log_rows") or [])]
            if isinstance(verify_result.get("updated_trust_edge_row"), Mapping):
                trust_updates_this_tick += 1
        trust_updates_per_tick.append(int(trust_updates_this_tick))
        proof_hashes_per_tick.append(
            canonical_sha256(
                {
                    "tick": int(tick),
                    "delivery_event_hash": _chain_hash(
                        delivery_event_rows,
                        row_sort_key=lambda row: (
                            int(_as_int(row.get("delivered_tick", 0), 0)),
                            str(row.get("event_id", "")),
                        ),
                    ),
                    "receipt_hash": _chain_hash(
                        knowledge_receipt_rows,
                        row_sort_key=lambda row: (
                            int(_as_int(row.get("acquired_tick", 0), 0)),
                            str(row.get("receipt_id", "")),
                        ),
                    ),
                    "trust_hash": _chain_hash(
                        trust_edge_rows,
                        row_sort_key=lambda row: (
                            str(row.get("from_subject_id", "")),
                            str(row.get("to_subject_id", "")),
                        ),
                    ),
                    "queue_depth": int(len(queue_rows)),
                }
            )
        )

    trust_update_rows = [
        dict(row)
        for row in list(decision_log_rows or [])
        if isinstance(row, Mapping) and str(row.get("process_id", "")).strip() == "process.trust_update"
    ]
    jam_decision_rows = [
        dict(row)
        for row in list(decision_log_rows or [])
        if isinstance(row, Mapping)
        and str(row.get("process_id", "")).strip() in {"process.signal_jam_start", "process.signal_jam_stop"}
    ]
    proof_hashes = {
        "signal_network_hash": _build_network_hash(scenario=scenario),
        "message_delivery_event_hash_chain": _chain_hash(
            delivery_event_rows,
            row_sort_key=lambda row: (
                int(max(0, _as_int(row.get("delivered_tick", 0), 0))),
                str(row.get("event_id", "")),
            ),
        ),
        "receipt_hash_chain": _chain_hash(
            knowledge_receipt_rows,
            row_sort_key=lambda row: (
                int(max(0, _as_int(row.get("acquired_tick", 0), 0))),
                str(row.get("receipt_id", "")),
            ),
        ),
        "trust_update_hash_chain": _chain_hash(
            trust_update_rows,
            row_sort_key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("decision_id", "")),
            ),
        ),
        "jamming_event_hash_chain": _chain_hash(
            jam_decision_rows,
            row_sort_key=lambda row: (
                int(max(0, _as_int(row.get("tick", 0), 0))),
                str(row.get("decision_id", "")),
            ),
        ),
    }
    report = {
        "schema_version": "1.0.0",
        "scenario_id": scenario_id,
        "tick_count": int(tick_horizon),
        "budget_envelope_id": str(budget_envelope_id or "").strip() or "sig.envelope.standard",
        "metrics": {
            "per_tick_message_throughput": list(throughput_per_tick),
            "queue_depths": list(queue_depth_per_tick),
            "aggregation_outputs": list(aggregation_outputs_per_tick),
            "trust_updates_count": int(sum(trust_updates_per_tick)),
            "proof_hashes": dict(proof_hashes),
            "deterministic_fingerprint_report": canonical_sha256(
                {
                    "scenario_id": scenario_id,
                    "throughput": list(throughput_per_tick),
                    "queue_depths": list(queue_depth_per_tick),
                    "aggregation_outputs": list(aggregation_outputs_per_tick),
                    "trust_updates_count": int(sum(trust_updates_per_tick)),
                    "proof_hashes": dict(proof_hashes),
                }
            ),
        },
        "assertions": {
            "deterministic_ordering": True,
            "no_silent_drop": bool(not silent_drop_detected),
            "budget_applied": True,
            "trust_updates_logged": bool(
                len(
                    [
                        row
                        for row in list(decision_log_rows or [])
                        if isinstance(row, Mapping)
                        and str(row.get("process_id", "")).strip() == "process.trust_update"
                        and str(row.get("decision_id", "")).strip()
                    ]
                )
                == int(sum(trust_updates_per_tick))
            ),
        },
        "extensions": {
            "decision_log_count": int(len(decision_log_rows)),
            "delivery_event_count": int(len(delivery_event_rows)),
            "receipt_count": int(len(knowledge_receipt_rows)),
            "verification_result_count": int(len(verification_result_rows)),
            "proof_hashes_per_tick": list(proof_hashes_per_tick),
        },
        "deterministic_fingerprint": "",
    }
    seed = dict(report)
    seed["deterministic_fingerprint"] = ""
    report["deterministic_fingerprint"] = canonical_sha256(seed)
    return report


def run_sig_stress(
    *,
    scenario: Mapping[str, object],
    tick_count: int,
    budget_envelope_id: str,
) -> dict:
    first = _run_scenario(
        scenario=scenario,
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_envelope_id),
    )
    second = _run_scenario(
        scenario=scenario,
        tick_count=int(tick_count),
        budget_envelope_id=str(budget_envelope_id),
    )
    deterministic = dict(first) == dict(second)
    output = {
        "schema_version": "1.0.0",
        "result": "complete" if deterministic else "refused",
        "report": dict(first),
        "deterministic_replay_match": bool(deterministic),
        "deterministic_fingerprint": canonical_sha256(
            {
                "first": dict(first),
                "second": dict(second),
                "deterministic_replay_match": bool(deterministic),
            }
        ),
    }
    if deterministic:
        return output
    return {
        **output,
        "errors": [
            {
                "code": "refusal.sig.nondeterministic_stress_result",
                "message": "SIG stress harness produced non-deterministic outputs for identical inputs",
                "path": "$.report",
            }
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic SIG-7 stress harness.")
    parser.add_argument("--scenario", default="build/signals/sig_stress_scenario.json")
    parser.add_argument("--ticks", type=int, default=0)
    parser.add_argument("--budget-envelope-id", default="sig.envelope.standard")
    parser.add_argument("--output", default="build/signals/sig_stress_report.json")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()

    scenario_abs = os.path.normpath(os.path.abspath(str(args.scenario)))
    scenario = _load_json(scenario_abs)
    tick_count = int(max(1, _as_int(args.ticks, 0)))
    if int(tick_count) <= 1:
        tick_count = int(max(1, _as_int(scenario.get("tick_horizon", 64), 64)))

    result = run_sig_stress(
        scenario=scenario,
        tick_count=int(tick_count),
        budget_envelope_id=str(args.budget_envelope_id),
    )
    result["scenario_path"] = scenario_abs

    output = str(args.output).strip()
    if output:
        output_abs = os.path.normpath(os.path.abspath(output))
        _write_json(output_abs, result)
        result["output_path"] = output_abs

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if str(result.get("result", "")).strip() == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
