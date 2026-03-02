"""SIG-6 deterministic institutional standards and certification engine."""

from __future__ import annotations

from typing import Dict, List, Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256

from src.signals.transport import normalize_info_artifact_rows, process_signal_send


REFUSAL_STANDARDS_SPEC_TYPE_FORBIDDEN = "refusal.standards.spec_type_forbidden"


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


def standards_policy_rows_by_id(registry_payload: Mapping[str, object] | None) -> Dict[str, dict]:
    payload = _as_map(registry_payload)
    rows = payload.get("standards_policies")
    if not isinstance(rows, list):
        rows = _as_map(payload.get("record")).get("standards_policies")
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("standards_policy_id", ""))):
        policy_id = str(row.get("standards_policy_id", "")).strip()
        if not policy_id:
            continue
        out[policy_id] = {
            "schema_version": "1.0.0",
            "standards_policy_id": policy_id,
            "allowed_spec_types": _sorted_tokens(row.get("allowed_spec_types")),
            "credential_issuance_rules": _as_map(row.get("credential_issuance_rules")),
            "compliance_reporting_rules": _as_map(row.get("compliance_reporting_rules")),
            "extensions": _as_map(row.get("extensions")),
        }
    return dict((key, dict(out[key])) for key in sorted(out.keys()))


def deterministic_spec_issue_id(
    *,
    institution_id: str,
    spec_id: str,
    spec_type_id: str,
    tick: int,
) -> str:
    digest = canonical_sha256(
        {
            "institution_id": str(institution_id or "").strip(),
            "spec_id": str(spec_id or "").strip(),
            "spec_type_id": str(spec_type_id or "").strip(),
            "tick": int(max(0, _as_int(tick, 0))),
        }
    )
    return "issue.spec.{}".format(digest[:16])


def build_spec_issue_request(
    *,
    request_id: str,
    institution_id: str,
    spec_id: str,
    spec_type_id: str,
    spec_parameters: Mapping[str, object] | None = None,
    compliance_check_ids: object = None,
    notes: str = "",
    extensions: Mapping[str, object] | None = None,
) -> dict:
    payload = {
        "schema_version": "1.0.0",
        "request_id": str(request_id or "").strip(),
        "institution_id": str(institution_id or "").strip(),
        "spec_id": str(spec_id or "").strip(),
        "spec_type_id": str(spec_type_id or "").strip(),
        "spec_parameters": _as_map(spec_parameters),
        "compliance_check_ids": _sorted_tokens(compliance_check_ids),
        "notes": str(notes or "").strip(),
        "deterministic_fingerprint": "",
        "extensions": _as_map(extensions),
    }
    if (not payload["request_id"]) or (not payload["spec_id"]) or (not payload["spec_type_id"]):
        return {}
    return _with_fingerprint(payload)


def normalize_spec_issue_request_rows(rows: object) -> List[dict]:
    if not isinstance(rows, list):
        rows = []
    out: Dict[str, dict] = {}
    for row in sorted((dict(item) for item in rows if isinstance(item, Mapping)), key=lambda item: str(item.get("request_id", ""))):
        built = build_spec_issue_request(
            request_id=str(row.get("request_id", "")).strip(),
            institution_id=str(row.get("institution_id", "")).strip(),
            spec_id=str(row.get("spec_id", "")).strip(),
            spec_type_id=str(row.get("spec_type_id", "")).strip(),
            spec_parameters=_as_map(row.get("spec_parameters")),
            compliance_check_ids=row.get("compliance_check_ids"),
            notes=str(row.get("notes", "")).strip(),
            extensions=_as_map(row.get("extensions")),
        )
        request_id = str(built.get("request_id", "")).strip()
        if request_id:
            out[request_id] = dict(built)
    return [dict(out[key]) for key in sorted(out.keys())]


def _build_issued_spec_row(
    *,
    issue_request_row: Mapping[str, object],
    institution_id: str,
    tick: int,
) -> dict:
    row = dict(issue_request_row or {})
    spec_id = str(row.get("spec_id", "")).strip()
    return {
        "schema_version": "1.0.0",
        "spec_id": spec_id,
        "spec_type_id": str(row.get("spec_type_id", "")).strip(),
        "parameters": _as_map(row.get("spec_parameters")),
        "compliance_check_ids": _sorted_tokens(row.get("compliance_check_ids")),
        "created_tick": int(max(0, _as_int(tick, 0))),
        "extensions": {
            "issued_by_institution_id": institution_id,
            "issue_request_id": str(row.get("request_id", "")).strip(),
            "issue_id": deterministic_spec_issue_id(
                institution_id=institution_id,
                spec_id=spec_id,
                spec_type_id=str(row.get("spec_type_id", "")).strip(),
                tick=tick,
            ),
            "notes": str(row.get("notes", "")).strip(),
        },
    }


def _build_credential_artifact_row(
    *,
    institution_id: str,
    spec_row: Mapping[str, object],
    tick: int,
    credential_rules: Mapping[str, object],
) -> dict:
    spec_id = str(spec_row.get("spec_id", "")).strip()
    credential_id = "artifact.credential.{}".format(
        canonical_sha256(
            {
                "institution_id": institution_id,
                "spec_id": spec_id,
                "tick": int(max(0, _as_int(tick, 0))),
                "credential_kind": str(credential_rules.get("credential_kind", "certificate")).strip() or "certificate",
            }
        )[:16]
    )
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "artifact_id": credential_id,
            "artifact_family_id": "CREDENTIAL",
            "created_tick": int(max(0, _as_int(tick, 0))),
            "source_artifact_ids": [],
            "summary": {
                "credential_kind": str(credential_rules.get("credential_kind", "certificate")).strip() or "certificate",
                "institution_id": institution_id,
                "spec_id": spec_id,
            },
            "deterministic_fingerprint": "",
            "extensions": {
                "institution_id": institution_id,
                "spec_id": spec_id,
                "requires_signing_key": bool(credential_rules.get("requires_signing_key", False)),
            },
        }
    )


def _build_spec_model_artifact_row(
    *,
    institution_id: str,
    spec_row: Mapping[str, object],
    credential_artifact_row: Mapping[str, object],
    tick: int,
) -> dict:
    spec_id = str(spec_row.get("spec_id", "")).strip()
    artifact_id = "artifact.model.spec.{}".format(
        canonical_sha256(
            {
                "institution_id": institution_id,
                "spec_id": spec_id,
                "tick": int(max(0, _as_int(tick, 0))),
                "credential_artifact_id": str(credential_artifact_row.get("artifact_id", "")).strip(),
            }
        )[:16]
    )
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "artifact_id": artifact_id,
            "artifact_family_id": "MODEL",
            "created_tick": int(max(0, _as_int(tick, 0))),
            "source_artifact_ids": [str(credential_artifact_row.get("artifact_id", "")).strip()],
            "summary": {
                "institution_id": institution_id,
                "spec_id": spec_id,
                "spec_type_id": str(spec_row.get("spec_type_id", "")).strip(),
            },
            "deterministic_fingerprint": "",
            "extensions": {
                "institution_id": institution_id,
                "spec_id": spec_id,
                "spec_type_id": str(spec_row.get("spec_type_id", "")).strip(),
                "credential_artifact_id": str(credential_artifact_row.get("artifact_id", "")).strip(),
            },
        }
    )


def _build_compliance_report_artifact_row(
    *,
    institution_id: str,
    standards_policy_id: str,
    compliance_rows: object,
    tick: int,
) -> dict:
    rows = [dict(item) for item in list(compliance_rows or []) if isinstance(item, Mapping)]
    pass_count = len([row for row in rows if str(row.get("overall_grade", "")).strip() == "pass"])
    warn_count = len([row for row in rows if str(row.get("overall_grade", "")).strip() == "warn"])
    fail_count = len([row for row in rows if str(row.get("overall_grade", "")).strip() == "fail"])
    artifact_id = "artifact.report.compliance.{}".format(
        canonical_sha256(
            {
                "institution_id": institution_id,
                "standards_policy_id": standards_policy_id,
                "tick": int(max(0, _as_int(tick, 0))),
                "result_ids": sorted(
                    set(str(row.get("result_id", "")).strip() for row in rows if str(row.get("result_id", "")).strip())
                ),
            }
        )[:16]
    )
    return _with_fingerprint(
        {
            "schema_version": "1.0.0",
            "artifact_id": artifact_id,
            "artifact_family_id": "REPORT",
            "created_tick": int(max(0, _as_int(tick, 0))),
            "source_artifact_ids": sorted(
                set(str(row.get("result_id", "")).strip() for row in rows if str(row.get("result_id", "")).strip())
            ),
            "summary": {
                "institution_id": institution_id,
                "standards_policy_id": standards_policy_id,
                "result_count": int(len(rows)),
                "grade_counts": {
                    "pass": int(pass_count),
                    "warn": int(warn_count),
                    "fail": int(fail_count),
                },
            },
            "deterministic_fingerprint": "",
            "extensions": {
                "institution_id": institution_id,
                "standards_policy_id": standards_policy_id,
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


def process_standards_issue_and_report(
    *,
    current_tick: int,
    institution_profile_row: Mapping[str, object],
    standards_policy_registry: Mapping[str, object] | None,
    spec_issue_request_rows: object,
    spec_compliance_rows: object,
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
    institution_id = str(profile_row.get("institution_id", "")).strip() or "institution.unknown"
    standards_policy_id = str(profile_row.get("standards_policy_id", "")).strip()

    policy_rows = standards_policy_rows_by_id(standards_policy_registry)
    policy_row = dict(policy_rows.get(standards_policy_id) or {})
    allowed_spec_types = set(_sorted_tokens(policy_row.get("allowed_spec_types")))
    credential_rules = _as_map(policy_row.get("credential_issuance_rules"))
    policy_ext = _as_map(policy_row.get("extensions"))

    next_artifacts = [dict(row) for row in normalize_info_artifact_rows(info_artifact_rows)]
    next_envelopes = [dict(row) for row in list(signal_message_envelope_rows or []) if isinstance(row, Mapping)]
    next_queue = [dict(row) for row in list(signal_transport_queue_rows or []) if isinstance(row, Mapping)]
    next_decisions = [dict(row) for row in list(decision_log_rows or []) if isinstance(row, Mapping)]

    issue_requests = normalize_spec_issue_request_rows(spec_issue_request_rows)
    issued_spec_rows: List[dict] = []
    credential_artifacts: List[dict] = []
    model_artifacts: List[dict] = []
    refused_requests: List[dict] = []

    for request_row in issue_requests:
        request = dict(request_row)
        if institution_id and str(request.get("institution_id", "")).strip() not in {"", institution_id}:
            continue
        spec_type_id = str(request.get("spec_type_id", "")).strip()
        if allowed_spec_types and spec_type_id not in allowed_spec_types:
            refused = {
                "request_id": str(request.get("request_id", "")).strip(),
                "reason_code": REFUSAL_STANDARDS_SPEC_TYPE_FORBIDDEN,
                "spec_type_id": spec_type_id,
            }
            refused_requests.append(refused)
            next_decisions.append(
                {
                    "decision_id": "decision.standards.refusal.{}".format(
                        canonical_sha256(refused)[:16]
                    ),
                    "tick": tick,
                    "process_id": "process.standards_issue",
                    "result": "refused",
                    "reason_code": REFUSAL_STANDARDS_SPEC_TYPE_FORBIDDEN,
                    "extensions": {
                        "institution_id": institution_id,
                        "standards_policy_id": standards_policy_id,
                        **refused,
                    },
                }
            )
            continue

        issued_spec_row = _build_issued_spec_row(
            issue_request_row=request,
            institution_id=institution_id,
            tick=tick,
        )
        credential_artifact = _build_credential_artifact_row(
            institution_id=institution_id,
            spec_row=issued_spec_row,
            tick=tick,
            credential_rules=credential_rules,
        )
        model_artifact = _build_spec_model_artifact_row(
            institution_id=institution_id,
            spec_row=issued_spec_row,
            credential_artifact_row=credential_artifact,
            tick=tick,
        )
        issued_spec_rows.append(dict(issued_spec_row))
        credential_artifacts.append(dict(credential_artifact))
        model_artifacts.append(dict(model_artifact))
        next_artifacts.append(dict(credential_artifact))
        next_artifacts.append(dict(model_artifact))
        next_decisions.append(
            {
                "decision_id": "decision.standards.issue.{}".format(
                    canonical_sha256(
                        {
                            "institution_id": institution_id,
                            "request_id": str(request.get("request_id", "")).strip(),
                            "spec_id": str(issued_spec_row.get("spec_id", "")).strip(),
                            "credential_artifact_id": str(credential_artifact.get("artifact_id", "")).strip(),
                        }
                    )[:16]
                ),
                "tick": tick,
                "process_id": "process.standards_issue",
                "result": "issued",
                "extensions": {
                    "institution_id": institution_id,
                    "standards_policy_id": standards_policy_id,
                    "request_id": str(request.get("request_id", "")).strip(),
                    "spec_id": str(issued_spec_row.get("spec_id", "")).strip(),
                    "credential_artifact_id": str(credential_artifact.get("artifact_id", "")).strip(),
                    "model_artifact_id": str(model_artifact.get("artifact_id", "")).strip(),
                },
            }
        )

    compliance_report = _build_compliance_report_artifact_row(
        institution_id=institution_id,
        standards_policy_id=standards_policy_id or "standards.policy.unknown",
        compliance_rows=spec_compliance_rows,
        tick=tick,
    )
    next_artifacts.append(dict(compliance_report))

    channel_id = str(policy_ext.get("report_channel_id", "")).strip()
    if not channel_id:
        channels = _sorted_tokens(profile_row.get("channels_available"))
        channel_id = channels[0] if channels else "channel.local_institutional"
    recipient_address = {
        "kind": "group",
        "group_id": str(policy_ext.get("report_group_id", "group.dispatch.default")).strip() or "group.dispatch.default",
        "to_node_id": str(policy_ext.get("report_from_node_id", "node.unknown")).strip() or "node.unknown",
    }
    sent = process_signal_send(
        current_tick=tick,
        channel_id=channel_id,
        from_node_id=str(policy_ext.get("report_from_node_id", "node.unknown")).strip() or "node.unknown",
        artifact_id=str(compliance_report.get("artifact_id", "")).strip(),
        sender_subject_id=_institution_sender_subject_id(
            institution_id=institution_id,
            explicit_sender_subject_id=str(policy_ext.get("report_sender_subject_id", "")).strip(),
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
            "standards_policy_id": standards_policy_id,
            "report_kind": "compliance",
        },
    )
    next_envelopes = [dict(row) for row in list(sent.get("signal_message_envelope_rows") or []) if isinstance(row, Mapping)]
    next_queue = [dict(row) for row in list(sent.get("signal_transport_queue_rows") or []) if isinstance(row, Mapping)]
    next_decisions = [dict(row) for row in list(sent.get("decision_log_rows") or []) if isinstance(row, Mapping)]

    return {
        "issued_spec_rows": sorted(
            (dict(row) for row in issued_spec_rows if isinstance(row, Mapping)),
            key=lambda row: str(row.get("spec_id", "")),
        ),
        "credential_artifacts": sorted(
            (dict(row) for row in credential_artifacts if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "model_artifacts": sorted(
            (dict(row) for row in model_artifacts if isinstance(row, Mapping)),
            key=lambda row: str(row.get("artifact_id", "")),
        ),
        "refused_issue_requests": sorted(
            (dict(row) for row in refused_requests if isinstance(row, Mapping)),
            key=lambda row: str(row.get("request_id", "")),
        ),
        "compliance_report_artifact": dict(compliance_report),
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
    "REFUSAL_STANDARDS_SPEC_TYPE_FORBIDDEN",
    "build_spec_issue_request",
    "deterministic_spec_issue_id",
    "normalize_spec_issue_request_rows",
    "process_standards_issue_and_report",
    "standards_policy_rows_by_id",
]
