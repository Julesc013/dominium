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

    from meta.explain import cached_explain_artifact, generate_explain_artifact

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

    from tools.xstack.testx.tests.sys7_testlib import (
        base_state as sys7_base_state,
        execute_system_explain,
        seed_reliability_events,
    )

    state_a = sys7_base_state()
    state_b = sys7_base_state()
    health_a, reliability_a = seed_reliability_events(repo_root=repo_root, state=state_a)
    health_b, reliability_b = seed_reliability_events(repo_root=repo_root, state=state_b)
    if str(health_a.get("result", "")).strip() != "complete" or str(reliability_a.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-7 setup failed for first deterministic run"}
    if str(health_b.get("result", "")).strip() != "complete" or str(reliability_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-7 setup failed for second deterministic run"}

    system_id = str(((state_a.get("system_rows") or [{}])[0]).get("system_id", "")).strip()
    if not system_id:
        return {"status": "fail", "message": "SYS-7 deterministic run missing system_id"}

    sys7_a = execute_system_explain(
        repo_root=repo_root,
        state=state_a,
        system_id=system_id,
        explain_level="L2",
        requester_policy_id="policy.epistemic.admin",
        requester_subject_id="admin.sys7",
    )
    sys7_b = execute_system_explain(
        repo_root=repo_root,
        state=state_b,
        system_id=system_id,
        explain_level="L2",
        requester_policy_id="policy.epistemic.admin",
        requester_subject_id="admin.sys7",
    )
    if str(sys7_a.get("result", "")).strip() != "complete" or str(sys7_b.get("result", "")).strip() != "complete":
        return {"status": "fail", "message": "SYS-7 process.system_generate_explain deterministic runs did not complete"}

    explain_id_a = str(sys7_a.get("sys7_explain_id", "")).strip()
    explain_id_b = str(sys7_b.get("sys7_explain_id", "")).strip()
    if not explain_id_a or not explain_id_b:
        return {"status": "fail", "message": "SYS-7 explain_id missing from system explain helper result"}
    if explain_id_a != explain_id_b:
        return {"status": "fail", "message": "SYS-7 explain_id drifted across equivalent runs"}

    chain_a = str(state_a.get("system_explain_hash_chain", "")).strip().lower()
    chain_b = str(state_b.get("system_explain_hash_chain", "")).strip().lower()
    if (not _SHA256.fullmatch(chain_a)) or (not _SHA256.fullmatch(chain_b)):
        return {"status": "fail", "message": "SYS-7 system_explain_hash_chain missing/invalid"}
    if chain_a != chain_b:
        return {"status": "fail", "message": "SYS-7 system_explain_hash_chain drifted across equivalent runs"}
    return {"status": "pass", "message": "explain artifact generation is deterministic"}
