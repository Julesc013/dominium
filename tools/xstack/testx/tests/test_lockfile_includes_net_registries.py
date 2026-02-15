"""FAST test: lockfile registries include multiplayer policy registry hashes."""

from __future__ import annotations

import json
import os
import re
import sys


TEST_ID = "testx.net.lockfile_includes_net_registries"
TEST_TAGS = ["smoke", "lockfile", "net"]


SHA256_RE = re.compile(r"^[A-Fa-f0-9]{64}$")


def run(repo_root: str):
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from tools.xstack.registry_compile.compiler import compile_bundle

    result = compile_bundle(
        repo_root=repo_root,
        bundle_id="bundle.base.lab",
        out_dir_rel="build/registries",
        lockfile_out_rel="build/lockfile.json",
        packs_root_rel="packs",
        schema_repo_root=repo_root,
        use_cache=True,
    )
    if result.get("result") != "complete":
        return {"status": "fail", "message": "compile_bundle failed before lockfile checks"}

    lock_path = os.path.join(repo_root, "build", "lockfile.json")
    try:
        lock_payload = json.load(open(lock_path, "r", encoding="utf-8"))
    except (OSError, ValueError):
        return {"status": "fail", "message": "build/lockfile.json missing or invalid"}

    registries = lock_payload.get("registries")
    if not isinstance(registries, dict):
        return {"status": "fail", "message": "lockfile registries object missing"}

    required = [
        "net_replication_policy_registry_hash",
        "net_resync_strategy_registry_hash",
        "net_server_policy_registry_hash",
        "shard_map_registry_hash",
        "perception_interest_policy_registry_hash",
        "anti_cheat_policy_registry_hash",
        "anti_cheat_module_registry_hash",
    ]
    for key in required:
        value = str(registries.get(key, "")).strip()
        if not SHA256_RE.fullmatch(value):
            return {"status": "fail", "message": "lockfile registries missing valid '{}'".format(key)}

    return {"status": "pass", "message": "lockfile contains multiplayer registry hashes"}
