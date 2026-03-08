"""Shared deterministic GEO-10 fixtures for TestX."""

from __future__ import annotations

import copy
import sys
from functools import lru_cache
from typing import Mapping

from tools.xstack.compatx.canonical_json import canonical_sha256


GEO10_REFERENCE_EVALUATOR_IDS = [
    "ref.metric_distance_small",
    "ref.neighborhood_small",
    "ref.overlay_merge_small",
]


def _ensure_repo_root(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


@lru_cache(maxsize=4)
def _scenario_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.geo.geo10_stress_common import DEFAULT_GEO10_SEED, generate_geo_stress_scenario

    return generate_geo_stress_scenario(seed=DEFAULT_GEO10_SEED, include_cctv=True)


def geo10_scenario(repo_root: str) -> dict:
    return copy.deepcopy(_scenario_cached(repo_root))


def _truth_hash_anchor(scenario: Mapping[str, object]) -> str:
    suites = [dict(row) for row in list(scenario.get("topology_suites") or []) if isinstance(row, Mapping)]
    return canonical_sha256(
        {
            "scenario_id": str(scenario.get("scenario_id", "")).strip(),
            "scenario_seed": int(scenario.get("scenario_seed", 0) or 0),
            "suite_fingerprints": [str(row.get("deterministic_fingerprint", "")).strip() for row in suites],
        }
    )


def _suite_by_id(scenario: Mapping[str, object], suite_id: str) -> dict:
    suites = [dict(row) for row in list(scenario.get("topology_suites") or []) if isinstance(row, Mapping)]
    by_id = {
        str(row.get("suite_id", "")).strip(): dict(row)
        for row in sorted(suites, key=lambda item: str(item.get("suite_id", "")))
        if str(row.get("suite_id", "")).strip()
    }
    return copy.deepcopy(dict(by_id.get(str(suite_id).strip()) or {}))


@lru_cache(maxsize=4)
def _stress_report_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.geo.geo10_stress_runtime import verify_geo_stress_scenario

    scenario = copy.deepcopy(_scenario_cached(repo_root))
    return verify_geo_stress_scenario(
        scenario,
        seed=int(scenario.get("scenario_seed", 0) or 0),
    )


def geo10_stress_report(repo_root: str) -> dict:
    return copy.deepcopy(_stress_report_cached(repo_root))


@lru_cache(maxsize=4)
def _overlay_identity_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.geo.tool_verify_overlay_identity import verify_overlay_identity

    return verify_overlay_identity(scenario=copy.deepcopy(_scenario_cached(repo_root)))


def geo10_overlay_identity_report(repo_root: str) -> dict:
    return copy.deepcopy(_overlay_identity_cached(repo_root))


@lru_cache(maxsize=4)
def _replay_report_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from tools.geo.tool_replay_geo_window import replay_geo_window

    return replay_geo_window(scenario=copy.deepcopy(_scenario_cached(repo_root)))


def geo10_replay_report(repo_root: str) -> dict:
    return copy.deepcopy(_replay_report_cached(repo_root))


def geo10_projection_redaction_fixture(repo_root: str, suite_id: str = "geo10.suite.r3_grid") -> dict:
    _ensure_repo_root(repo_root)
    from tools.geo.geo10_stress_runtime import _suite_geometry_and_compaction, _suite_projection_and_views

    scenario = geo10_scenario(repo_root)
    suite = _suite_by_id(scenario, suite_id)
    geometry_data = _suite_geometry_and_compaction(suite=suite, scenario=scenario)
    view_data = _suite_projection_and_views(
        suite=suite,
        geometry_rows=list(geometry_data.get("geometry_rows") or []),
        scenario_truth_anchor=_truth_hash_anchor(scenario),
    )
    return {
        "scenario": scenario,
        "suite": suite,
        "geometry_data": copy.deepcopy(geometry_data),
        "view_data": copy.deepcopy(view_data),
    }


@lru_cache(maxsize=4)
def _reference_suite_cached(repo_root: str) -> dict:
    _ensure_repo_root(repo_root)
    from src.meta.reference import evaluate_reference_suite

    return evaluate_reference_suite(
        evaluator_ids=list(GEO10_REFERENCE_EVALUATOR_IDS),
        state_payload={},
        current_tick=3,
        seed=1107,
        tick_start=0,
        tick_end=3,
        configs_by_evaluator_id={},
    )


def geo10_reference_suite(repo_root: str) -> dict:
    return copy.deepcopy(_reference_suite_cached(repo_root))
