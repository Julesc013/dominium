"""Helpers for REPO-REVIEW-3 TestX coverage."""

from __future__ import annotations

from tools.review.doc_inventory_common import (
    build_doc_inventory,
    missing_stability_header_entries,
    superseded_without_replacement_entries,
)
from tools.xstack.compatx.canonical_json import canonical_json_text


def build_report(repo_root: str) -> dict:
    return build_doc_inventory(repo_root)


def canonical_report_text(repo_root: str) -> str:
    return canonical_json_text(build_report(repo_root))


def missing_stability_headers(repo_root: str) -> list[dict]:
    return missing_stability_header_entries(build_report(repo_root))


def superseded_without_replacement(repo_root: str) -> list[dict]:
    return superseded_without_replacement_entries(build_report(repo_root))
