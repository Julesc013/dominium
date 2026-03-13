"""Shared DIST-5 UX polish TestX helpers."""

from __future__ import annotations


from tools.dist.ux_smoke_common import build_ux_smoke_report, load_ux_smoke_report


def load_report(repo_root: str) -> dict:
    report = load_ux_smoke_report(repo_root)
    if report:
        return report
    return build_ux_smoke_report(repo_root)


def help_rows(report: dict) -> list[dict]:
    return sorted(
        [dict(row or {}) for row in list(dict(report or {}).get("help_rows") or [])],
        key=lambda row: (str(row.get("product_id", "")).strip(), str(row.get("bin_name", "")).strip()),
    )


def refusal_rows(report: dict) -> list[dict]:
    return sorted(
        [dict(row or {}) for row in list(dict(report or {}).get("refusal_rows") or [])],
        key=lambda row: str(row.get("surface_id", "")).strip(),
    )


def status_rows(report: dict) -> list[dict]:
    return sorted(
        [dict(row or {}) for row in list(dict(report or {}).get("status_rows") or [])],
        key=lambda row: str(row.get("surface_id", "")).strip(),
    )


__all__ = [
    "help_rows",
    "load_report",
    "refusal_rows",
    "status_rows",
]
