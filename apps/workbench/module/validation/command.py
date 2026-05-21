"""Typed command boundary for ``dominium.validation.run``."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping


COMMAND_ID = "dominium.validation.run"
COMMAND_VERSION = "0.1.0"
INPUT_SCHEMA = "contracts/command/validation_run_input.schema.json"
RESULT_SCHEMA = "contracts/result/result.schema.json"
VALIDATION_RESULT_SCHEMA = "contracts/schema/validation_result.schema.json"
EVIDENCE_SCHEMA = "contracts/evidence/evidence_packet.schema.json"
REFUSAL_REGISTRY = "contracts/refusal/refusal_code.registry.json"
DIAGNOSTIC_REGISTRY = "contracts/diagnostics/diagnostic_code.registry.json"

SUPPORTED_PROFILES = ("FAST", "STRICT", "FULL")
SUPPORTED_SURFACES = ("cli", "headless", "workbench", "aide", "test")
SUPPORTED_TARGETS = ("", "all", "validate.all", "validation", "dominium.validation", COMMAND_ID)

REFUSAL_INVALID_TARGET = "dominium.refusal.validation.invalid_target"
REFUSAL_TOOL_UNAVAILABLE = "dominium.refusal.validation.tool_unavailable"
REFUSAL_INVALID_INPUT = "dominium.refusal.command.invalid_input"
REFUSAL_UNSUPPORTED_SURFACE = "dominium.refusal.command.unsupported_surface"

DIAG_INVALID_INPUT = "DOM-CMD-INVALID-INPUT"
DIAG_UNSUPPORTED_SURFACE = "DOM-CMD-UNSUPPORTED-SURFACE"
DIAG_EVIDENCE_MISSING = "DOM-EVIDENCE-MISSING"
DIAG_VALIDATION_REFUSED = "DOM-VALIDATION-RUN-REFUSED"
DIAG_VALIDATION_WARNING = "DOM-VALIDATION-RUN-WARNING"


class ValidationCommandError(Exception):
    """Raised for service-boundary failures that must become typed refusals."""

    def __init__(self, refusal_code: str, diagnostic_code: str, message: str):
        super().__init__(message)
        self.refusal_code = refusal_code
        self.diagnostic_code = diagnostic_code
        self.message = message


def _repo_root(repo_root: str | None = None) -> str:
    return os.path.normpath(os.path.abspath(repo_root or os.getcwd()))


def _token(value: object) -> str:
    return str(value or "").strip()


def _unique_strings(values: object) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    if not isinstance(values, list):
        values = [values]
    for value in values:
        token = _token(value).replace("\\", "/")
        if token and token not in seen:
            seen.add(token)
            result.append(token)
    return result


def _stable_run_id(seed: Mapping[str, object]) -> str:
    text = json.dumps(dict(seed), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "{}.{}".format(COMMAND_ID, hashlib.sha256(text.encode("utf-8")).hexdigest()[:16])


def _diagnostic(
    *,
    code: str,
    message: str,
    severity: str,
    refusal_code: str = "",
    path: str = "",
    suite_id: str = "",
    source_code: str = "",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "code": code,
        "message": message,
        "severity": severity,
        "command_id": COMMAND_ID,
    }
    if refusal_code:
        payload["refusal_code"] = refusal_code
    if path:
        payload["path"] = path.replace("\\", "/")
    if suite_id:
        payload["suite_id"] = suite_id
    if source_code:
        payload["source_code"] = source_code
    return payload


def _refusal_payload(
    *,
    refusal_code: str,
    reason: str,
    diagnostic: Mapping[str, object],
    recovery_action: str,
    recovery_summary: str,
) -> dict[str, object]:
    return {
        "refusal_id": refusal_code,
        "code": refusal_code,
        "reason": reason,
        "recovery": {
            "action": recovery_action,
            "summary": recovery_summary,
        },
        "diagnostics": [dict(diagnostic)],
        "evidence_reference": EVIDENCE_SCHEMA,
    }


def _result(
    *,
    request: Mapping[str, object],
    status: str,
    summary: str,
    diagnostics: list[dict[str, object]],
    evidence: list[str],
    payload: Mapping[str, object],
) -> dict[str, object]:
    return {
        "command_id": COMMAND_ID,
        "run_id": _stable_run_id({"request": dict(request), "status": status, "summary": summary}),
        "status": status,
        "summary": summary,
        "diagnostics": diagnostics,
        "evidence": _unique_strings(evidence),
        "payload": dict(payload),
    }


def _refused_result(
    *,
    request: Mapping[str, object],
    refusal_code: str,
    diagnostic_code: str,
    message: str,
    recovery_action: str,
    recovery_summary: str,
    evidence: list[str] | None = None,
) -> dict[str, object]:
    diagnostic = _diagnostic(
        code=diagnostic_code,
        message=message,
        severity="error",
        refusal_code=refusal_code,
    )
    refusal = _refusal_payload(
        refusal_code=refusal_code,
        reason=message,
        diagnostic=diagnostic,
        recovery_action=recovery_action,
        recovery_summary=recovery_summary,
    )
    return _result(
        request=request,
        status="refused",
        summary="Validation command refused: {}".format(message),
        diagnostics=[diagnostic],
        evidence=_unique_strings(evidence or [INPUT_SCHEMA, REFUSAL_REGISTRY, DIAGNOSTIC_REGISTRY]),
        payload={
            "schema_version": "dominium.workbench.validation_slice.result.v1",
            "command_version": COMMAND_VERSION,
            "request": dict(request),
            "refusal": refusal,
            "validation_report": None,
        },
    )


def _normalize_request(input_payload: Mapping[str, object] | None, invocation_surface: str) -> tuple[dict[str, object], list[dict[str, str]]]:
    raw = dict(input_payload or {})
    errors: list[dict[str, str]] = []

    surface = _token(raw.get("surface")).lower() or _token(invocation_surface).lower() or "headless"
    if surface not in SUPPORTED_SURFACES:
        errors.append(
            {
                "refusal_code": REFUSAL_UNSUPPORTED_SURFACE,
                "diagnostic_code": DIAG_UNSUPPORTED_SURFACE,
                "message": "surface '{}' is not declared for {}".format(surface, COMMAND_ID),
                "recovery_action": "select_alternative",
                "recovery_summary": "Use one of: {}.".format(", ".join(SUPPORTED_SURFACES)),
            }
        )

    if "strict" in raw and not isinstance(raw.get("strict"), bool):
        errors.append(
            {
                "refusal_code": REFUSAL_INVALID_INPUT,
                "diagnostic_code": DIAG_INVALID_INPUT,
                "message": "strict must be a boolean when provided",
                "recovery_action": "inspect_evidence",
                "recovery_summary": "Validate input against {} and rerun.".format(INPUT_SCHEMA),
            }
        )

    profile = _token(raw.get("profile")).upper()
    if not profile:
        profile = "STRICT" if raw.get("strict") is True else "FAST"
    if profile not in SUPPORTED_PROFILES:
        errors.append(
            {
                "refusal_code": REFUSAL_INVALID_INPUT,
                "diagnostic_code": DIAG_INVALID_INPUT,
                "message": "profile '{}' is not one of {}".format(profile, ", ".join(SUPPORTED_PROFILES)),
                "recovery_action": "inspect_evidence",
                "recovery_summary": "Use FAST, STRICT, or FULL.",
            }
        )

    target = _token(raw.get("target")) or "all"
    if target not in SUPPORTED_TARGETS:
        errors.append(
            {
                "refusal_code": REFUSAL_INVALID_TARGET,
                "diagnostic_code": DIAG_INVALID_INPUT,
                "message": "validation target '{}' is not supported by this skeletal slice".format(target),
                "recovery_action": "select_alternative",
                "recovery_summary": "Use target 'all' or '{}'; scoped targets require a later command adapter.".format(COMMAND_ID),
            }
        )

    for key in ("emit_reports", "continue_on_fail"):
        if key in raw and not isinstance(raw.get(key), bool):
            errors.append(
                {
                    "refusal_code": REFUSAL_INVALID_INPUT,
                    "diagnostic_code": DIAG_INVALID_INPUT,
                    "message": "{} must be a boolean when provided".format(key),
                    "recovery_action": "inspect_evidence",
                    "recovery_summary": "Validate input against {} and rerun.".format(INPUT_SCHEMA),
                }
            )

    request = {
        "target": target,
        "profile": profile,
        "surface": surface,
        "emit_reports": bool(raw.get("emit_reports", False)),
        "continue_on_fail": bool(raw.get("continue_on_fail", False)),
    }
    if "json_out" in raw:
        request["json_out"] = _token(raw.get("json_out"))
    if "md_out" in raw:
        request["md_out"] = _token(raw.get("md_out"))
    return request, errors


def _diagnostics_from_validation_report(report: Mapping[str, object]) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    for item in list(report.get("errors") or []):
        if not isinstance(item, Mapping):
            continue
        diagnostics.append(
            _diagnostic(
                code=DIAG_VALIDATION_REFUSED,
                message=_token(item.get("message")) or "validation suite refused",
                severity="error",
                path=_token(item.get("path")),
                suite_id=_token(item.get("suite_id")),
                source_code=_token(item.get("code")),
            )
        )
    for item in list(report.get("warnings") or []):
        if not isinstance(item, Mapping):
            continue
        diagnostics.append(
            _diagnostic(
                code=DIAG_VALIDATION_WARNING,
                message=_token(item.get("message")) or "validation suite warning",
                severity="warning",
                path=_token(item.get("path")),
                suite_id=_token(item.get("suite_id")),
                source_code=_token(item.get("code")),
            )
        )
    return diagnostics


def _status_from_report(report: Mapping[str, object], diagnostics: list[dict[str, object]]) -> str:
    result = _token(report.get("result"))
    if result == "complete":
        return "warning" if any(item.get("severity") == "warning" for item in diagnostics) else "ok"
    if result == "skipped":
        return "warning"
    return "refused"


def run_validation_command(
    input_payload: Mapping[str, object] | None = None,
    *,
    repo_root: str | None = None,
    invocation_surface: str = "headless",
    service: object | None = None,
) -> dict[str, object]:
    """Run the validation command through a service adapter and return a command result."""

    request, errors = _normalize_request(input_payload, invocation_surface)
    if errors:
        first = errors[0]
        return _refused_result(
            request=request,
            refusal_code=first["refusal_code"],
            diagnostic_code=first["diagnostic_code"],
            message=first["message"],
            recovery_action=first["recovery_action"],
            recovery_summary=first["recovery_summary"],
        )

    root = _repo_root(repo_root)
    if service is None:
        from apps.workbench.module.validation.service_adapter import ValidationServiceAdapter

        service = ValidationServiceAdapter(root)

    try:
        service_result = service.run_validation(request)
    except ValidationCommandError as exc:
        return _refused_result(
            request=request,
            refusal_code=exc.refusal_code,
            diagnostic_code=exc.diagnostic_code,
            message=exc.message,
            recovery_action="inspect_evidence",
            recovery_summary="Inspect the service adapter evidence and rerun after the validation service is available.",
            evidence=[INPUT_SCHEMA, REFUSAL_REGISTRY, DIAGNOSTIC_REGISTRY],
        )
    except Exception as exc:  # pragma: no cover - defensive boundary
        return _refused_result(
            request=request,
            refusal_code=REFUSAL_TOOL_UNAVAILABLE,
            diagnostic_code=DIAG_EVIDENCE_MISSING,
            message="validation service adapter failed: {}".format(exc),
            recovery_action="inspect_evidence",
            recovery_summary="Inspect the service adapter failure and rerun after the validation service is available.",
            evidence=[INPUT_SCHEMA, REFUSAL_REGISTRY, DIAGNOSTIC_REGISTRY],
        )

    report = dict(service_result.get("report") or {})
    diagnostics = _diagnostics_from_validation_report(report)
    status = _status_from_report(report, diagnostics)
    evidence = _unique_strings(
        [
            INPUT_SCHEMA,
            RESULT_SCHEMA,
            VALIDATION_RESULT_SCHEMA,
            EVIDENCE_SCHEMA,
            DIAGNOSTIC_REGISTRY,
        ]
        + list(service_result.get("evidence") or [])
    )
    refusal = None
    if status == "refused":
        diagnostic = diagnostics[0] if diagnostics else _diagnostic(
            code=DIAG_VALIDATION_REFUSED,
            message=_token(report.get("message")) or "validation run refused",
            severity="error",
        )
        refusal = _refusal_payload(
            refusal_code=REFUSAL_INVALID_TARGET if _token(report.get("result")) == "skipped" else REFUSAL_TOOL_UNAVAILABLE,
            reason=_token(report.get("message")) or "validation run refused",
            diagnostic=diagnostic,
            recovery_action="inspect_evidence",
            recovery_summary="Inspect validation report diagnostics and rerun after remediation.",
        )

    return _result(
        request=request,
        status=status,
        summary=_token(report.get("message")) or "validation pipeline result",
        diagnostics=diagnostics,
        evidence=evidence,
        payload={
            "schema_version": "dominium.workbench.validation_slice.result.v1",
            "command_version": COMMAND_VERSION,
            "request": request,
            "refusal": refusal,
            "validation_report": report,
            "written_outputs": dict(service_result.get("written_outputs") or {}),
        },
    )
