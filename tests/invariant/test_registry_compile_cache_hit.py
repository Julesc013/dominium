import argparse
import os
import shutil
import sys

from registry_compile_testlib import make_temp_repo_fixture


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: second compile pass should be cache hit.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo = os.path.abspath(args.repo_root)
    if source_repo not in sys.path:
        sys.path.insert(0, source_repo)

    from tools.xstack.registry_compile.compiler import compile_bundle

    tmp_repo = make_temp_repo_fixture(source_repo)
    try:
        out_rel = "build/registries"
        lock_rel = "build/lockfile.json"
        first = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel=out_rel,
            lockfile_out_rel=lock_rel,
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        second = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel=out_rel,
            lockfile_out_rel=lock_rel,
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        if first.get("result") != "complete" or second.get("result") != "complete":
            print("compile failed: first={}, second={}".format(first, second))
            return 1
        if bool(second.get("cache_hit", False)) is not True:
            print("expected cache hit on second compile")
            return 1
        if str(first.get("cache_key", "")) != str(second.get("cache_key", "")):
            print("cache key mismatch across identical runs")
            return 1
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print("registry compile cache hit OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

