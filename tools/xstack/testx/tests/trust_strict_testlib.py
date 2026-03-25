"""Shared TRUST-STRICT-VERIFY-0 TestX helpers."""

from __future__ import annotations

import os

from tools.security.trust_strict_common import load_trust_strict_baseline, run_trust_strict_suite
from tools.xstack.compatx.canonical_json import canonical_json_text


def build_report(repo_root: str) -> dict:
    root = os.path.abspath(repo_root)
    return run_trust_strict_suite(root, write_outputs=False)


def committed_baseline(repo_root: str) -> dict:
    return load_trust_strict_baseline(os.path.abspath(repo_root))


def case_by_id(report: dict, case_id: str) -> dict:
    for row in list(dict(report or {}).get("cases") or []):
        item = dict(row or {})
        if str(item.get("case_id", "")).strip() == str(case_id).strip():
            return item
    return {}


def reports_match(repo_root: str) -> bool:
    left = build_report(repo_root)
    right = build_report(repo_root)
    return canonical_json_text(left) == canonical_json_text(right)


__all__ = ["build_report", "case_by_id", "committed_baseline", "reports_match"]
