"""TestX registry compile deterministic smoke check."""

from __future__ import annotations

import os
import shutil
import sys

TEST_ID = "testx.registry.compile"
TEST_TAGS = ["smoke", "registry"]


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)
    from testlib import make_temp_repo_with_test_packs
    from tools.xstack.registry_compile.compiler import compile_bundle

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
            return {"status": "fail", "message": "compile_bundle failed in fixture repo"}
        lock_path = os.path.join(temp_repo, "build", "lockfile.json")
        if not os.path.isfile(lock_path):
            return {"status": "fail", "message": "missing fixture lockfile output"}
    finally:
        shutil.rmtree(temp_repo, ignore_errors=True)

    return {"status": "pass", "message": "registry compile smoke passed"}
