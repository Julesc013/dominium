"""FAST test: multiplayer refusal codes are documented in refusal contract."""

from __future__ import annotations

import os


TEST_ID = "testx.net.refusal_codes_present"
TEST_TAGS = ["smoke", "docs", "net"]


def run(repo_root: str):
    refusal_path = os.path.join(repo_root, "docs", "contracts", "refusal_contract.md")
    try:
        text = open(refusal_path, "r", encoding="utf-8").read()
    except OSError:
        return {"status": "fail", "message": "docs/contracts/refusal_contract.md missing"}

    required_codes = [
        "refusal.net.handshake_pack_lock_mismatch",
        "refusal.net.handshake_registry_hash_mismatch",
        "refusal.net.handshake_schema_version_mismatch",
        "refusal.net.handshake_policy_not_allowed",
        "refusal.net.handshake_securex_denied",
        "refusal.net.envelope_invalid",
        "refusal.net.sequence_violation",
        "refusal.net.replay_detected",
        "refusal.net.authority_violation",
        "refusal.net.shard_target_invalid",
        "refusal.net.resync_required",
        "refusal.net.resync_snapshot_missing",
        "refusal.net.join_snapshot_invalid",
        "refusal.net.join_policy_mismatch",
        "refusal.ac.policy_violation",
        "refusal.ac.rank_policy_required",
        "refusal.ac.attestation_missing",
        "refusal.agent.unembodied",
        "refusal.agent.ownership_violation",
        "refusal.agent.boundary_cross_forbidden",
        "refusal.cosmetic.forbidden",
        "refusal.cosmetic.unsigned_not_allowed",
        "refusal.cosmetic.not_in_whitelist",
    ]
    for code in required_codes:
        if code not in text:
            return {"status": "fail", "message": "missing refusal code '{}'".format(code)}

    return {"status": "pass", "message": "multiplayer refusal codes documented"}
