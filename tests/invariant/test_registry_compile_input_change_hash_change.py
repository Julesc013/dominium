import argparse
import json
import os
import shutil
import sys

from registry_compile_testlib import make_temp_repo_fixture


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _write_json(path: str, payload: dict) -> None:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Invariant: pack changes must change lockfile and registry hashes.")
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
            print("first compile failed")
            return 1
        lock_path = os.path.join(tmp_repo, lock_rel.replace("/", os.sep))
        lock1 = _read_json(lock_path)
        hash1 = str(lock1.get("pack_lock_hash", ""))
        domain_hash1 = str((lock1.get("registries") or {}).get("domain_registry_hash", ""))

        manifest_path = os.path.join(
            tmp_repo,
            "packs",
            "domain",
            "pack.test.domain",
            "pack.json",
        )
        payload = _read_json(manifest_path)
        payload["canonical_hash"] = "placeholder.pack.test.domain.v2"
        _write_json(manifest_path, payload)

        second = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel=out_rel,
            lockfile_out_rel=lock_rel,
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        if second.get("result") != "complete":
            print("second compile failed")
            return 1
        lock2 = _read_json(lock_path)
        hash2 = str(lock2.get("pack_lock_hash", ""))
        domain_hash2 = str((lock2.get("registries") or {}).get("domain_registry_hash", ""))

        if hash1 == hash2:
            print("pack_lock_hash did not change after pack manifest change")
            return 1
        if domain_hash1 == domain_hash2:
            print("domain registry hash did not change after pack manifest change")
            return 1
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print("registry compile input-change hash propagation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

