"""STRICT test: FLUID containment proof hash fields are deterministic in control proof bundle."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_proof_hash_stable"
TEST_TAGS = ["strict", "fluid", "proof", "determinism"]

_HASH64 = re.compile(r"^[0-9a-f]{64}$")


def _marker() -> dict:
    base = "4" * 64
    return {
        "control_decision_id": "decision.fluid.proof",
        "control_decision_log_hash": base,
        "control_fidelity_allocation_hash": "5" * 64,
        "control_abstraction_downgrade_hash": "6" * 64,
        "control_view_policy_changes_hash": "7" * 64,
        "control_meta_override_hash": "8" * 64,
    }


def _surface() -> dict:
    return {
        "fluid_flow_hash_chain": "0" * 64,
        "leak_hash_chain": "1" * 64,
        "burst_hash_chain": "2" * 64,
        "relief_event_hash_chain": "3" * 64,
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from control.proof import build_control_proof_bundle_from_markers

    a = build_control_proof_bundle_from_markers(
        tick_start=70,
        tick_end=70,
        decision_markers=[_marker()],
        mobility_proof_surface=_surface(),
        extensions={"source": "test.fluid.proof"},
    )
    b = build_control_proof_bundle_from_markers(
        tick_start=70,
        tick_end=70,
        decision_markers=[_marker()],
        mobility_proof_surface=_surface(),
        extensions={"source": "test.fluid.proof"},
    )
    if a != b:
        return {"status": "fail", "message": "control proof bundle drifted for equivalent FLUID proof inputs"}
    for key in ("fluid_flow_hash_chain", "leak_hash_chain", "burst_hash_chain", "relief_event_hash_chain"):
        token = str(a.get(key, "")).strip().lower()
        if not _HASH64.fullmatch(token):
            return {"status": "fail", "message": "{} missing/invalid in proof bundle".format(key)}
    return {"status": "pass", "message": "fluid containment proof hash fields are deterministic"}
