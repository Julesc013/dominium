"""Shared CAP-NEG-4 interop stress helpers."""

from __future__ import annotations

import json
import os
from functools import lru_cache


def ensure_repo_on_path(repo_root: str) -> None:
    from tools.xstack.testx.tests.cap_neg_testlib import ensure_repo_on_path as _ensure_repo_on_path

    _ensure_repo_on_path(repo_root)


@lru_cache(maxsize=4)
def interop_matrix(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.compat.cap_neg4_common import DEFAULT_CAP_NEG4_SEED, generate_interop_matrix

    return generate_interop_matrix(repo_root=repo_root, seed=DEFAULT_CAP_NEG4_SEED)


@lru_cache(maxsize=4)
def interop_stress_report(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.compat.cap_neg4_common import DEFAULT_CAP_NEG4_SEED, run_interop_stress

    matrix = interop_matrix(repo_root)
    return run_interop_stress(repo_root=repo_root, matrix=matrix, seed=DEFAULT_CAP_NEG4_SEED)


@lru_cache(maxsize=4)
def interop_baseline(repo_root: str) -> dict:
    path = os.path.join(repo_root, "data", "regression", "cap_neg_full_baseline.json")
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return dict(payload)


def build_current_baseline(repo_root: str) -> dict:
    ensure_repo_on_path(repo_root)
    from tools.compat.cap_neg4_common import DEFAULT_CAP_NEG4_SEED, build_cap_neg_full_baseline

    return build_cap_neg_full_baseline(
        repo_root=repo_root,
        matrix=interop_matrix(repo_root),
        stress_report=interop_stress_report(repo_root),
        seed=DEFAULT_CAP_NEG4_SEED,
    )


def scenario_row(report: dict, scenario_id: str) -> dict:
    scenario_key = str(scenario_id).strip()
    for row in list(dict(report or {}).get("scenario_reports") or []):
        row_map = dict(row or {})
        if str(row_map.get("scenario_id", "")).strip() == scenario_key:
            return row_map
    raise KeyError("scenario not found: {}".format(scenario_key))
