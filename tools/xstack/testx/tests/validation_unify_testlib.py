"""Helpers for VALIDATION-UNIFY-0 TestX coverage."""

from __future__ import annotations

from validation import build_validation_report, validation_surface_rows
from tools.xstack.compatx.canonical_json import canonical_json_text


def build_report(repo_root: str, profile: str) -> dict:
    return build_validation_report(repo_root, profile=profile)


def canonical_report_text(repo_root: str, profile: str) -> str:
    return canonical_json_text(build_report(repo_root, profile))


def legacy_adapter_rows(repo_root: str) -> list[dict]:
    return validation_surface_rows(repo_root)
