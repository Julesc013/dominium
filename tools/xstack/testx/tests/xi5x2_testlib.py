"""FAST Xi-5x2 TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.xi5x2_common import (
    XI5X2_BATCH_PLAN_REL,
    XI5X2_BLOCKER_DELTA_REL,
    XI5X2_CLASSIFICATION_LOCK_REL,
    XI5X2_EXECUTION_LOG_REL,
    XI5X2_POSTMOVE_RESIDUAL_REPORT_REL,
    XI5X2_XI6_GATE_MODEL_REL,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def committed_classification_lock(repo_root: str) -> dict:
    return _load_json(repo_root, XI5X2_CLASSIFICATION_LOCK_REL)


def committed_batch_plan(repo_root: str) -> dict:
    return _load_json(repo_root, XI5X2_BATCH_PLAN_REL)


def committed_execution_log(repo_root: str) -> dict:
    return _load_json(repo_root, XI5X2_EXECUTION_LOG_REL)


def committed_postmove_report(repo_root: str) -> dict:
    return _load_json(repo_root, XI5X2_POSTMOVE_RESIDUAL_REPORT_REL)


def committed_xi6_gate_model(repo_root: str) -> dict:
    return _load_json(repo_root, XI5X2_XI6_GATE_MODEL_REL)


def committed_blocker_delta(repo_root: str) -> dict:
    return _load_json(repo_root, XI5X2_BLOCKER_DELTA_REL)


def recompute_fingerprint(payload: dict) -> str:
    clone = dict(payload)
    clone["deterministic_fingerprint"] = ""
    return canonical_sha256(clone)
