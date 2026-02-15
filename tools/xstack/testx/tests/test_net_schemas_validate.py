"""FAST test: validate all multiplayer net schema examples."""

from __future__ import annotations

import sys


TEST_ID = "testx.net.schemas_validate"
TEST_TAGS = ["smoke", "schema", "net"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_schema_example

    schema_names = [
        "net_intent_envelope",
        "net_tick_intent_list",
        "net_hash_anchor_frame",
        "net_snapshot",
        "net_delta",
        "net_perceived_delta",
        "net_handshake",
        "net_anti_cheat_event",
        "net_server_policy_registry",
    ]
    for schema_name in schema_names:
        result = validate_schema_example(repo_root=repo_root, schema_name=schema_name)
        if not bool(result.get("valid", False)):
            return {
                "status": "fail",
                "message": "schema example validation failed for '{}'".format(schema_name),
            }
    return {"status": "pass", "message": "all multiplayer net schema examples validate"}
