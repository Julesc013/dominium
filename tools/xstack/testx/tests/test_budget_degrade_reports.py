"""FAST test: institutional bulletin budget degradation is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.institutions.budget_degrade_reports"
TEST_TAGS = ["fast", "signals", "institutions", "budget", "determinism"]


def _profile_rows():
    from src.signals import build_institution_profile

    return [
        build_institution_profile(
            institution_id="institution.alpha",
            bulletin_policy_id="bulletin.daily_local",
            dispatch_policy_id="dispatch.rail_basic",
            standards_policy_id="standards.basic_body",
            channels_available=["channel.local_institutional"],
            extensions={},
        ),
        build_institution_profile(
            institution_id="institution.beta",
            bulletin_policy_id="bulletin.daily_local",
            dispatch_policy_id="dispatch.rail_basic",
            standards_policy_id="standards.basic_body",
            channels_available=["channel.local_institutional"],
            extensions={},
        ),
        build_institution_profile(
            institution_id="institution.gamma",
            bulletin_policy_id="bulletin.daily_local",
            dispatch_policy_id="dispatch.rail_basic",
            standards_policy_id="standards.basic_body",
            channels_available=["channel.local_institutional"],
            extensions={},
        ),
    ]


def _run_once() -> dict:
    from src.signals import build_signal_channel, process_institution_bulletin_tick

    out = process_institution_bulletin_tick(
        current_tick=1200,
        institution_profile_rows=_profile_rows(),
        bulletin_policy_registry={
            "record": {
                "bulletin_policies": [
                    {
                        "schema_version": "1.0.0",
                        "bulletin_policy_id": "bulletin.daily_local",
                        "schedule_id": "schedule.bulletin.daily",
                        "aggregation_policy_id": "agg.daily_summary",
                        "audience_address": {
                            "address_type": "group",
                            "target_id": "group.dispatch.default",
                            "to_node_id": "node.inst.a",
                        },
                        "severity_rules": {},
                        "extensions": {
                            "dispatch_channel_id": "channel.local_institutional",
                            "dispatch_from_node_id": "node.inst.a",
                        },
                    }
                ]
            }
        },
        schedule_rows=[
            {
                "schema_version": "1.0.0",
                "schedule_id": "schedule.bulletin.daily",
                "next_due_tick": 1200,
                "interval_ticks": 200,
                "extensions": {},
            }
        ],
        info_artifact_rows=[],
        signal_channel_rows=[
            build_signal_channel(
                channel_id="channel.local_institutional",
                channel_type_id="channel.local_institutional",
                network_graph_id="graph.sig.budget.001",
                capacity_per_tick=8,
                base_delay_ticks=0,
                loss_policy_id="loss.none",
                encryption_policy_id="enc.none",
            )
        ],
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
        max_cost_units=1,
        cost_units_per_institution=1,
    )
    return {
        "budget_outcome": str(out.get("budget_outcome", "")),
        "processed_institution_ids": list(out.get("processed_institution_ids") or []),
        "deferred_institution_ids": list(out.get("deferred_institution_ids") or []),
        "created_report_artifacts": list(out.get("created_report_artifacts") or []),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "report budget degradation drifted across identical runs"}
    if str(first.get("budget_outcome", "")) != "degraded":
        return {"status": "fail", "message": "expected degraded budget outcome"}
    processed = list(first.get("processed_institution_ids") or [])
    deferred = list(first.get("deferred_institution_ids") or [])
    if processed != ["institution.alpha"]:
        return {"status": "fail", "message": "processed institution ordering should be deterministic lexicographic"}
    if deferred != ["institution.beta", "institution.gamma"]:
        return {"status": "fail", "message": "deferred institution ordering should be deterministic lexicographic"}
    reports = list(first.get("created_report_artifacts") or [])
    if len(reports) != 1:
        return {"status": "fail", "message": "expected one created report under constrained budget"}
    report_ext = dict(dict(reports[0]).get("extensions") or {})
    if not bool(report_ext.get("coarse_summary", False)):
        return {"status": "fail", "message": "degraded budget should emit coarse summary report"}
    return {"status": "pass", "message": "institutional report budget degradation deterministic"}

