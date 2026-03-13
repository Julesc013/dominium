"""Deterministic adapters from legacy validation entrypoints to validate --all."""

from __future__ import annotations

import json
import os
import shutil
from typing import Mapping

from src.validation import (
    VALIDATION_REPORT_DOC_TEMPLATE,
    VALIDATION_REPORT_JSON_TEMPLATE,
    build_validation_report,
    write_validation_outputs,
)

from .common import SHIM_SUNSET_TARGET, build_shim_stability, emit_deprecation_warning, stable_rows


VALIDATION_WARNING_KEY = "warn.deprecated_validator_usage"
VALIDATION_SHIM_ROWS = stable_rows(
    (
        {
            "shim_id": "shim.validation.validate_all_py",
            "legacy_surface": "tools/ci/validate_all.py",
            "replacement_surface": "validate --all --profile FAST|STRICT|FULL",
            "message_key": VALIDATION_WARNING_KEY,
            "stability": build_shim_stability(
                rationale="Legacy aggregate validation entrypoint remains callable while validation surfaces converge.",
                replacement_target="Remove tools/ci/validate_all.py after VALIDATION-UNIFY convergence and v0.0.1 cleanup.",
            ),
            "sunset_target": SHIM_SUNSET_TARGET,
        },
    )
)


def _token(value: object) -> str:
    return str(value or "").strip()


def validation_shim_rows() -> list[dict]:
    return [dict(row) for row in VALIDATION_SHIM_ROWS]


def _write_json(path: str, payload: Mapping[str, object]) -> str:
    target = os.path.normpath(os.path.abspath(_token(path)))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(dict(payload or {}), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return target


def run_legacy_validate_all(
    *,
    repo_root: str,
    strict: bool = False,
    profile: str = "",
    json_out: str = "",
    text_out: str = "",
    ignored_exe_path: str = "",
) -> dict:
    profile_token = _token(profile).upper() or ("STRICT" if bool(strict) else "FAST")
    emit_deprecation_warning(
        category="validation",
        severity="warn",
        shim_id="shim.validation.validate_all_py",
        warning_code="deprecated_validator_usage",
        message_key=VALIDATION_WARNING_KEY,
        original_surface="tools/ci/validate_all.py",
        replacement_surface="validate --all --profile {}".format(profile_token),
        details={"ignored_exe_path": _token(ignored_exe_path)},
    )
    report = build_validation_report(repo_root, profile=profile_token)
    written = write_validation_outputs(repo_root, report)
    if _token(json_out):
        written["legacy_json_out"] = _write_json(json_out, report)
    if _token(text_out):
        source = os.path.join(repo_root, VALIDATION_REPORT_DOC_TEMPLATE.format(profile=profile_token).replace("/", os.sep))
        target = os.path.normpath(os.path.abspath(_token(text_out)))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(source, target)
        written["legacy_text_out"] = target.replace("\\", "/")
    report = dict(report)
    extensions = dict(report.get("extensions") or {})
    extensions["legacy_shim"] = {
        "legacy_surface": "tools/ci/validate_all.py",
        "replacement_surface": "validate --all --profile {}".format(profile_token),
        "written_outputs": {key: str(value).replace("\\", "/") for key, value in sorted(written.items(), key=lambda item: str(item[0]))},
        "canonical_report_json_path": VALIDATION_REPORT_JSON_TEMPLATE.format(profile=profile_token),
    }
    report["extensions"] = extensions
    return report


__all__ = [
    "VALIDATION_SHIM_ROWS",
    "VALIDATION_WARNING_KEY",
    "run_legacy_validate_all",
    "validation_shim_rows",
]
