"""FAST test: multiplayer policy matrix constraints are coherent."""

from __future__ import annotations

import json
import os


TEST_ID = "testx.net.policy_matrix_rules"
TEST_TAGS = ["smoke", "net", "registry"]


def _read_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def _by_id(rows, key):
    out = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        token = str(row.get(key, "")).strip()
        if token:
            out[token] = row
    return out


def run(repo_root: str):
    replication_path = os.path.join(repo_root, "data", "registries", "net_replication_policy_registry.json")
    anti_cheat_path = os.path.join(repo_root, "data", "registries", "anti_cheat_policy_registry.json")
    module_path = os.path.join(repo_root, "data", "registries", "anti_cheat_module_registry.json")
    try:
        replication_payload = _read_json(replication_path)
        anti_cheat_payload = _read_json(anti_cheat_path)
        module_payload = _read_json(module_path)
    except (OSError, ValueError):
        return {"status": "fail", "message": "multiplayer policy registry JSON is missing or invalid"}

    replication = _by_id((((replication_payload.get("record") or {}).get("policies")) or []), "policy_id")
    anti_cheat = _by_id((((anti_cheat_payload.get("record") or {}).get("policies")) or []), "policy_id")
    modules = _by_id((((module_payload.get("record") or {}).get("modules")) or []), "module_id")

    lockstep = dict(replication.get("policy.net.lockstep") or {})
    if not lockstep:
        return {"status": "fail", "message": "policy.net.lockstep is missing"}
    if bool(lockstep.get("allowed_in_ranked", False)) is not True:
        return {"status": "fail", "message": "policy.net.lockstep must explicitly allow ranked"}

    authoritative = dict(replication.get("policy.net.server_authoritative") or {})
    hybrid = dict(replication.get("policy.net.srz_hybrid") or {})
    if not authoritative or not hybrid:
        return {"status": "fail", "message": "required replication policy IDs are missing"}
    if bool(authoritative.get("allowed_in_private_server", False)) is not True:
        return {"status": "fail", "message": "policy.net.server_authoritative must allow private server"}
    if bool(hybrid.get("allowed_in_private_server", False)) is not True:
        return {"status": "fail", "message": "policy.net.srz_hybrid must allow private server"}

    rank_strict = dict(anti_cheat.get("policy.ac.rank_strict") or {})
    if not rank_strict:
        return {"status": "fail", "message": "policy.ac.rank_strict is missing"}
    if bool(rank_strict.get("required_for_ranked", False)) is not True:
        return {"status": "fail", "message": "policy.ac.rank_strict must require ranked enforcement"}

    module_ids = set(modules.keys())
    for policy_id in sorted(anti_cheat.keys()):
        row = dict(anti_cheat.get(policy_id) or {})
        enabled = set(str(item).strip() for item in (row.get("modules_enabled") or []) if str(item).strip())
        if not enabled:
            return {"status": "fail", "message": "anti-cheat policy '{}' must enable at least one module".format(policy_id)}
        if not enabled.issubset(module_ids):
            return {"status": "fail", "message": "anti-cheat policy '{}' has unknown module".format(policy_id)}

    if "ac.module.client_attestation" not in set(str(item).strip() for item in (rank_strict.get("modules_enabled") or [])):
        return {"status": "fail", "message": "policy.ac.rank_strict must include ac.module.client_attestation"}

    return {"status": "pass", "message": "multiplayer policy matrix checks passed"}
