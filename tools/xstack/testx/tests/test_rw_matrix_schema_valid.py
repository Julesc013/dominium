"""STRICT test: RWAM payload validates against schema and strict top-level rules."""

from __future__ import annotations

import json
import os
import sys


TEST_ID = "test_rw_matrix_schema_valid"
TEST_TAGS = ["strict", "schema", "meta", "affordance", "rwam"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.compatx.validator import validate_instance

    matrix_rel = "data/meta/real_world_affordance_matrix.json"
    matrix_path = os.path.join(repo_root, matrix_rel.replace("/", os.sep))
    if not os.path.isfile(matrix_path):
        return {"status": "fail", "message": "{} missing".format(matrix_rel)}

    try:
        payload = json.load(open(matrix_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "invalid RWAM payload"}

    valid = validate_instance(
        repo_root=repo_root,
        schema_name="real_world_affordance_matrix",
        payload=payload,
        strict_top_level=True,
    )
    if not bool(valid.get("valid", False)):
        return {"status": "fail", "message": "RWAM schema validation failed"}

    mutated = dict(payload)
    mutated["unexpected_top_level"] = True
    invalid = validate_instance(
        repo_root=repo_root,
        schema_name="real_world_affordance_matrix",
        payload=mutated,
        strict_top_level=True,
    )
    if bool(invalid.get("valid", True)):
        return {"status": "fail", "message": "strict top-level validation did not reject unknown field"}

    return {"status": "pass", "message": "RWAM schema validation passed"}
