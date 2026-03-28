"""Shared fixtures for PACK-COMPAT-0 TestX coverage."""

from __future__ import annotations

import json
import os
import shutil
import sys
from typing import Callable


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def make_temp_pack_compat_repo(repo_root: str) -> str:
    from testlib import make_temp_repo_with_test_packs

    return make_temp_repo_with_test_packs(repo_root)


def cleanup_temp_repo(path: str) -> None:
    shutil.rmtree(path, ignore_errors=True)


def read_json(path: str) -> dict:
    return json.load(open(path, "r", encoding="utf-8"))


def write_json(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _descriptor_hash(payload: dict) -> str:
    from packs.compat.pack_compat_validator import pack_compat_manifest_fingerprint

    return pack_compat_manifest_fingerprint(payload)


def _find_pack_dir(repo_root: str, pack_id: str) -> str:
    for root, _dirs, files in os.walk(os.path.join(repo_root, "packs")):
        if "pack.json" not in files:
            continue
        payload = read_json(os.path.join(root, "pack.json"))
        if str(payload.get("pack_id", "")).strip() == str(pack_id).strip():
            return root
    raise FileNotFoundError("unable to locate pack {}".format(pack_id))


def pack_compat_path(repo_root: str, pack_id: str) -> str:
    return os.path.join(_find_pack_dir(repo_root, pack_id), "pack.compat.json")


def remove_pack_compat(repo_root: str, pack_id: str) -> None:
    path = pack_compat_path(repo_root, pack_id)
    if os.path.isfile(path):
        os.remove(path)


def mutate_pack_compat(repo_root: str, pack_id: str, mutator: Callable[[dict], dict]) -> str:
    path = pack_compat_path(repo_root, pack_id)
    payload = read_json(path)
    payload = dict(mutator(dict(payload)) or {})
    payload["deterministic_fingerprint"] = _descriptor_hash(payload)
    write_json(path, payload)
    return path


def compile_fixture_bundle(source_repo_root: str, temp_repo: str, mod_policy_id: str = "mod_policy.lab") -> dict:
    from tools.xstack.registry_compile.compiler import compile_bundle

    return compile_bundle(
        repo_root=temp_repo,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/pack_compat/registries",
        lockfile_out_rel="build/pack_compat/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=source_repo_root,
        mod_policy_id=mod_policy_id,
        use_cache=False,
    )


def load_fixture_lockfile(temp_repo: str) -> dict:
    return read_json(os.path.join(temp_repo, "build", "pack_compat", "lockfile.json"))
