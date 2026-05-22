"""Typed command boundary for ``dominium.validation.run``."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping


COMMAND_ID = "dominium.validation.run"
COMMAND_VERSION = "0.1.0"
INPUT_SCHEMA = "contracts/command/validation_run_input.schema.json"
VALIDATION_RESULT_SCHEMA = "contracts/schema/validation_result.schema.json"
VALIDATION_RUN_RESULT_SCHEMA = "contracts/command/validation_run_result.schema.json"
EVIDENCE_SCHEMA = "contracts/evidence/evidence_packet.schema.json"
REFUSAL_REGISTRY = "contracts/refusal/refusal_code.registry.json"
DIAGNOSTIC_REGISTRY = "contracts/diagnostic/diagnostic_code.registry.json"

SUPPORTED_PROFILES = ("FAST", "STRICT", "FULL")
SUPPORTED_SURFACES = ("cli", "headless", "workbench", "aide", "test")
SUPPORTED_TARGET_KINDS = ("validation_suite", "contract_schema")
SUPPORTED_TARGETS = ("", "all", "validate.all", "validation", "dominium.validation", COMMAND_ID)
CONTRACT_SCHEMA_SUITE_ID = "validate.contract_schema_artifact"
DEFAULT_CONTRACT_SCHEMA_TARGET = "contracts/command/validation_run_input.schema.json"
ALLOWED_CONTRACT_SCHEMA_ROOTS = ("contracts/command", "contracts/schema")

REFUSAL_INVALID_TARGET = "dominium.refusal.validation.invalid_target"
REFUSAL_TARGET_UNKNOWN = "dominium.refusal.validation.target_unknown"
REFUSAL_TARGET_KIND_UNSUPPORTED = "dominium.refusal.validation.target_kind_unsupported"
REFUSAL_TARGET_OUTSIDE_ROOT = "dominium.refusal.validation.target_outside_allowed_root"
REFUSAL_TOOL_UNAVAILABLE = "dominium.refusal.validation.tool_unavailable"
REFUSAL_INVALID_INPUT = "dominium.refusal.command.invalid_input"
REFUSAL_UNSUPPORTED_SURFACE = "dominium.refusal.command.unsupported_surface"
REFUSAL_CAPABILITY_MISSING = "dominium.refusal.command.capability_missing"

DIAG_INVALID_INPUT = "DOM-CMD-INVALID-INPUT"
DIAG_UNSUPPORTED_SURFACE = "DOM-CMD-UNSUPPORTED-SURFACE"
DIAG_CAPABILITY_MISSING = "DOM-CAPABILITY-MISSING"
DIAG_EVIDENCE_MISSING = "DOM-EVIDENCE-MISSING"
DIAG_TARGET_UNKNOWN = "DOM-VALIDATION-TARGET-UNKNOWN"
DIAG_TARGET_KIND_UNSUPPORTED = "DOM-VALIDATION-TARGET-KIND-UNSUPPORTED"
DIAG_TARGET_OUTSIDE_ROOT = "DOM-VALIDATION-TARGET-OUTSIDE-ROOT"
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


def _status_payload_value(status: str, diagnostics: list[dict[str, object]]) -> str:
    if status == "ok":
        return "pass"
    if status == "warning":
        return "pass_with_warnings"
    if status == "refused":
        return "refused"
    return "fail"


def _summary_counts(diagnostics: list[dict[str, object]]) -> dict[str, int]:
    return {
        "errors": sum(1 for item in diagnostics if item.get("severity") == "error"),
        "warnings": sum(1 for item in diagnostics if item.get("severity") == "warning"),
        "diagnostics": len(diagnostics),
    }


def _artifact_ref_from_request(request: Mapping[str, object]) -> dict[str, object] | None:
    target_path = _token(request.get("target_path"))
    artifact_ref = _token(request.get("artifact_ref"))
    if not target_path and not artifact_ref:
        return None
    return {
        "artifact_ref": artifact_ref or target_path,
        "target_kind": _token(request.get("target_kind")) or "validation_suite",
        "target_path": target_path.replace("\\", "/"),
        "suite_id": _token(request.get("suite_id")),
    }


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
    run_id = _stable_run_id({"request": dict(request), "status": status, "summary": summary})
    payload_data = dict(payload)
    payload_data.setdefault("validation_status", _status_payload_value(status, diagnostics))
    payload_data.setdefault("summary_counts", _summary_counts(diagnostics))
    artifact_ref = _artifact_ref_from_request(request)
    if artifact_ref is not None:
        payload_data.setdefault("validated_artifact_ref", artifact_ref)
    evidence_refs = _unique_strings(evidence)
    payload_data.setdefault(
        "evidence_packet",
        {
            "evidence_id": "evidence.{}".format(run_id),
            "subject_id": COMMAND_ID,
            "subject_kind": "command",
            "command_id": COMMAND_ID,
            "run_id": run_id,
            "status": status,
            "diagnostic_codes": _unique_strings([item.get("code") for item in diagnostics]),
            "proof": evidence_refs,
            "artifact_refs": [artifact_ref] if artifact_ref is not None else [],
            "summary": summary,
        },
    )
    return {
        "command_id": COMMAND_ID,
        "run_id": run_id,
        "status": status,
        "summary": summary,
        "diagnostics": diagnostics,
        "evidence": evidence_refs,
        "payload": payload_data,
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

    mode = _token(raw.get("mode")).lower()
    if not mode:
        mode = "strict" if raw.get("strict") is True or profile in {"STRICT", "FULL"} else "dry_run"
    if mode not in {"dry_run", "strict"}:
        errors.append(
            {
                "refusal_code": REFUSAL_INVALID_INPUT,
                "diagnostic_code": DIAG_INVALID_INPUT,
                "message": "mode '{}' is not one of dry_run, strict".format(mode),
                "recovery_action": "inspect_evidence",
                "recovery_summary": "Use mode dry_run or strict.",
            }
        )

    target_kind = _token(raw.get("target_kind")).lower()
    if not target_kind:
        target_kind = "contract_schema" if _token(raw.get("target_path")) else "validation_suite"
    if target_kind not in SUPPORTED_TARGET_KINDS:
        errors.append(
            {
                "refusal_code": REFUSAL_TARGET_KIND_UNSUPPORTED,
                "diagnostic_code": DIAG_TARGET_KIND_UNSUPPORTED,
                "message": "target_kind '{}' is not supported by {}".format(target_kind, COMMAND_ID),
                "recovery_action": "select_alternative",
                "recovery_summary": "Use one of: {}.".format(", ".join(SUPPORTED_TARGET_KINDS)),
            }
        )

    suite_id = _token(raw.get("suite_id"))
    if not suite_id:
        suite_id = CONTRACT_SCHEMA_SUITE_ID if target_kind == "contract_schema" else "validate.all"

    target = _token(raw.get("target")) or "all"
    if target_kind == "validation_suite" and target not in SUPPORTED_TARGETS:
        errors.append(
            {
                "refusal_code": REFUSAL_TARGET_UNKNOWN,
                "diagnostic_code": DIAG_TARGET_UNKNOWN,
                "message": "validation target '{}' is not registered for this slice".format(target),
                "recovery_action": "select_alternative",
                "recovery_summary": "Use target 'all' or '{}'; scoped targets require a later command adapter.".format(COMMAND_ID),
            }
        )
    if target_kind == "validation_suite" and suite_id != "validate.all":
        errors.append(
            {
                "refusal_code": REFUSAL_TARGET_UNKNOWN,
                "diagnostic_code": DIAG_TARGET_UNKNOWN,
                "message": "suite_id '{}' is not registered for validation_suite target".format(suite_id),
                "recovery_action": "select_alternative",
                "recovery_summary": "Use suite_id validate.all for aggregate validation.",
            }
        )
    if target_kind == "contract_schema" and suite_id != CONTRACT_SCHEMA_SUITE_ID:
        errors.append(
            {
                "refusal_code": REFUSAL_TARGET_UNKNOWN,
                "diagnostic_code": DIAG_TARGET_UNKNOWN,
                "message": "suite_id '{}' is not registered for contract_schema target".format(suite_id),
                "recovery_action": "select_alternative",
                "recovery_summary": "Use suite_id {} for the contract schema artifact proof.".format(CONTRACT_SCHEMA_SUITE_ID),
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
        "target_kind": target_kind,
        "target_path": _token(raw.get("target_path")) or (DEFAULT_CONTRACT_SCHEMA_TARGET if target_kind == "contract_schema" else ""),
        "artifact_ref": _token(raw.get("artifact_ref")),
        "suite_id": suite_id,
        "mode": mode,
        "profile": profile,
        "surface": surface,
        "emit_reports": bool(raw.get("emit_reports", False)),
        "continue_on_fail": bool(raw.get("continue_on_fail", False)),
        "capabilities": _unique_strings(raw.get("capabilities") or []),
        "required_capabilities": _unique_strings(raw.get("required_capabilities") or []),
    }
    if "json_out" in raw:
        request["json_out"] = _token(raw.get("json_out"))
    if "md_out" in raw:
        request["md_out"] = _token(raw.get("md_out"))
    return request, errors


def _relative_target_path(repo_root: str, target_path: str) -> tuple[str, str]:
    root = os.path.normpath(os.path.abspath(repo_root))
    raw_path = _token(target_path)
    if not raw_path:
        return "", ""
    target_abs = os.path.normpath(os.path.abspath(raw_path if os.path.isabs(raw_path) else os.path.join(root, raw_path)))
    try:
        inside_repo = os.path.commonpath([root, target_abs]) == root
    except ValueError:
        inside_repo = False
    if not inside_repo:
        return target_abs, ""
    return target_abs, os.path.relpath(target_abs, root).replace("\\", "/")


def _target_validation_error(request: Mapping[str, object], repo_root: str) -> dict[str, str] | None:
    missing_capabilities = sorted(set(_unique_strings(request.get("required_capabilities"))) - set(_unique_strings(request.get("capabilities"))))
    if missing_capabilities:
        return {
            "refusal_code": REFUSAL_CAPABILITY_MISSING,
            "diagnostic_code": DIAG_CAPABILITY_MISSING,
            "message": "required capability missing: {}".format(", ".join(missing_capabilities)),
            "recovery_action": "enable_pack",
            "recovery_summary": "Provide the required capability through an approved profile, pack, authority, or provider path.",
        }

    target_kind = _token(request.get("target_kind"))
    if target_kind != "contract_schema":
        return None

    target_abs, rel_path = _relative_target_path(repo_root, _token(request.get("target_path")))
    if not rel_path:
        return {
            "refusal_code": REFUSAL_TARGET_OUTSIDE_ROOT,
            "diagnostic_code": DIAG_TARGET_OUTSIDE_ROOT,
            "message": "validation target is outside the repository root: {}".format(target_abs),
            "recovery_action": "select_alternative",
            "recovery_summary": "Choose a target under {}.".format(", ".join(ALLOWED_CONTRACT_SCHEMA_ROOTS)),
        }
    if not any(rel_path == root or rel_path.startswith(root + "/") for root in ALLOWED_CONTRACT_SCHEMA_ROOTS):
        return {
            "refusal_code": REFUSAL_TARGET_OUTSIDE_ROOT,
            "diagnostic_code": DIAG_TARGET_OUTSIDE_ROOT,
            "message": "validation target '{}' is outside allowed validation roots".format(rel_path),
            "recovery_action": "select_alternative",
            "recovery_summary": "Choose a target under {}.".format(", ".join(ALLOWED_CONTRACT_SCHEMA_ROOTS)),
        }
    if not os.path.exists(target_abs):
        return {
            "refusal_code": REFUSAL_TARGET_UNKNOWN,
            "diagnostic_code": DIAG_TARGET_UNKNOWN,
            "message": "validation target '{}' does not exist".format(rel_path),
            "recovery_action": "select_alternative",
            "recovery_summary": "Choose an existing contract schema artifact.",
        }
    if not rel_path.endswith(".json"):
        return {
            "refusal_code": REFUSAL_INVALID_INPUT,
            "diagnostic_code": DIAG_INVALID_INPUT,
            "message": "contract_schema target '{}' must be a JSON artifact".format(rel_path),
            "recovery_action": "inspect_evidence",
            "recovery_summary": "Use a governed JSON schema artifact.",
        }
    return None


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
    target_error = _target_validation_error(request, root)
    if target_error:
        return _refused_result(
            request=request,
            refusal_code=target_error["refusal_code"],
            diagnostic_code=target_error["diagnostic_code"],
            message=target_error["message"],
            recovery_action=target_error["recovery_action"],
            recovery_summary=target_error["recovery_summary"],
        )

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
            VALIDATION_RUN_RESULT_SCHEMA,
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
