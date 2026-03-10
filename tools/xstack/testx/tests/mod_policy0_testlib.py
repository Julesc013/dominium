"""Shared fixtures for MOD-POLICY-0 TestX coverage."""

from __future__ import annotations

import json
import os
import shutil
import sys


def ensure_repo_on_path(repo_root: str) -> None:
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    if test_dir not in sys.path:
        sys.path.insert(0, test_dir)


def make_temp_mod_policy_repo(repo_root: str) -> str:
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
    from tools.xstack.compatx.canonical_json import canonical_sha256

    body = dict(payload)
    body["deterministic_fingerprint"] = ""
    return canonical_sha256(body)


def _pack_descriptor_path(temp_repo: str, pack_id: str, filename: str) -> str:
    rel = pack_id.replace(".", os.sep)
    pack_dir = os.path.join(temp_repo, "packs", *pack_id.split("."))
    if os.path.isdir(pack_dir):
        return os.path.join(pack_dir, filename)
    candidates = []
    packs_root = os.path.join(temp_repo, "packs")
    for root, _dirs, files in os.walk(packs_root):
        if filename not in files:
            continue
        payload = read_json(os.path.join(root, filename))
        if str(payload.get("pack_id", "")).strip() == pack_id:
            candidates.append(os.path.join(root, filename))
    if len(candidates) == 1:
        return candidates[0]
    raise FileNotFoundError("unable to locate {} for {}".format(filename, pack_id))


def rewrite_pack_trust(temp_repo: str, pack_id: str, trust_level_id: str) -> str:
    path = _pack_descriptor_path(temp_repo, pack_id, "pack.trust.json")
    payload = read_json(path)
    payload["trust_level_id"] = str(trust_level_id)
    payload["deterministic_fingerprint"] = _descriptor_hash(payload)
    write_json(path, payload)
    return path


def rewrite_pack_capabilities(
    temp_repo: str,
    pack_id: str,
    capability_ids: list[str],
    *,
    extensions: dict | None = None,
) -> str:
    path = _pack_descriptor_path(temp_repo, pack_id, "pack.capabilities.json")
    payload = read_json(path)
    payload["capability_ids"] = sorted(set(str(item).strip() for item in list(capability_ids or []) if str(item).strip()))
    payload["extensions"] = dict(sorted(dict(extensions or payload.get("extensions") or {}).items(), key=lambda item: str(item[0])))
    payload["deterministic_fingerprint"] = _descriptor_hash(payload)
    write_json(path, payload)
    return path


def compile_fixture_bundle(source_repo_root: str, temp_repo: str, mod_policy_id: str) -> dict:
    from tools.xstack.registry_compile.compiler import compile_bundle

    return compile_bundle(
        repo_root=temp_repo,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/mod_policy/registries",
        lockfile_out_rel="build/mod_policy/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=source_repo_root,
        mod_policy_id=mod_policy_id,
        use_cache=False,
    )


def load_fixture_lockfile(temp_repo: str) -> dict:
    return read_json(os.path.join(temp_repo, "build", "mod_policy", "lockfile.json"))
