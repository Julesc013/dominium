"""Helpers for MVP smoke gate TestX coverage."""

from __future__ import annotations

from typing import Any


def load_scenario(repo_root: str) -> dict:
    from tools.mvp.mvp_smoke_common import DEFAULT_SCENARIO_REL, DEFAULT_MVP_SMOKE_SEED, generate_mvp_smoke_scenario, load_json_if_present

    scenario = load_json_if_present(repo_root, DEFAULT_SCENARIO_REL)
    if scenario:
        return scenario
    return generate_mvp_smoke_scenario(repo_root, seed=DEFAULT_MVP_SMOKE_SEED)


def load_expected_hashes(repo_root: str) -> dict:
    from tools.mvp.mvp_smoke_common import DEFAULT_HASHES_REL, load_json_if_present

    return load_json_if_present(repo_root, DEFAULT_HASHES_REL)


def load_complete_report(repo_root: str) -> tuple[dict, str]:
    from tools.mvp.mvp_smoke_common import DEFAULT_HASHES_REL, DEFAULT_REPORT_REL, load_json_if_present, maybe_load_cached_mvp_smoke_report

    scenario = load_scenario(repo_root)
    expected_hashes = load_expected_hashes(repo_root)
    if not expected_hashes:
        return {}, "missing '{}'".format(DEFAULT_HASHES_REL.replace("\\", "/"))
    report = maybe_load_cached_mvp_smoke_report(
        repo_root,
        scenario=scenario,
        expected_hashes=expected_hashes,
        report_path=DEFAULT_REPORT_REL,
    )
    if not report:
        report = load_json_if_present(repo_root, DEFAULT_REPORT_REL)
    if not report:
        return {}, "missing cached MVP smoke report"
    if str(report.get("result", "")).strip() != "complete":
        return report, "MVP smoke report is not complete"
    return report, ""


def load_baseline(repo_root: str) -> dict:
    from tools.mvp.mvp_smoke_common import DEFAULT_BASELINE_REL, load_json_if_present

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
