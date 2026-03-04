"""FAST test: explain artifact generation is deterministic for equivalent inputs."""

from __future__ import annotations

import re
import sys


TEST_ID = "test_explain_artifact_deterministic"
TEST_TAGS = ["fast", "meta", "contracts", "explain", "determinism"]


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from src.meta.explain import cached_explain_artifact, generate_explain_artifact

    build_inputs = {
        "event_id": "event.elec.trip.001",
        "target_id": "assembly.breaker.main",
        "event_kind_id": "elec.trip",
        "truth_hash_anchor": "truth.hash.anchor.001",
        "epistemic_policy_id": "policy.epistemic.observer",
        "explain_contract_row": {
            "contract_id": "explain.elec.trip",
            "event_kind_id": "elec.trip",
            "explain_artifact_type_id": "artifact.explain.elec_trip",
            "required_inputs": ["artifact.decision", "artifact.record"],
            "remediation_hint_keys": ["hint.inspect.breaker_panel", "hint.reduce.load"],
        },
        "decision_log_rows": [{"decision_id": "decision.trip.1", "kind_id": "trip"}],
        "safety_event_rows": [{"event_id": "event.trip.1", "event_kind_id": "elec.trip"}],
        "hazard_rows": [{"event_id": "hazard.overload.1", "event_kind_id": "overload"}],
        "compliance_rows": [{"result_id": "compliance.elec.1", "kind_id": "spec"}],
        "model_result_rows": [{"result_id": "model.elec.1", "kind_id": "model"}],
    }

    first = generate_explain_artifact(**build_inputs)
    second = generate_explain_artifact(**build_inputs)
    if not first or not second:
        return {"status": "fail", "message": "explain artifact generation returned empty payload"}
    if dict(first) != dict(second):
        return {"status": "fail", "message": "explain artifact generation drifted across equivalent inputs"}
    if str(first.get("explain_id", "")).strip() != str(second.get("explain_id", "")).strip():
        return {"status": "fail", "message": "explain_id drifted across equivalent inputs"}

    fingerprint = str(first.get("deterministic_fingerprint", "")).strip().lower()
    if not _SHA256.fullmatch(fingerprint):
        return {"status": "fail", "message": "deterministic_fingerprint missing/invalid"}

    cache_a = cached_explain_artifact(
        cache_rows=[],
        event_id="event.elec.trip.001",
        truth_hash_anchor="truth.hash.anchor.001",
        epistemic_policy_id="policy.epistemic.observer",
        build_inputs=build_inputs,
    )
    cache_b = cached_explain_artifact(
        cache_rows=list(cache_a.get("cache_rows") or []),
        event_id="event.elec.trip.001",
        truth_hash_anchor="truth.hash.anchor.001",
        epistemic_policy_id="policy.epistemic.observer",
        build_inputs=build_inputs,
    )
    if bool(cache_b.get("cache_hit", False)) is not True:
        return {"status": "fail", "message": "second explain cache lookup should be a hit"}
    if dict(cache_a.get("artifact") or {}) != dict(cache_b.get("artifact") or {}):
        return {"status": "fail", "message": "cached explain artifact payload drifted"}
    return {"status": "pass", "message": "explain artifact generation is deterministic"}

