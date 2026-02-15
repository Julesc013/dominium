"""TestX lockfile validation + tamper refusal check."""

from __future__ import annotations

import json
import os
import shutil
import sys

TEST_ID = "testx.lockfile.validate"
TEST_TAGS = ["smoke", "lockfile", "registry"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)
    from testlib import make_temp_repo_with_test_packs
    from tools.xstack.registry_compile.compiler import compile_bundle
    from tools.xstack.registry_compile.lockfile import validate_lockfile_payload

    temp_repo = make_temp_repo_with_test_packs(repo_root)
    try:
        result = compile_bundle(
            repo_root=temp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel="build/registries",
            lockfile_out_rel="build/lockfile.json",
            packs_root_rel="packs",
            schema_repo_root=repo_root,
            use_cache=True,
        )
        if result.get("result") != "complete":
            return {"status": "fail", "message": "compile failed before lockfile validation"}
        lock_path = os.path.join(temp_repo, "build", "lockfile.json")
        payload = json.load(open(lock_path, "r", encoding="utf-8"))
        valid = validate_lockfile_payload(payload if isinstance(payload, dict) else {})
        if valid.get("result") != "complete":
            return {"status": "fail", "message": "lockfile payload should be valid before tamper"}
        resolved = payload.get("resolved_packs") or []
        if not resolved:
            return {"status": "fail", "message": "missing resolved_packs in fixture lockfile"}
        resolved[0]["pack_id"] = "pack.test.tampered"
        invalid = validate_lockfile_payload(payload)
        if invalid.get("result") != "refused":
            return {"status": "fail", "message": "tampered lockfile should be refused"}
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)

    return {"status": "pass", "message": "lockfile validation checks passed"}
