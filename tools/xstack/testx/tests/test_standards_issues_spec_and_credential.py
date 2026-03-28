"""FAST test: SIG-6 standards workflow issues spec-linked credentials."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.institutions.standards_issues_spec_and_credential"
TEST_TAGS = ["fast", "signals", "institutions", "standards", "credential"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from signals import (
        build_signal_channel,
        build_spec_issue_request,
        process_standards_issue_and_report,
    )

    institution_profile = {
        "schema_version": "1.0.0",
        "institution_id": "institution.standards.metro",
        "bulletin_policy_id": "bulletin.daily_local",
        "dispatch_policy_id": "dispatch.rail_basic",
        "standards_policy_id": "standards.basic_body",
        "channels_available": ["channel.local_institutional"],
        "extensions": {},
    }
    standards_registry = {
        "record": {
            "standards_policies": [
                {
                    "schema_version": "1.0.0",
                    "standards_policy_id": "standards.basic_body",
                    "allowed_spec_types": ["spec.track"],
                    "credential_issuance_rules": {"credential_kind": "certificate"},
                    "compliance_reporting_rules": {},
                    "extensions": {
                        "report_channel_id": "channel.local_institutional",
                        "report_from_node_id": "node.standards.a",
                    },
                }
            ]
        }
    }
    requests = [
        build_spec_issue_request(
            request_id="request.spec.001",
            institution_id="institution.standards.metro",
            spec_id="spec.track.standard.001",
            spec_type_id="spec.track",
            spec_parameters={"gauge_mm": 1435},
            compliance_check_ids=["check.track.gauge"],
            notes="baseline metro rail gauge",
            extensions={},
        )
    ]
    out = process_standards_issue_and_report(
        current_tick=700,
        institution_profile_row=institution_profile,
        standards_policy_registry=standards_registry,
        spec_issue_request_rows=requests,
        spec_compliance_rows=[{"result_id": "compliance.001", "overall_grade": "pass"}],
        signal_channel_rows=[
            build_signal_channel(
                channel_id="channel.local_institutional",
                channel_type_id="channel.local_institutional",
                network_graph_id="graph.sig.standards.001",
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
    issued_specs = list(out.get("issued_spec_rows") or [])
    if len(issued_specs) != 1:
        return {"status": "fail", "message": "expected one issued spec row"}
    credentials = list(out.get("credential_artifacts") or [])
    if not credentials:
        return {"status": "fail", "message": "expected credential artifact"}
    if str(dict(credentials[0]).get("artifact_family_id", "")).strip() != "CREDENTIAL":
        return {"status": "fail", "message": "credential artifact family mismatch"}
    models = list(out.get("model_artifacts") or [])
    if not models or str(dict(models[0]).get("artifact_family_id", "")).strip() != "MODEL":
        return {"status": "fail", "message": "expected model artifact linked to issued spec"}
    compliance_report = dict(out.get("compliance_report_artifact") or {})
    if str(compliance_report.get("artifact_family_id", "")).strip() != "REPORT":
        return {"status": "fail", "message": "expected compliance REPORT artifact"}
    if not dict(out.get("dispatched_envelope") or {}):
        return {"status": "fail", "message": "compliance report should be sent through signal pipeline"}
    return {"status": "pass", "message": "standards issues spec and credential artifacts deterministically"}

