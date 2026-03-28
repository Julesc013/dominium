"""FAST test: SIG-5 message verification produces trust updates."""

from __future__ import annotations

import sys


TEST_ID = "testx.signals.verification_updates_trust"
TEST_TAGS = ["fast", "signals", "trust", "verification"]


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


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from signals import process_message_verify_claim

    initial_trust = 0.45
    out = process_message_verify_claim(
        current_tick=140,
        artifact_id="artifact.sig.verify.001",
        verifier_subject_id="subject.receiver",
        claimed_sender_subject_id="subject.sender",
        evidence_artifact_rows=[
            {
                "artifact_id": "artifact.obs.001",
                "artifact_family_id": "INFO.OBSERVATION",
                "extensions": {
                    "claim_artifact_id": "artifact.sig.verify.001",
                    "sender_subject_id": "subject.sender",
                },
            }
        ],
        verification_result_rows=[],
        trust_edge_rows=[
            {
                "from_subject_id": "subject.receiver",
                "to_subject_id": "subject.sender",
                "trust_weight": initial_trust,
                "evidence_count": 0,
                "last_updated_tick": 0,
                "extensions": {},
            }
        ],
        belief_policy_registry=_belief_registry(),
        trust_update_rule_registry=_update_rule_registry(),
        belief_policy_id="belief.default",
        decision_log_rows=[],
    )
    verification_row = dict(out.get("verification_result_row") or {})
    if str(verification_row.get("verification_state", "")).strip() != "verified":
        return {"status": "fail", "message": "verification should resolve to verified with matching observation evidence"}
    updated_edge = dict(out.get("updated_trust_edge_row") or {})
    if not updated_edge:
        return {"status": "fail", "message": "verification should trigger trust update"}
    if float(updated_edge.get("trust_weight", 0.0)) <= initial_trust:
        return {"status": "fail", "message": "verified claim should increase trust weight"}
    return {"status": "pass", "message": "verification updates trust deterministically"}
