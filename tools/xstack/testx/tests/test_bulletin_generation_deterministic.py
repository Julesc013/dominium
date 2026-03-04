"""FAST test: SIG-6 bulletin generation is deterministic."""

from __future__ import annotations

import copy
import sys


TEST_ID = "testx.signals.institutions.bulletin_generation_deterministic"
TEST_TAGS = ["fast", "signals", "institutions", "bulletin", "determinism"]


def _run_once() -> dict:
    from src.signals import build_institution_profile, build_signal_channel, process_institution_bulletin_tick

    institution_profiles = [
        build_institution_profile(
            institution_id="institution.metro_dispatch",
            bulletin_policy_id="bulletin.daily_local",
            dispatch_policy_id="dispatch.rail_basic",
            standards_policy_id="standards.basic_body",
            channels_available=["channel.local_institutional"],
            extensions={},
        )
    ]
    bulletin_registry = {
        "record": {
            "bulletin_policies": [
                {
                    "schema_version": "1.0.0",
                    "bulletin_policy_id": "bulletin.daily_local",
                    "schedule_id": "schedule.bulletin.daily.metro",
                    "aggregation_policy_id": "agg.daily_summary",
                    "audience_address": {
                        "address_type": "group",
                        "target_id": "group.metro.public",
                        "to_node_id": "node.metro.a",
                    },
                    "severity_rules": {},
                    "extensions": {
                        "dispatch_channel_id": "channel.local_institutional",
                        "dispatch_from_node_id": "node.metro.a",
                    },
                }
            ]
        }
    }
    schedule_rows = [
        {
            "schema_version": "1.0.0",
            "schedule_id": "schedule.bulletin.daily.metro",
            "temporal_domain_id": "time.canonical_tick",
            "next_due_tick": 500,
            "interval_ticks": 1440,
            "extensions": {},
        }
    ]
    channels = [
        build_signal_channel(
            channel_id="channel.local_institutional",
            channel_type_id="channel.local_institutional",
            network_graph_id="graph.sig.metro.001",
            capacity_per_tick=16,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    out = process_institution_bulletin_tick(
        current_tick=500,
        institution_profile_rows=institution_profiles,
        bulletin_policy_registry=bulletin_registry,
        schedule_rows=schedule_rows,
        info_artifact_rows=[],
        signal_channel_rows=channels,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
        group_membership_rows=[{"group_id": "group.metro.public", "subject_ids": ["subject.a", "subject.b"]}],
        mat_event_rows=[{"event_id": "event.metro.001"}],
        mobility_travel_event_rows=[{"event_id": "event.travel.001", "kind": "delay"}],
        maintenance_wear_rows=[{"target_id": "edge.track.01", "extensions": {"wear_ratio_permille": 250}}],
        mobility_edge_occupancy_rows=[{"edge_id": "edge.track.01", "congestion_ratio": 300}],
        spec_compliance_rows=[{"result_id": "spec.result.001", "overall_grade": "pass"}],
        max_cost_units=4,
        cost_units_per_institution=1,
    )
    return {
        "created_report_artifacts": list(out.get("created_report_artifacts") or []),
        "dispatched_envelopes": list(out.get("dispatched_envelopes") or []),
        "signal_transport_queue_rows": list(out.get("signal_transport_queue_rows") or []),
        "processed_institution_ids": list(out.get("processed_institution_ids") or []),
        "budget_outcome": str(out.get("budget_outcome", "")),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "bulletin generation drifted across identical runs"}
    reports = list(first.get("created_report_artifacts") or [])
    if not reports:
        return {"status": "fail", "message": "expected bulletin report artifact"}
    family_id = str(dict(reports[0]).get("artifact_family_id", "")).strip()
    if family_id != "REPORT":
        return {"status": "fail", "message": "bulletin should emit REPORT artifact"}
    queues = list(first.get("signal_transport_queue_rows") or [])
    if not queues:
        return {"status": "fail", "message": "bulletin report should be dispatched through signal queue"}
    return {"status": "pass", "message": "institution bulletin generation deterministic"}
