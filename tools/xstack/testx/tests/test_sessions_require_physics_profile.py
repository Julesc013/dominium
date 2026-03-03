"""FAST test: SessionSpec schema requires top-level physics_profile_id."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.physics.sessions_require_profile"
TEST_TAGS = ["fast", "physics", "schema", "session"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_instance

    example_path = os.path.join(repo_root, "schemas", "examples", "session_spec.example.json")
    try:
        payload = json.load(open(example_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid session_spec example fixture"}

    valid_result = validate_instance(
        repo_root=repo_root,
        schema_name="session_spec",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(valid_result.get("valid", False)):
        return {"status": "fail", "message": "session_spec example should validate with physics_profile_id"}

    missing_payload = dict(payload)
    missing_payload.pop("physics_profile_id", None)
    invalid_result = validate_instance(
        repo_root=repo_root,
        schema_name="session_spec",
        payload=missing_payload,
        strict_top_level=True,
    )
    if bool(invalid_result.get("valid", True)):
        return {"status": "fail", "message": "session_spec must refuse payloads missing physics_profile_id"}

    return {"status": "pass", "message": "session_spec physics_profile_id requirement enforced"}
