"""FAST XI-5a-v4 TestX helpers."""

from __future__ import annotations

import json
import os

from tools.review.xi5a_v4_execute_common import (
    XI5A_ATTIC_MAP_REL,
    XI5A_EXECUTION_LOG_REL,
    XI5A_MOVE_MAP_REL,
    XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL,
)
from tools.xstack.compatx.canonical_json import canonical_sha256


def _load_json(repo_root: str, rel_path: str) -> dict:
    path = os.path.join(os.path.abspath(repo_root), rel_path.replace("/", os.sep))
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise AssertionError(f"{rel_path} is not a JSON object")
    return payload


def committed_move_map(repo_root: str) -> dict:
    return _load_json(repo_root, XI5A_MOVE_MAP_REL)


def committed_attic_map(repo_root: str) -> dict:
    return _load_json(repo_root, XI5A_ATTIC_MAP_REL)


def committed_execution_log(repo_root: str) -> dict:
    return _load_json(repo_root, XI5A_EXECUTION_LOG_REL)


def committed_residual_report(repo_root: str) -> dict:
    return _load_json(repo_root, XI5A_POSTMOVE_RESIDUAL_SRC_REPORT_REL)


def recompute_fingerprint(payload: dict) -> str:
    clone = dict(payload)
    clone["deterministic_fingerprint"] = ""
    return canonical_sha256(clone)
