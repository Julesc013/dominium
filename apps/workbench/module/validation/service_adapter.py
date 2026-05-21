"""Service adapter boundary for validation command execution."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from collections.abc import Mapping

from apps.workbench.module.validation.command import (
    DIAG_EVIDENCE_MISSING,
    REFUSAL_TOOL_UNAVAILABLE,
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


class ValidationServiceAdapter:
    """Headless service adapter over the public unified validation suite export."""

    service_id = "service.validation"

    def __init__(self, repo_root: str | None = None):
        self.repo_root = _repo_root(repo_root)
        if self.repo_root not in sys.path:
            sys.path.insert(0, self.repo_root)

    def run_validation(self, request: Mapping[str, object]) -> dict[str, object]:
        profile = str(request.get("profile") or "FAST").strip().upper() or "FAST"
        emit_reports = bool(request.get("emit_reports", False))
        try:
            from tools.validators.suite import (
                VALIDATION_REPORT_DOC_TEMPLATE,
                VALIDATION_REPORT_JSON_TEMPLATE,
                VALIDATION_SUITE_REGISTRY_REL,
                build_validation_report,
                write_validation_outputs,
            )
        except Exception as exc:  # pragma: no cover - depends on local checkout shape
            raise ValidationCommandError(
                REFUSAL_TOOL_UNAVAILABLE,
                DIAG_EVIDENCE_MISSING,
                "validation service import failed: {}".format(exc),
            ) from exc

        report = build_validation_report(self.repo_root, profile=profile)
        written_outputs: dict[str, str] = {}
        if emit_reports:
            written_outputs = {
                key: _rel_or_norm(self.repo_root, value)
                for key, value in write_validation_outputs(self.repo_root, report).items()
                if value
            }

        extensions = dict(report.get("extensions") or {})
        evidence = [
            VALIDATION_SUITE_REGISTRY_REL,
            VALIDATION_RESULT_SCHEMA,
            VALIDATION_REPORT_JSON_TEMPLATE.format(profile=profile),
            VALIDATION_REPORT_DOC_TEMPLATE.format(profile=profile),
        ]
        evidence.extend(_rel_or_norm(self.repo_root, value) for value in extensions.values())
        evidence.extend(written_outputs.values())
        return {
            "service_id": self.service_id,
            "report": report,
            "evidence": [item for item in evidence if item],
            "written_outputs": written_outputs,
        }
