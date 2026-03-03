"""FAST test: exception_event schema is registered and example-valid."""

from __future__ import annotations

import sys


TEST_ID = "testx.physics.exception_event_schema_valid"
TEST_TAGS = ["fast", "physics", "schema"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_schema_example

    result = validate_schema_example(repo_root, "exception_event")
    if not bool(result.get("valid", False)):
        return {"status": "fail", "message": "exception_event schema example invalid"}
    return {"status": "pass", "message": "exception_event schema example valid"}
