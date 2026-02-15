import argparse
import hashlib
import os
import shutil
import sys

from registry_compile_testlib import make_temp_repo_fixture


def _hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1 << 16)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _snapshot(dir_path: str):
    rows = {}
    for root, _dirs, files in os.walk(dir_path):
        for name in files:
            abs_path = os.path.join(root, name)
            rel = os.path.relpath(abs_path, dir_path).replace("\\", "/")
            rows[rel] = _hash_file(abs_path)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: registry compile outputs are deterministic across runs.")
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
        if first.get("result") != "complete":
            print("first compile failed: {}".format(first))
            return 1
        snapshot1 = _snapshot(os.path.join(tmp_repo, out_rel.replace("/", os.sep)))
        lock1 = _hash_file(os.path.join(tmp_repo, lock_rel.replace("/", os.sep)))

        shutil.rmtree(os.path.join(tmp_repo, ".xstack_cache"), ignore_errors=True)
        second = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel=out_rel,
            lockfile_out_rel=lock_rel,
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        if second.get("result") != "complete":
            print("second compile failed: {}".format(second))
            return 1
        snapshot2 = _snapshot(os.path.join(tmp_repo, out_rel.replace("/", os.sep)))
        lock2 = _hash_file(os.path.join(tmp_repo, lock_rel.replace("/", os.sep)))

        if snapshot1 != snapshot2 or lock1 != lock2:
            print("registry compile outputs are not deterministic")
            return 1
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print("registry compile deterministic outputs OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

