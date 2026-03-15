"""Shared DIST-6 version interop TestX helpers."""

from __future__ import annotations

from tools.dist.dist6_interop_common import (
    DIST6_CASE_IDS,
    build_version_interop_reports,
    version_interop_violations,
)


_CACHE: dict[str, dict] = {}


def load_reports(repo_root: str) -> dict[str, dict]:
    global _CACHE
    if _CACHE:
        return dict(_CACHE)
    report_map: dict[str, dict] = {}
    missing = False
    for case_id in DIST6_CASE_IDS:
        from tools.dist.dist6_interop_common import _load_case_report  # lazy import to avoid test bootstrap cost

        payload = _load_case_report(repo_root, case_id)
        if not payload:
            missing = True
            break
        report_map[case_id] = dict(payload)
    if missing:
        generated = build_version_interop_reports(repo_root)
        report_map = {
            str(row.get("case_id", "")).strip(): dict(row)
            for row in list(generated or [])
            if str(dict(row or {}).get("case_id", "")).strip()
        }
    _CACHE = dict(report_map)
    return dict(_CACHE)


def load_case(repo_root: str, case_id: str) -> dict:
    return dict(load_reports(repo_root).get(str(case_id).strip()) or {})


def current_violations(repo_root: str) -> list[dict]:
    return version_interop_violations(repo_root)


__all__ = [
    "current_violations",
    "load_case",
    "load_reports",
]
