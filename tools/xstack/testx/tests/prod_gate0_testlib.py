"""Helpers for PROD-GATE-0 TestX coverage."""

from __future__ import annotations

from tools.xstack.compatx.canonical_json import canonical_json_text


def load_report(repo_root: str, *, prefer_cached: bool = True) -> tuple[dict, str]:
    from tools.mvp.prod_gate0_common import load_or_run_product_boot_matrix_report

    report = load_or_run_product_boot_matrix_report(repo_root, prefer_cached=prefer_cached)
    if str(report.get("report_id", "")).strip() != "mvp.product_boot_matrix.v1":
        return report, "product boot matrix report_id mismatch"
    if str(report.get("result", "")).strip() != "complete":
        return report, "product boot matrix report is not complete"
    return report, ""


def build_report(repo_root: str) -> dict:
    from tools.mvp.prod_gate0_common import build_product_boot_matrix_report

    return build_product_boot_matrix_report(repo_root)


def canonical_report_text(report: dict) -> str:
    return canonical_json_text(report)


def command_rows(report: dict, command_id: str) -> list[dict]:
    return [
        dict(row or {})
        for row in list(report.get("command_rows") or [])
        if str(dict(row or {}).get("command_id", "")).strip() == str(command_id).strip()
    ]


def mode_row(report: dict, product_id: str, invocation_kind: str, scenario_id: str) -> dict:
    for row in list(report.get("mode_rows") or []):
        row_map = dict(row or {})
        if (
            str(row_map.get("product_id", "")).strip() == str(product_id).strip()
            and str(row_map.get("invocation_kind", "")).strip() == str(invocation_kind).strip()
            and str(row_map.get("scenario_id", "")).strip() == str(scenario_id).strip()
        ):
            return row_map
    return {}


def ipc_rows(report: dict) -> list[dict]:
    return [dict(row or {}) for row in list(report.get("ipc_rows") or [])]
