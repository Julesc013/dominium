"""FAST test: SIG-2 aggregation output is deterministic."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.aggregation_deterministic"
TEST_TAGS = ["fast", "signals", "aggregation", "determinism"]


def _run_once() -> dict:
    from src.signals import build_signal_channel, process_signal_aggregation_tick

    channel_rows = [
        build_signal_channel(
            channel_id="channel.local_institutional",
            channel_type_id="channel.local_institutional",
            network_graph_id="graph.sig.agg.001",
            capacity_per_tick=8,
            base_delay_ticks=0,
            loss_policy_id="loss.none",
            encryption_policy_id="enc.none",
        )
    ]
    policy_registry = {
        "record": {
            "aggregation_policies": [
                {
                    "schema_version": "1.0.0",
                    "aggregation_policy_id": "agg.daily_summary",
                    "input_family_ids": ["INFO.OBSERVATION", "INFO.RECORD"],
                    "output_family_id": "REPORT",
                    "schedule_id": "schedule.signal.agg.daily_summary",
                    "summarization_rules": {
                        "method": "count_by_family",
                        "window_ticks": 100,
                        "max_source_refs": 32,
                    },
                    "extensions": {
                        "dispatch_channel_id": "channel.local_institutional",
                        "dispatch_address_type": "group",
                        "dispatch_target_id": "group.dispatch.default",
                    },
                }
            ]
        }
    }
    info_artifacts = [
        {"artifact_id": "artifact.obs.001", "artifact_family_id": "INFO.OBSERVATION", "created_tick": 95},
        {"artifact_id": "artifact.rec.001", "artifact_family_id": "INFO.RECORD", "created_tick": 96},
    ]
    out = process_signal_aggregation_tick(
        current_tick=100,
        aggregation_policy_registry=policy_registry,
        schedule_rows=[{"schedule_id": "schedule.signal.agg.daily_summary", "next_due_tick": 100, "interval_ticks": 1440}],
        info_artifact_rows=info_artifacts,
        signal_channel_rows=channel_rows,
        signal_message_envelope_rows=[],
        signal_transport_queue_rows=[],
        group_membership_rows=[{"group_id": "group.dispatch.default", "subject_ids": ["subject.b", "subject.a"]}],
    )
    return {
        "created_reports": list(out.get("created_report_artifacts") or []),
        "dispatched_envelopes": list(out.get("dispatched_envelopes") or []),
        "queue_rows": list(out.get("signal_transport_queue_rows") or []),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "aggregation output drifted across identical runs"}
    if not list(first.get("created_reports") or []):
        return {"status": "fail", "message": "expected aggregation to create report artifact"}
    if not list(first.get("queue_rows") or []):
        return {"status": "fail", "message": "expected aggregated report to dispatch through signal queue"}
    return {"status": "pass", "message": "aggregation deterministic"}
