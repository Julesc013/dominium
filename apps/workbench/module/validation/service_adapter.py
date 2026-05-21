"""Service adapter boundary for validation command execution."""

from __future__ import annotations

import os
import sys
import hashlib
import json
from pathlib import Path
from collections.abc import Mapping

from apps.workbench.module.validation.command import (
    CONTRACT_SCHEMA_SUITE_ID,
    DIAG_EVIDENCE_MISSING,
    REFUSAL_TOOL_UNAVAILABLE,
    VALIDATION_RUN_RESULT_SCHEMA,
    VALIDATION_RESULT_SCHEMA,
    ValidationCommandError,
)


def _repo_root(repo_root: str | None = None) -> str:
    if repo_root:
        return os.path.normpath(os.path.abspath(repo_root))
    cursor = Path(__file__).resolve()
    for parent in cursor.parents:
        if (parent / "AGENTS.md").exists():
            return os.path.normpath(str(parent))
    return os.path.normpath(os.getcwd())


def _rel_or_norm(repo_root: str, path: object) -> str:
    token = str(path or "").strip()
    if not token:
        return ""
    normalized = os.path.normpath(os.path.abspath(token)) if os.path.isabs(token) else token.replace("\\", "/")
    root_prefix = os.path.normpath(os.path.abspath(repo_root))
    if os.path.isabs(normalized) and normalized.startswith(root_prefix):
        return os.path.relpath(normalized, root_prefix).replace("\\", "/")
    return str(normalized).replace("\\", "/")


def _canonical_fingerprint(payload: Mapping[str, object]) -> str:
    text = json.dumps(dict(payload or {}), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _finding(*, code: str, path: str, message: str, suite_id: str, severity: str = "error") -> dict[str, str]:
    return {
        "code": code,
        "path": path,
        "message": message,
        "suite_id": suite_id,
        "severity": severity,
    }


def _validation_result(
    *,
    suite_id: str,
    profile: str,
    target_path: str,
    result: str,
    message: str,
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]] | None = None,
    metrics: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload = {
        "schema_version": "1.0.0",
        "validation_id": "validation.{}.{}".format(suite_id, profile.lower()),
        "suite_id": suite_id,
        "category_id": "validate.contract_artifact",
        "profile": profile,
        "result": result,
        "message": message,
        "suite_order": 5,
        "adapter_id": "validation_contract_artifact_adapter",
        "description": "Validate one governed contract schema artifact through the Workbench validation command adapter.",
        "checked_paths": [target_path],
        "errors": errors,
        "warnings": list(warnings or []),
        "metrics": dict(metrics or {}),
        "fingerprints": {},
        "legacy_adapters": [],
        "suite_results": [],
        "deterministic_fingerprint": "",
        "extensions": {
            "target_kind": "contract_schema",
            "target_path": target_path,
        },
    }
    payload["deterministic_fingerprint"] = _canonical_fingerprint(payload)
    return payload


class ValidationServiceAdapter:
    """Headless service adapter for the bounded contract-schema validation target."""

    service_id = "service.validation"

    def __init__(self, repo_root: str | None = None):
        self.repo_root = _repo_root(repo_root)
        if self.repo_root not in sys.path:
            sys.path.insert(0, self.repo_root)

    def run_validation(self, request: Mapping[str, object]) -> dict[str, object]:
        profile = str(request.get("profile") or "FAST").strip().upper() or "FAST"
        if str(request.get("target_kind") or "") == "contract_schema":
            return self._run_contract_schema_validation(request, profile)

        raise ValidationCommandError(
            REFUSAL_TOOL_UNAVAILABLE,
            DIAG_EVIDENCE_MISSING,
            "aggregate validation suite service is not bound in the Workbench validation slice",
        )

    def _run_contract_schema_validation(self, request: Mapping[str, object], profile: str) -> dict[str, object]:
        target_path = _rel_or_norm(self.repo_root, request.get("target_path"))
        abs_path = os.path.join(self.repo_root, target_path.replace("/", os.sep))
        errors: list[dict[str, str]] = []
        metrics: dict[str, object] = {
            "artifact_count": 1,
            "mode": str(request.get("mode") or ""),
        }

        try:
            with open(abs_path, "r", encoding="utf-8-sig") as handle:
                payload = json.load(handle)
        except (OSError, ValueError) as exc:
            errors.append(
                _finding(
                    code="refusal.validation.contract_schema",
                    path=target_path,
                    message="contract schema artifact did not parse as JSON: {}".format(exc),
                    suite_id=CONTRACT_SCHEMA_SUITE_ID,
                )
            )
            payload = {}

        if not isinstance(payload, dict):
            errors.append(
                _finding(
                    code="refusal.validation.contract_schema",
                    path=target_path,
                    message="contract schema artifact root must be a JSON object",
                    suite_id=CONTRACT_SCHEMA_SUITE_ID,
                )
            )
        else:
            metrics["top_level_keys"] = len(payload)
            if not payload.get("$schema"):
                errors.append(
                    _finding(
                        code="refusal.validation.contract_schema",
                        path=target_path,
                        message="contract schema artifact is missing $schema",
                        suite_id=CONTRACT_SCHEMA_SUITE_ID,
                    )
                )
            if not payload.get("$id"):
                errors.append(
                    _finding(
                        code="refusal.validation.contract_schema",
                        path=target_path,
                        message="contract schema artifact is missing $id",
                        suite_id=CONTRACT_SCHEMA_SUITE_ID,
                    )
                )
            if payload.get("type") != "object":
                errors.append(
                    _finding(
                        code="refusal.validation.contract_schema",
                        path=target_path,
                        message="contract schema artifact must describe an object root",
                        suite_id=CONTRACT_SCHEMA_SUITE_ID,
                    )
                )
            if not isinstance(payload.get("properties"), dict):
                errors.append(
                    _finding(
                        code="refusal.validation.contract_schema",
                        path=target_path,
                        message="contract schema artifact must declare object properties",
                        suite_id=CONTRACT_SCHEMA_SUITE_ID,
                    )
                )

        report = _validation_result(
            suite_id=CONTRACT_SCHEMA_SUITE_ID,
            profile=profile,
            target_path=target_path,
            result="complete" if not errors else "refused",
            message="contract schema artifact {} ({})".format("passed" if not errors else "failed", target_path),
            errors=errors,
            metrics=metrics,
        )
        return {
            "service_id": self.service_id,
            "report": report,
            "evidence": [
                target_path,
                VALIDATION_RESULT_SCHEMA,
                VALIDATION_RUN_RESULT_SCHEMA,
            ],
            "written_outputs": {},
        }
