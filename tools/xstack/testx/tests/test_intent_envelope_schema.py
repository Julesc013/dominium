"""FAST test: intent envelope schema validation and deterministic hashing."""

from __future__ import annotations

import sys


TEST_ID = "testx.srz.intent_envelope_schema"
TEST_TAGS = ["smoke", "schema", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.canonical_json import canonical_sha256
    from tools.xstack.compatx.validator import validate_instance
    from tools.xstack.sessionx.srz import build_intent_envelopes

    envelopes = build_intent_envelopes(
        intents=[
            {
                "intent_id": "intent.test.0001",
                "process_id": "process.camera_teleport",
                "inputs": {"target_object_id": "object.earth"},
            }
        ],
        authority_origin="client",
        source_shard_id="shard.0",
        target_shard_id="shard.0",
        starting_tick=0,
    )
    if len(envelopes) != 1:
        return {"status": "fail", "message": "expected one intent envelope from one intent input"}
    envelope = dict(envelopes[0] or {})
    valid = validate_instance(
        repo_root=repo_root,
        schema_name="intent_envelope",
        payload=envelope,
        strict_top_level=True,
    )
    if not bool(valid.get("valid", False)):
        return {"status": "fail", "message": "generated intent envelope failed schema validation"}

    first_hash = canonical_sha256(envelope)
    second_hash = canonical_sha256(envelope)
    if str(first_hash) != str(second_hash):
        return {"status": "fail", "message": "intent envelope canonical hash must be deterministic"}
    return {"status": "pass", "message": "intent envelope schema and hash stability check passed"}
