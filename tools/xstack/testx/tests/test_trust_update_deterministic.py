"""FAST test: SIG-5 trust updates are deterministic for identical inputs."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.trust_update_deterministic"
TEST_TAGS = ["fast", "signals", "trust", "determinism"]


def _belief_registry() -> dict:
    return {
        "record": {
            "belief_policies": [
                {
                    "schema_version": "1.0.0",
                    "belief_policy_id": "belief.default",
                    "acceptance_threshold": 0.5,
                    "decay_rate_per_tick": 0.0,
                    "update_rule_id": "update.linear_adjust",
                    "extensions": {},
                }
            ]
        }
    }


def _update_rule_registry() -> dict:
    return {
        "record": {
            "trust_update_rules": [
                {
                    "schema_version": "1.0.0",
                    "update_rule_id": "update.linear_adjust",
                    "description": "deterministic linear adjustment",
                    "extensions": {
                        "model": "linear_adjust",
                        "delta_verified": 0.1,
                        "delta_disputed": -0.08,
                        "delta_failed": -0.15,
                    },
                }
            ]
        }
    }


def _run_once() -> dict:
    from src.signals import build_verification_result, process_trust_update

    verification_row = build_verification_result(
        result_id="verification.test.det.001",
        artifact_id="artifact.test.det.001",
        verifier_subject_id="subject.verifier",
        verification_state="verified",
        extensions={},
    )
    out = process_trust_update(
        current_tick=50,
        from_subject_id="subject.receiver",
        to_subject_id="subject.sender",
        verification_result_row=verification_row,
        trust_edge_rows=[
            {
                "from_subject_id": "subject.receiver",
                "to_subject_id": "subject.sender",
                "trust_weight": 0.4,
                "evidence_count": 2,
                "last_updated_tick": 40,
                "extensions": {},
            }
        ],
        belief_policy_registry=_belief_registry(),
        trust_update_rule_registry=_update_rule_registry(),
        belief_policy_id="belief.default",
        decision_log_rows=[],
    )
    return {
        "trust_edge_rows": list(out.get("trust_edge_rows") or []),
        "updated_edge_row": dict(out.get("updated_edge_row") or {}),
        "decision_log_entry": dict(out.get("decision_log_entry") or {}),
    }


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    first = _run_once()
    second = _run_once()
    if first != second:
        return {"status": "fail", "message": "trust update output drifted across identical runs"}
    row = dict(first.get("updated_edge_row") or {})
    if not row:
        return {"status": "fail", "message": "missing updated trust edge row"}
    if float(row.get("trust_weight", 0.0)) <= 0.4:
        return {"status": "fail", "message": "verified update should increase trust weight"}
    return {"status": "pass", "message": "trust update deterministic"}
