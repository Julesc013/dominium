"""Helpers for MVP cross-platform gate TestX coverage."""

from __future__ import annotations

from typing import Any


def load_report(repo_root: str) -> tuple[dict, str]:
    from tools.mvp.cross_platform_gate_common import DEFAULT_REPORT_REL, load_json_if_present, maybe_load_cached_mvp_cross_platform_report

    report = maybe_load_cached_mvp_cross_platform_report(repo_root, report_path=DEFAULT_REPORT_REL)
    if not report:
        report = load_json_if_present(repo_root, DEFAULT_REPORT_REL)
    if not report:
        return {}, "missing cached MVP cross-platform report"
    if str(report.get("result", "")).strip() != "complete":
        return report, "MVP cross-platform report is not complete"
    return report, ""


def load_baseline(repo_root: str) -> dict:
    from tools.mvp.cross_platform_gate_common import DEFAULT_BASELINE_REL, load_json_if_present

    return load_json_if_present(repo_root, DEFAULT_BASELINE_REL)


def first_mismatch(expected: Any, actual: Any, path: str = "$") -> str:
    if isinstance(expected, dict) and isinstance(actual, dict):
        keys = sorted(set(expected.keys()) | set(actual.keys()))
        for key in keys:
            mismatch = first_mismatch(expected.get(key), actual.get(key), "{}.{}".format(path, key))
            if mismatch:
                return mismatch
        return ""
    if isinstance(expected, list) and isinstance(actual, list):
        for index in range(max(len(expected), len(actual))):
            exp_item = expected[index] if index < len(expected) else None
            act_item = actual[index] if index < len(actual) else None
            mismatch = first_mismatch(exp_item, act_item, "{}[{}]".format(path, index))
            if mismatch:
                return mismatch
        return ""
    if expected == actual:
        return ""
    return "{} expected={} actual={}".format(path, repr(expected), repr(actual))
