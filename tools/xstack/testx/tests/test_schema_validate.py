"""TestX schema validation checks for CompatX integration."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "testx.compatx.schema_validate"
TEST_TAGS = ["smoke", "schema"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from tools.xstack.compatx.validator import validate_instance

    example_path = os.path.join(repo_root, "schemas", "examples", "session_spec.example.json")
    try:
        payload = json.load(open(example_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid session_spec example fixture"}

    good = validate_instance(
        repo_root=repo_root,
        schema_name="session_spec",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(good.get("valid", False)):
        return {"status": "fail", "message": "expected valid session_spec example"}

    mutated = dict(payload)
    mutated["xstack_unknown_flag"] = True
    bad = validate_instance(
        repo_root=repo_root,
        schema_name="session_spec",
        payload=mutated,
        strict_top_level=True,
    )
    if bool(bad.get("valid", True)):
        return {"status": "fail", "message": "unknown top-level field should be refused"}
    return {"status": "pass", "message": "schema validate checks passed"}

