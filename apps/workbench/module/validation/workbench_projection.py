"""Headless Workbench projection for validation command results."""

from __future__ import annotations

from collections.abc import Mapping

from apps.workbench.module.validation.command import COMMAND_ID, run_validation_command


MODULE_ID = "dominium.workbench.validation"
VIEW_BINDING_ID = "dominium.workbench.binding.validation_result_table"
SUMMARY_VIEW_ID = "dominium.validation.summary.v1"
SUMMARY_VIEW_BINDING_ID = "dominium.workbench.binding.validation_summary"
VALIDATION_ACTIONS = [
    "dominium.validation.open_report.v1",
    "dominium.validation.export_evidence.v1",
    "dominium.validation.rerun.v1",
]


def validation_module_descriptor() -> dict[str, object]:
    return {
        "module_id": MODULE_ID,
        "module_kind": "workbench_module",
        "version": "0.1.0",
        "stability": "provisional",
        "implementation_status": "skeletal_headless",
        "commands": [COMMAND_ID],
        "services": ["service.command", "service.validation", "service.diagnostics"],
        "views": ["view.table", "view.inspector"],
        "semantic_views": [SUMMARY_VIEW_ID],
        "view_bindings": [VIEW_BINDING_ID, SUMMARY_VIEW_BINDING_ID],
        "actions": list(VALIDATION_ACTIONS),
        "projection_fixtures": [
            "tests/contract/presentation/fixtures/valid_validation_summary_workbench_projection.json",
        ],
        "result_schema": "contracts/command/validation_run_result.schema.json",
        "validation_result_schema": "contracts/schema/validation_result.schema.json",
        "evidence_schema": "contracts/evidence/evidence_packet.schema.json",
        "default_target_kind": "contract_schema",
        "default_target_path": "contracts/command/validation_run_input.schema.json",
        "default_suite_id": "validate.contract_schema_artifact",
        "workspace_runtime_implemented": False,
    }


def project_validation_summary(command_result: Mapping[str, object]) -> dict[str, object]:
    payload = dict(command_result.get("payload") or {})
    request = dict(payload.get("request") or {})
    counts = dict(payload.get("summary_counts") or {})
    refusal = payload.get("refusal")
    target = payload.get("validated_artifact_ref")

    return {
        "schema_version": "dominium.workbench.validation_summary_projection.v1",
        "view_id": SUMMARY_VIEW_ID,
        "binding_id": SUMMARY_VIEW_BINDING_ID,
        "projection_kind": "headless",
        "shell_host": "workbench",
        "command_id": COMMAND_ID,
        "source_result_schema": "contracts/command/validation_run_result.schema.json",
        "source_status": str(command_result.get("status") or ""),
        "summary": str(command_result.get("summary") or ""),
        "sections": {
            "summary": {
                "text": str(command_result.get("summary") or ""),
            },
            "status": {
                "command_status": str(command_result.get("status") or ""),
                "validation_status": str(payload.get("validation_status") or ""),
            },
            "counts": {
                "errors": int(counts.get("errors") or 0),
                "warnings": int(counts.get("warnings") or 0),
                "diagnostics": int(counts.get("diagnostics") or 0),
            },
            "diagnostics": list(command_result.get("diagnostics") or []),
            "evidence": {
                "refs": list(command_result.get("evidence") or []),
                "packet": dict(payload.get("evidence_packet") or {}),
            },
            "target": dict(target) if isinstance(target, Mapping) else None,
            "refusal": dict(refusal) if isinstance(refusal, Mapping) else None,
        },
        "actions": [
            {
                "action_id": action_id,
                "enabled": bool(request) if action_id.endswith(".rerun.v1") else bool(command_result.get("evidence")),
                "implementation_status": "command_backed" if action_id.endswith(".rerun.v1") else "contract_only",
            }
            for action_id in VALIDATION_ACTIONS
        ],
        "private_tool_calls": False,
        "runtime_projection_engine": False,
        "workspace_runtime_implemented": False,
    }


def project_validation_run(input_payload: Mapping[str, object] | None = None, *, service: object | None = None) -> dict[str, object]:
    payload = dict(input_payload or {})
    payload["surface"] = "workbench"
    return run_validation_command(payload, invocation_surface="workbench", service=service)


def _count(values: object) -> int:
    return len(values) if isinstance(values, list) else 0


def project_result_table(command_result: Mapping[str, object]) -> dict[str, object]:
    payload = dict(command_result.get("payload") or {})
    report = dict(payload.get("validation_report") or {})
    rows: list[dict[str, object]] = []
    for suite in list(report.get("suite_results") or []):
        if not isinstance(suite, Mapping):
            continue
        rows.append(
            {
                "suite_id": str(suite.get("suite_id") or ""),
                "result": str(suite.get("result") or ""),
                "adapter_id": str(suite.get("adapter_id") or ""),
                "error_count": _count(suite.get("errors")),
                "warning_count": _count(suite.get("warnings")),
                "fingerprint": str(suite.get("deterministic_fingerprint") or ""),
            }
        )
    if not rows and report:
        rows.append(
            {
                "suite_id": str(report.get("suite_id") or ""),
                "result": str(report.get("result") or ""),
                "adapter_id": str(report.get("adapter_id") or ""),
                "error_count": _count(report.get("errors")),
                "warning_count": _count(report.get("warnings")),
                "fingerprint": str(report.get("deterministic_fingerprint") or ""),
            }
        )
    if not rows and payload.get("refusal"):
        refusal = dict(payload.get("refusal") or {})
        rows.append(
            {
                "suite_id": "refusal",
                "result": "refused",
                "adapter_id": "command_boundary",
                "error_count": _count(refusal.get("diagnostics")),
                "warning_count": 0,
                "fingerprint": "",
            }
        )

    return {
        "schema_version": "dominium.workbench.validation_table.v1",
        "binding_id": VIEW_BINDING_ID,
        "command_id": COMMAND_ID,
        "source_status": str(command_result.get("status") or ""),
        "columns": ["suite_id", "result", "adapter_id", "error_count", "warning_count", "fingerprint"],
        "rows": rows,
        "evidence": list(command_result.get("evidence") or []),
    }
