"""Headless Workbench projection for validation command results."""

from __future__ import annotations

from collections.abc import Mapping

from apps.workbench.module.validation.command import COMMAND_ID, run_validation_command


MODULE_ID = "dominium.workbench.validation"
VIEW_BINDING_ID = "dominium.workbench.binding.validation_result_table"


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
        "view_bindings": [VIEW_BINDING_ID],
        "result_schema": "contracts/result/result.schema.json",
        "validation_result_schema": "contracts/schema/validation_result.schema.json",
        "evidence_schema": "contracts/evidence/evidence_packet.schema.json",
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
