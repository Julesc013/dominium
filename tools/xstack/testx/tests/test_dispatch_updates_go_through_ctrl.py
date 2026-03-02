"""FAST test: SIG-6 dispatch updates are emitted through ControlIntent rows."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.institutions.dispatch_updates_go_through_ctrl"
TEST_TAGS = ["fast", "signals", "institutions", "dispatch", "control"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.signals import (
        build_dispatch_update,
        build_signal_channel,
        deterministic_dispatch_update_id,
        process_dispatch_issue_updates,
    )

    institution_profile = {
        "schema_version": "1.0.0",
        "institution_id": "institution.metro_dispatch",
        "bulletin_policy_id": "bulletin.daily_local",
        "dispatch_policy_id": "dispatch.rail_basic",
        "standards_policy_id": "standards.basic_body",
        "channels_available": ["channel.local_institutional"],
        "extensions": {},
    }
    dispatch_registry = {
        "record": {
            "dispatch_policies": [
                {
                    "schema_version": "1.0.0",
                    "dispatch_policy_id": "dispatch.rail_basic",
                    "allowed_schedule_kinds": ["travel.departure", "travel.arrive"],
                    "priority_rules": {},
                    "extensions": {
                        "dispatch_report_channel_id": "channel.local_institutional",
                        "dispatch_from_node_id": "node.metro.a",
                    },
                }
            ]
        }
    }
    update_id = deterministic_dispatch_update_id(
        institution_id="institution.metro_dispatch",
        schedule_id="schedule.metro.001",
        vehicle_id="vehicle.metro.001",
        itinerary_id="itinerary.metro.001",
        schedule_kind="travel.departure",
        requested_tick=600,
    )
    updates = [
        build_dispatch_update(
            update_id=update_id,
            institution_id="institution.metro_dispatch",
            schedule_id="schedule.metro.001",
            vehicle_id="vehicle.metro.001",
            itinerary_id="itinerary.metro.001",
            schedule_kind="travel.departure",
            requested_tick=600,
            priority="passenger",
            notes="platform assignment stable",
            extensions={},
        )
    ]
    out = process_dispatch_issue_updates(
        current_tick=580,
        institution_profile_row=institution_profile,
        dispatch_policy_registry=dispatch_registry,
        dispatch_update_rows=updates,
        requester_subject_id="subject.dispatcher.metro",
        signal_channel_rows=[
            build_signal_channel(
                channel_id="channel.local_institutional",
                channel_type_id="channel.local_institutional",
                network_graph_id="graph.sig.metro.001",
                capacity_per_tick=16,
                base_delay_ticks=0,
                loss_policy_id="loss.none",
                encryption_policy_id="enc.none",
            )
        ],
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
        info_artifact_rows=[],
    )
    intents = list(out.get("control_intent_rows") or [])
    if len(intents) != 1:
        return {"status": "fail", "message": "dispatch update should emit exactly one control intent"}
    intent = dict(intents[0])
    params = dict(intent.get("parameters") or {})
    inputs = dict(params.get("inputs") or {})
    process_id = str(dict(params).get("process_id", "")).strip()
    if process_id != "process.travel_schedule_set":
        return {"status": "fail", "message": "dispatch update must route through process.travel_schedule_set"}
    if str(inputs.get("dispatch_update_id", "")).strip() != update_id:
        return {"status": "fail", "message": "control intent inputs missing deterministic dispatch_update_id"}
    if not dict(out.get("dispatch_report_artifact") or {}):
        return {"status": "fail", "message": "dispatch report artifact not produced"}
    if not dict(out.get("dispatched_envelope") or {}):
        return {"status": "fail", "message": "dispatch report not sent through signal pipeline"}
    return {"status": "pass", "message": "dispatch updates go through control intent path"}
