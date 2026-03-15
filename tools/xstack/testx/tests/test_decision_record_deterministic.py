"""FAST test: migration decision records are deterministic for identical inputs."""

from __future__ import annotations

import json


TEST_ID = "test_decision_record_deterministic"
TEST_TAGS = ["fast", "compat", "migration", "determinism"]


def run(repo_root: str):
    from tools.xstack.testx.tests.migration_lifecycle_testlib import (
        blueprint_migrate_decision,
        blueprint_migrate_decision_for_path,
        path_variant_blueprint_decisions_stable,
        repeated_blueprint_decisions_match,
    )

    left = blueprint_migrate_decision(repo_root)
    right = blueprint_migrate_decision(repo_root)
    path_left = blueprint_migrate_decision_for_path(repo_root, "build/tmp/a/blueprint.json")
    path_right = blueprint_migrate_decision_for_path(repo_root, "build/tmp/b/blueprint.json")
    if not repeated_blueprint_decisions_match(repo_root):
        return {"status": "fail", "message": "migration decision record payload drifted across repeated identical runs"}
    if str(left.get("deterministic_fingerprint", "")).strip() != str(right.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "migration decision fingerprint drifted across repeated identical runs"}
    if json.dumps(left, sort_keys=True) != json.dumps(right, sort_keys=True):
        return {"status": "fail", "message": "migration decision JSON drifted across repeated identical runs"}
    if str(path_left.get("decision_record_id", "")).strip() != str(path_right.get("decision_record_id", "")).strip():
        return {"status": "fail", "message": "migration decision id changed across path-only diagnostic differences"}
    if str(path_left.get("deterministic_fingerprint", "")).strip() != str(path_right.get("deterministic_fingerprint", "")).strip():
        return {"status": "fail", "message": "migration decision fingerprint changed across path-only diagnostic differences"}
    if not path_variant_blueprint_decisions_stable(repo_root):
        return {"status": "fail", "message": "migration decision payload changed across path-only diagnostic differences"}
    return {"status": "pass", "message": "migration decision records are deterministic"}
