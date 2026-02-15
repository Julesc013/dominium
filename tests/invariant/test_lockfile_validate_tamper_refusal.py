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
    parser = argparse.ArgumentParser(description="Invariant: tampered lockfile must be rejected.")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source_repo = os.path.abspath(args.repo_root)
    if source_repo not in sys.path:
        sys.path.insert(0, source_repo)

    from tools.xstack.registry_compile.compiler import compile_bundle
    from tools.xstack.registry_compile.lockfile import validate_lockfile_payload

    tmp_repo = make_temp_repo_fixture(source_repo)
    try:
        lock_rel = "build/lockfile.json"
        result = compile_bundle(
            repo_root=tmp_repo,
            bundle_id="bundle.base.lab",
            out_dir_rel="build/registries",
            lockfile_out_rel=lock_rel,
            packs_root_rel="packs",
            schema_repo_root=source_repo,
        )
        if result.get("result") != "complete":
            print("compile failed")
            return 1

        lock_path = os.path.join(tmp_repo, lock_rel.replace("/", os.sep))
        payload = _read_json(lock_path)
        if not isinstance(payload, dict):
            print("lockfile payload invalid")
            return 1
        resolved = payload.get("resolved_packs") or []
        if not resolved:
            print("lockfile missing resolved packs")
            return 1
        resolved[0]["pack_id"] = "pack.test.tampered"
        _write_json(lock_path, payload)

        validation = validate_lockfile_payload(payload)
        if validation.get("result") != "refused":
            print("tampered lockfile was not rejected")
            return 1
        codes = [str(row.get("code", "")) for row in (validation.get("errors") or [])]
        if "refuse.lockfile.pack_lock_hash_mismatch" not in codes:
            print("missing pack_lock_hash mismatch refusal code")
            return 1
    finally:
        shutil.rmtree(tmp_repo, ignore_errors=True)

    print("tampered lockfile refusal OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

