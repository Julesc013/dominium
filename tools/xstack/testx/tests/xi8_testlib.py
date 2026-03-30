from __future__ import annotations

import json
import os
import sys


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT_HINT = os.path.normpath(os.path.join(THIS_DIR, "..", "..", "..", ".."))
if REPO_ROOT_HINT not in sys.path:
    sys.path.insert(0, REPO_ROOT_HINT)


from tools.review.xi8_common import (
    AUDITX_DETECTOR_IDS,
    REPOSITORY_STRUCTURE_LOCK_REL,
    REPOX_RULE_IDS,
    build_repository_structure_snapshot,
    recompute_structure_lock_content_hash,
    recompute_structure_lock_fingerprint,
)


EXPECTED_STAGE_ORDER = ["repox", "auditx", "testx", "validation_and_omega"]


def _read_json(repo_root: str, rel_path: str) -> dict:
    with open(os.path.join(repo_root, rel_path.replace("/", os.sep)), "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def committed_structure_lock(repo_root: str) -> dict:
    return _read_json(repo_root, REPOSITORY_STRUCTURE_LOCK_REL)


def committed_gate_definitions(repo_root: str) -> dict:
    return _read_json(repo_root, "data/xstack/gate_definitions.json")


def committed_profile(repo_root: str, profile_id: str) -> dict:
    return _read_json(repo_root, "tools/xstack/ci/profiles/{}.json".format(str(profile_id).strip().upper()))


def committed_ci_run_report(repo_root: str) -> dict:
    return _read_json(repo_root, "data/audit/ci_run_report.json")


def live_snapshot(repo_root: str) -> dict:
    return build_repository_structure_snapshot(repo_root)


__all__ = [
    "AUDITX_DETECTOR_IDS",
    "EXPECTED_STAGE_ORDER",
    "REPOX_RULE_IDS",
    "committed_ci_run_report",
    "committed_gate_definitions",
    "committed_profile",
    "committed_structure_lock",
    "live_snapshot",
    "recompute_structure_lock_content_hash",
    "recompute_structure_lock_fingerprint",
]
