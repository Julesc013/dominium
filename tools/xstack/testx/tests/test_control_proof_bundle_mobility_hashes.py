"""STRICT test: control proof bundles include deterministic mobility proof hashes."""

from __future__ import annotations

import re
import sys


TEST_ID = "testx.control.proof_bundle_mobility_hashes"
TEST_TAGS = ["strict", "control", "mobility", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _build_once(repo_root: str) -> dict:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from src.control.proof import build_control_proof_bundle_from_markers

    return build_control_proof_bundle_from_markers(
        tick_start=101,
        tick_end=101,
        decision_markers=[
            {
                "control_decision_id": "decision.alpha",
                "control_decision_log_hash": "a" * 64,
                "control_fidelity_allocation_hash": "b" * 64,
                "control_abstraction_downgrade_hash": "c" * 64,
                "control_view_policy_changes_hash": "d" * 64,
                "control_meta_override_hash": "e" * 64,
            }
        ],
        mobility_proof_surface={
            "mobility_event_hash": "1" * 64,
            "congestion_hash": "2" * 64,
            "signal_state_hash": "3" * 64,
            "derailment_hash": "4" * 64,
        },
        extensions={"source": "test"},
    )


def run(repo_root: str):
    first = _build_once(repo_root=repo_root)
    second = _build_once(repo_root=repo_root)
    if dict(first) != dict(second):
        return {"status": "fail", "message": "control proof bundle with mobility hashes is not deterministic"}
    for key in ("mobility_event_hash", "congestion_hash", "signal_state_hash", "derailment_hash"):
        token = str(first.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "control proof bundle missing deterministic {}".format(key)}
    if str(first.get("mobility_event_hash", "")).lower() != "1" * 64:
        return {"status": "fail", "message": "mobility_event_hash changed unexpectedly"}
    if str(first.get("congestion_hash", "")).lower() != "2" * 64:
        return {"status": "fail", "message": "congestion_hash changed unexpectedly"}
    if str(first.get("signal_state_hash", "")).lower() != "3" * 64:
        return {"status": "fail", "message": "signal_state_hash changed unexpectedly"}
    if str(first.get("derailment_hash", "")).lower() != "4" * 64:
        return {"status": "fail", "message": "derailment_hash changed unexpectedly"}
    return {"status": "pass", "message": "control proof bundle deterministically carries mobility proof hashes"}
