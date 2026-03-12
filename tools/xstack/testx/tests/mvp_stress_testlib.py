"""Helpers for MVP stress gate TestX coverage."""

from __future__ import annotations

from typing import Any


def _report_result(report: dict) -> str:
    explicit = str(report.get("result", "")).strip()
    if explicit:
        return explicit
    assertions = dict(report.get("assertions") or {})
    if all(bool(assertions.get(key, False)) for key in ("all_suites_passed", "cross_thread_hash_match", "no_unexpected_refusals", "suite_order_deterministic")):
        return "complete"
    return "violation"


def load_report(repo_root: str) -> tuple[dict, str]:
    from tools.mvp.stress_gate_common import DEFAULT_REPORT_REL, load_json_if_present, maybe_load_cached_mvp_stress_report

    report = maybe_load_cached_mvp_stress_report(repo_root, report_path=DEFAULT_REPORT_REL)
    if not report:
        report = load_json_if_present(repo_root, DEFAULT_REPORT_REL)
    if not report:
        return {}, "missing cached MVP stress report"
    if _report_result(report) != "complete":
        return report, "MVP stress report is not complete"
    return report, ""


def load_proof_report(repo_root: str, report: dict | None = None) -> tuple[dict, str]:
    from tools.mvp.stress_gate_common import DEFAULT_PROOF_REPORT_REL, load_json_if_present, maybe_load_cached_mvp_stress_proof_report

    active_report = dict(report or {})
    if not active_report:
        active_report, error = load_report(repo_root)
        if error:
            return {}, error
    proof_report = maybe_load_cached_mvp_stress_proof_report(repo_root, report=active_report, proof_report_path=DEFAULT_PROOF_REPORT_REL)
    if not proof_report:
        proof_report = load_json_if_present(repo_root, DEFAULT_PROOF_REPORT_REL)
    if not proof_report:
        return {}, "missing cached MVP stress proof report"
    if str(proof_report.get("result", "")).strip() != "complete":
        return proof_report, "MVP stress proof report is not complete"
    return proof_report, ""


def load_baseline(repo_root: str) -> dict:
    from tools.mvp.stress_gate_common import DEFAULT_BASELINE_REL, load_json_if_present

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
